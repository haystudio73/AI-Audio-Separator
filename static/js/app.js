// Main Application Logic: Upload, Validation, Separation, Player & History
// Ensure API URL helper is available
if (typeof getApiUrl === "undefined") {
  window.getApiUrl = function(endpoint) {
    const base = window.BACKEND_API_URL || (window.location.protocol + "//" + (window.location.hostname || "localhost") + ":5000");
    if (!endpoint) return base;
    if (endpoint.startsWith("http://") || endpoint.startsWith("https://")) return endpoint;
    const clean = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
    return `${base}${clean}`;
  };
}
if (typeof getAudioUrl === "undefined") {
  window.getAudioUrl = window.getApiUrl;
}

let currentFileId = null;
let currentSourceFile = null;
let currentJobId = null;      // tracks the active separation job for cancellation
let currentAudioDuration = 0; // tracks audio duration for accurate progress estimation

const MAX_BYTES = 100 * 1024 * 1024; // 100 MB
const MAX_DURATION = 480;             // 8 minutes (480 seconds)

document.addEventListener("DOMContentLoaded", () => {
  setupUploadDropzone();
  setupGoAction();
  setupStopButton();
  setupSectionCollapsibles();
  setupHistory();
  loadHistory();
});


// Setup Upload & Validation
function setupUploadDropzone() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("audio-file-input");

  if (!dropzone || !fileInput) return;

  // Click & Drag events
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleSelectedFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleSelectedFile(e.target.files[0]);
    }
  });
}

function handleSelectedFile(file) {
  hideAlert();
  disableGoButton();

  // 1. Client-side Size Validation (Max 100MB)
  if (file.size > MAX_BYTES) {
    showAlert(t("err_size_exceeded"));
    return;
  }

  // 2. Client-side Duration Validation (Max 8 minutes)
  const audioObj = new Audio();
  const objectUrl = URL.createObjectURL(file);
  audioObj.src = objectUrl;

  audioObj.addEventListener("loadedmetadata", () => {
    const duration = audioObj.duration;
    currentAudioDuration = isFinite(duration) ? duration : 300;
    if (duration > MAX_DURATION) {
      URL.revokeObjectURL(objectUrl);
      const mins = Math.floor(duration / 60);
      const secs = Math.floor(duration % 60);
      const formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      showAlert(`${t("err_duration_exceeded")} (${formatted} > 08:00)`);
      return;
    }

    // Passed client checks -> Upload to server
    uploadFileToServer(file, duration, objectUrl);
  });

  audioObj.addEventListener("error", () => {
    currentAudioDuration = 300; // fallback
    // If browser cannot decode metadata directly (e.g. some FLAC/WAV or codecs), still attempt upload for server validation
    uploadFileToServer(file, null, objectUrl);
  });
}

