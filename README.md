# Fashion Finder

Ứng dụng web tìm kiếm cửa hàng thời trang gần vị trí hiện tại với tư vấn AI thông minh sử dụng Google Gemini.

## Tổng quan

Fashion Finder là hệ thống tích hợp địa lý và trí tuệ nhân tạo, cho phép người dùng:
- Tìm kiếm cửa hàng quần áo trong bán kính tối đa 500km
- Nhận tư vấn thời trang từ AI dựa trên vị trí và nhu cầu
- Xem bản đồ tương tác với vị trí người dùng và cửa hàng
- Mở cửa hàng trực tiếp trong Google Maps

## Công nghệ sử dụng

**Frontend**
- HTML5, CSS3, JavaScript ES6+
- LeafletJS cho bản đồ tương tác
- Dark/Light mode toggle

**Backend**
- Python 3.9+
- FastAPI framework
- Geopy cho tính toán địa lý

**AI & Database**
- Google Gemini API (Gemini Flash Latest)
- Google Sheets API (tùy chọn)
- Dữ liệu mẫu tích hợp sẵn

## Cấu trúc dự án

```
HTKDTM/
├── backend/
│   ├── app.py                  # FastAPI application
│   ├── geofilter.py            # Lọc cửa hàng theo vị trí địa lý
│   ├── gsheet_connector.py     # Kết nối Google Sheets
│   ├── gemini_service.py       # Xử lý AI Gemini
│   ├── requirements.txt        # Dependencies
│   ├── .env                    # Environment variables (không commit)
│   └── sample_data.json        # Dữ liệu mẫu 15 cửa hàng
├── frontend/
│   ├── index.html              # Trang chính
│   ├── script.js               # Logic xử lý
│   └── styles.css              # Styling
├── .gitignore                  # Git ignore rules
├── install_python_deps.ps1     # Script cài đặt dependencies
├── GITHUB_SETUP.md             # Hướng dẫn push code lên GitHub
└── README.md                   # Tài liệu này
```

## Yêu cầu hệ thống

- Python 3.9 trở lên
- Trình duyệt web hiện đại (Chrome, Firefox, Edge)
- Kết nối Internet
- Google Gemini API Key (tùy chọn, nếu muốn dùng AI)

## Cài đặt

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd HTKDTM
```

### Bước 2: Cài đặt Python dependencies

**Cách 1: Sử dụng script tự động (khuyến nghị)**

```powershell
.\install_python_deps.ps1
```

**Cách 2: Cài đặt thủ công**

```bash
cd backend
pip install -r requirements.txt
```

### Bước 3: Cấu hình môi trường

Tạo file `backend/.env` với nội dung:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_SHEETS_CREDENTIALS=your_credentials_json
HOST=0.0.0.0
PORT=8000
PRIORITY_RADIUS_KM=20.0
MAX_RADIUS_KM=500.0
MAX_SHOPS=30
```

**Lưu ý:**
- Lấy Gemini API Key tại: https://aistudio.google.com/app/apikey
- Nếu không có API key, ứng dụng vẫn hoạt động với phản hồi mặc định
- File `.env` đã được loại khỏi git, cần tự tạo trên mỗi máy

### Bước 4: Khởi động Ứng dụng

Terminal 1 - Backend (không reload):
```bash
cd backend
py app.py
```

