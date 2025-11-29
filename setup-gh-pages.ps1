# Script tạo branch gh-pages cho GitHub Pages deployment
# Sử dụng: .\setup-gh-pages.ps1

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Setup GitHub Pages Branch (gh-pages)" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra đang ở repository git
if (-not (Test-Path .git)) {
    Write-Host "ERROR: Không tìm thấy repository git!" -ForegroundColor Red
    Write-Host "Hãy chạy script này trong thư mục gốc của repository." -ForegroundColor Yellow
    exit 1
}

# Kiểm tra frontend folder tồn tại
if (-not (Test-Path frontend)) {
    Write-Host "ERROR: Không tìm thấy thư mục 'frontend'!" -ForegroundColor Red
    exit 1
}

Write-Host "Bước 1: Đảm bảo đang ở branch main..." -ForegroundColor Yellow
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne "main") {
    Write-Host "  Đang checkout sang branch main..." -ForegroundColor Gray
    git checkout main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Không thể checkout sang branch main!" -ForegroundColor Red
        exit 1
    }
}

git pull origin main
Write-Host "  ✓ Đang ở branch main" -ForegroundColor Green
Write-Host ""

# Tạo hoặc checkout branch gh-pages
Write-Host "Bước 2: Tạo/checkout branch gh-pages..." -ForegroundColor Yellow
$ghPagesExists = git show-ref --verify --quiet refs/heads/gh-pages
if ($ghPagesExists) {
    Write-Host "  Branch gh-pages đã tồn tại, đang checkout..." -ForegroundColor Gray
    git checkout gh-pages
    git pull origin gh-pages
} else {
    Write-Host "  Tạo branch gh-pages mới..." -ForegroundColor Gray
    git checkout -b gh-pages
}
Write-Host "  ✓ Đang ở branch gh-pages" -ForegroundColor Green
Write-Host ""

# Backup và xóa tất cả files (trừ .git và frontend)
Write-Host "Bước 3: Xóa các file không cần thiết..." -ForegroundColor Yellow
$filesToRemove = @(
    "backend",
    "DEPLOY.md",
    "QUICK_START_DEPLOY.md",
    "FIX_DEPLOY_ISSUES.md",
    "README.md",
    "render.yaml",
    ".gitignore",
    "install_python_deps.ps1",
    "setup-gh-pages.ps1",
    "setup-gh-pages.sh"
)

foreach ($item in $filesToRemove) {
    if (Test-Path $item) {
        Write-Host "  Xóa: $item" -ForegroundColor Gray
        git rm -rf $item 2>$null
        Remove-Item -Path $item -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "  ✓ Đã xóa các file không cần thiết" -ForegroundColor Green
Write-Host ""

# Di chuyển files từ frontend lên root
Write-Host "Bước 4: Di chuyển files từ frontend/ lên root..." -ForegroundColor Yellow
$frontendFiles = Get-ChildItem -Path frontend -File
foreach ($file in $frontendFiles) {
    $destPath = Join-Path "." $file.Name
    Write-Host "  Di chuyển: $($file.Name)" -ForegroundColor Gray
    if (Test-Path $destPath) {
        git rm $destPath 2>$null
        Remove-Item -Path $destPath -Force -ErrorAction SilentlyContinue
    }
    Copy-Item -Path $file.FullName -Destination $destPath -Force
    git add $destPath
}

# Xóa thư mục frontend
if (Test-Path frontend) {
    git rm -rf frontend 2>$null
    Remove-Item -Path frontend -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "  ✓ Đã di chuyển tất cả files" -ForegroundColor Green
Write-Host ""

# Commit changes
Write-Host "Bước 5: Commit và push lên GitHub..." -ForegroundColor Yellow
git add -A
$hasChanges = git diff --cached --quiet
if (-not $hasChanges) {
    Write-Host "  Không có thay đổi để commit." -ForegroundColor Gray
} else {
    git commit -m "Setup gh-pages branch for GitHub Pages deployment"
    Write-Host "  ✓ Đã commit" -ForegroundColor Green
    
    Write-Host "  Đang push lên GitHub..." -ForegroundColor Gray
    git push origin gh-pages --force
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Đã push thành công" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Cảnh báo: Push có thể đã thất bại. Hãy kiểm tra lại." -ForegroundColor Yellow
    }
}
Write-Host ""

# Quay lại branch main
Write-Host "Bước 6: Quay lại branch main..." -ForegroundColor Yellow
git checkout main
Write-Host "  ✓ Đã quay lại branch main" -ForegroundColor Green
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "HOÀN TẤT!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Bước tiếp theo:" -ForegroundColor Yellow
Write-Host "1. Vào GitHub repository → Settings → Pages" -ForegroundColor White
Write-Host "2. Source: Deploy from a branch" -ForegroundColor White
Write-Host "3. Branch: gh-pages, Folder: / (root)" -ForegroundColor White
Write-Host "4. Click Save" -ForegroundColor White
Write-Host ""
Write-Host "URL của bạn sẽ là:" -ForegroundColor Yellow
Write-Host "  https://[username].github.io/[repo-name]/" -ForegroundColor Cyan
Write-Host ""

