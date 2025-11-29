# Hướng dẫn đẩy code lên GitHub

## Bước 1: Cài đặt Git

Nếu chưa có Git, tải và cài đặt tại: https://git-scm.com/download/win

## Bước 2: Cấu hình Git (lần đầu)

```powershell
git config --global user.name "Tên của bạn"
git config --global user.email "fedorra.2004@gmail.com"
```

## Bước 3: Khởi tạo Git repository

```powershell
cd E:\HTKDTM
git init
```

## Bước 4: Thêm các file vào git

```powershell
git add .
```

## Bước 5: Commit code

```powershell
git commit -m "Initial commit: Fashion Finder project"
```

## Bước 6: Kết nối với GitHub repository

Thay `YOUR_USERNAME` và `YOUR_REPO_NAME` bằng thông tin repo của bạn:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

Hoặc nếu dùng SSH:
```powershell
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
```

## Bước 7: Đẩy code lên GitHub

```powershell
git branch -M main
git push -u origin main
```

Nếu repo GitHub yêu cầu authentication, bạn sẽ cần:
- Tạo Personal Access Token tại: https://github.com/settings/tokens
- Hoặc sử dụng GitHub Desktop

## Lưu ý

- File `.env` đã được loại bỏ khỏi git (trong .gitignore)
- Cần tạo file `.env` trên máy mới khi clone repo
- Các file credentials không được commit lên GitHub

