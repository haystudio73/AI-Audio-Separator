// Settings & Hardware Management
const API_BASE = window.BACKEND_API_URL || (window.location.protocol + "//" + (window.location.hostname || "localhost") + ":5000");

function getApiUrl(endpoint) {
  if (!endpoint) return API_BASE;
  if (endpoint.startsWith("http://") || endpoint.startsWith("https://")) return endpoint;
  const clean = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  return `${API_BASE}${clean}`;
}

function getAudioUrl(url) {
  return getApiUrl(url);
}

let systemSettings = {};
let availableModels = [];

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem("app_theme") || "dark";
  document.documentElement.setAttribute("data-bs-theme", savedTheme);
  updateThemeIcon(savedTheme);

  const themeToggleBtn = document.getElementById("theme-toggle");
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-bs-theme");
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-bs-theme", next);
      localStorage.setItem("app_theme", next);
      updateThemeIcon(next);
      // Also update settings on server if available
      saveSettingsToServer({ theme: next });
    });
  }
}

function updateThemeIcon(theme) {
  const icon = document.getElementById("theme-icon");
  if (icon) {
    if (theme === "dark") {
      icon.className = "bi bi-sun-fill text-warning";
    } else {
      icon.className = "bi bi-moon-stars-fill text-primary";
    }
  }
}

// System Hardware Info
async function loadSystemInfo() {
  const apiBadge = document.getElementById("api-status-badge");
  const apiIndicator = document.getElementById("api-status-indicator");
  const apiText = document.getElementById("api-status-text");

  try {
    const res = await fetch(getApiUrl("/api/system_info"));
    const data = await res.json();
    
    // Update API connection indicator
    if (apiBadge && apiIndicator && apiText) {
      apiIndicator.className = "spinner-grow spinner-grow-sm text-success";
      apiText.textContent = "API: Connected (:5000)";
      apiBadge.title = "Backend REST API: http://localhost:5000 · Trạng thái: Đang kết nối tốt";
    }

    const hwText = document.getElementById("hardware-text");
    const hwShort = document.getElementById("hardware-short-text");
    const hwBadge = document.getElementById("hardware-badge");
    const mGpu = document.getElementById("m-gpu-name");
    const mVram = document.getElementById("m-gpu-vram");
    const mCpu = document.getElementById("m-cpu-cores");
    const mCuda = document.getElementById("m-cuda-status");

    if (data.cuda_available) {
      if (hwText) hwText.textContent = `${data.device_name} (${data.vram_free || data.vram_total || "CUDA Ready"})`;
      if (hwShort) {
        // E.g. "RTX 3060", "GTX 1660", or "GPU"
        let shortName = "GPU";
        const m = (data.device_name || "").match(/(RTX\s*\d+\s*(?:Ti|SUPER)?|GTX\s*\d+\s*(?:Ti|SUPER)?|Radeon\s*[\w\d]+|Apple\s*M\d+)/i);
        if (m) {
          shortName = m[0].trim();
        } else {
          shortName = (data.device_name || "").replace(/NVIDIA\s+GeForce\s+/i, "").replace(/NVIDIA\s+/i, "").split("(")[0].trim() || "GPU";
        }
        hwShort.textContent = shortName;
      }
      if (hwBadge) {
        hwBadge.title = `${data.device_name} | VRAM: ${data.vram_free || data.vram_total || 'CUDA'} | Tăng tốc CUDA: Hoạt động`;
      }
      if (mGpu) mGpu.textContent = data.device_name;
      if (mVram) mVram.textContent = `${data.vram_free} free / ${data.vram_total} total`;
      if (mCuda) {
        mCuda.textContent = "Khả dụng (Active)";
        mCuda.className = "badge bg-success-subtle text-success";
      }
    } else {
      if (hwText) hwText.textContent = `CPU Mode (${data.cpu_threads} threads)`;
      if (hwShort) hwShort.textContent = "CPU";
      if (hwBadge) hwBadge.title = `CPU Mode (${data.cpu_threads} threads)`;
      if (mGpu) mGpu.textContent = "Không tìm thấy GPU tương thích";
      if (mVram) mVram.textContent = "N/A";
      if (mCuda) {
        mCuda.textContent = "Không khả dụng";
        mCuda.className = "badge bg-secondary-subtle text-secondary";
      }
    }
    if (mCpu) mCpu.textContent = `${data.cpu_threads} Threads`;
  } catch (err) {
    console.error("Failed to load system info:", err);
    if (apiBadge && apiIndicator && apiText) {
      apiIndicator.className = "spinner-grow spinner-grow-sm text-danger";
      apiText.textContent = "API: Disconnected (:5000)";
      apiBadge.title = "Backend REST API: Mất kết nối (:5000)";
    }
  }
}


