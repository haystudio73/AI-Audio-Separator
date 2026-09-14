# Hướng Dẫn Vận Hành & Nhật Ký Kiểm Thử (Walkthrough)

## 1. Giới thiệu Ứng dụng
Ứng dụng Phân tách Giọng hát và Nhạc nền AI (Music Source Separation) được xây dựng dựa trên nghiên cứu các mô hình AI hiện đại nhất (Mel-Band RoFormer, UVR-MDX-Net, HT-Demucs) từ Hugging Face.

## 2. Nhật ký Tiến độ & Thực thi
- **Khởi tạo**: Đã tạo cấu trúc dự án và thiết lập hệ thống theo dõi tác vụ.
- **Backend & Core**: Đang triển khai logic xử lý âm thanh, tải mô hình và quản lý lịch sử (tối đa 67 bản ghi).
- **Giao diện**: Triển khai giao diện Bootstrap 5 với Dark/Light mode và song ngữ VI/EN.
- **Kiến trúc 2 Cổng**: Tách biệt thành Frontend UI (Port 3000) và Backend REST API (Port 5000), tích hợp CORS và runner `run.py`.

## 3. Kiến Trúc Phân Tách 2 Cổng
- **Frontend (Port 3000)**: `frontend.py` phục vụ giao diện trình duyệt tại `http://localhost:3000`.
- **Backend (Port 5000)**: `backend.py` phục vụ toàn bộ REST APIs và audio streaming tại `http://localhost:5000`.
- **Khởi chạy**: Dùng `python run.py` hoặc `start.bat` để chạy đồng thời cả hai.


### [2026-09-04 12:22:30] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-04 12:22:30] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-04 12:58:36] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-04 12:58:36] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-04 13:04:08] Cập Nhật Cài Đặt
- **theme**: dark

### [2026-09-04 13:04:19] Cập Nhật Cài Đặt
- **theme**: light

### [2026-09-04 15:47:37] Upload Audio Thành Công
- **Filename**: test_sample.wav
- **Dung lượng**: 344.6 KB
- **Thời lượng**: 00:04

### [2026-09-05 10:53:33] Upload Audio Thành Công
- **Filename**: SAI_GON_24H_Claude_Cover.mp3
- **Dung lượng**: 8.0 MB
- **Thời lượng**: 05:38

### [2026-09-05 11:04:10] Tải Model Thành Công
- **Model**: melband_roformer_big_beta4.ckpt

### [2026-09-05 11:07:42] Upload Audio Thành Công
- **Filename**: SAI_GON_24H_Claude_Cover.mp3
- **Dung lượng**: 8.0 MB
- **Thời lượng**: 05:38

### [2026-09-05 11:56:24] Upload Audio Thành Công
- **Filename**: SAI_GON_24H_Claude_Cover.mp3
- **Dung lượng**: 8.0 MB
- **Thời lượng**: 05:38

### [2026-09-05 12:09:30] Upload Audio Thành Công
- **Filename**: December_in_Saigon_Final.mp3
- **Dung lượng**: 3.5 MB
- **Thời lượng**: 02:43

### [2026-09-05 12:15:09] Upload Audio Thành Công
- **Filename**: December_in_Saigon_Final.mp3
- **Dung lượng**: 3.5 MB
- **Thời lượng**: 02:43

### [2026-09-05 14:57:39] Upload Audio Thành Công
- **Filename**: December_in_Saigon_Final.mp3
- **Dung lượng**: 3.5 MB
- **Thời lượng**: 02:43

### [2026-09-06 11:21:48] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 11:21:48] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 11:29:14] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 11:29:14] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 11:29:57] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 11:29:57] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 11:36:12] Upload Audio Thành Công
- **Filename**: December_in_Saigon_Final.mp3
- **Dung lượng**: 3.5 MB
- **Thời lượng**: 02:43

### [2026-09-06 12:06:21] Upload Audio Thành Công
- **Filename**: December_in_Saigon_Final.mp3
- **Dung lượng**: 3.5 MB
- **Thời lượng**: 02:43

