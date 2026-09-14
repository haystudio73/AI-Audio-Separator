# AI Music Source Separation (MSS) - Web Application

Ứng dụng web phân tách giọng hát (Vocals) và nhạc nền (Instrumental/Stems) chất lượng cao bằng Trí tuệ Nhân tạo thế hệ mới (Mel-Band RoFormer, BS-RoFormer, UVR-MDX-Net, HT-Demucs), xây dựng trên nền tảng **Python Flask** và **Bootstrap 5**.

Dự án được xây dựng dựa trên báo cáo nghiên cứu kỹ thuật chuyên sâu về các mô hình phân tách nguồn âm thanh (MSS) nguồn mở hàng đầu trên Hugging Face.

---

## 🌟 Tính Năng Nổi Bật

1. **Kiến Trúc AI Hiện Đại (Hugging Face & Audio-Separator)**:
   - **Mel-Band RoFormer (KimberleyJensen / Unwa)**: Tiêu chuẩn phòng thu (SDR lên tới 14 dB), bảo toàn dải tần số cao và âm hơi (breathiness/sibilants).
   - **UVR-MDX-NET-Inst_HQ_3**: Tối ưu hóa cho Karaoke, dung lượng siêu nhẹ (<70MB), chạy cực nhanh trên CPU (<4GB RAM) hoặc GPU (RTF ~0.01x).
   - **BS-RoFormer (Viperx)**: Band-Split RoFormer kinh điển, tái hiện trung âm chi tiết.
   - **HT-Demucs v4 (Meta AI)**: Tách cùng lúc 4 nguồn âm thanh: Vocals, Drums, Bass, Other.
   - **Dereverb RoFormer**: Khử tiếng vang phòng thu và tiếng vọng, làm sạch giọng hát.
   - **Tự động tải mô hình (Auto Download)**: Kiểm tra và tải tự động các checkpoint từ Hugging Face / GitHub khi người dùng lựa chọn mô hình chưa có trong máy.

2. **Giao Diện Bootstrap 5 Hiện Đại**:
   - Thiết kế giao diện thẻ mờ **Glassmorphism**, hiện đại, sang trọng.
   - **Hỗ trợ 2 chế độ Sáng / Tối (Dark / Light Mode)** chuyển đổi mượt mà với 1 nút bấm.
   - **Song ngữ Toàn diện (Tiếng Việt / English)**: Chuyển đổi ngôn ngữ tức thời không cần tải lại trang.

3. **Kiểm Soát & Xác Thực Tệp Âm Thanh**:
   - **Giới hạn dung lượng**: Tối đa **100 MB** (kiểm tra client-side và server-side `MAX_CONTENT_LENGTH`).
   - **Giới hạn thời lượng**: Tối đa **8 phút** (08:00) (kiểm tra tức thì trên trình duyệt bằng HTML5 Audio metadata và xác minh qua thư viện âm thanh server).
   - **Nút Hành Động GO (Start Separation)**: Mặc định bị **vô hiệu hóa (disabled)**; chỉ khi người dùng chọn/upload tệp hợp lệ (≤ 100MB và ≤ 8 phút), nút GO mới tự động được kích hoạt (enabled) kèm hiệu ứng phát sáng (pulse glow).

4. **Quản Lý Cài Đặt (Settings Management)**:
   - Tự động phát hiện phần cứng: Nhận diện GPU NVIDIA CUDA (ví dụ: RTX 3060/4060) hoặc chuyển đổi chế độ CPU.
   - Cho phép tinh chỉnh cửa sổ trượt Overlap-Add: Segment Size (256, 128, 64) và Overlap (2, 4, 8) nhằm tối ưu chất lượng và tránh tràn VRAM.
   - Tùy chọn định dạng xuất: Lossless WAV, FLAC hoặc nén MP3.
   - Bật/tắt tính toán dấu phẩy động nửa chính xác (FP16 Autocast) giúp tiết kiệm 50% VRAM.

