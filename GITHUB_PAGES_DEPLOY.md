# Hướng dẫn Deploy lên GitHub Pages

## Vấn đề khi deploy

Khi deploy frontend lên GitHub Pages, bạn có thể gặp các lỗi:
- ❌ Không thể tìm cửa hàng
- ❌ Không thể chat
- ❌ Lỗi CORS hoặc kết nối

## Nguyên nhân

GitHub Pages chỉ host **static files** (HTML, CSS, JS), không thể chạy backend Python. Vì vậy bạn cần:

1. **Backend phải được deploy riêng** (ví dụ: Render.com, Heroku, Railway)
2. **Frontend trên GitHub Pages** phải trỏ API URL đến backend đã deploy

## Các bước deploy

### Bước 1: Deploy Backend (bắt buộc)

Deploy backend lên một trong các nền tảng sau:

#### Render.com (Miễn phí)
1. Đăng ký tại [render.com](https://render.com)
2. Tạo mới **Web Service**
3. Kết nối GitHub repository
4. Chọn folder `backend`
5. Cấu hình:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Thêm các biến môi trường từ file `backend/.env`
7. Lấy URL backend (ví dụ: `https://your-app.onrender.com`)

#### Heroku
```bash
cd backend
heroku create your-app-name
git subtree push --prefix backend heroku main
heroku config:set GEMINI_API_KEY=your_key
```

### Bước 2: Cấu hình API URL cho GitHub Pages

Sau khi có backend URL, cập nhật file `config.js`:

```javascript
// config.js
window.API_BASE_URL = 'https://your-backend.onrender.com';  // Thay bằng URL backend của bạn
```

Hoặc cập nhật trong `index.html`:

```html
<!-- index.html -->
<meta name="api-base-url" content="https://your-backend.onrender.com">
```

### Bước 3: Deploy Frontend lên GitHub Pages

#### Cách 1: Tự động (GitHub Actions)

1. Tạo file `.github/workflows/deploy.yml`:
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: .
```

2. Push code lên GitHub

3. Vào Settings > Pages > Source: chọn "GitHub Actions"

#### Cách 2: Thủ công

1. Vào Settings > Pages trong repository GitHub
2. Chọn branch `main` và folder `/ (root)`
3. Save

### Bước 4: Kiểm tra

1. Mở GitHub Pages URL (ví dụ: `https://your-username.github.io/repo-name`)
2. Mở Console (F12) để xem logs:
   - Nên thấy: `[Fashion Finder] API URL: https://your-backend.onrender.com`
   - Nếu thấy lỗi, kiểm tra:
     - Backend URL có đúng không?
     - Backend có đang hoạt động không? (mở URL + `/docs`)
     - CORS có được cấu hình đúng không?

## Cấu hình CORS trong Backend

Backend phải cho phép requests từ GitHub Pages domain. File `backend/app.py` đã có:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả (development)
    # Production: thay bằng domain cụ thể
    # allow_origins=["https://your-username.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Lưu ý**: Trong production, nên giới hạn `allow_origins` thay vì `["*"]`.

## Troubleshooting

### Lỗi: "Failed to fetch" hoặc CORS error

**Nguyên nhân**: Backend không cho phép requests từ domain GitHub Pages.

**Giải pháp**:
1. Kiểm tra backend có đang chạy: Mở `https://your-backend.onrender.com/docs`
2. Kiểm tra CORS settings trong `backend/app.py`
3. Kiểm tra API URL trong `config.js`

### Lỗi: "API URL chưa được cấu hình"

**Nguyên nhân**: File `config.js` không được load hoặc API_URL là empty.

**Giải pháp**:
1. Kiểm tra file `config.js` có tồn tại không
2. Kiểm tra trong `index.html` có load `config.js` trước `script.js`:
```html
<script src="config.js"></script>
<script src="script.js"></script>
```
3. Mở Console (F12) xem log: `[Fashion Finder] API URL: ...`

### Lỗi: Backend timeout

**Nguyên nhân**: Backend free tier có thể bị "sleep" sau 15 phút không dùng.

**Giải pháp**:
- Sử dụng Render.com Pro (có phí) hoặc
- Sử dụng uptime monitoring service để keep-alive

### Lỗi: 422 Unprocessable Content

**Nguyên nhân**: Request validation fail.

**Giải pháp**: Kiểm tra trong Console để xem chi tiết lỗi validation.

## Checklist

- [ ] Backend đã được deploy và có thể truy cập (URL + `/docs`)
- [ ] File `config.js` đã được cập nhật với backend URL
- [ ] File `index.html` có meta tag hoặc load `config.js`
- [ ] CORS trong backend cho phép GitHub Pages domain
- [ ] Frontend đã được deploy lên GitHub Pages
- [ ] Đã test trên GitHub Pages URL

## Cấu trúc file trên GitHub Pages

```
repository/
├── index.html          # Frontend chính
├── script.js          # Frontend JavaScript
├── styles.css         # Frontend CSS
├── config.js          # API URL config (QUAN TRỌNG!)
├── backend/           # Backend code (không cần trên Pages)
└── README.md
```

**Lưu ý**: GitHub Pages chỉ cần các file frontend. Backend code không cần trên Pages.

## Liên hệ

Nếu vẫn gặp vấn đề, kiểm tra:
1. Console logs (F12) trong trình duyệt
2. Backend logs trên platform bạn deploy
3. Network tab trong DevTools để xem request/response

