# app.py - File chính của Backend API
# Sử dụng FastAPI framework

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os
import logging
from dotenv import load_dotenv

# Import các module đã tách
from geofilter import filter_shops_by_radius
from gsheet_connector import add_shops_to_sheet_batch
from gemini_service import get_gemini_service
from places_service import search_nearby_shops, PLACES_API_ENABLED

# Load biến môi trường từ file .env
load_dotenv()

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Khởi tạo FastAPI app
app = FastAPI(
    title="Fashion Shop Finder API",
    description="API tim kiem cua hang quan ao gan day va tu van thoi trang bang AI",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: giới hạn domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Pydantic Models =====
class ChatRequest(BaseModel):
    """Schema cho request từ client"""
    lat: float = Field(..., ge=-90, le=90, description="Vĩ độ vị trí người dùng (-90 đến 90)")
    lon: float = Field(..., ge=-180, le=180, description="Kinh độ vị trí người dùng (-180 đến 180)")
    message: str = Field(..., min_length=1, max_length=500, description="Câu hỏi của người dùng")
    priority_radius_km: Optional[float] = Field(None, ge=0.1, le=100, description="Bán kính ưu tiên (km)")
    max_radius_km: Optional[float] = Field(None, ge=0.1, le=1000, description="Bán kính tối đa (km)")
    max_shops: Optional[int] = Field(None, ge=1, le=100, description="Số lượng cửa hàng tối đa")

class ShopResponse(BaseModel):
    """Schema cho thông tin cửa hàng trong response"""
    name: str
    address: str
    lat: float
    lon: float
    distance_km: float
    category: str
    price_range: str
    item_suggestion: str
    promo_text: str

class ChatResponse(BaseModel):
    """Schema cho response trả về client"""
    shops: list[ShopResponse]
    ai_message: str

# ===== Cấu hình từ biến môi trường =====
GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID', '')
PRIORITY_RADIUS_KM = float(os.getenv('PRIORITY_RADIUS_KM', '20.0'))
MAX_RADIUS_KM = float(os.getenv('MAX_RADIUS_KM', '500.0'))
MAX_SHOPS = int(os.getenv('MAX_SHOPS', '30'))


# ===== Helper Functions =====
def _prepare_shops_for_saving(shops: list[dict]) -> list[dict]:
    """Chuẩn bị dữ liệu cửa hàng để lưu vào Google Sheets"""
    return [
        {
            'name': shop.get('name', ''),
            'address': shop.get('address', ''),
            'lat': shop.get('lat', ''),
            'lon': shop.get('lon', ''),
            'category': shop.get('category', 'Quần áo'),
            'price_range': shop.get('price_range', ''),
            'notes': shop.get('notes', '')
        }
        for shop in shops
    ]


def _format_shops_response(nearby_shops: list[dict], suggestions: list[dict]) -> list[ShopResponse]:
    """Format danh sách cửa hàng thành response"""
    shops_response = []
    for i, shop in enumerate(nearby_shops):
        suggestion = suggestions[i] if i < len(suggestions) else {}
        
        shops_response.append(ShopResponse(
            name=shop.get('name', 'N/A'),
            address=shop.get('address', 'N/A'),
            lat=float(shop.get('lat', 0)),
            lon=float(shop.get('lon', 0)),
            distance_km=shop.get('distance_km', 0),
            category=shop.get('category', 'N/A'),
            price_range=shop.get('price_range', 'N/A'),
            item_suggestion=suggestion.get('item_suggestion', ''),
            promo_text=suggestion.get('promo_text', '')
        ))
    
    return shops_response


def _merge_shops_without_duplicates(shops1: list[dict], shops2: list[dict]) -> list[dict]:
    """Kết hợp 2 danh sách cửa hàng và loại bỏ trùng lặp"""
    existing = {(shop.get('name', '').lower(), round(shop.get('lat', 0), 4), round(shop.get('lon', 0), 4)) 
                for shop in shops1}
    
    merged = shops1.copy()
    for shop in shops2:
        shop_key = (shop.get('name', '').lower(), round(shop.get('lat', 0), 4), round(shop.get('lon', 0), 4))
        if shop_key not in existing:
            merged.append(shop)
            existing.add(shop_key)
    
    return merged


# ===== API Endpoints =====
@app.get("/")
async def root():
    """Endpoint kiểm tra server hoạt động"""
    return {
        "message": "Fashion Shop Finder API đang hoạt động",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat (POST)",
            "health": "/health (GET)",
            "docs": "/docs (GET)"
        }
    }