async function uploadFileToServer(file, clientDuration, previewUrl) {
  showToast("Đang tải tệp lên máy chủ...", "info");
  const formData = new FormData();
  formData.append("audio_file", file);

  try {
    const res = await fetch(getApiUrl("/api/upload"), {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    if (!res.ok || !data.success) {
      showAlert(data.error || t("err_upload_failed"));
      disableGoButton();
      return;
    }

    // Success: Store file_id and metadata
    currentFileId = data.file_id;
    currentSourceFile = data.original_filename;
    displayFileInfo(data.original_filename, data.metadata, previewUrl);
    
    // CRITICAL REQUIREMENT: Enable GO button only after valid audio file upload
    enableGoButton();
    showToast("Tải tệp thành công! Đã kích hoạt nút Bắt đầu tách nhạc (GO).", "success");

  } catch (err) {
    console.error("Upload error:", err);
    showAlert(t("err_upload_failed"));
    disableGoButton();
  }
}

function displayFileInfo(filename, meta, previewUrl) {
  const card = document.getElementById("file-info-card");
  if (!card) return;

  document.getElementById("info-filename").textContent = filename;
  document.getElementById("info-filesize").textContent = meta.file_size_formatted || "-";
  document.getElementById("info-duration").textContent = meta.duration_formatted || "-";
  document.getElementById("info-format").textContent = meta.format || "-";

  const preview = document.getElementById("source-audio-preview");
  if (preview && previewUrl) {
    preview.src = previewUrl;
  }

  card.classList.remove("d-none");
}

function showAlert(message) {
  const alertEl = document.getElementById("upload-alert");
  const textEl = document.getElementById("upload-alert-text");
  if (alertEl && textEl) {
    textEl.textContent = message;
    alertEl.classList.remove("d-none");
    alertEl.classList.add("d-flex");
  }
}

function hideAlert() {
  const alertEl = document.getElementById("upload-alert");
  if (alertEl) {
    alertEl.classList.add("d-none");
    alertEl.classList.remove("d-flex");
  }
}

function enableGoButton() {
  const btn = document.getElementById("btn-go");
  const hint = document.getElementById("btn-hint");
  if (btn) {
    btn.disabled = false;
  }
  if (hint) {
    hint.classList.add("d-none");
  }
}

function disableGoButton() {
  const btn = document.getElementById("btn-go");
  const hint = document.getElementById("btn-hint");
  if (btn) {
    btn.disabled = true;
  }
  if (hint) {
    hint.classList.remove("d-none");
  }
}

// ── Global poll timer ─────────────────────────────────────────────────────────
let _pollTimer = null;

// Setup GO Separation Action
function setupGoAction() {
  const btn = document.getElementById("btn-go");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    if (!currentFileId) {
      showAlert(t("err_select_file_first"));
      return;
    }

    const model = document.getElementById("select-model").value;
    const device = document.getElementById("select-device").value;
    const outputFormat = document.getElementById("select-format").value;
    const segmentSize = parseInt(document.getElementById("select-segment").value, 10);
    const overlap = parseInt(document.getElementById("select-overlap").value, 10);

    // Lock GO button while processing
    btn.disabled = true;
    const spinner = document.getElementById("btn-go-spinner");
    const icon = document.getElementById("btn-go-icon");
    const text = document.getElementById("btn-go-text");
    if (spinner) spinner.classList.remove("d-none");
    if (icon) icon.classList.add("d-none");
    if (text) text.textContent = t("btn_processing");

    showProgressPanel();
    showToast(t("toast_processing_started"), "primary");

    try {
      const res = await fetch(getApiUrl("/api/separate"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_id: currentFileId,
          model,
          device,
          output_format: outputFormat,
          segment_size: segmentSize,
          overlap,
          audio_duration_seconds: currentAudioDuration || 300
        })
      });
      const data = await res.json();
      if (!res.ok || !data.success || !data.job_id) {
        throw new Error(data.error || "Không thể khởi tạo tác vụ tách nhạc.");
      }

      currentJobId = data.job_id;
      // Start polling — this resolves when done or throws on error/cancelled
      const result = await pollJobStatus(data.job_id);

      showToast("Phân tách âm thanh hoàn tất!", "success");
      setTimeout(() => {
        hideProgressPanel();
        renderResults(result);
        loadHistory();
        // Restore GO button after results are shown
        btn.disabled = false;
        if (spinner) spinner.classList.add("d-none");
        if (icon) icon.classList.remove("d-none");
        if (text) text.textContent = t("btn_go");
      }, 700);

    } catch (err) {
      console.error("Separation error:", err);
      showAlert(err.message || "Lỗi xử lý âm thanh.");
      showToast(err.message || "Lỗi phân tách âm thanh.", "danger");
      hideProgressPanel();
      // Restore GO button on error
      btn.disabled = false;
      if (spinner) spinner.classList.add("d-none");
      if (icon) icon.classList.remove("d-none");
      if (text) text.textContent = t("btn_go");
    }
  });
}