### [2026-09-06 12:34:44] Upload Audio Thành Công
- **Filename**: December_in_Saigon_Final.mp3
- **Dung lượng**: 3.5 MB
- **Thời lượng**: 02:43

### [2026-09-06 12:49:57] Upload Audio Thành Công
- **Filename**: SAI_GON_24H_Claude_Cover.mp3
- **Dung lượng**: 8.0 MB
- **Thời lượng**: 05:38

### [2026-09-06 12:50:18] Upload Audio Thành Công
- **Filename**: MUA_LANH_Final.mp3
- **Dung lượng**: 5.4 MB
- **Thời lượng**: 04:18

### [2026-09-06 13:09:08] Upload Audio Thành Công
- **Filename**: MUA_LANH_Final.mp3
- **Dung lượng**: 5.4 MB
- **Thời lượng**: 04:18

### [2026-09-06 13:11:21] Upload Audio Thành Công
- **Filename**: Khong_Ban.mp3
- **Dung lượng**: 2.3 MB
- **Thời lượng**: 02:30

### [2026-09-06 16:46:05] Tải Model Thành Công
- **Model**: dereverb_mel_band_roformer_anvuew_sdr_19.1729.ckpt

### [2026-09-06 16:47:39] Tải Model Thành Công
- **Model**: model_bs_roformer_ep_317_sdr_12.9755.ckpt

### [2026-09-06 16:48:03] Upload Audio Thành Công
- **Filename**: MUA_LANH_ver_2.mp3
- **Dung lượng**: 4.7 MB
- **Thời lượng**: 03:37

### [2026-09-06 18:52:50] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:52:50] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:53:13] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:53:13] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:53:27] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:53:27] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:53:44] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:53:44] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:53:57] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:53:57] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:54:12] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:54:12] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:54:27] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:54:27] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:54:44] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:54:45] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:54:57] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:54:58] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:55:11] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:55:11] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:55:26] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:55:26] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:56:07] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:56:07] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:56:55] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:56:55] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:58:43] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:58:43] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:59:25] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:59:25] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:59:41] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:59:41] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-07 13:22:57] Upload Audio Thành Công
- **Filename**: MUA_LANH_ver_2.mp3
- **Dung lượng**: 4.7 MB
- **Thời lượng**: 03:37

### [2026-09-07 13:24:31] Hoàn Tất Phân Tách Âm Thanh
- **File**: MUA_LANH_ver_2.mp3
- **Model**: mel_band_roformer_kim_ft3_unwa.ckpt
- **Thiết bị**: cuda
- **Thời gian xử lý**: 50.49s
- **Số lượng stems**: 2

### [2026-09-07 13:36:13] Hoàn Tất Phân Tách Âm Thanh
- **File**: MUA_LANH_ver_2.mp3
- **Model**: dereverb_mel_band_roformer_anvuew_sdr_19.1729.ckpt
- **Thiết bị**: cuda
- **Thời gian xử lý**: 47.78s
- **Số lượng stems**: 2

### [2026-09-07 13:42:01] Upload Audio Thành Công
- **Filename**: December_in_Saigon_Final.mp3
- **Dung lượng**: 3.5 MB
- **Thời lượng**: 02:43

### [2026-09-07 13:43:38] Hoàn Tất Phân Tách Âm Thanh
- **File**: December_in_Saigon_Final.mp3
- **Model**: mel_band_roformer_kim_ft3_unwa.ckpt
- **Thiết bị**: cuda
- **Thời gian xử lý**: 79.52s
- **Số lượng stems**: 2

### [2026-09-13 19:56:31] Tải Model Thành Công
- **Model**: htdemucs.yaml

### [2026-09-13 19:56:58] Upload Audio Thành Công
- **Filename**: MUA_LANH_Final_Cover.mp3
- **Dung lượng**: 5.4 MB
- **Thời lượng**: 03:54