// Load Models & Status
async function loadModels() {
  try {
    const res = await fetch(getApiUrl("/api/models"));
    const data = await res.json();
    if (data.success) {
      availableModels = data.models;
      populateModelSelectors();
      renderModelsTable();
    }
  } catch (err) {
    console.error("Failed to load models:", err);
  }
}

function populateModelSelectors() {
  const select = document.getElementById("select-model");
  if (!select) return;

  const savedMode = localStorage.getItem("app_separation_mode") || "quick";
  let currentVal = select.value;
  if (!currentVal) {
    currentVal = (savedMode === "quick") ? "htdemucs.yaml" : (systemSettings.model || "htdemucs.yaml");
  }

  select.innerHTML = "";

  availableModels.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m.id;
    opt.textContent = `${m.name} [${m.badge}] - ${m.sdr}`;
    if (m.id === currentVal) opt.selected = true;
    select.appendChild(opt);
  });

  // Ensure Quick Mode selects htdemucs.yaml if present
  if (savedMode === "quick") {
    const hasDemucs = availableModels.some(m => m.id === "htdemucs.yaml");
    if (hasDemucs) select.value = "htdemucs.yaml";
  }

  updateModelDescription();
  select.addEventListener("change", updateModelDescription);
}


function updateModelDescription() {
  const select = document.getElementById("select-model");
  const descEl = document.getElementById("model-desc");
  if (!select || !descEl) return;

  const m = availableModels.find(x => x.id === select.value);
  if (m) {
    const isVi = currentLang === "vi";
    const descText = isVi ? m.description_vi : m.description_en;
    const downloadBadge = m.is_downloaded
      ? `<span class="badge bg-success-subtle text-success me-1"><i class="bi bi-check2"></i> ${t("status_downloaded")}</span>`
      : `<span class="badge bg-warning-subtle text-warning me-1"><i class="bi bi-cloud-arrow-down"></i> ${t("status_not_downloaded")} (Auto-download)</span>`;
    
    descEl.innerHTML = `${downloadBadge} <strong>${m.architecture}</strong> &bull; ${m.recommended_hardware} &bull; ${m.size_mb} MB<br>${descText}`;
  }
}