// ── Progress Polling ──────────────────────────────────────────────────────────
function pollJobStatus(jobId) {
  return new Promise((resolve, reject) => {
    let lastPct = 0;

    function poll() {
      fetch(getApiUrl(`/api/job/${jobId}/status`))
        .then(r => r.json())
        .then(data => {
          if (!data.success) {
            reject(new Error(data.error || "Job polling error"));
            return;
          }

          const pct = data.progress_pct || 0;
          const label = data.phase_label_vi || "";
          const elapsed = data.elapsed_seconds || 0;
          const status = data.status;

          // Smooth bar: only advance, never go backward
          const displayPct = Math.max(pct, lastPct);
          lastPct = displayPct;
          updateProgressPanel(displayPct, label, elapsed, status);

          if (status === "done") {
            updateProgressPanel(100, "Hoàn tất!", elapsed, "done");
            currentJobId = null;
            resolve(data.result);
          } else if (status === "error" || status === "cancelled") {
            currentJobId = null;
            const msg = status === "cancelled"
              ? "Đã dừng xử lý theo yêu cầu."
              : (data.error || "Lỗi xử lý âm thanh.");
            reject(new Error(msg));
          } else {
            _pollTimer = setTimeout(poll, 800);
          }
        })
        .catch(err => {
          console.warn("Poll network error, retrying:", err);
          _pollTimer = setTimeout(poll, 1500);
        });
    }

    poll();
  });
}


// ── Progress Panel Helpers ────────────────────────────────────────────────────
function showProgressPanel() {
  const panel = document.getElementById("progress-panel");
  if (!panel) return;
  updateProgressPanel(0, "Đang chuẩn bị...", 0, "queued");
  panel.classList.remove("d-none");
  // Show stop button
  const stopBtn = document.getElementById("btn-stop-job");
  if (stopBtn) { stopBtn.disabled = false; stopBtn.classList.remove("d-none"); }
  panel.scrollIntoView({ behavior: "smooth", block: "center" });
}

function hideProgressPanel() {
  const panel = document.getElementById("progress-panel");
  if (panel) panel.classList.add("d-none");
  if (_pollTimer) { clearTimeout(_pollTimer); _pollTimer = null; }
}

// ── Stop / Cancel Button ──────────────────────────────────────────────────────
function setupStopButton() {
  const btn = document.getElementById("btn-stop-job");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    if (!currentJobId) return;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Đang dừng...';
    try {
      await fetch(getApiUrl(`/api/job/${currentJobId}/cancel`), { method: "POST" });
      showToast("Đã gửi yêu cầu dừng xử lý...", "warning");
    } catch (e) {
      console.warn("Cancel request error:", e);
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-stop-circle-fill"></i><span>Dừng</span>';
    }
  });
}

function updateProgressPanel(pct, label, elapsed, status) {
  const bar       = document.getElementById("progress-bar");
  const labelEl   = document.getElementById("progress-label");
  const pctEl     = document.getElementById("progress-pct");
  const elapsedEl = document.getElementById("progress-elapsed");
  const iconEl    = document.getElementById("progress-icon");
  const stopBtn   = document.getElementById("btn-stop-job");

  if (bar) {
    bar.style.width = `${pct}%`;
    bar.setAttribute("aria-valuenow", pct);
    bar.className = "progress-bar progress-bar-striped progress-bar-animated";
    if (status === "done") {
      bar.classList.remove("progress-bar-animated");
      bar.classList.add("bg-success");
    } else if (status === "error") {
      bar.classList.remove("progress-bar-animated");
      bar.classList.add("bg-danger");
    } else if (status === "cancelled") {
      bar.classList.remove("progress-bar-animated");
      bar.classList.add("bg-warning");
    }
  }
  if (labelEl)   labelEl.textContent   = label;
  if (pctEl)     pctEl.textContent     = `${pct}%`;
  if (elapsedEl) elapsedEl.textContent = elapsed > 0 ? `${elapsed}s` : "";
  if (iconEl) {
    if (status === "done")      iconEl.className = "bi bi-check-circle-fill text-success fs-4";
    else if (status === "error")     iconEl.className = "bi bi-x-circle-fill text-danger fs-4";
    else if (status === "cancelled") iconEl.className = "bi bi-slash-circle-fill text-warning fs-4";
    else iconEl.className = "bi bi-cpu-fill text-primary fs-4";
  }
  // Hide stop button once finished
  if (stopBtn && ["done", "error", "cancelled"].includes(status)) {
    stopBtn.classList.add("d-none");
  }
}

