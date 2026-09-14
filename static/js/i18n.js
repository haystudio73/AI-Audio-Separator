const I18N = {
  vi: {
    app_title: "AI Music Source Separation",
    app_subtitle: "Phân tách Giọng hát & Nhạc nền bằng Trí tuệ Nhân tạo thế hệ mới",
    nav_home: "Trang chủ",
    nav_models: "Mô hình",
    nav_history: "Lịch sử",
    nav_settings: "Cấu hình",
    
    // Hardware badge
    hw_detected: "Phần cứng phát hiện",
    hw_cuda_ready: "NVIDIA CUDA Khả dụng",
    hw_cpu_mode: "Chế độ CPU Đa luồng",
    
    // Upload area
    upload_title: "Tải tệp âm thanh lên",
    upload_desc: "Kéo thả hoặc nhấp để chọn tệp âm thanh bài hát",
    upload_hint: "Hỗ trợ MP3, WAV, FLAC, M4A, OGG. Tối đa 100 MB, thời lượng tối đa 8 phút.",
    select_file_btn: "Chọn tệp từ máy tính",
    file_info_title: "Thông tin tệp nguồn",
    file_name: "Tên tệp:",
    file_size: "Dung lượng:",
    file_duration: "Thời lượng:",
    file_format: "Định dạng:",
    status_valid: "Hợp lệ (≤ 100MB, ≤ 8 phút)",
    status_invalid: "Không hợp lệ",
    
    // Action button
    btn_go: "BẮT ĐẦU TÁCH NHẠC (GO)",
    btn_processing: "Đang phân tách âm thanh...",
    
    // Options
    opt_model: "Chọn Mô hình AI:",
    opt_model_header: "Chọn Mô hình AI:",
    opt_device: "Thiết bị xử lý:",
    opt_format: "Định dạng xuất:",
    opt_quality: "Tối ưu hóa (Segment & Overlap):",
    mode_quick: "Quick Mode",
    mode_adv: "Adv Mode",
    quick_mode_desc: "Cấu hình mặc định tối ưu: HT-Demucs v4 (4 Stems), GPU (CUDA), MP3 320kbps, Segment 256, Overlap 4.",
    adv_mode_desc: "Chế độ nâng cao: Toàn quyền tùy biến mô hình AI, thiết bị xử lý, định dạng xuất và thông số Overlap-Add.",
    quick_mode_applied: "Đã kích hoạt Quick Mode với cấu hình tối ưu!",
    adv_mode_applied: "Đã chuyển sang Adv Mode (Tùy biến nâng cao)!",
    
    // Results
    results_title: "Kết quả Phân tách",
    results_desc: "Các track âm thanh độc lập sau khi bóc tách:",
    btn_download: "Tải xuống",
    btn_download_all: "Tải tất cả (ZIP)",
    stem_vocals: "Giọng hát (Vocals)",
    stem_instrumental: "Nhạc nền (Instrumental)",
    stem_drums: "Bộ gõ (Drums)",
    stem_bass: "Âm trầm (Bass)",
    stem_other: "Khác (Other)",
    
    // History
    history_title: "Lịch sử Xử lý",
    history_subtitle: "Tối đa 67 lượt thực hiện gần nhất (tự động luân chuyển FIFO)",
    history_empty: "Chưa có lượt phân tách nào trong lịch sử.",
    btn_clear_history: "Xóa tất cả lịch sử",
    history_item_model: "Mô hình:",
    history_item_time: "Thời gian xử lý:",
    confirm_delete_history_item: "Bạn có chắc chắn muốn xóa bản ghi lịch sử này không?",
    confirm_clear_history: "Bạn có chắc chắn muốn xóa toàn bộ lịch sử phân tách không?",
    history_item_deleted: "Đã xóa bản ghi lịch sử.",
    history_cleared: "Đã xóa sạch toàn bộ lịch sử.",

    
    // Settings modal
    modal_settings_title: "Cấu hình Hệ thống & Mô hình AI",
    settings_device_label: "Chế độ phần cứng",
    settings_device_gpu: "GPU (NVIDIA CUDA) - Tốc độ cao, chuẩn phòng thu",
    settings_device_cpu: "CPU Đa luồng - Thích hợp UVR-MDX-Net",
    settings_model_label: "Mô hình mặc định",
    settings_format_label: "Định dạng âm thanh đầu ra",
    settings_segment_label: "Kích thước đoạn (Segment Size)",
    settings_overlap_label: "Mức độ chồng lấn (Overlap)",
    settings_autocast_label: "Kích hoạt FP16 Autocast (Tiết kiệm 50% VRAM)",
    settings_models_installed: "Các mô hình có sẵn trong máy:",
    btn_download_model: "Tải mô hình",
    status_downloaded: "Đã có sẵn",
    status_not_downloaded: "Chưa tải",
    btn_save_settings: "Lưu cấu hình",
    btn_close: "Đóng",

    // Errors & warnings
    err_size_exceeded: "Lỗi: Dung lượng tệp vượt quá giới hạn 100 MB!",
    err_duration_exceeded: "Lỗi: Thời lượng âm thanh vượt quá giới hạn 8 phút (08:00)!",
    err_upload_failed: "Không thể tải tệp lên máy chủ.",
    err_select_file_first: "Vui lòng chọn hoặc tải lên tệp âm thanh trước.",
    success_saved: "Đã lưu cài đặt thành công!",
    toast_processing_started: "Bắt đầu xử lý! Quá trình có thể mất từ 15-40 giây tùy cấu hình phần cứng...",

    // Lyrics / Karaoke Editor
    lyrics_btn: "🎤 Trích xuất Lyrics",
    lyrics_editor_title: "Karaoke Lyrics Editor",
    lyrics_model_label: "Whisper Model:",
    lyrics_lang_label: "Ngôn ngữ:",
    lyrics_lang_auto: "Tự động nhận diện",
    lyrics_btn_extract: "Trích xuất Lyrics",
    lyrics_btn_reextract: "🔄 Trích xuất lại",
    lyrics_download_srt: "💾 Tải SRT",
    lyrics_download_lrc: "💾 Tải LRC",
    lyrics_col_no: "#",
    lyrics_col_start: "Bắt đầu",
    lyrics_col_end: "Kết thúc",
    lyrics_col_text: "Nội dung lyrics (click để sửa)",
    lyrics_col_seek: "",
    lyrics_extracting: "Đang nhận diện giọng hát bằng Whisper AI...",
    lyrics_extract_success: "Trích xuất thành công",
    lyrics_extract_error: "Trích xuất lyrics thất bại.",
    lyrics_lines: "dòng",
    lyrics_empty_hint: "Nhấn \"Trích xuất Lyrics\" để bắt đầu nhận diện giọng hát.",
    lyrics_seek_hint: "Nhảy đến đoạn này",
    lyrics_confirm_reextract: "Trích xuất lại sẽ ghi đè lyrics hiện tại. Bạn có muốn tiếp tục không?",
    lyrics_confirm_download_srt: "Bạn sắp tải xuống file SRT với {n} dòng lyrics.\nTiếp tục tải xuống?",
    lyrics_confirm_download_lrc: "Bạn sắp tải xuống file LRC với {n} dòng lyrics.\nTiếp tục tải xuống?",
    lyrics_no_segments_to_download: "Chưa có lyrics để tải xuống. Hãy trích xuất trước.",
    lyrics_downloading: "Đang tải xuống",
    lyrics_save_ok: "Đã lưu lyrics đã chỉnh sửa.",

    // Help / User Guide Modal
    help_modal_title: "Hướng Dẫn Sử Dụng Chi Tiết",
    help_modal_subtitle: "Quy trình từng bước từ tải nhạc, tách kênh đến tạo lời bài hát Karaoke",
    help_step1_title: "Tải Tệp Nhạc Lên",
    help_step1_desc: "Kéo thả hoặc nhấp vào khung để chọn tệp âm thanh bài hát. Hỗ trợ đầy đủ định dạng: MP3, WAV, FLAC, M4A, OGG (Tối đa 100MB, thời lượng đến 8 phút). Sau khi tải lên, bạn có thể phát nghe thử tệp gốc ngay trên trình phát.",
    help_step2_title: "Chọn Chế Độ: Quick Mode hoặc Adv Mode",
    help_step2_desc: "⚡ Quick Mode (Mặc định): Tự động cấu hình mô hình HT-Demucs v4 (Meta AI), bóc tách thành 4 track (Vocals, Drums, Bass, Other), tăng tốc GPU NVIDIA CUDA và xuất MP3 320kbps. Toàn bộ thông số nâng cao được ẩn đi để bạn tách nhạc với 1-click tiện lợi.<br>⚙️ Adv Mode (Nâng cao): Mở toàn quyền tùy biến chọn mô hình Mel-Band RoFormer (chuẩn phòng thu), UVR-MDX-Net, định dạng WAV Lossless 24-bit, Segment Size và Overlap.",
    help_step3_title: "Bắt Đầu Tách Nhạc (GO)",
    help_step3_desc: "Nhấn nút màu tím BẮT ĐẦU TÁCH NHẠC (GO). Hệ thống sẽ hiển thị thanh tiến trình xử lý thời gian thực theo từng giai đoạn. Bạn có thể nhấn nút Dừng bất kỳ lúc nào nếu muốn hủy tác vụ.",
    help_step4_title: "Nghe Thử & Tải Các Track (Stems)",
    help_step4_desc: "Mỗi track âm thanh được bóc tách riêng (Vocals, Drums, Bass, Other) có audio player riêng để bạn nghe thử độc lập. Nhấn Tải xuống trên từng track hoặc tải toàn bộ. Bạn có thể dùng nút mũi tên đỏ > để thu gọn/mở rộng khu vực kết quả.",
    help_step5_title: "Trích Xuất Lời Bài Hát & Karaoke Editor",
    help_step5_desc: "Trên thẻ Vocals, nhấp vào nút 🎤 Trích xuất Lyrics. AI Whisper (chạy local 100% miễn phí) tự động nhận diện lời bài hát. Trình phát sẽ highlight câu hát theo thời gian thực khi nghe, cho phép bạn nhấp vào từng câu để chỉnh sửa nội dung hoặc mốc thời gian và tải về file .SRT hoặc .LRC.",
    help_step6_title: "Quản Lý Lịch Sử & Mở Lại Từ Database",
    help_step6_desc: "Hệ thống lưu các lượt thực hiện và toàn bộ lời bài hát vào cơ sở dữ liệu SQLite (data/lyrics.db). Nhấn nút Karaoke Editor trên thẻ lịch sử để mở lại lời bài hát bất cứ lúc nào mà không cần chạy lại mô hình AI. Có hộp thoại xác nhận trước khi xóa bản ghi.",
    help_got_it: "Đã Hiểu"
  },
  en: {
    app_title: "AI Music Source Separation",
    app_subtitle: "Next-Gen Vocal & Instrumental Separation Powered by State-of-the-Art AI",
    nav_home: "Home",
    nav_models: "Models",
    nav_history: "History",
    nav_settings: "Settings",
    
    // Hardware badge
    hw_detected: "Hardware Detected",
    hw_cuda_ready: "NVIDIA CUDA Ready",
    hw_cpu_mode: "Multi-threaded CPU Mode",
    
    // Upload area
    upload_title: "Upload Audio Track",
    upload_desc: "Drag and drop or click to browse audio file",
    upload_hint: "Supports MP3, WAV, FLAC, M4A, OGG. Max 100 MB, max duration 8 minutes.",
    select_file_btn: "Browse Audio File",
    file_info_title: "Source Track Details",
    file_name: "File Name:",
    file_size: "File Size:",
    file_duration: "Duration:",
    file_format: "Format:",
    status_valid: "Valid (≤ 100MB, ≤ 8 mins)",
    status_invalid: "Invalid File",
    
    // Action button
    btn_go: "START SEPARATION (GO)",
    btn_processing: "Separating audio stems...",
    
    // Options
    opt_model: "Select AI Model:",
    opt_model_header: "Select AI Model:",
    opt_device: "Inference Device:",
    opt_format: "Output Format:",
    opt_quality: "Segment & Overlap Optimization:",
    mode_quick: "Quick Mode",
    mode_adv: "Adv Mode",
    quick_mode_desc: "Optimized default configuration: HT-Demucs v4 (4 Stems), GPU (CUDA), MP3 320kbps, Segment 256, Overlap 4.",
    adv_mode_desc: "Advanced mode: Full manual control over AI models, inference hardware, audio formats, and Overlap-Add tuning.",
    quick_mode_applied: "Quick Mode activated with optimized defaults!",
    adv_mode_applied: "Switched to Adv Mode (Advanced Customization)!",
    
    // Results
    results_title: "Separation Results",
    results_desc: "Isolated stems generated by AI model:",
    btn_download: "Download",
    btn_download_all: "Download All (ZIP)",
    stem_vocals: "Vocals",
    stem_instrumental: "Instrumental",
    stem_drums: "Drums",
    stem_bass: "Bass",
    stem_other: "Other",
    
    // History
    history_title: "Processing History",
    history_subtitle: "Up to 67 most recent separation tasks (automatic FIFO queue)",
    history_empty: "No separation tasks in history yet.",
    btn_clear_history: "Clear All History",
    history_item_model: "Model:",
    history_item_time: "Processing time:",
    confirm_delete_history_item: "Are you sure you want to delete this history record?",
    confirm_clear_history: "Are you sure you want to clear all history records?",
    history_item_deleted: "History record deleted.",
    history_cleared: "All history records cleared.",

    
    // Settings modal
    modal_settings_title: "System & AI Model Settings",
    settings_device_label: "Hardware Mode",
    settings_device_gpu: "GPU (NVIDIA CUDA) - Ultra Fast, Studio Quality",
    settings_device_cpu: "CPU Mode - Recommended for UVR-MDX-Net",
    settings_model_label: "Default AI Model",
    settings_format_label: "Output Audio Format",
    settings_segment_label: "Segment Size",
    settings_overlap_label: "Overlap Ratio",
    settings_autocast_label: "Enable FP16 Autocast (Saves 50% VRAM)",
    settings_models_installed: "Local Models Status:",
    btn_download_model: "Download Model",
    status_downloaded: "Ready",
    status_not_downloaded: "Not downloaded",
    btn_save_settings: "Save Settings",
    btn_close: "Close",

    // Errors & warnings
    err_size_exceeded: "Error: File size exceeds 100 MB limit!",
    err_duration_exceeded: "Error: Audio duration exceeds 8 minutes (08:00) limit!",
    err_upload_failed: "Failed to upload audio to server.",
    err_select_file_first: "Please select or upload an audio file first.",
    success_saved: "Settings saved successfully!",
    toast_processing_started: "Separation started! This may take 15-40 seconds depending on your hardware...",

    // Lyrics / Karaoke Editor
    lyrics_btn: "🎤 Extract Lyrics",
    lyrics_editor_title: "Karaoke Lyrics Editor",
    lyrics_model_label: "Whisper Model:",
    lyrics_lang_label: "Language:",
    lyrics_lang_auto: "Auto-detect",
    lyrics_btn_extract: "Extract Lyrics",
    lyrics_btn_reextract: "🔄 Re-extract",
    lyrics_download_srt: "💾 Download SRT",
    lyrics_download_lrc: "💾 Download LRC",
    lyrics_col_no: "#",
    lyrics_col_start: "Start",
    lyrics_col_end: "End",
    lyrics_col_text: "Lyrics (click to edit)",
    lyrics_col_seek: "",
    lyrics_extracting: "Recognizing vocals with Whisper AI...",
    lyrics_extract_success: "Extraction complete",
    lyrics_extract_error: "Lyrics extraction failed.",
    lyrics_lines: "lines",
    lyrics_empty_hint: "Click \"Extract Lyrics\" to begin vocal recognition.",
    lyrics_seek_hint: "Jump to this line",
    lyrics_confirm_reextract: "Re-extracting will overwrite current lyrics. Continue?",
    lyrics_confirm_download_srt: "You are about to download an SRT file with {n} lines.\nProceed with download?",
    lyrics_confirm_download_lrc: "You are about to download an LRC file with {n} lines.\nProceed with download?",
    lyrics_no_segments_to_download: "No lyrics to download yet. Please extract first.",
    lyrics_downloading: "Downloading",
    lyrics_save_ok: "Edited lyrics saved.",

    // Help / User Guide Modal
    help_modal_title: "Detailed User Guide",
    help_modal_subtitle: "Step-by-step workflow from uploading audio to source separation & Karaoke editor",
    help_step1_title: "Upload Your Audio Track",
    help_step1_desc: "Drag & drop or click the upload area to choose your audio file. Fully supports MP3, WAV, FLAC, M4A, OGG (Max 100MB, up to 8 minutes). Once uploaded, you can preview the original song directly in the player.",
    help_step2_title: "Select Mode: Quick Mode or Adv Mode",
    help_step2_desc: "⚡ Quick Mode (Default): Automatically preconfigures HT-Demucs v4 (Meta AI), 4-stem separation (Vocals, Drums, Bass, Other), NVIDIA CUDA GPU acceleration, and 320kbps MP3 output. All advanced sliders are hidden for effortless 1-click separation.<br>⚙️ Adv Mode: Unlocks full control to pick Mel-Band RoFormer (Studio standard), UVR-MDX-Net, 24-bit Lossless WAV, Segment Size, and Overlap.",
    help_step3_title: "Start Separation (GO)",
    help_step3_desc: "Click the purple START SEPARATION (GO) button. Real-time progress will track each inference stage. You can click Stop at any time to cancel.",
    help_step4_title: "Preview & Download Stems",
    help_step4_desc: "Each separated stem (Vocals, Drums, Bass, Other) has its own independent audio player. Download individual tracks or grab all of them at once. Click the red arrow button > to toggle collapsing/expanding results.",
    help_step5_title: "Extract Lyrics & Karaoke Editor",
    help_step5_desc: "On the Vocals stem card, click 🎤 Extract Lyrics. Local AI Whisper (100% free offline) will transcribe lyrics. Lines light up in real-time as the song plays, allowing you to edit text, adjust timestamps, and export .SRT or .LRC subtitles.",
    help_step6_title: "History Management & DB Reloading",
    help_step6_desc: "Separations and lyrics are permanently saved into an SQLite database (data/lyrics.db). Click Karaoke Editor on any history card to reopen lyrics instantly without re-running models. Deletion requires user confirmation dialog.",
    help_got_it: "Got It"
  }
};

let currentLang = localStorage.getItem("app_lang") || "vi";

function t(key) {
  const dict = I18N[currentLang] || I18N.vi;
  return dict[key] || key;
}

function applyLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("app_lang", lang);
  document.documentElement.setAttribute("lang", lang);

  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (I18N[lang] && I18N[lang][key]) {
      if (el.tagName === "INPUT" && el.getAttribute("placeholder")) {
        el.placeholder = I18N[lang][key];
      } else {
        el.textContent = I18N[lang][key];
      }
    }
  });

  // Update language toggle UI
  const viBtn = document.getElementById("lang-vi");
  const enBtn = document.getElementById("lang-en");
  if (viBtn && enBtn) {
    if (lang === "vi") {
      viBtn.classList.add("btn-primary");
      viBtn.classList.remove("btn-outline-secondary");
      enBtn.classList.remove("btn-primary");
      enBtn.classList.add("btn-outline-secondary");
    } else {
      enBtn.classList.add("btn-primary");
      enBtn.classList.remove("btn-outline-secondary");
      viBtn.classList.remove("btn-primary");
      viBtn.classList.add("btn-outline-secondary");
    }
  }

  if (typeof updateModeBannerText === "function") {
    updateModeBannerText();
  }
}