### [2026-09-13 19:57:32] Hoàn Tất Phân Tách Âm Thanh
- **File**: MUA_LANH_Final_Cover.mp3
- **Model**: htdemucs.yaml
- **Thiết bị**: cuda
- **Thời gian xử lý**: 20.73s
- **Số lượng stems**: 4

### [2026-09-13 20:00:52] Upload Audio Thành Công
- **Filename**: Revenge_on_xDemon_SELECTED.mp3
- **Dung lượng**: 3.7 MB
- **Thời lượng**: 02:44

### [2026-09-13 20:01:07] Hoàn Tất Phân Tách Âm Thanh
- **File**: Revenge_on_xDemon_SELECTED.mp3
- **Model**: htdemucs.yaml
- **Thiết bị**: cuda
- **Thời gian xử lý**: 12.65s
- **Số lượng stems**: 4

### [2026-09-13 20:05:06] Xóa Toàn Bộ Lịch Sử
- **Status**: Cleared

### [2026-09-13 20:42:29] Upload Audio Thành Công
- **Filename**: Revenge_on_xDemon_SELECTED.mp3
- **Dung lượng**: 3.7 MB
- **Thời lượng**: 02:44

### [2026-09-13 20:42:53] Hoàn Tất Phân Tách Âm Thanh
- **File**: Revenge_on_xDemon_SELECTED.mp3
- **Model**: htdemucs.yaml
- **Thiết bị**: cuda
- **Thời gian xử lý**: 11.51s
- **Số lượng stems**: 4

### [2026-09-06 18:53:27] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:53:44] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:53:44] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:53:57] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:53:57] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:54:12] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:54:12] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:54:27] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:54:27] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:54:44] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:54:45] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:54:57] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:54:58] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:55:11] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:55:11] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:55:26] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:55:26] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:56:07] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:56:07] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:56:55] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:56:55] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:58:43] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:58:43] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:59:25] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:59:25] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-06 18:59:41] Cập Nhật Cài Đặt
- **output_format**: MP3
- **theme**: light

### [2026-09-06 18:59:41] Upload Audio Thành Công
- **Filename**: test_track.wav
- **Dung lượng**: 62.5 KB
- **Thời lượng**: 00:02

### [2026-09-07 13:22:57] Upload Audio Thành Công
- **Filename**: MUA_LANH_ver_2.mp3
- **Dung lượng**: 4.7 MB
- **Thời lượng**: 03:37

### [2026-09-07 13:24:31] Hoàn Tất Phân Tách Âm Thanh
- **File**: MUA_LANH_ver_2.mp3
- **Model**: mel_band_roformer_kim_ft3_unwa.ckpt
- **Thiết bị**: cuda
- **Thời gian xử lý**: 50.49s
- **Số lượng stems**: 2

### [2026-09-07 13:36:13] Hoàn Tất Phân Tách Âm Thanh
- **File**: MUA_LANH_ver_2.mp3
- **Model**: dereverb_mel_band_roformer_anvuew_sdr_19.1729.ckpt
- **Thiết bị**: cuda
- **Thời gian xử lý**: 47.78s
- **Số lượng stems**: 2

### [2026-09-07 13:42:01] Upload Audio Thành Công
- **Filename**: December_in_Saigon_Final.mp3
- **Dung lượng**: 3.5 MB
- **Thời lượng**: 02:43

### [2026-09-07 13:43:38] Hoàn Tất Phân Tách Âm Thanh
- **File**: December_in_Saigon_Final.mp3
- **Model**: mel_band_roformer_kim_ft3_unwa.ckpt
- **Thiết bị**: cuda
- **Thời gian xử lý**: 79.52s
- **Số lượng stems**: 2

### [2026-09-13 19:56:31] Tải Model Thành Công
- **Model**: htdemucs.yaml

### [2026-09-13 19:56:58] Upload Audio Thành Công
- **Filename**: MUA_LANH_Final_Cover.mp3
- **Dung lượng**: 5.4 MB
- **Thời lượng**: 03:54

