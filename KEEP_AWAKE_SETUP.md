# Hướng dẫn cấu hình Keep Backend Awake

Hệ thống tự động ping backend mỗi 10 phút để giữ backend FastAPI trên Render.com không bị sleep.

## ✅ Đã hoàn thành

1. ✅ Route `/health` đã được thêm vào backend (`backend/app.py`)
   - Trả về `{"status": "ok"}` với HTTP 200
   - Không yêu cầu xác thực
   - Luôn hoạt động

2. ✅ GitHub Actions workflow đã được tạo (`.github/workflows/keep_awake.yml`)
   - Tự động chạy mỗi 10 phút
   - Sử dụng cron: `*/10 * * * *`
   - Không làm fail workflow nếu request thất bại

## 🔧 Cấu hình biến môi trường

### Bước 1: Lấy URL backend trên Render.com

1. Đăng nhập vào [Render.com](https://render.com)
2. Vào dashboard của service backend
3. Copy URL của service (ví dụ: `https://my-backend.onrender.com`)
4. Thêm `/health` vào cuối URL: `https://my-backend.onrender.com/health`

### Bước 2: Thêm Secret vào GitHub Repository

1. Vào repository trên GitHub
2. Click **Settings** (Cài đặt)
3. Trong menu bên trái, chọn **Secrets and variables** > **Actions**
4. Click nút **New repository secret**
5. Điền thông tin:
   - **Name**: `WORKFLOW_BACKEND_URL`
   - **Secret**: URL đầy đủ đến endpoint `/health` (ví dụ: `https://my-backend.onrender.com/health`)
6. Click **Add secret**

### Bước 3: Kiểm tra endpoint hoạt động

Trước khi workflow chạy, hãy kiểm tra endpoint bằng cách:

1. Mở trình duyệt hoặc dùng curl:
   ```bash
   curl https://my-backend.onrender.com/health
   ```

2. Kết quả mong đợi:
   ```json
   {"status": "ok"}
   ```

3. Nếu nhận được kết quả trên, endpoint đã hoạt động đúng ✅

## 🚀 Kích hoạt workflow

### Cách 1: Tự động (khuyến nghị)

Workflow sẽ tự động chạy sau khi:
- Push code lên repository
- Mỗi 10 phút theo lịch cron

### Cách 2: Chạy thủ công

1. Vào tab **Actions** trên GitHub repository
2. Chọn workflow **Keep Backend Awake**
3. Click **Run workflow**
4. Chọn branch và click **Run workflow**

## 📊 Kiểm tra workflow đang chạy

1. Vào tab **Actions** trên GitHub repository
2. Xem workflow **Keep Backend Awake**
3. Click vào run mới nhất để xem log
4. Tìm dòng:
   - ✅ `Backend đang hoạt động (HTTP 200)` → Thành công
   - ⚠️ `Backend không phản hồi` → Cần kiểm tra URL hoặc backend

## 🔍 Troubleshooting

### Workflow không chạy

- Kiểm tra xem repository có bật GitHub Actions không
- Kiểm tra xem file `.github/workflows/keep_awake.yml` đã được commit chưa
- Kiểm tra xem cron schedule có đúng format không

### Backend không phản hồi

- Kiểm tra URL trong secret `WORKFLOW_BACKEND_URL` có đúng không
- Kiểm tra backend trên Render.com có đang chạy không
- Kiểm tra endpoint `/health` có hoạt động bằng cách mở trong trình duyệt

### Workflow fail nhưng không ảnh hưởng

- Đây là hành vi mong muốn: workflow không fail ngay cả khi backend không phản hồi
- Backend sẽ được ping lại sau 10 phút
- Nếu backend đang sleep, request đầu tiên có thể mất thời gian để "đánh thức" backend

## 📝 Lưu ý

- Workflow chạy mỗi 10 phút, đảm bảo backend không bị sleep (Render.com thường sleep sau 15 phút không có traffic)
- Nếu muốn thay đổi tần suất ping, sửa cron schedule trong file `.github/workflows/keep_awake.yml`
- Không cần cấu hình thêm gì trên Render.com, chỉ cần đảm bảo endpoint `/health` hoạt động

## 🎯 Kết quả mong đợi

Sau khi cấu hình xong:
- ✅ Workflow chạy tự động mỗi 10 phút
- ✅ Backend nhận được request ping định kỳ
- ✅ Backend không bị sleep trên Render.com
- ✅ Log trong GitHub Actions hiển thị `Backend đang hoạt động (HTTP 200)`

