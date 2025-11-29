# Hướng dẫn Deploy Ứng dụng Web lên GitHub và Render

Hướng dẫn chi tiết để deploy ứng dụng Fashion Finder lên web, cho phép mọi người truy cập và sử dụng trực tiếp trên trình duyệt.

## Tổng quan

Ứng dụng bao gồm 2 phần:
- **Frontend**: HTML/CSS/JavaScript → Deploy lên **GitHub Pages** (miễn phí)
- **Backend**: FastAPI Python → Deploy lên **Render.com** (miễn phí)

## Bước 1: Chuẩn bị Repository trên GitHub

### 1.1. Đảm bảo code đã được push lên GitHub

```bash
git add .
git commit -m "Chuẩn bị code cho deployment"
git push origin main
```

### 1.2. Đảm bảo repository là Public

- Vào **Settings** → **Danger Zone** → **Change visibility** → Chọn **Public**

## Bước 2: Deploy Backend lên Render.com

Render.com là dịch vụ miễn phí để host ứng dụng backend.

### 2.1. Đăng ký tài khoản Render

1. Truy cập: https://render.com
2. Đăng ký bằng GitHub account (khuyến nghị)
3. Xác thực email nếu cần

### 2.2. Tạo Web Service mới

1. **Đăng nhập vào Render Dashboard**
   - Click **New +** → Chọn **Web Service**

2. **Kết nối GitHub Repository**
   - Chọn **Build and deploy from a Git repository**
   - Chọn repository của bạn
   - Click **Connect**

3. **Cấu hình Service**

   **Basic Settings:**
   - **Name**: `fashion-finder-backend` (hoặc tên bạn muốn)
   - **Region**: Singapore (gần Việt Nam nhất)
   - **Branch**: `main`
   - **Root Directory**: `backend` ⚠️ **KHÔNG có khoảng trắng đầu/cuối**
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   
   **⚠️ QUAN TRỌNG:** Khi nhập Root Directory, đảm bảo:
   - Không có khoảng trắng ở đầu: ` backend` ❌
   - Không có khoảng trắng ở cuối: `backend ` ❌
   - Chỉ là: `backend` ✅
   
   Nếu gặp lỗi "Service Root Directory is missing", xem file [FIX_DEPLOY_ISSUES.md](FIX_DEPLOY_ISSUES.md)

   **Advanced Settings:**
   - **Auto-Deploy**: `Yes` (tự động deploy khi có code mới)

4. **Cấu hình Environment Variables**

   Click vào **Environment Variables** và thêm:

   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   PRIORITY_RADIUS_KM=20.0
   MAX_RADIUS_KM=500.0
   MAX_SHOPS=30
   PORT=8000
   ```

   **Lưu ý:**
   - `GEMINI_API_KEY`: Lấy tại https://aistudio.google.com/app/apikey
   - Các biến khác đã có giá trị mặc định, có thể không cần set

5. **Plan và Deploy**

   - **Free Plan** là đủ cho dự án này
   - Click **Create Web Service**
   - Render sẽ tự động build và deploy (mất khoảng 3-5 phút)

6. **Lấy URL Backend**

   Sau khi deploy thành công, bạn sẽ có URL dạng:
   ```
   https://fashion-finder-backend.onrender.com
   ```

   **Lưu ý:** URL này cần vài phút để khởi động sau khi deploy (free tier có "sleep" khi không dùng)

### 2.3. Kiểm tra Backend hoạt động

Truy cập URL backend:
- Health check: `https://your-backend-url.onrender.com/health`
- API Docs: `https://your-backend-url.onrender.com/docs`
- Root: `https://your-backend-url.onrender.com/`

## Bước 3: Deploy Frontend lên GitHub Pages

### 3.1. Tạo branch gh-pages cho Frontend

**⚠️ Lưu ý:** GitHub Pages không hỗ trợ deploy trực tiếp từ subfolder. Cần tạo branch `gh-pages` riêng.

