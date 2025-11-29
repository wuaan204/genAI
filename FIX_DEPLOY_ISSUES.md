# Sửa Lỗi Deploy - Hướng dẫn Chi tiết

Hướng dẫn sửa 2 lỗi thường gặp khi deploy.

## ❌ Lỗi 1: Backend - Root Directory không tìm thấy

### Lỗi gặp phải:
```
Service Root Directory "/opt/render/project/src/ backend" is missing.
builder.sh: line 51: cd: /opt/render/project/src/ backend: No such file or directory
```

### Nguyên nhân:
- Có **khoảng trắng thừa** trong Root Directory (ví dụ: ` backend` thay vì `backend`)
- Hoặc Root Directory không được cấu hình đúng

### Cách sửa:

#### **Cách 1: Sửa trong Render Dashboard (Khuyến nghị)**

1. Vào Render Dashboard → Service của bạn
2. Vào tab **Settings**
3. Tìm phần **Root Directory**
4. **XÓA HẾT** khoảng trắng, chỉ để lại: `backend` (không có khoảng trắng đầu/cuối)
5. Scroll xuống, click **Save Changes**
6. Vào tab **Manual Deploy** → Click **Deploy latest commit**

#### **Cách 2: Xóa và tạo lại Service**

1. Vào Render Dashboard
2. Vào Service → **Settings** → Scroll xuống **Danger Zone**
3. Click **Delete Service** (đừng lo, có thể tạo lại)
4. Tạo lại Service mới với cấu hình sau:

   **Basic Settings:**
   - **Name**: `fashion-finder-backend`
   - **Region**: `Singapore`
   - **Branch**: `main`
   - **Root Directory**: `backend` ⚠️ **KHÔNG có khoảng trắng**
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

5. Thêm Environment Variables:
   - `GEMINI_API_KEY` = API key của bạn
   - `PORT` = `8000`

6. Click **Create Web Service**

### Kiểm tra:

Sau khi deploy, kiểm tra logs:
- Vào tab **Events** hoặc **Logs**
- Không thấy lỗi "No such file or directory"
- Thấy "Application is live"

---

## ❌ Lỗi 2: Frontend - Không tìm thấy thư mục frontend trong GitHub Pages

### Vấn đề:
- GitHub Pages Settings không có tùy chọn folder `/frontend`
- Chỉ có thể deploy từ root `/` hoặc `/docs`

### Nguyên nhân:
GitHub Pages **không hỗ trợ** deploy từ subfolder trực tiếp.

### Giải pháp: Tạo branch `gh-pages` chứa frontend files

#### **Cách 1: Tạo branch gh-pages thủ công (Dễ nhất)**

1. **Tạo branch mới từ main:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b gh-pages
   ```

2. **Xóa tất cả files và chỉ giữ frontend:**
   ```bash
   # Xóa tất cả files ngoài frontend
   git rm -rf backend DEPLOY.md QUICK_START_DEPLOY.md README.md render.yaml .gitignore install_python_deps.ps1
   
   # Di chuyển tất cả files từ frontend/ lên root
   git mv frontend/* .
   git rm -rf frontend
   
   # Commit
   git add .
   git commit -m "Setup gh-pages branch for GitHub Pages"
   git push origin gh-pages
   ```

3. **Cấu hình GitHub Pages:**
   - Vào repository → **Settings** → **Pages**
   - **Source**: `Deploy from a branch`
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
   - Click **Save**

4. **URL sẽ là:**
   ```
   https://[username].github.io/[repo-name]/
   ```

#### **Cách 2: Dùng script tự động (Nhanh hơn)**

Tạo file `setup-gh-pages.ps1` (PowerShell) hoặc `setup-gh-pages.sh` (Bash):

**PowerShell (setup-gh-pages.ps1):**
```powershell
# Script tạo branch gh-pages cho GitHub Pages
Write-Host "Creating gh-pages branch..." -ForegroundColor Green

# Đảm bảo đang ở branch main
git checkout main
git pull origin main

# Tạo hoặc checkout branch gh-pages
git checkout -b gh-pages 2>$null || git checkout gh-pages

# Xóa tất cả files trừ frontend
Write-Host "Removing unnecessary files..." -ForegroundColor Yellow
Get-ChildItem -Exclude frontend | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Di chuyển files từ frontend lên root
Write-Host "Moving frontend files to root..." -ForegroundColor Yellow
Get-ChildItem -Path frontend -File | ForEach-Object {
    Move-Item $_.FullName -Destination . -Force
}
Remove-Item -Path frontend -Recurse -Force -ErrorAction SilentlyContinue

# Commit và push
Write-Host "Committing changes..." -ForegroundColor Yellow
git add -A
git commit -m "Setup gh-pages branch for GitHub Pages deployment"
git push origin gh-pages --force

Write-Host "Done! Now configure GitHub Pages to use gh-pages branch" -ForegroundColor Green
```

**Chạy script:**
```powershell
.\setup-gh-pages.ps1
```

#### **Cách 3: Dùng GitHub Actions (Tự động) - Nâng cao**

Tạo file `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend to GitHub Pages

on:
  push:
    branches:
      - main
    paths:
      - 'frontend/**'

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Pages
        uses: actions/configure-pages@v2
      
      - name: Copy frontend files
        run: |
          cp -r frontend/* ./public/ || mkdir -p ./public && cp -r frontend/* ./public/
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v1
        with:
          path: './public'
      
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v1
```

Sau đó cấu hình GitHub Pages:
- **Settings** → **Pages** → **Source**: `GitHub Actions`

---

## ✅ Sau khi sửa xong

### Backend:
- URL: `https://your-backend-url.onrender.com`
- Test: Truy cập `/health` để kiểm tra

### Frontend:
- URL: `https://username.github.io/repo-name/`
- Test: Mở trình duyệt và kiểm tra ứng dụng

### Kết nối Frontend với Backend:

1. **Cập nhật `frontend/config.js`** (hoặc trong branch gh-pages):
   ```javascript
   window.API_BASE_URL = 'https://your-backend-url.onrender.com';
   ```

2. **Commit và push:**
   ```bash
   # Nếu dùng cách 1 (gh-pages branch):
   git checkout gh-pages
   # Sửa config.js
   git add config.js
   git commit -m "Update backend URL"
   git push origin gh-pages
   ```

---

## 🔍 Kiểm tra lỗi thường gặp

### Backend vẫn lỗi:
- ✅ Kiểm tra Root Directory = `backend` (không có khoảng trắng)
- ✅ Kiểm tra Build Command và Start Command đúng
- ✅ Xem logs trong Render dashboard để biết lỗi cụ thể

### Frontend không hiển thị:
- ✅ Đảm bảo branch `gh-pages` đã được push
- ✅ Kiểm tra GitHub Pages đã được enable
- ✅ Chờ 1-2 phút sau khi cấu hình
- ✅ Kiểm tra file `index.html` có trong root của branch gh-pages

### Frontend không kết nối được Backend:
- ✅ Kiểm tra `config.js` có URL backend đúng
- ✅ Kiểm tra backend đã hoạt động (truy cập /health)
- ✅ Mở Developer Tools (F12) → Console để xem lỗi CORS

---

**Nếu vẫn gặp vấn đề, xem logs chi tiết và thử lại từng bước!**