5. **Hệ Thống Lưu Trữ Lịch Sử (History Queue - Tối đa 67 Mục)**:
   - Tự động lưu mọi lượt phân tách thành công vào `history.json`.
   - Cơ chế hàng đợi **FIFO tối đa đúng 67 bản ghi**: Tự động luân chuyển và loại bỏ bản ghi cũ nhất khi vượt quá 67.
   - Trình phát âm thanh trực tiếp (Audio Player) cho từng stem trong lịch sử kèm nút tải xuống riêng lẻ hoặc xóa lịch sử.

---

## 📁 Cấu Trúc Dự Án (Kiến Trúc Tách Biệt 2 Cổng)

```
00. AI app project/
├── frontend.py                 # [Port 3000] Frontend UI Server (Bootstrap 5, Glassmorphism, i18n)
├── backend.py                  # [Port 5000] Backend REST API Server (AI Processing, Audio Streams)
├── run.py                      # Bộ điều khiển thống nhất (khởi chạy cả 2 cổng hoặc riêng lẻ)
├── start.bat                   # File chạy nhanh 1-click cho Windows
├── app.py                      # Wrapper tương thích ngược cho Backend
├── config.py                   # Cấu hình hệ thống (100MB limit, 8 mins limit, paths)
├── settings.json               # Lưu trữ cấu hình người dùng
├── history.json                # Lưu trữ lịch sử xử lý (tối đa 67 mục)
├── requirements.txt            # Danh sách dependencies
├── README.md                   # Hướng dẫn chi tiết sử dụng & cài đặt
├── .agent/                     # Thư mục theo dõi tự động của Agent
│   ├── tasks.md                # Danh sách công việc
│   └── walkthrough.md          # Nhật ký vận hành & kết quả kiểm thử
├── separator_core/             # Module lõi xử lý AI và âm thanh
│   ├── audio_utils.py          # Kiểm tra file size, duration (max 8 phút), format
│   ├── history_manager.py      # Quản lý lịch sử (tối đa 67 items FIFO)
│   ├── model_manager.py        # Quản lý danh mục mô hình & tự động tải
│   ├── separator_service.py    # Wrapper điều khiển audio-separator (CUDA/CPU)
│   └── settings_service.py     # Đọc/Lưu cài đặt người dùng
├── static/
│   ├── css/
│   │   └── style.css           # Custom CSS, dark/light theme tokens, animations
│   └── js/
│       ├── i18n.js             # Từ điển song ngữ VI / EN
│       ├── settings.js         # Quản lý cài đặt & gọi Backend API (Port 5000)
│       └── app.js              # Upload, validation, nút GO, player & stems (Port 5000)
├── templates/
│   └── index.html              # Giao diện chính Bootstrap 5
└── data/
    ├── uploads/                # Tệp âm thanh upload tạm
    ├── outputs/                # Các stems âm thanh sau khi phân tách
    └── models/                 # Cache lưu trữ các mô hình AI đã tải
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Yêu Cầu Hệ Thống
- Hệ điều hành: Windows 10/11, Linux, macOS.
- Python: Phiên bản >= 3.10 (khuyến nghị Python 3.11 - 3.13). Links down => https://www.python.org/downloads/windows/
- Phần cứng:
  - Khuyến nghị có GPU NVIDIA (tối thiểu 4GB VRAM cho segment 128, hoặc >= 6-8GB VRAM cho segment 256) kèm driver CUDA.
  - Hoặc CPU đa luồng (với mô hình UVR-MDX-NET Inst HQ 3).
- Đã cài đặt **FFmpeg** trên hệ thống (đã có trong PATH). Link down => https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z

### 2. Cài Đặt Thư Viện

Mở terminal trong thư mục dự án và chạy lệnh:
```bash
# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

Nếu sử dụng GPU NVIDIA CUDA:
```bash
pip install "audio-separator[gpu]"
```

Nếu sử dụng máy thuần CPU:
```bash
pip install "audio-separator[cpu]"
```

### 3. Khởi Chạy Ứng Dụng (2 Cổng: 3000 UI & 5000 API)

#### Cách 1: Chạy đồng thời cả 2 dịch vụ bằng 1 lệnh (Khuyến nghị)
- **Trên Windows**: Nhấp đúp chuột vào tệp `start.bat`
- Hoặc chạy lệnh qua terminal:
```bash
python run.py
```