function renderModelsTable() {
  const tbody = document.getElementById("models-table-body");
  if (!tbody) return;

  tbody.innerHTML = "";
  availableModels.forEach(m => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>
        <div class="fw-semibold">${m.name}</div>
        <span class="badge bg-info-subtle text-info">${m.badge}</span>
      </td>
      <td><small class="text-secondary">${m.architecture}</small></td>
      <td><span class="badge bg-secondary-subtle text-body">${m.target_stems} Stems</span></td>
      <td>
        ${m.is_downloaded 
          ? `<span class="badge bg-success-subtle text-success"><i class="bi bi-check-circle me-1"></i>${t("status_downloaded")}</span>` 
          : `<span class="badge bg-secondary-subtle text-muted"><i class="bi bi-cloud-arrow-down me-1"></i>${t("status_not_downloaded")}</span>`}
      </td>
      <td class="text-end">
        <button class="btn btn-sm ${m.is_downloaded ? 'btn-outline-secondary' : 'btn-outline-primary'}" 
                onclick="triggerModelDownload('${m.id}')" ${m.is_downloaded ? 'disabled' : ''}>
          <i class="bi bi-download me-1"></i>${t("btn_download_model")}
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function triggerModelDownload(modelId) {
  showToast(`Đang tải mô hình ${modelId}... Vui lòng đợi trong giây lát.`);
  try {
    const res = await fetch(getApiUrl("/api/models/download"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_filename: modelId })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      await loadModels();
    } else {
      showToast(data.error || "Lỗi khi tải mô hình.", "danger");
    }
  } catch (err) {
    showToast("Lỗi kết nối tải mô hình.", "danger");
  }
}

// Load & Save Settings
async function loadSettings() {
  try {
    const res = await fetch(getApiUrl("/api/settings"));
    const data = await res.json();
    if (data.success) {
      systemSettings = data.settings;
      if (document.getElementById("select-device")) {
        document.getElementById("select-device").value = systemSettings.device || "cuda";
      }
      if (document.getElementById("select-format")) {
        document.getElementById("select-format").value = systemSettings.output_format || "WAV";
      }
      if (document.getElementById("pref-device")) {
        document.getElementById("pref-device").value = systemSettings.device || "cuda";
      }
      if (document.getElementById("pref-format")) {
        document.getElementById("pref-format").value = systemSettings.output_format || "WAV";
      }
      if (document.getElementById("pref-autocast")) {
        document.getElementById("pref-autocast").checked = systemSettings.use_autocast !== false;
      }
      if (systemSettings.theme) {
        document.documentElement.setAttribute("data-bs-theme", systemSettings.theme);
        updateThemeIcon(systemSettings.theme);
      }
    }
  } catch (err) {
    console.error("Failed to load settings:", err);
  }
}

async function saveSettingsToServer(settingsObj) {
  try {
    const res = await fetch(getApiUrl("/api/settings"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settingsObj)
    });
    const data = await res.json();
    if (data.success) {
      systemSettings = data.settings;
    }
  } catch (err) {
    console.error("Failed to save settings:", err);
  }
}

// Toast helper
function showToast(message, type = "primary") {
  const toastEl = document.getElementById("liveToast");
  const msgEl = document.getElementById("toast-message");
  if (!toastEl || !msgEl) return;

  toastEl.className = `toast align-items-center text-bg-${type} border-0`;
  msgEl.textContent = message;
  const toast = bootstrap.Toast.getOrCreateInstance(toastEl);
  toast.show();
}

// ── Quick Mode vs Adv Mode Management ────────────────────────────────────────

const QUICK_MODE_PRESETS = {
  model: "htdemucs.yaml",
  device: "cuda",
  output_format: "MP3",
  segment_size: "256",
  overlap: "4"
};

let currentAppMode = localStorage.getItem("app_separation_mode") || "quick";

function applySeparationMode(mode, userInitiated = false) {
  currentAppMode = mode;
  localStorage.setItem("app_separation_mode", mode);

  const quickRadio = document.getElementById("mode-quick");
  const advRadio   = document.getElementById("mode-adv");
  if (quickRadio) quickRadio.checked = (mode === "quick");
  if (advRadio)   advRadio.checked   = (mode === "adv");

  updateModeBannerText();

  const advPanel = document.getElementById("adv-settings-panel");

  if (mode === "quick") {
    // 1-In Quick mode, hide all settings
    if (advPanel) advPanel.classList.add("d-none");

    // Apply exact default settings matching the reference screenshot:
    // HT-Demucs v4, GPU (NVIDIA CUDA), MP3 (320kbps), Segment 256, Overlap 4
    const selectModel   = document.getElementById("select-model");
    const selectDevice  = document.getElementById("select-device");
    const selectFormat  = document.getElementById("select-format");
    const selectSegment = document.getElementById("select-segment");
    const selectOverlap = document.getElementById("select-overlap");

    if (selectModel) {
      const hasDemucs = Array.from(selectModel.options).some(o => o.value === QUICK_MODE_PRESETS.model);
      if (hasDemucs) {
        selectModel.value = QUICK_MODE_PRESETS.model;
      }
      updateModelDescription();
    }

    if (selectDevice) {
      const hasCuda = Array.from(selectDevice.options).some(o => o.value === "cuda");
      selectDevice.value = hasCuda ? QUICK_MODE_PRESETS.device : "cpu";
    }

    if (selectFormat) {
      selectFormat.value = QUICK_MODE_PRESETS.output_format;
    }

    if (selectSegment) {
      selectSegment.value = QUICK_MODE_PRESETS.segment_size;
    }

    if (selectOverlap) {
      selectOverlap.value = QUICK_MODE_PRESETS.overlap;
    }

    if (userInitiated) {
      showToast(t("quick_mode_applied"), "info");
    }
  } else {
    // Adv Mode: Show all settings for full customization
    if (advPanel) advPanel.classList.remove("d-none");

    if (userInitiated) {
      showToast(t("adv_mode_applied"), "primary");
    }
  }
}