@app.get("/health")
async def health_check():
    """Endpoint kiểm tra trạng thái hệ thống"""
    gemini_service = get_gemini_service()
    
    return {
        "status": "healthy",
        "gemini_connected": gemini_service.model is not None,
        "google_sheets_configured": bool(GOOGLE_SHEETS_ID),
        "places_api_enabled": PLACES_API_ENABLED
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint chính xử lý yêu cầu tìm kiếm và tư vấn
    
    Args:
        request: ChatRequest chứa vị trí và câu hỏi người dùng
    
    Returns:
        ChatResponse chứa danh sách cửa hàng và phản hồi AI
    
    Raises:
        HTTPException: Khi có lỗi xử lý
    """
    try:
        logger.info(f"Nhận request: lat={request.lat}, lon={request.lon}, message='{request.message[:50]}...'")
        
        # Lấy các tham số từ request hoặc dùng giá trị mặc định
        priority_radius = request.priority_radius_km or PRIORITY_RADIUS_KM
        max_radius = request.max_radius_km or MAX_RADIUS_KM
        max_shops = request.max_shops or MAX_SHOPS
        
        logger.info(f"Tham số tìm kiếm: bán kính ưu tiên={priority_radius}km, bán kính tối đa={max_radius}km, số lượng={max_shops}")
        
        # Bước 1: Tìm kiếm cửa hàng từ OpenStreetMap
        all_shops = search_nearby_shops(
            lat=request.lat,
            lon=request.lon,
            radius_meters=int(priority_radius * 1000),
            keyword="cửa hàng quần áo"
        )
        logger.info(f"Tìm thấy {len(all_shops)} cửa hàng từ OpenStreetMap")
        
        # Mở rộng bán kính nếu chưa đủ
        if len(all_shops) < max_shops and max_radius > priority_radius:
            logger.info(f"Mở rộng bán kính tìm kiếm đến {max_radius}km...")
            more_shops = search_nearby_shops(
                lat=request.lat,
                lon=request.lon,
                radius_meters=int(max_radius * 1000),
                keyword="cửa hàng quần áo"
            )
            all_shops = _merge_shops_without_duplicates(all_shops, more_shops)
            logger.info(f"Tổng cộng tìm thấy {len(all_shops)} cửa hàng sau khi mở rộng")
        
        # Bước 2: Lọc và sắp xếp theo khoảng cách
        nearby_shops = filter_shops_by_radius(
            user_lat=request.lat,
            user_lon=request.lon,
            shops=all_shops,
            radius_km=max_radius,
            limit=max_shops
        )
        logger.info(f"Cửa hàng trong bán kính {max_radius}km: {len(nearby_shops)}")
        
        # Bước 3: Lưu các cửa hàng vào Google Sheets (nền, không chặn response)
        if nearby_shops and GOOGLE_SHEETS_ID:
            try:
                shops_to_save = _prepare_shops_for_saving(nearby_shops)
                added_count = add_shops_to_sheet_batch(GOOGLE_SHEETS_ID, shops_to_save, "Trang tính 1")
                if added_count > 0:
                    logger.info(f"Đã lưu {added_count} cửa hàng mới vào Google Sheets")
            except Exception as e:
                logger.error(f"Lỗi khi lưu vào Google Sheets: {str(e)}", exc_info=True)
        
        # Bước 4: Gọi Gemini AI để sinh nội dung tư vấn
        gemini_service = get_gemini_service()
        user_location = {"lat": request.lat, "lon": request.lon}
        
        ai_message = gemini_service.generate_fashion_advice(
            shops=nearby_shops,
            user_location=user_location,
            user_query=request.message
        )
        
        # Bước 5: Sinh gợi ý sản phẩm cho từng cửa hàng
        suggestions = gemini_service.generate_item_suggestions(nearby_shops)
        
        # Bước 6: Format response
        shops_response = _format_shops_response(nearby_shops, suggestions)
        
        logger.info(f"Trả về {len(shops_response)} cửa hàng và AI message")
        
        return ChatResponse(
            shops=shops_response,
            ai_message=ai_message
        )
        
    except ValueError as e:
        logger.error(f"Lỗi validate dữ liệu: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Dữ liệu không hợp lệ: {str(e)}")
    except Exception as e:
        logger.error(f"Lỗi xử lý request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Lỗi xử lý yêu cầu. Vui lòng thử lại sau."
        )


# Chạy server nếu file được thực thi trực tiếp
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    
    logger.info(f"Khởi động server tại http://{host}:{port}")
    logger.info(f"API docs: http://{host}:{port}/docs")
    
    # Sử dụng import string để enable reload (không có cảnh báo)
    # Hoặc tắt reload nếu không cần
    use_reload = os.getenv('RELOAD', 'false').lower() == 'true'
    
    if use_reload:
        # Chạy với reload (cần import string)
        uvicorn.run("app:app", host=host, port=port, reload=True)
    else:
        # Chạy không reload (đơn giản, không cảnh báo)
        uvicorn.run(app, host=host, port=port, reload=False)
