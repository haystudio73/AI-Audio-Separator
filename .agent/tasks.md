# Danh sách Công việc (Tasks) - AI Music Source Separation

- [x] **Giai đoạn 1: Khởi tạo cấu trúc dự án và tài liệu**
  - [x] Tạo thư mục `.agent/` và các tệp theo dõi `tasks.md`, `walkthrough.md`
  - [x] Cấu hình `requirements.txt` và cài đặt thư viện (`audio-separator`, `flask`, ...)
  - [x] Tạo `README.md` chi tiết tại thư mục gốc của ứng dụng

- [x] **Giai đoạn 2: Xây dựng Backend Core**
  - [x] `config.py`: Định nghĩa cấu hình hệ thống (100MB upload limit, 8 phút duration limit, thư mục dữ liệu)
  - [x] `separator_core/audio_utils.py`: Kiểm tra định dạng file, xác minh độ dài (max 8 phút) và dung lượng (max 100MB)
  - [x] `separator_core/history_manager.py`: Hệ thống quản lý lịch sử (tối đa đúng 67 mục, FIFO, lưu vào `history.json`)
  - [x] `separator_core/model_manager.py`: Danh mục các mô hình theo báo cáo (Mel-Band RoFormer, MDX-Net, HT-Demucs), kiểm tra và tải mô hình
  - [x] `separator_core/separator_service.py`: Xử lý phân tách âm thanh bằng `audio-separator`, hỗ trợ GPU (CUDA) và CPU, autocast FP16

- [x] **Giai đoạn 3: Phân tách Kiến trúc 2 Cổng (Port 3000 UI & Port 5000 API)**
  - [x] `backend.py`: Flask REST API độc lập chạy trên cổng **5000**
    - `POST /api/upload`: Nhận file upload, kiểm tra validation (100MB, 8 phút), lưu tạm
    - `POST /api/separate`: Kích hoạt bóc tách với model & device đã chọn
    - `GET /api/models`: Danh sách mô hình và trạng thái đã tải
    - `POST /api/models/download`: Kích hoạt tải model trước
    - `GET/POST /api/settings`: Đọc/Lưu cấu hình hệ thống
    - `GET/DELETE /api/history`: Quản lý danh sách lịch sử (tối đa 67 mục)
    - `GET /api/audio/<folder>/<filename>`: Stream audio và tải file stems
    - `GET /api/health`: Health check & API status
    - Hỗ trợ CORS đầy đủ cho giao tiếp từ Frontend (port 3000)
  - [x] `frontend.py`: Flask Web Server chạy trên cổng **3000**
    - Phục vụ giao diện người dùng Bootstrap 5 tại `http://localhost:3000`
    - Cấu hình Backend URL linh hoạt qua biến môi trường hoặc mặc định `http://localhost:5000`
    - Tích hợp reverse-proxy fallback cho `/api/<endpoint>`
  - [x] `run.py`: Script điều khiển hợp nhất, chạy song song cả 2 dịch vụ hoặc chạy riêng lẻ
  - [x] `start.bat`: Script khởi chạy nhanh 1-click cho Windows

- [x] **Giai đoạn 4: Giao diện Người dùng (Frontend)**
  - [x] `templates/index.html`: Giao diện Bootstrap 5, Dark/Light mode, badges UI:3000 và API:5000, trạng thái kết nối backend
  - [x] `static/css/style.css`: Theme Dark/Light mượt mà, hiệu ứng glassmorphism, pulse cho nút GO
  - [x] `static/js/i18n.js`: Hệ thống song ngữ VI / EN toàn diện
  - [x] `static/js/app.js`: Xử lý kéo thả upload, kiểm tra client-side (<100MB, <8min), kích hoạt nút GO khi hợp lệ, player đồng bộ stems trỏ về Backend port 5000
  - [x] `static/js/settings.js`: Quản lý cài đặt cấu hình GPU/CPU, mô hình mặc định, theo dõi API health kết nối port 5000

- [x] **Giai đoạn 5: Kiểm thử, Tối ưu và Hoàn thiện**
  - [x] Kiểm thử toàn diện 9 test cases trong `tests/test_app.py` (Backend API, CORS, Preflight OPTIONS, Frontend HTML, Audio Validation, 67 History FIFO)
  - [x] Cập nhật tài liệu `README.md` và `walkthrough.md`
