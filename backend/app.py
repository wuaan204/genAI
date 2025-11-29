# app.py - File chính của Backend API
# Sử dụng FastAPI framework

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Import các module đã tách
from geofilter import filter_shops_by_radius, get_nearby_shops_summary
from gsheet_connector import fetch_all_shops
from gemini_service import get_gemini_service

# Load biến môi trường từ file .env
load_dotenv()

# Khởi tạo FastAPI app
app = FastAPI(
    title="Fashion Shop Finder API",
    description="API tim kiem cua hang quan ao gan day va tu van thoi trang bang AI",
    version="1.0.0"
)

# Cấu hình CORS để cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Định nghĩa schema cho request
class ChatRequest(BaseModel):
    """
    Schema cho request từ client
    
    Attributes:
        lat: Vĩ độ vị trí người dùng
        lon: Kinh độ vị trí người dùng
        message: Câu hỏi của người dùng
    """
    lat: float
    lon: float
    message: str

# Định nghĩa schema cho shop trong response
class ShopResponse(BaseModel):
    """
    Schema cho thông tin cửa hàng trong response
    """
    name: str
    address: str
    lat: float
    lon: float
    distance_km: float
    category: str
    price_range: str
    item_suggestion: str
    promo_text: str

# Định nghĩa schema cho response
class ChatResponse(BaseModel):
    """
    Schema cho response trả về client
    """
    shops: list[ShopResponse]
    ai_message: str

# Lấy cấu hình từ biến môi trường
GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID', '')
PRIORITY_RADIUS_KM = float(os.getenv('PRIORITY_RADIUS_KM', '20.0'))
MAX_RADIUS_KM = float(os.getenv('MAX_RADIUS_KM', '500.0'))
MAX_SHOPS = int(os.getenv('MAX_SHOPS', '30'))


@app.get("/")
async def root():
    """
    Endpoint kiểm tra server hoạt động
    """
    return {
        "message": "Fashion Shop Finder API dang hoat dong",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat (POST)",
            "health": "/health (GET)"
        }
    }


@app.get("/health")
async def health_check():
    """
    Endpoint kiểm tra trạng thái hệ thống
    """
    gemini_service = get_gemini_service()
    
    return {
        "status": "healthy",
        "gemini_connected": gemini_service.model is not None,
        "google_sheets_configured": bool(GOOGLE_SHEETS_ID)
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
        print(f"Nhan request: lat={request.lat}, lon={request.lon}, message='{request.message}'")
        
        # Bước 1: Lấy dữ liệu cửa hàng từ Google Sheets
        all_shops = fetch_all_shops(GOOGLE_SHEETS_ID)
        print(f"Tong so cua hang: {len(all_shops)}")
        
        # Bước 2: Lọc cửa hàng theo vị trí và bán kính
        # Ưu tiên tìm trong bán kính 20km trước
        nearby_shops = filter_shops_by_radius(
            user_lat=request.lat,
            user_lon=request.lon,
            shops=all_shops,
            radius_km=PRIORITY_RADIUS_KM,
            limit=MAX_SHOPS
        )
        print(f"Cua hang trong ban kinh uu tien {PRIORITY_RADIUS_KM}km: {len(nearby_shops)}")
        
        # Nếu chưa đủ, mở rộng bán kính tìm kiếm
        if len(nearby_shops) < MAX_SHOPS:
            print(f"Mo rong ban kinh tim kiem den {MAX_RADIUS_KM}km...")
            all_nearby = filter_shops_by_radius(
                user_lat=request.lat,
                user_lon=request.lon,
                shops=all_shops,
                radius_km=MAX_RADIUS_KM,
                limit=MAX_SHOPS * 2
            )
            
            # Kết hợp và loại bỏ trùng lặp
            existing_names = {shop.get('name') for shop in nearby_shops}
            for shop in all_nearby:
                if shop.get('name') not in existing_names and len(nearby_shops) < MAX_SHOPS:
                    nearby_shops.append(shop)
                    existing_names.add(shop.get('name'))
            
            # Sắp xếp lại theo khoảng cách
            nearby_shops.sort(key=lambda x: x.get('distance_km', 999))
            nearby_shops = nearby_shops[:MAX_SHOPS]
            
            print(f"Tong cong tim thay {len(nearby_shops)} cua hang")
        
        # Bước 3: Gọi Gemini AI để sinh nội dung tư vấn
        gemini_service = get_gemini_service()
        
        user_location = {"lat": request.lat, "lon": request.lon}
        ai_message = gemini_service.generate_fashion_advice(
            shops=nearby_shops,
            user_location=user_location,
            user_query=request.message
        )
        
        # Bước 4: Sinh gợi ý sản phẩm cho từng cửa hàng
        suggestions = gemini_service.generate_item_suggestions(nearby_shops)
        
        # Bước 5: Format response
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
        
        print(f"Tra ve {len(shops_response)} cua hang va AI message")
        
        return ChatResponse(
            shops=shops_response,
            ai_message=ai_message
        )
        
    except Exception as e:
        print(f"Loi xu ly request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Loi xu ly yeu cau: {str(e)}"
        )


@app.get("/shops")
async def get_all_shops():
    """
    Endpoint lấy tất cả cửa hàng (dùng để debug)
    """
    all_shops = fetch_all_shops(GOOGLE_SHEETS_ID)
    return {"total": len(all_shops), "shops": all_shops}


# Chạy server nếu file được thực thi trực tiếp
if __name__ == "__main__":
    import uvicorn
    
    # Cấu hình server
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    
    print(f"Khoi dong server tai http://{host}:{port}")
    print(f"API docs: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port, reload=True)