### [2026-09-13 19:57:32] Hoàn Tất Phân Tách Âm Thanh
- **File**: MUA_LANH_Final_Cover.mp3
- **Model**: htdemucs.yaml
- **Thiết bị**: cuda
- **Thời gian xử lý**: 20.73s
- **Số lượng stems**: 4

### [2026-09-13 20:00:52] Upload Audio Thành Công
- **Filename**: Revenge_on_xDemon_SELECTED.mp3
- **Dung lượng**: 3.7 MB
- **Thời lượng**: 02:44

### [2026-09-13 20:01:07] Hoàn Tất Phân Tách Âm Thanh
- **File**: Revenge_on_xDemon_SELECTED.mp3
- **Model**: htdemucs.yaml
- **Thiết bị**: cuda
- **Thời gian xử lý**: 12.65s
- **Số lượng stems**: 4

### [2026-09-13 20:05:06] Xóa Toàn Bộ Lịch Sử
- **Status**: Cleared

### [2026-09-13 20:42:29] Upload Audio Thành Công
- **Filename**: Revenge_on_xDemon_SELECTED.mp3
- **Dung lượng**: 3.7 MB
- **Thời lượng**: 02:44

### [2026-09-13 20:42:53] Hoàn Tất Phân Tách Âm Thanh
- **File**: Revenge_on_xDemon_SELECTED.mp3
- **Model**: htdemucs.yaml
- **Thiết bị**: cuda
- **Thời gian xử lý**: 11.51s
- **Số lượng stems**: 4

### [2026-09-13 20:45:26] Trích Xuất Lyrics
- **File**: 7f5f030ed635_Revenge_on_xDemon_SELECTED_(Demucs_Vocals).wav
- **Model Whisper**: small
- **Số dòng**: 38