// Render Stems Results
function renderResults(result) {
  const sec = document.getElementById("results-section");
  const container = document.getElementById("stems-container");
  const timeBadge = document.getElementById("result-time-badge");
  const devBadge = document.getElementById("result-device-badge");

  if (!sec || !container) return;

  if (timeBadge) timeBadge.textContent = `Time: ${result.processing_time_seconds}s`;
  if (devBadge) devBadge.textContent = `Device: ${result.device_used.toUpperCase()}`;

  // Auto-expand results section if it was previously collapsed
  const resultsContent = document.getElementById("results-collapse-content");
  const arrowResults = document.getElementById("arrow-results");
  if (resultsContent && resultsContent.classList.contains("d-none")) {
    resultsContent.classList.remove("d-none");
    if (arrowResults) arrowResults.classList.remove("collapsed");
  }

  container.innerHTML = "";


  result.stems.forEach(stem => {
    const col = document.createElement("div");
    col.className = "col-md-6";

    let badgeClass = "stem-vocals";
    const lower = stem.stem_name.toLowerCase();
    if (lower.includes("inst")) badgeClass = "stem-instrumental";
    else if (lower.includes("drum")) badgeClass = "stem-drums";
    else if (lower.includes("bass")) badgeClass = "stem-bass";

    // Show Lyrics button only for Vocals stems
    const isVocals = lower.includes("vocal");
    const lyricsBtn = isVocals
      ? `<button class="btn-lyrics" onclick="openKaraokeEditor('${getAudioUrl(stem.download_url)}', '${stem.filename}')">
           <i class="bi bi-mic-fill me-1"></i>${t('lyrics_btn')}
         </button>`
      : "";

    col.innerHTML = `
      <div class="stem-player-card">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <span class="stem-badge ${badgeClass}">${stem.stem_name}</span>
            ${lyricsBtn}
          </div>
          <span class="small text-secondary">${stem.file_size_formatted} &bull; ${stem.format}</span>
        </div>
        <div class="mb-2">
          <audio controls class="w-100" preload="none">
            <source src="${getAudioUrl(stem.download_url)}" type="audio/wav">
            Trình duyệt không hỗ trợ audio player.
          </audio>
        </div>
        <div class="d-flex justify-content-between align-items-center">
          <small class="text-truncate text-secondary" style="max-width: 200px;" title="${stem.filename}">${stem.filename}</small>
          <a href="${getAudioUrl(stem.download_url)}" download="${stem.filename}" class="btn btn-sm btn-outline-primary rounded-pill px-3">
            <i class="bi bi-download me-1"></i>${t("btn_download")}
          </a>
        </div>
      </div>
    `;
    container.appendChild(col);
  });


  sec.classList.remove("d-none");
  sec.scrollIntoView({ behavior: "smooth" });
}

// History Management (Max 67 items FIFO)
function setupHistory() {
  const clearBtn = document.getElementById("btn-clear-history");
  if (clearBtn) {
    clearBtn.addEventListener("click", async () => {
      const confirmMsg = t("confirm_clear_history") || "Bạn có chắc chắn muốn xóa toàn bộ lịch sử phân tách?";
      if (!confirm(confirmMsg)) return;
      try {
        const res = await fetch(getApiUrl("/api/history"), { method: "DELETE" });
        const data = await res.json();
        if (data.success) {
          showToast(t("history_cleared") || "Đã xóa sạch toàn bộ lịch sử.", "info");
          loadHistory();
        }
      } catch (err) {
        console.error("Failed to clear history:", err);
      }
    });

  }
}