Hoặc Backend với reload (tự động reload khi code thay đổi):
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
py -m http.server 5500
```

Truy cập:
- Frontend: http://localhost:5500
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Sử dụng

1. **Lấy vị trí**: Nhấn nút "Vị trí" để cấp quyền GPS hoặc sử dụng vị trí mặc định
2. **Tìm cửa hàng**: Nhấn nút "Tìm cửa hàng" để hiển thị tối đa 30 cửa hàng gần nhất
3. **Tư vấn AI**: Nhập câu hỏi vào khung chat để nhận tư vấn thời trang
4. **Xem chi tiết**: Click vào cửa hàng trên bản đồ hoặc danh sách để xem thông tin
5. **Mở Google Maps**: Click nút bản đồ để mở vị trí trong Google Maps

## API Documentation

### GET /

Kiểm tra server hoạt động

**Response:**
```json
{
  "message": "Fashion Shop Finder API dang hoat dong",
  "version": "1.0.0",
  "endpoints": {
    "chat": "/chat (POST)",
    "health": "/health (GET)"
  }
}
```

### GET /health

Kiểm tra trạng thái các service

**Response:**
```json
{
  "status": "healthy",
  "gemini_connected": true,
  "google_sheets_configured": false
}
```

### POST /chat

Endpoint chính để tìm kiếm cửa hàng và tư vấn AI

**Request:**
```json
{
  "lat": 21.0285,
  "lon": 105.8542,
  "message": "Tìm cửa hàng gần đây"
}
```

**Response:**
```json
{
  "shops": [
    {
      "name": "Elise Fashion Hoan Kiem",
      "address": "42 Trang Tien, Hoan Kiem, Ha Noi",
      "lat": 21.0245,
      "lon": 105.853,
      "distance_km": 0.45,
      "category": "Thoi trang nu cao cap",
      "price_range": "500k - 2tr",
      "item_suggestion": "Đầm công sở, áo kiểu thanh lịch",
      "promo_text": "Giam 20% cuoi tuan"
    }
  ],
  "ai_message": "Dựa trên vị trí của bạn..."
}
```

### GET /shops

Lấy danh sách tất cả cửa hàng (debug endpoint)

## Cấu trúc Google Sheets

Nếu sử dụng Google Sheets làm database, tạo spreadsheet với các cột:

| Cột | Mô tả | Ví dụ |
|-----|-------|-------|
| name | Tên cửa hàng | Elise Fashion |
| address | Địa chỉ đầy đủ | 42 Trang Tien, Hoan Kiem, Ha Noi |
| lat | Vĩ độ | 21.0245 |
| lon | Kinh độ | 105.8530 |
| category | Danh mục sản phẩm | Thoi trang nu cao cap |
| price_range | Mức giá | 500k - 2tr |
| notes | Khuyến mãi/Ghi chú | Giam 20% cuoi tuan |

## Thuật toán tìm kiếm

Hệ thống sử dụng thuật toán ưu tiên 2 bước:

1. **Bước 1**: Tìm kiếm trong bán kính 20km (ưu tiên)
2. **Bước 2**: Nếu chưa đủ, mở rộng đến 500km

Điểm ưu tiên cửa hàng:
- Khoảng cách càng gần càng cao
- Cửa hàng có đầy đủ thông tin (+10 điểm)
- Có danh mục và giá (+5 điểm mỗi mục)
- Có khuyến mãi (+15 điểm)

## Dữ liệu mẫu

Dự án tích hợp sẵn 15 cửa hàng mẫu tại Hà Nội và TP.HCM, bao gồm các thương hiệu phổ biến như Elise Fashion, CANIFA, Routine Store, YODY, NEM Fashion, Owen, Ivy Moda, JUNO, Blue Exchange.

## Troubleshooting

**Lỗi CORS**
- Đảm bảo backend đang chạy tại `http://localhost:8000`
- Kiểm tra frontend gọi đúng địa chỉ API

**Không lấy được vị trí GPS**
- Cho phép trình duyệt truy cập vị trí
- Ứng dụng tự động dùng vị trí mặc định (Hà Nội) nếu không có GPS

**Gemini API không hoạt động**
- Kiểm tra API key trong `backend/.env`
- Ứng dụng vẫn hoạt động với phản hồi mặc định

**Backend không khởi động**
- Kiểm tra Python version (cần 3.9+)
- Cài đặt lại dependencies: `pip install -r requirements.txt`
- Kiểm tra port 8000 có bị chiếm không

## Development

### Cấu trúc module Backend

- `app.py`: FastAPI application với các endpoints chính
- `geofilter.py`: Tính toán khoảng cách và lọc cửa hàng theo bán kính
- `gsheet_connector.py`: Kết nối và đọc dữ liệu từ Google Sheets
- `gemini_service.py`: Xử lý gọi Google Gemini API và format response

### Thêm cửa hàng mới

Có 2 cách:

1. **Thêm vào Google Sheets**: Tạo Google Spreadsheet, điền thông tin cửa hàng, cập nhật `GOOGLE_SHEETS_ID` trong `.env`

2. **Thêm vào sample_data.json**: Chỉnh sửa file `backend/sample_data.json` theo format có sẵn

## Deploy lên Web

Để deploy ứng dụng lên web và chia sẻ với mọi người:

**Cách nhanh (10 phút):**
- Xem [QUICK_START_DEPLOY.md](QUICK_START_DEPLOY.md)

**Hướng dẫn chi tiết:**
- Xem [DEPLOY.md](DEPLOY.md)

**Tóm tắt:**
- Frontend → GitHub Pages (miễn phí)
- Backend → Render.com (miễn phí)

## License

MIT License - Sử dụng tự do cho mục đích học tập và nghiên cứu.

## Tác giả

Dự án demo cho môn học - Xây dựng ứng dụng bản đồ và GenAI trong thương mại điện tử.