function updateModeBannerText() {
  const banner = document.getElementById("mode-banner");
  const bannerIcon = document.getElementById("mode-banner-icon");
  const bannerText = document.getElementById("mode-banner-text");
  if (!banner || !bannerText) return;

  if (currentAppMode === "quick") {
    banner.className = "alert py-2 px-3 mb-3 d-flex align-items-center gap-2 small border-0 rounded-3 shadow-xs";
    banner.style.background = "rgba(13, 202, 240, 0.12)";
    banner.style.color = "var(--bs-info-text-emphasis)";
    if (bannerIcon) bannerIcon.className = "bi bi-lightning-charge-fill text-warning fs-6";
    bannerText.innerHTML = `<strong>Quick Mode:</strong> <span>${t("quick_mode_desc")}</span>`;
  } else {
    banner.className = "alert py-2 px-3 mb-3 d-flex align-items-center gap-2 small border-0 rounded-3 shadow-xs";
    banner.style.background = "rgba(99, 102, 241, 0.12)";
    banner.style.color = "var(--bs-primary-text-emphasis, #6366f1)";
    if (bannerIcon) bannerIcon.className = "bi bi-gear-wide-connected text-primary fs-6";
    bannerText.innerHTML = `<strong>Adv Mode:</strong> <span>${t("adv_mode_desc")}</span>`;
  }
}

function initModeSwitcher() {
  const quickRadio = document.getElementById("mode-quick");
  const advRadio   = document.getElementById("mode-adv");

  if (quickRadio) {
    quickRadio.addEventListener("change", () => {
      if (quickRadio.checked) applySeparationMode("quick", true);
    });
  }

  if (advRadio) {
    advRadio.addEventListener("change", () => {
      if (advRadio.checked) applySeparationMode("adv", true);
    });
  }

  applySeparationMode(currentAppMode, false);
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  applyLanguage(currentLang);
  loadSystemInfo();
  initModeSwitcher();

  loadSettings()
    .then(() => loadModels())
    .then(() => {
      // Re-apply separation mode presets once all models are loaded
      applySeparationMode(currentAppMode, false);
    });

  // Save preferences button in modal
  const saveBtn = document.getElementById("btn-save-pref");
  if (saveBtn) {
    saveBtn.addEventListener("click", async () => {
      const dev = document.getElementById("pref-device").value;
      const fmt = document.getElementById("pref-format").value;
      const autocast = document.getElementById("pref-autocast").checked;

      await saveSettingsToServer({
        device: dev,
        output_format: fmt,
        use_autocast: autocast
      });

      // Synchronize with main form
      if (document.getElementById("select-device")) document.getElementById("select-device").value = dev;
      if (document.getElementById("select-format")) document.getElementById("select-format").value = fmt;

      showToast(t("success_saved"), "success");
      const modal = bootstrap.Modal.getInstance(document.getElementById("settingsModal"));
      if (modal) modal.hide();
    });
  }
});

