/**
 * Karaoke Lyrics Editor — lyrics.js
 * Tính năng: Trích xuất lyrics từ Vocals bằng Whisper, hiển thị editor có thể
 * chỉnh sửa inline, đồng bộ highlight theo audio playback, export SRT/LRC.
 */

// ── State ──────────────────────────────────────────────────────────────────────
let _karaokeSegments   = [];   // [{id, start, end, text, start_display, end_display}]
let _karaokeVocalsFile = "";   // e.g. "xxx_Vocals.wav"
let _karaokeAudioEl    = null; // <audio> element inside modal
let _highlightRaf      = null; // requestAnimationFrame handle
let _srtFilename       = "";
let _lrcFilename       = "";

// ── Open modal ────────────────────────────────────────────────────────────────

/**
 * Mở Karaoke Editor cho một file vocals cụ thể.
 * @param {string} vocalsUrl       - URL phát audio (qua Backend)
 * @param {string} vocalsFilename  - Tên file vocals (dùng cho API call)
 */
function openKaraokeEditor(vocalsUrl, vocalsFilename) {
  _karaokeVocalsFile = vocalsFilename;
  _karaokeSegments   = [];
  _srtFilename       = "";
  _lrcFilename       = "";

  // Set audio source
  const audioEl = document.getElementById("kara-audio");
  if (audioEl) {
    audioEl.src = vocalsUrl;
    audioEl.load();
    _karaokeAudioEl = audioEl;
  }

  // Update modal title filename
  const titleFile = document.getElementById("kara-title-file");
  if (titleFile) titleFile.textContent = vocalsFilename;

  // Reset UI state
  _setKaraStatus("idle");
  _renderTable([]);

  // Open Bootstrap modal
  const modal = document.getElementById("karaokeModal");
  if (modal) {
    const bsModal = bootstrap.Modal.getOrCreateInstance(modal);
    bsModal.show();
  }
}

// ── Extract Lyrics ─────────────────────────────────────────────────────────────

async function extractLyrics() {
  const whisperModel = document.getElementById("kara-model-select")?.value || "base";
  const langSelect   = document.getElementById("kara-lang-select")?.value || "";

  // Confirm nếu đã có lyrics (re-extract)
  if (_karaokeSegments.length > 0) {
    const msg = t("lyrics_confirm_reextract");
    if (!confirm(msg)) return;
  }

  _setKaraStatus("extracting");
  _renderTable([]);

  try {
    const res = await fetch(getApiUrl("/api/lyrics/extract"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        vocals_filename: _karaokeVocalsFile,
        whisper_model:   whisperModel,
        language:        langSelect || null,
      }),
    });
    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.error || t("lyrics_extract_error"));
    }

    _karaokeSegments = data.segments || [];
    _srtFilename     = data.srt_filename || "";
    _lrcFilename     = data.lrc_filename || "";

    _setKaraStatus("done", `${t("lyrics_extract_success")} (${_karaokeSegments.length} ${t("lyrics_lines")})`);
    _renderTable(_karaokeSegments);
    showToast(`${t("lyrics_extract_success")} — ${_karaokeSegments.length} ${t("lyrics_lines")}`, "success");

    // Start highlight sync
    _startHighlightSync();

  } catch (err) {
    console.error("[Karaoke] Extract error:", err);
    _setKaraStatus("error", err.message);
    showToast(err.message, "danger");
  }
}

// ── Render Lyrics Table ────────────────────────────────────────────────────────