### [2026-09-13 20:50:00] Tích Hợp Lịch Sử Lyrics Vào DB (history.json & SQLite)
- **Cơ sở dữ liệu SQLite**:
  - Tệp DB: `data/lyrics.db` quản lý qua [`separator_core/lyrics_db.py`](file:///e:/Projects/00.%20AI%20app%20project/separator_core/lyrics_db.py).
  - Lưu trữ đầy đủ bảng `lyrics_history`: ID, tên file vocals, whisper model, ngôn ngữ, tổng số dòng, đường dẫn SRT/LRC, toàn bộ phân đoạn JSON (`segments_json`), timestamp.
  - Hỗ trợ REST APIs: `/api/lyrics/db/history`, `/api/lyrics/db/history/<id>`, DELETE, CLEAR.
- **Tính năng Mở lại (Reopen in Karaoke Editor)**:
  - Khi người dùng click **"Karaoke Editor"** từ mục lịch sử, hệ thống tự động tải lại các câu lyrics từ SQLite DB và mở trình chỉnh sửa ngay lập tức mà **không cần chạy lại Whisper STT**.
- **Đồng bộ hóa 2 chiều**:
  - Vừa lưu vào SQLite DB (lưu toàn bộ segments chi tiết), vừa đồng bộ với `history.json` (hiển thị danh sách UI).
  - Khi xóa bản ghi khỏi lịch sử, hệ thống tự động dọn dẹp bản ghi tương ứng trong SQLite DB.

### [2026-09-13 21:05:00] Tích Hợp Chế Độ Quick Mode & Adv Mode
- **Giao diện chuyển đổi Mode**:
  - Tích hợp bộ nút chuyển đổi dạng capsule `[⚡ Quick Mode]` và `[⚙️ Adv Mode]` tại tiêu đề thẻ cấu hình mô hình AI.
  - Banner trạng thái thông minh hiển thị mô tả trực quan theo từng chế độ.
- **Cấu hình mặc định của Quick Mode (Khớp 100% hình ảnh yêu cầu)**:
  - **Mô hình AI**: `HT-Demucs v4 (Meta AI) [4 Stems Isolation] - 9.2 - 11.5 dB` (`htdemucs.yaml`)
  - **Thiết bị xử lý**: `GPU (NVIDIA CUDA)` (`cuda`)
  - **Định dạng xuất**: `MP3 (320kbps)` (`MP3`)
  - **Tối ưu hóa (Segment & Overlap)**:
    - **Segment Size**: `256 (Khuyến nghị VRAM >= 6GB)`
    - **Overlap**: `4 (Mượt mà, cân bằng)`
    - Huy hiệu **SDR Optimizer**
- **Chế độ Adv Mode**:
  - Cho phép tùy chỉnh thủ công toàn diện mọi mô hình (Mel-Band RoFormer, UVR-MDX-Net, BS-RoFormer...), thiết bị (CPU/GPU), định dạng xuất lossless (WAV, FLAC, MP3), và các thông số Overlap-Add.
- **Lưu trữ trạng thái**:
  - Lưu chế độ đã chọn vào `localStorage.setItem("app_separation_mode", mode)`, tự động ghi nhớ cho các phiên làm việc tiếp theo.
  - Hỗ trợ song ngữ đầy đủ (VI/EN).


### [2026-09-13 21:47:00] Cập Nhật Cài Đặt
- **device**: cuda
- **output_format**: MP3
- **use_autocast**: False

### [2026-09-13 21:47:07] Xóa Toàn Bộ Lịch Sử
- **Status**: Cleared

### [2026-09-13 21:47:48] Upload Audio Thành Công
- **Filename**: HIDING_IN_THE_JUNGLE_SELECTED.mp3
- **Dung lượng**: 5.2 MB
- **Thời lượng**: 04:01

### [2026-09-13 21:52:34] Hoàn Tất Phân Tách Âm Thanh
- **File**: HIDING_IN_THE_JUNGLE_SELECTED.mp3

### [2026-09-13 21:47:00] Cập Nhật Cài Đặt
- **device**: cuda
- **output_format**: MP3
- **use_autocast**: False

### [2026-09-13 21:47:07] Xóa Toàn Bộ Lịch Sử
- **Status**: Cleared

### [2026-09-13 21:47:48] Upload Audio Thành Công
- **Filename**: HIDING_IN_THE_JUNGLE_SELECTED.mp3
- **Dung lượng**: 5.2 MB
- **Thời lượng**: 04:01

### [2026-09-13 21:52:34] Hoàn Tất Phân Tách Âm Thanh
- **File**: HIDING_IN_THE_JUNGLE_SELECTED.mp3
- **Model**: mel_band_roformer_kim_ft3_unwa.ckpt
- **Thiết bị**: cuda
- **Thời gian xử lý**: 203.47s
- **Số lượng stems**: 2

### [2026-09-13 22:12:53] Trích Xuất Lyrics
- **File**: eb3aa3e93ec7_HIDING_IN_THE_JUNGLE_SELECTED_(vocals)_mel_band_roformer_kim_ft3_unwa.mp3
- **Model Whisper**: base
- **Ngôn ngữ phát hiện**: en
- **Số dòng**: 104
- **DB ID**: 3

### [2026-09-13 22:18:00] Tối Giản Quick Mode & Nút Mũi Tên Đóng/Mở (Collapsible Sections)
1. **Ẩn toàn bộ cài đặt khi ở Quick Mode**:
   - Khung tham số nâng cao (`#adv-settings-panel`) được ẩn hoàn toàn (`d-none`) khi ở Quick Mode.
   - Chỉ giữ lại banner trạng thái cấu hình tối ưu sẵn và nút GO (1-Click Separation).
   - Khi chuyển sang **Adv Mode**, toàn bộ các cài đặt mô hình, thiết bị, định dạng xuất và thông số Overlap-Add xuất hiện trở lại đầy đủ.
2. **Nút mũi tên đóng/mở (Show/Hidden) nội dung**:
   - **Mục "Kết quả Phân tách"**: Thêm mũi tên màu đỏ `>` bên cạnh tiêu đề. Nhấp vào sẽ thu gọn/mở rộng các stem âm thanh bên dưới. Tự động mở rộng khi có kết quả mới.
   - **Mục "Lịch sử Xử lý"**: Thêm mũi tên màu đỏ `>` bên cạnh huy hiệu đếm `1/67`. Nhấp vào sẽ thu gọn/mở rộng toàn bộ danh sách lịch sử.
   - Hiệu ứng xoay mũi tên 90 độ mượt mà khi đóng/mở.

### [2026-09-13 22:23:20] Trích Xuất Lyrics
- **File**: eb3aa3e93ec7_HIDING_IN_THE_JUNGLE_SELECTED_(vocals)_mel_band_roformer_kim_ft3_unwa.mp3
- **Model Whisper**: medium
- **Ngôn ngữ phát hiện**: en
- **Số dòng**: 74
- **DB ID**: 5

### [2026-09-13 22:29:16] Xóa Mục Lịch Sử
- **ID**: hist_1789313000587

### [2026-09-13 22:29:17] Xóa Mục Lịch Sử

### [2026-09-13 22:23:20] Trích Xuất Lyrics
- **File**: eb3aa3e93ec7_HIDING_IN_THE_JUNGLE_SELECTED_(vocals)_mel_band_roformer_kim_ft3_unwa.mp3
- **Model Whisper**: medium
- **Ngôn ngữ phát hiện**: en
- **Số dòng**: 74
- **DB ID**: 5

### [2026-09-13 22:29:16] Xóa Mục Lịch Sử
- **ID**: hist_1789313000587

### [2026-09-13 22:29:17] Xóa Mục Lịch Sử
- **ID**: hist_1789312878485

### [2026-09-13 22:29:26] Xóa Mục Lịch Sử
- **ID**: hist_1789311154829

### [2026-09-13 22:29:31] Xóa Mục Lịch Sử
- **ID**: hist_1789313209579

### [2026-09-13 22:31:00] Bổ Sung Xác Nhận (Confirm Dialog) Trước Khi Xóa
1. **Xóa từng bản ghi lịch sử (`deleteHistoryEntry`)**:
   - Khi người dùng nhấp vào biểu tượng thùng rác (icon trash), hệ thống hiển thị hộp thoại xác nhận:
     `"Bạn có chắc chắn muốn xóa bản ghi lịch sử này không?"` kèm theo tên tệp bài hát / file vocals tương ứng.
   - Nếu người dùng chọn **Cancel / Hủy**: Thao tác xóa bị hủy bỏ ngay lập tức, dữ liệu được giữ nguyên vẹn.
   - Nếu người dùng chọn **OK / Xác nhận**: Thực hiện gọi API DELETE và hiển thị Toast thông báo.
2. **Xóa toàn bộ lịch sử (`btn-clear-history`)**:
   - Tương tự, bổ sung thông điệp đa ngôn ngữ (VI/EN) chuẩn qua `i18n.js`.

### [2026-09-13 22:35:42] Xóa Mục Lịch Sử
- **ID**: hist_1789312373332

### [2026-09-13 22:36:11] Upload Audio Thành Công
- **Filename**: Ky_uc_Tay_Nguyen_master.wav
- **Dung lượng**: 97.0 MB
- **Thời lượng**: 04:24

### [2026-09-13 22:36:34] Hoàn Tất Phân Tách Âm Thanh
- **File**: Ky_uc_Tay_Nguyen_master.wav
- **Model**: htdemucs.yaml
- **Thiết bị**: cuda
- **Thời gian xử lý**: 15.68s
- **Số lượng stems**: 4

### [2026-09-13 22:38:00] Trích Xuất Lyrics
- **File**: e705db9454d5_Ky_uc_Tay_Nguyen_master_(Demucs_Vocals).wav
- **Model Whisper**: medium
- **Ngôn ngữ phát hiện**: vi
- **Số dòng**: 19
- **DB ID**: 7

### [2026-09-13 22:42:09] Cập Nhật Cài Đặt
- **theme**: dark

### [2026-09-13 22:43:25] Cập Nhật Cài Đặt
- **theme**: light

### [2026-09-13 22:50:41] Cập Nhật Cài Đặt
- **theme**: dark

### [2026-09-13 22:54:56] Cập Nhật Cài Đặt
- **theme**: light