Lệnh trên sẽ tự động khởi động:
- **Frontend Browser UI**: `http://localhost:3000`
- **Backend REST API**: `http://localhost:5000`

#### Cách 2: Chạy riêng lẻ từng dịch vụ

- **Chỉ chạy Backend API (Port 5000)**:
```bash
python run.py --backend
# hoặc:
python backend.py
```

- **Chỉ chạy Frontend UI (Port 3000)**:
```bash
python run.py --frontend
# hoặc:
python frontend.py
```

#### Cách 3: Tùy chỉnh cổng tùy ý
```bash
python run.py --port-front 3000 --port-back 5000
```

Mở trình duyệt web và truy cập giao diện tại:
```
http://localhost:3000
```

---

## 📖 Hướng Dẫn Sử Dụng

1. **Kiểm tra phần cứng & Cấu hình**:
   - Ở thanh điều hướng trên cùng, ứng dụng sẽ hiển thị GPU phát hiện được (ví dụ: *NVIDIA GeForce RTX 3060*).
   - Nhấp vào nút **Cấu hình (Settings)** để xem các mô hình và trạng thái tải sẵn. Bạn có thể nhấn *Tải mô hình* trước hoặc để ứng dụng tự động tải khi bắt đầu tách.
2. **Chọn ngôn ngữ & Chế độ Sáng/Tối**:
   - Nhấn **VI** hoặc **EN** để chuyển đổi ngôn ngữ.
   - Nhấn nút biểu tượng Mặt trời / Mặt trăng để chuyển chế độ Dark / Light.
3. **Tải lên tệp âm thanh**:
   - Kéo thả file nhạc hoặc nhấn *Chọn tệp từ máy tính*.
   - Hệ thống sẽ tự động xác thực:
     - Dung lượng ≤ 100 MB.
     - Thời lượng ≤ 8 phút (08:00).
   - Nếu file hợp lệ: Thông tin bài hát sẽ hiển thị và nút **BẮT ĐẦU TÁCH NHẠC (GO)** sẽ sáng lên kèm hiệu ứng phát sáng.
   - Nếu file vượt quá giới hạn: Thông báo lỗi cảnh báo màu đỏ sẽ xuất hiện và nút **GO** vẫn bị khóa.
4. **Bắt đầu phân tách**:
   - Chọn mô hình mong muốn (Mel-Band RoFormer cho chất lượng phòng thu cao nhất, hoặc UVR-MDX-Net nếu muốn tạo beat Karaoke nhanh).
   - Nhấn nút **BẮT ĐẦU TÁCH NHẠC (GO)**.
   - Quá trình tách sẽ diễn ra (thường mất 15 - 35 giây với GPU RTX 3060).
5. **Nghe thử & Tải về**:
   - Sau khi hoàn tất, kết quả các track (Vocals, Instrumental, v.v.) sẽ xuất hiện trực quan với player nghe thử và nút *Tải xuống*.
   - Bản ghi này đồng thời được lưu vào bảng **Lịch sử Xử lý** (tối đa 67 lượt).

---

## 📡 Danh Sách API Endpoints

| Phương thức | Đường dẫn | Chức năng |
|---|---|---|
| `GET` | `/` | Giao diện web chính |
| `GET` | `/api/system_info` | Thông tin GPU, CUDA, VRAM, CPU threads |
| `GET` | `/api/models` | Danh sách mô hình AI và trạng thái tải |
| `POST` | `/api/models/download` | Tải trước một checkpoint mô hình AI |
| `GET` | `/api/settings` | Lấy cấu hình hệ thống |
| `POST` | `/api/settings` | Lưu cấu hình hệ thống |
| `POST` | `/api/upload` | Upload audio và xác thực giới hạn (100MB, 8 phút) |
| `POST` | `/api/separate` | Kích hoạt phân tách stems và lưu vào lịch sử |
| `GET` | `/api/history` | Lấy danh sách lịch sử (tối đa 67 bản ghi) |
| `DELETE` | `/api/history/<id>` | Xóa 1 bản ghi lịch sử cụ thể |
| `DELETE` | `/api/history` | Xóa sạch toàn bộ lịch sử |
| `GET` | `/api/audio/<folder>/<filename>` | Stream hoặc tải file âm thanh |