#### **Cách 1: Dùng script tự động (Khuyến nghị)**

1. Chạy script PowerShell:
   ```powershell
   .\setup-gh-pages.ps1
   ```

   Script này sẽ:
   - Tạo branch `gh-pages`
   - Di chuyển tất cả files từ `frontend/` lên root
   - Xóa các files không cần thiết
   - Push lên GitHub

#### **Cách 2: Tạo thủ công**

Xem hướng dẫn chi tiết tại [FIX_DEPLOY_ISSUES.md](FIX_DEPLOY_ISSUES.md#lỗi-2-frontend)

### 3.2. Cấu hình GitHub Pages

1. **Vào repository trên GitHub**
   - Vào tab **Settings**
   - Cuộn xuống phần **Pages** (bên trái menu)

2. **Cấu hình Source**
   - **Source**: Chọn `Deploy from a branch`
   - **Branch**: Chọn `gh-pages`
   - **Folder**: Chọn `/ (root)`
   - Click **Save**

3. **Lấy URL Frontend**

   Sau khi save, GitHub sẽ cung cấp URL:
   ```
   https://[username].github.io/[repo-name]/
   ```

### 3.2. Cập nhật Frontend để kết nối với Backend

1. **Tạo file cấu hình cho production**

   Tạo file `frontend/config.js`:

   ```javascript
   // Config cho production - Thay YOUR_BACKEND_URL bằng URL backend thực tế
   window.API_BASE_URL = 'https://your-backend-url.onrender.com';
   ```

2. **Cập nhật index.html**

   Thêm vào `<head>` của `frontend/index.html`:

   ```html
   <!-- Load config từ file riêng (cho production) -->
   <script src="config.js"></script>
   ```

   HOẶC cập nhật meta tag đã có:

   ```html
   <meta name="api-base-url" content="https://your-backend-url.onrender.com">
   ```

3. **Commit và Push**

   ```bash
   git add frontend/index.html frontend/config.js
   git commit -m "Cập nhật API URL cho production"
   git push origin main
   ```

4. **Chờ GitHub Pages deploy**

   - GitHub Pages tự động deploy sau khi push (1-2 phút)
   - Xem status tại: **Settings** → **Pages** → **Build and deployment**

## Bước 4: Cấu hình CORS cho Backend (Nếu cần)

Nếu frontend và backend ở domain khác nhau, cần cấu hình CORS.

### Cách 1: Cập nhật trong `backend/app.py`

Thay đổi dòng 38:

```python
# Thay vì allow_origins=["*"]
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Thêm vào Environment Variables trên Render:
```
ALLOWED_ORIGINS=https://username.github.io,https://your-custom-domain.com
```

### Cách 2: Giữ nguyên `allow_origins=["*"]`

Hiện tại code đã cho phép tất cả origins, nên không cần thay đổi gì.

## Bước 5: Kiểm tra và Test

### 5.1. Kiểm tra Frontend

1. Truy cập URL GitHub Pages
2. Mở Developer Tools (F12)
3. Kiểm tra Console không có lỗi
4. Thử các chức năng:
   - Lấy vị trí GPS
   - Tìm cửa hàng
   - Chat với AI

### 5.2. Kiểm tra Backend

1. Truy cập `/health` endpoint
2. Truy cập `/docs` để xem Swagger UI
3. Test API từ frontend

### 5.3. Kiểm tra kết nối Frontend - Backend

1. Mở Developer Tools → **Network** tab
2. Thực hiện một action (ví dụ: tìm cửa hàng)
3. Kiểm tra request đến backend có thành công không
4. Nếu lỗi CORS, xem lại cấu hình CORS ở Bước 4

## Bước 6: Chia sẻ Ứng dụng

Sau khi deploy thành công, bạn có thể chia sẻ:

### Link Frontend (Ứng dụng chính):
```
https://[username].github.io/[repo-name]/
```

### Link Backend API Docs:
```
https://your-backend-url.onrender.com/docs
```

### Link Repository:
```
https://github.com/[username]/[repo-name]
```

## Troubleshooting

### Backend không khởi động

**Vấn đề**: Service trên Render báo lỗi
- **Nguyên nhân**: Thiếu dependencies hoặc sai start command
- **Giải pháp**: 
  - Kiểm tra `requirements.txt` đầy đủ
  - Kiểm tra `Procfile` hoặc start command đúng
  - Xem logs trên Render dashboard

### Backend "sleep" sau vài phút không dùng

**Vấn đề**: Request đầu tiên sau khi sleep rất chậm (15-30 giây)
- **Nguyên nhân**: Free tier của Render tự động sleep khi không có traffic
- **Giải pháp**: 
  - Chấp nhận (free tier bình thường)
  - Hoặc upgrade lên paid plan ($7/tháng) để không sleep

### Frontend không kết nối được Backend

**Vấn đề**: Lỗi CORS hoặc 404
- **Nguyên nhân**: URL backend sai hoặc CORS chưa cấu hình
- **Giải pháp**:
  - Kiểm tra `API_BASE_URL` trong frontend đúng chưa
  - Kiểm tra CORS settings trong backend
  - Kiểm tra backend URL có hoạt động không

### Frontend không hiển thị trên GitHub Pages

**Vấn đề**: 404 khi truy cập GitHub Pages
- **Nguyên nhân**: Cấu hình folder sai hoặc file không tồn tại
- **Giải pháp**:
  - Kiểm tra Settings → Pages → Folder đúng chưa
  - Đảm bảo file `index.html` tồn tại trong folder được chọn
  - Kiểm tra build logs trong Actions tab

### Environment Variables không hoạt động

**Vấn đề**: API key không được nhận
- **Nguyên nhân**: Biến môi trường chưa được set hoặc sai tên
- **Giải pháp**:
  - Kiểm tra lại tên biến trong Render dashboard
  - Restart service sau khi thêm biến mới
  - Kiểm tra logs để xem giá trị biến

## Các Dịch vụ Deploy Khác (Tùy chọn)

### Backend Alternatives:

1. **Railway.app** (Miễn phí với giới hạn)
   - Dễ sử dụng, tự động detect Python
   - URL: https://railway.app

2. **Fly.io** (Miễn phí)
   - Có thể chạy gần người dùng hơn
   - URL: https://fly.io

3. **Heroku** (Có giới hạn miễn phí)
   - Phổ biến nhưng giới hạn nhiều hơn
   - URL: https://heroku.com

### Frontend Alternatives:

1. **Vercel** (Miễn phí)
   - Tốt cho static sites
   - URL: https://vercel.com

2. **Netlify** (Miễn phí)
   - Tương tự GitHub Pages
   - URL: https://netlify.com

## Chi phí

- **GitHub Pages**: Hoàn toàn miễn phí
- **Render.com Free Tier**: Miễn phí, nhưng:
  - Service sẽ "sleep" sau 15 phút không dùng
  - Request đầu tiên sau sleep sẽ chậm (cold start)
  - Có thể upgrade lên $7/tháng để không sleep

## Bước Tiếp theo

Sau khi deploy thành công:

1. ✅ Test đầy đủ các chức năng
2. ✅ Thêm link vào README.md
3. ✅ Chia sẻ với bạn bè, mentor
4. ✅ Thêm vào portfolio/CV
5. ✅ Monitor logs để phát hiện lỗi sớm

## Tài liệu tham khảo

- [Render Documentation](https://render.com/docs)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [CORS Configuration](https://fastapi.tiangolo.com/tutorial/cors/)

---

**Chúc bạn deploy thành công!** 🚀

Nếu gặp vấn đề, hãy kiểm tra logs và xem lại các bước trên.