function _renderTable(segments) {
  const tbody = document.getElementById("kara-lyrics-tbody");
  const empty = document.getElementById("kara-empty-hint");
  const table = document.getElementById("kara-table");
  if (!tbody) return;

  tbody.innerHTML = "";

  if (!segments || segments.length === 0) {
    if (empty) empty.classList.remove("d-none");
    if (table) table.classList.add("d-none");
    return;
  }
  if (empty) empty.classList.add("d-none");
  if (table) table.classList.remove("d-none");

  segments.forEach((seg, idx) => {
    const tr = document.createElement("tr");
    tr.id            = `kara-row-${idx}`;
    tr.className     = "lyric-line";
    tr.dataset.start = seg.start;
    tr.dataset.end   = seg.end;
    tr.dataset.idx   = idx;

    tr.innerHTML = `
      <td class="kara-idx text-secondary small">${seg.id}</td>
      <td>
        <input type="text" class="kara-time-input"
               value="${seg.start_display}"
               onchange="editLine(${idx}, 'start_display', this.value)"
               aria-label="start time">
      </td>
      <td>
        <input type="text" class="kara-time-input"
               value="${seg.end_display}"
               onchange="editLine(${idx}, 'end_display', this.value)"
               aria-label="end time">
      </td>
      <td class="kara-text-cell">
        <input type="text" class="kara-text-input w-100"
               value="${_escHtml(seg.text)}"
               onchange="editLine(${idx}, 'text', this.value)"
               aria-label="lyrics text">
      </td>
      <td>
        <button class="btn btn-sm btn-link text-secondary p-0"
                onclick="_seekToLine(${idx})"
                title="${t('lyrics_seek_hint')}">
          <i class="bi bi-play-circle"></i>
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function _escHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

// ── Inline Edit ───────────────────────────────────────────────────────────────

/**
 * Cập nhật một trường của segment tại index.
 * @param {number} idx   - index trong _karaokeSegments
 * @param {string} field - 'start_display' | 'end_display' | 'text'
 * @param {string} val   - giá trị mới
 */
function editLine(idx, field, val) {
  if (!_karaokeSegments[idx]) return;
  _karaokeSegments[idx][field] = val;

  // If timing changed, also update numeric start/end
  if (field === "start_display") {
    _karaokeSegments[idx].start = _displayToSeconds(val);
    document.getElementById(`kara-row-${idx}`)?.setAttribute("data-start", _karaokeSegments[idx].start);
  } else if (field === "end_display") {
    _karaokeSegments[idx].end = _displayToSeconds(val);
    document.getElementById(`kara-row-${idx}`)?.setAttribute("data-end", _karaokeSegments[idx].end);
  }
}

function _displayToSeconds(display) {
  const parts = display.split(":").map(Number);
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return 0;
}

function _seekToLine(idx) {
  if (!_karaokeAudioEl || !_karaokeSegments[idx]) return;
  _karaokeAudioEl.currentTime = _karaokeSegments[idx].start;
  _karaokeAudioEl.play().catch(() => {});
}

// ── Highlight Sync ────────────────────────────────────────────────────────────

function _startHighlightSync() {
  if (_highlightRaf) cancelAnimationFrame(_highlightRaf);

  function sync() {
    if (!_karaokeAudioEl) return;
    const ct = _karaokeAudioEl.currentTime;

    document.querySelectorAll(".lyric-line").forEach(tr => {
      const s = parseFloat(tr.dataset.start);
      const e = parseFloat(tr.dataset.end);
      const active = ct >= s && ct <= e;
      tr.classList.toggle("active", active);
      if (active) {
        tr.scrollIntoView({ block: "nearest", behavior: "smooth" });
      }
    });

    _highlightRaf = requestAnimationFrame(sync);
  }
  _highlightRaf = requestAnimationFrame(sync);
}

function _stopHighlightSync() {
  if (_highlightRaf) {
    cancelAnimationFrame(_highlightRaf);
    _highlightRaf = null;
  }
}

// ── Download ──────────────────────────────────────────────────────────────────

/**
 * Confirm rồi download file lyrics.
 * @param {string} fmt - 'srt' hoặc 'lrc'
 */
async function confirmDownload(fmt) {
  if (_karaokeSegments.length === 0) {
    showToast(t("lyrics_no_segments_to_download"), "warning");
    return;
  }

  const n    = _karaokeSegments.length;
  const ext  = fmt.toUpperCase();
  const msg  = fmt === "srt"
    ? t("lyrics_confirm_download_srt").replace("{n}", n)
    : t("lyrics_confirm_download_lrc").replace("{n}", n);

  if (!confirm(msg)) return;

  // Save edited segments first (fire-and-forget, then download)
  try {
    await fetch(getApiUrl("/api/lyrics/save"), {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({
        vocals_filename: _karaokeVocalsFile,
        segments:        _karaokeSegments,
      }),
    });
  } catch (e) {
    console.warn("[Karaoke] Save before download failed:", e);
  }

  // Trigger download via backend serve endpoint
  const dlUrl = getApiUrl(`/api/lyrics/${encodeURIComponent(_karaokeVocalsFile)}/${fmt}`);
  const a = document.createElement("a");
  a.href = dlUrl;
  a.download = "";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  showToast(`${t("lyrics_downloading")} .${ext}`, "success");
}

// ── Status UI ─────────────────────────────────────────────────────────────────

function _setKaraStatus(state, message) {
  const spinner   = document.getElementById("kara-spinner");
  const statusMsg = document.getElementById("kara-status-msg");
  const bar       = document.getElementById("kara-progress-bar");
  const barWrap   = document.getElementById("kara-progress-wrap");

  if (state === "extracting") {
    if (spinner)   spinner.classList.remove("d-none");
    if (barWrap)   barWrap.classList.remove("d-none");
    if (bar) {
      bar.style.width = "100%";
      bar.className   = "progress-bar progress-bar-striped progress-bar-animated";
    }
    if (statusMsg) statusMsg.textContent = t("lyrics_extracting");
    // Disable buttons
    _setBtnLocked(true);
  } else if (state === "done") {
    if (spinner)   spinner.classList.add("d-none");
    if (barWrap)   barWrap.classList.add("d-none");
    if (statusMsg) statusMsg.textContent = message || t("lyrics_extract_success");
    _setBtnLocked(false);
  } else if (state === "error") {
    if (spinner)   spinner.classList.add("d-none");
    if (barWrap)   barWrap.classList.add("d-none");
    if (bar) {
      bar.style.width = "100%";
      bar.className   = "progress-bar bg-danger";
    }
    if (statusMsg) {
      statusMsg.textContent = message || t("lyrics_extract_error");
      statusMsg.className   = "small text-danger";
    }
    _setBtnLocked(false);
  } else {
    // idle
    if (spinner)   spinner.classList.add("d-none");
    if (barWrap)   barWrap.classList.add("d-none");
    if (statusMsg) { statusMsg.textContent = ""; statusMsg.className = "small text-secondary"; }
    _setBtnLocked(false);
  }
}

function _setBtnLocked(locked) {
  const extractBtn = document.getElementById("kara-btn-extract");
  const srtBtn     = document.getElementById("kara-btn-srt");
  const lrcBtn     = document.getElementById("kara-btn-lrc");
  [extractBtn, srtBtn, lrcBtn].forEach(b => { if (b) b.disabled = locked; });
}

// ── Reopen from SQLite Database ──────────────────────────────────────────────

/**
 * Tải lại lyrics từ SQLite DB và mở Karaoke Editor ngay lập tức mà không cần trích xuất lại.
 * @param {number} recordId - ID bản ghi trong DB SQLite
 * @param {string} vocalsFilename - Tên file vocals
 */
async function reopenKaraokeFromDb(recordId, vocalsFilename) {
  try {
    const res = await fetch(getApiUrl(`/api/lyrics/db/history/${recordId}`));
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || "Không thể tải dữ liệu từ DB");
    }

    const rec = data.record;
    const vFile = vocalsFilename || rec.vocals_filename;
    const vocalsUrl = getApiUrl(`/api/audio/outputs/${encodeURIComponent(vFile)}`);

    _karaokeVocalsFile = vFile;
    _karaokeSegments   = rec.segments || [];
    _srtFilename       = rec.srt_filename || "";
    _lrcFilename       = rec.lrc_filename || "";

    // Set audio source
    const audioEl = document.getElementById("kara-audio");
    if (audioEl) {
      audioEl.src = vocalsUrl;
      audioEl.load();
      _karaokeAudioEl = audioEl;
    }

    // Update modal title
    const titleFile = document.getElementById("kara-title-file");
    if (titleFile) titleFile.textContent = vFile;

    _renderTable(_karaokeSegments);
    _setKaraStatus("done", `DB #${recordId} (${_karaokeSegments.length} ${t("lyrics_lines")})`);

    const modal = document.getElementById("karaokeModal");
    if (modal) {
      const bsModal = bootstrap.Modal.getOrCreateInstance(modal);
      bsModal.show();
    }

    _startHighlightSync();
    showToast(`Đã tải từ DB (${_karaokeSegments.length} ${t("lyrics_lines")})`, "success");
  } catch (err) {
    console.error("[Karaoke] Error loading from DB:", err);
    showToast(err.message, "danger");
  }
}

// ── Cleanup on modal close ────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("karaokeModal");
  if (modal) {
    modal.addEventListener("hidden.bs.modal", () => {
      _stopHighlightSync();
      if (_karaokeAudioEl) _karaokeAudioEl.pause();
    });
  }
});