async function loadHistory() {
  try {
    const res = await fetch(getApiUrl("/api/history"));
    const data = await res.json();
    if (data.success) {
      renderHistoryList(data.history || []);
    }
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}

function renderHistoryList(items) {
  const counter = document.getElementById("history-counter");
  const container = document.getElementById("history-list");
  if (!counter || !container) return;

  counter.textContent = `${items.length} / 67`;
  container.innerHTML = "";

  if (items.length === 0) {
    container.innerHTML = `
      <div class="text-center py-4 text-secondary">
        <i class="bi bi-inbox fs-2 d-block mb-2"></i>
        <span>${t("history_empty")}</span>
      </div>
    `;
    return;
  }

  items.forEach(item => {
    const card = document.createElement("div");

    // ── Lyrics history entry ────────────────────────────────────────────────
    if (item.type === "lyrics" || item.type === "lyrics_edit") {
      const isEdit   = item.type === "lyrics_edit";
      const accentColor = isEdit ? "#10b981" : "#a855f7";  // green for edit, purple for extract
      const iconCls  = isEdit ? "bi-pencil-square text-success" : "bi-mic-fill text-purple";
      const badge    = isEdit
        ? `<span class="badge" style="background:rgba(16,185,129,.15);color:#10b981;border:1px solid rgba(16,185,129,.3);">Lyrics Edited</span>`
        : `<span class="badge" style="background:rgba(168,85,247,.15);color:#a855f7;border:1px solid rgba(168,85,247,.3);">Lyrics Extracted</span>`;

      const srtLink = item.srt_filename
        ? `<a href="${getApiUrl('/api/lyrics/' + encodeURIComponent(item.vocals_filename) + '/srt')}"
               class="btn btn-xs btn-outline-secondary btn-sm py-0 px-2" title="Download SRT">
             <i class="bi bi-download me-1"></i>SRT
           </a>`
        : "";
      const lrcLink = item.lrc_filename
        ? `<a href="${getApiUrl('/api/lyrics/' + encodeURIComponent(item.vocals_filename) + '/lrc')}"
               class="btn btn-xs btn-outline-secondary btn-sm py-0 px-2" title="Download LRC">
             <i class="bi bi-download me-1"></i>LRC
           </a>`
        : "";

      const langBadge = item.detected_language && !isEdit
        ? `<span class="badge bg-info-subtle text-info border border-info-subtle">${item.detected_language.toUpperCase()}</span>`
        : "";

      const dbBadge = item.db_id
        ? `<span class="badge bg-dark-subtle text-body border" title="Saved in SQLite DB">DB #${item.db_id}</span>`
        : "";

      const reopenBtn = item.db_id
        ? `<button class="btn btn-xs btn-outline-primary btn-sm py-0 px-2"
                   onclick="reopenKaraokeFromDb(${item.db_id}, '${item.vocals_filename}')"
                   title="Mở trong Karaoke Editor">
             <i class="bi bi-mic me-1"></i>Karaoke Editor
           </button>`
        : "";

      const safeTitle = (item.vocals_filename || "").replace(/'/g, "\\'");
      card.className = "card border p-3 history-card-item bg-body-tertiary";
      card.style.borderLeft = `4px solid ${accentColor}`;
      card.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
          <div class="d-flex align-items-start gap-2 flex-grow-1 me-2">
            <i class="bi ${iconCls} mt-1" style="font-size:1.1rem;color:${accentColor}"></i>
            <div>
              <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
                ${badge}
                ${dbBadge}
                <span class="fw-semibold small text-break">${item.vocals_filename}</span>
              </div>
              <div class="small text-secondary d-flex flex-wrap gap-2 mb-2">
                <span><i class="bi bi-clock me-1"></i>${item.timestamp}</span>
                ${item.whisper_model ? `<span>&bull;</span><span>Whisper: <strong>${item.whisper_model}</strong></span>` : ""}
                ${langBadge}
                <span>&bull;</span>
                <span><i class="bi bi-list-ol me-1"></i>${item.total_lines} ${t("lyrics_lines")}</span>
              </div>
              <div class="d-flex gap-2 flex-wrap align-items-center">
                ${reopenBtn}
                ${srtLink}
                ${lrcLink}
              </div>
            </div>
          </div>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteHistoryEntry('${item.id}', '${safeTitle}')" title="Delete">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      `;
      container.appendChild(card);
      return;  // skip default rendering

    }

    // ── Default: separation history entry ───────────────────────────────────
    const safeTitle = (item.original_filename || item.vocals_filename || "").replace(/'/g, "\\'");
    card.className = "card border p-3 history-card-item bg-body-tertiary";

    let stemsHtml = "";
    if (item.stems && item.stems.length > 0) {
      stemsHtml = item.stems.map(s => `
        <div class="d-flex align-items-center justify-content-between p-2 rounded border bg-body mb-2">
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-primary-subtle text-primary">${s.stem_name}</span>
            <span class="small text-truncate" style="max-width: 250px;">${s.filename}</span>
          </div>
          <div class="d-flex align-items-center gap-2">
            <audio controls style="height: 32px; width: 220px;" preload="none">
              <source src="${getAudioUrl(s.download_url)}" type="audio/wav">
            </audio>
            <a href="${getAudioUrl(s.download_url)}" download="${s.filename}" class="btn btn-sm btn-outline-secondary" title="Download">
              <i class="bi bi-download"></i>
            </a>
          </div>
        </div>
      `).join("");
    }

    card.innerHTML = `
      <div class="d-flex justify-content-between align-items-start mb-2">
        <div>
          <h6 class="fw-bold mb-1 text-break">${item.original_filename || item.vocals_filename || "—"}</h6>
          <div class="small text-secondary d-flex flex-wrap gap-2">
            <span><i class="bi bi-clock me-1"></i>${item.timestamp}</span>
            ${item.model_used ? `<span>&bull;</span><span>${t("history_item_model")} <strong>${item.model_used}</strong></span>` : ""}
            ${item.device_used ? `<span>&bull;</span><span class="badge bg-secondary-subtle text-body">${item.device_used.toUpperCase()}</span>` : ""}
            ${item.processing_time ? `<span>&bull;</span><span>${t("history_item_time")} ${item.processing_time}</span>` : ""}
          </div>
        </div>
        <button class="btn btn-sm btn-outline-danger" onclick="deleteHistoryEntry('${item.id}', '${safeTitle}')" title="Delete">
          <i class="bi bi-trash"></i>
        </button>
      </div>
      <div class="mt-2">
        ${stemsHtml}
      </div>
    `;

    container.appendChild(card);
  });
}

async function deleteHistoryEntry(id, itemName = "") {
  const baseMsg = t("confirm_delete_history_item") || "Bạn có chắc chắn muốn xóa bản ghi lịch sử này không?";
  const confirmMsg = itemName ? `${baseMsg}\n\n"${itemName}"` : baseMsg;
  if (!confirm(confirmMsg)) return;

  try {
    const res = await fetch(getApiUrl(`/api/history/${id}`), { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      showToast(t("history_item_deleted") || "Đã xóa bản ghi lịch sử.", "info");
      loadHistory();
    }
  } catch (err) {
    console.error("Failed to delete history item:", err);
  }
}


// ── Section Collapsibles (Results & History Toggle Arrows) ────────────────────
function setupSectionCollapsibles() {
  // 1. Toggle for Results Section
  const btnToggleResults = document.getElementById("btn-toggle-results");
  const resultsContent   = document.getElementById("results-collapse-content");
  const arrowResults     = document.getElementById("arrow-results");

  if (btnToggleResults && resultsContent) {
    btnToggleResults.addEventListener("click", () => {
      const isHidden = resultsContent.classList.toggle("d-none");
      if (arrowResults) {
        if (isHidden) {
          arrowResults.classList.add("collapsed");
        } else {
          arrowResults.classList.remove("collapsed");
        }
      }
    });
  }

  // 2. Toggle for History Section
  const btnToggleHistory = document.getElementById("btn-toggle-history");
  const historyContent   = document.getElementById("history-collapse-content");
  const arrowHistory     = document.getElementById("arrow-history");

  if (btnToggleHistory && historyContent) {
    btnToggleHistory.addEventListener("click", () => {
      const isHidden = historyContent.classList.toggle("d-none");
      if (arrowHistory) {
        if (isHidden) {
          arrowHistory.classList.add("collapsed");
        } else {
          arrowHistory.classList.remove("collapsed");
        }
      }
    });
  }
}

