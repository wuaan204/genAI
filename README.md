# 🛍️ Fashion Finder - Tìm Cửa Hàng Thời Trang với AI

## 📋 Giới thiệu

Fashion Finder là ứng dụng web giúp người dùng tìm kiếm các cửa hàng quần áo gần vị trí hiện tại và nhận tư vấn thời trang từ AI (Google Gemini). Ứng dụng sử dụng:

- **Frontend**: HTML/CSS/JavaScript với Google Maps JS API để hiển thị bản đồ
- **Backend**: Python FastAPI
- **AI**: Google Gemini 1.5 Flash
- **Database**: Google Sheets (hoặc dữ liệu mẫu tích hợp sẵn)

## 🏗️ Cấu trúc dự án

```
/backend
  ├── app.py              # API chính (FastAPI)
  ├── geofilter.py        # Module lọc theo vị trí địa lý
  ├── gsheet_connector.py # Module kết nối Google Sheets
  ├── gemini_service.py   # Module gọi Gemini API
  └── requirements.txt    # Thư viện Python cần thiết

/frontend
  ├── index.html          # Trang web chính
  ├── script.js           # Logic JavaScript
  └── styles.css          # Stylesheet

README.md                 # File hướng dẫn này
```

## 🚀 Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống

- Python 3.9 trở lên
- Trình duyệt web hiện đại (Chrome, Firefox, Edge)
- Kết nối Internet

### 2. Cài đặt Backend

```bash
# Di chuyển vào thư mục backend
cd backend

# Tạo môi trường ảo (khuyến nghị)
python -m venv venv

# Kích hoạt môi trường ảo
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường

Tạo file `.env` trong thư mục `backend` với nội dung:

```env
# Google Gemini API Key (bắt buộc để có tư vấn AI)
# Lấy tại: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Google Sheets ID (tùy chọn - nếu muốn dùng dữ liệu từ Sheets)
GOOGLE_SHEETS_ID=your_spreadsheet_id

# Google Sheets Credentials JSON (tùy chọn)
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account",...}

# Cấu hình server
HOST=0.0.0.0
PORT=8000

# Cấu hình tìm kiếm
SEARCH_RADIUS_KM=5.0
MAX_SHOPS=3
```

> **Lưu ý**: Nếu không có Gemini API key, ứng dụng vẫn hoạt động với phản hồi mặc định.

### 4. Chạy Backend

```bash
cd backend
python app.py
```

Server sẽ chạy tại `http://localhost:8000`

### 5. Chạy Frontend

Mở file `frontend/index.html` trong trình duyệt, hoặc sử dụng live server:

```bash
# Sử dụng Python HTTP server
cd frontend
python -m http.server 5500
```

Truy cập `http://localhost:5500`

## 📊 Cấu trúc Google Sheets

Nếu muốn sử dụng dữ liệu từ Google Sheets, tạo spreadsheet với các cột:

| name | address | lat | lon | category | price_range | notes |
|------|---------|-----|-----|----------|-------------|-------|
| Tên cửa hàng | Địa chỉ | Vĩ độ | Kinh độ | Danh mục | Mức giá | Khuyến mãi |

**Ví dụ:**
| name | address | lat | lon | category | price_range | notes |
|------|---------|-----|-----|----------|-------------|-------|
| Elise Fashion | 42 Trang Tien, Ha Noi | 21.0245 | 105.8530 | Thoi trang nu cao cap | 500k - 2tr | Giam 20% cuoi tuan |

## 🎮 Hướng dẫn sử dụng

1. **Cho phép truy cập vị trí**: Khi mở ứng dụng, cho phép trình duyệt truy cập GPS
2. **Xem bản đồ**: Vị trí của bạn hiển thị bằng marker xanh lá
3. **Hỏi AI**: Nhập câu hỏi vào ô chat, ví dụ:
   - "Tìm áo đầm đi tiệc"
   - "Cửa hàng nào có khuyến mãi?"
   - "Tôi muốn mua quần áo công sở"
4. **Xem kết quả**: Các cửa hàng gần nhất hiển thị trên bản đồ và danh sách
5. **Click vào cửa hàng**: Để xem chi tiết và zoom đến vị trí

## 🔌 API Endpoints

### `GET /`
Kiểm tra server hoạt động

### `GET /health`
Kiểm tra trạng thái các service

### `POST /chat`
Endpoint chính để tìm kiếm và tư vấn

**Request:**
```json
{
  "lat": 21.0285,
  "lon": 105.8542,
  "message": "Tìm áo đầm đẹp"
}
```

**Response:**
```json
{
  "shops": [
    {
      "name": "Elise Fashion",
      "address": "42 Trang Tien, Ha Noi",
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

### `GET /shops`
Lấy danh sách tất cả cửa hàng (debug)

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Frontend | HTML5, CSS3, JavaScript ES6+ |
| Bản đồ | Google Maps JS API |
| Backend | Python 3.9+, FastAPI |
| AI | Google Gemini 1.5 Flash |
| Database | Google Sheets API |
| Geospatial | Geopy |

## 📝 Dữ liệu mẫu

Ứng dụng tích hợp sẵn **15 cửa hàng mẫu** tại Hà Nội và TP.HCM, bao gồm:
- Elise Fashion
- CANIFA
- Routine Store
- YODY
- NEM Fashion
- Owen
- Ivy Moda
- JUNO
- Blue Exchange
- v.v...

## 🔧 Troubleshooting

### Lỗi CORS
Đảm bảo backend đang chạy và frontend gọi đúng địa chỉ `http://localhost:8000`

### Không lấy được vị trí GPS
- Kiểm tra trình duyệt đã cho phép truy cập vị trí
- Thử dùng HTTPS nếu HTTP không hoạt động
- Ứng dụng sẽ dùng vị trí mặc định (Hà Nội) nếu không có GPS

### Gemini API không hoạt động
- Kiểm tra API key trong file `.env`
- Ứng dụng vẫn hoạt động với phản hồi mặc định

## 👨‍💻 Tác giả

Dự án demo cho môn học - Xây dựng ứng dụng bản đồ và GenAI trong thương mại điện tử.

## 📄 License

MIT License - Sử dụng tự do cho mục đích học tập và nghiên cứu.