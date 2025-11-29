# 🔧 Hướng dẫn Sửa Lỗi Nhanh

## Lỗi 1: Backend - Root Directory

### Cách sửa nhanh:

1. Vào **Render Dashboard** → Service của bạn
2. Vào tab **Settings**
3. Tìm **Root Directory**
4. Xóa hết khoảng trắng, chỉ để lại: `backend`
5. Click **Save Changes**
6. Vào tab **Manual Deploy** → **Deploy latest commit**

✅ Xong! Xem chi tiết tại [FIX_DEPLOY_ISSUES.md](FIX_DEPLOY_ISSUES.md#lỗi-1-backend---root-directory-không-tìm-thấy)

---

## Lỗi 2: Frontend - Không tìm thấy folder frontend

### Cách sửa nhanh:

**Bước 1:** Chạy script tự động:
```powershell
.\setup-gh-pages.ps1
```

**Bước 2:** Vào GitHub → **Settings** → **Pages**
- **Source**: `Deploy from a branch`
- **Branch**: `gh-pages`
- **Folder**: `/ (root)`
- Click **Save**

✅ Xong! Xem chi tiết tại [FIX_DEPLOY_ISSUES.md](FIX_DEPLOY_ISSUES.md#lỗi-2-frontend---không-tìm-thấy-thư-mục-frontend-trong-github-pages)

---

## Sau khi sửa xong

1. ✅ Backend hoạt động: `https://your-backend.onrender.com/health`
2. ✅ Frontend hoạt động: `https://username.github.io/repo-name/`
3. ✅ Cập nhật `config.js` trong branch `gh-pages` với URL backend

**Xem hướng dẫn đầy đủ tại [FIX_DEPLOY_ISSUES.md](FIX_DEPLOY_ISSUES.md)**

