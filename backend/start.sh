#!/bin/bash
# Script khởi động backend cho deployment - Tối ưu cho production
set -e  # Exit on error

cd "$(dirname "$0")"

# Set Python options
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Determine number of workers (Render free tier: 1 worker recommended)
WORKERS=${WORKERS:-1}

# Start uvicorn with optimized settings
exec uvicorn app:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers $WORKERS \
    --timeout-keep-alive 30 \
    --log-level info \
    --no-access-log  # Disable access log for faster performance

