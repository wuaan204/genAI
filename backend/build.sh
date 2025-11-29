#!/bin/bash
# Build script tối ưu cho Render deployment
set -e

echo "🚀 Bắt đầu build backend..."

# Upgrade pip, setuptools, wheel để tăng tốc install
echo "📦 Upgrading pip, setuptools, wheel..."
pip install --upgrade --quiet pip setuptools wheel

# Install dependencies với cache
echo "📥 Installing dependencies..."
pip install --cache-dir /tmp/pip-cache -r requirements.txt

# Pre-compile Python files (optional, có thể bỏ qua nếu không cần)
echo "🔨 Pre-compiling Python files..."
python -m compileall -q . || true

echo "✅ Build hoàn tất!"

