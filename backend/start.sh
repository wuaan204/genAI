#!/bin/bash
# Script khởi động backend cho deployment
cd "$(dirname "$0")"
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}


