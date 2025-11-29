# gemini_service.py - Module gọi Google Gemini API để sinh nội dung tư vấn
# Sử dụng thư viện google-generativeai

import google.generativeai as genai
from typing import List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

# Model name
GEMINI_MODEL = 'gemini-flash-latest'


class GeminiService:
    """Lớp xử lý gọi Gemini API để sinh nội dung tư vấn thời trang"""
    
    def __init__(self, api_key: str = None):
        """
        Khởi tạo Gemini Service
        
        Args:
            api_key: API key của Google Gemini
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Khởi tạo model Gemini"""
        if not self.api_key:
            logger.warning("Không có GEMINI_API_KEY, sẽ trả về phản hồi mặc định")
            self.model = None
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            logger.info("Khởi tạo Gemini model thành công")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo Gemini: {str(e)}")
            self.model = None
    
    def generate_fashion_advice(
        self, 
        shops: List[Dict[str, Any]], 
        user_location: Dict[str, float],
        user_query: str
    ) -> str:
        """
        Sinh nội dung tư vấn thời trang dựa trên cửa hàng gần đó và câu hỏi người dùng
        
        Args:
            shops: Danh sách cửa hàng gần đó
            user_location: Vị trí người dùng {"lat": ..., "lon": ...}
            user_query: Câu hỏi của người dùng
        
        Returns:
            Chuỗi nội dung tư vấn từ AI
        """
        if not self.model:
            return self._generate_fallback_response(shops, user_query)
        
        try:
            prompt = self._build_prompt(shops, user_location, user_query)
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Lỗi gọi Gemini API: {str(e)}")
            return self._generate_fallback_response(shops, user_query)
    
    def _build_prompt(
        self, 
        shops: List[Dict[str, Any]], 
        user_location: Dict[str, float],
        user_query: str
    ) -> str:
        """Xây dựng prompt gửi cho Gemini"""
        shops_info = self._format_shops_info(shops)
        
        prompt = f"""Bạn là Fashion AI - trợ lý thời trang thông minh và thân thiện. 

THÔNG TIN CỬA HÀNG GẦN ĐÂY (để tham khảo khi cần):
{shops_info}

CÂU HỎI: {user_query}

HƯỚNG DẪN TRẢ LỜI:
- Trả lời bằng tiếng Việt, thân thiện như đang trò chuyện với bạn bè
- Tập trung vào câu hỏi của người dùng - có thể là về thời trang, phong cách, xu hướng, cách phối đồ, v.v.
- Nếu câu hỏi liên quan đến mua sắm hoặc tìm cửa hàng, hãy gợi ý từ danh sách trên
- Nếu câu hỏi chung về thời trang (xu hướng, phối đồ, chất liệu...), hãy tư vấn chuyên môn
- Nếu là câu chào hỏi hoặc trò chuyện, hãy đáp lại thân thiện
- Giữ câu trả lời ngắn gọn (50-150 từ), dễ đọc
- Có thể dùng emoji phù hợp để tăng tính thân thiện

Trả lời:"""
        
        return prompt
    
    def _format_shops_info(self, shops: List[Dict[str, Any]]) -> str:
        """Format thông tin cửa hàng thành chuỗi"""
        if not shops:
            return "Không tìm thấy cửa hàng nào gần đây."
        
        formatted_parts = []
        for i, shop in enumerate(shops, 1):
            part = f"""
{i}. {shop.get('name', 'N/A')}
   - Địa chỉ: {shop.get('address', 'N/A')}
   - Khoảng cách: {shop.get('distance_km', 'N/A')} km
   - Danh mục: {shop.get('category', 'N/A')}
   - Mức giá: {shop.get('price_range', 'N/A')}
   - Khuyến mãi: {shop.get('notes', 'Không có')}"""
            formatted_parts.append(part)
        
        return "\n".join(formatted_parts)
    
    def _generate_fallback_response(self, shops: List[Dict[str, Any]], user_query: str) -> str:
        """Sinh phản hồi mặc định khi không có API key hoặc lỗi"""
        if not shops:
            return "Xin lỗi, hiện tại không tìm thấy cửa hàng quần áo nào gần bạn. Bạn có thể mở rộng phạm vi tìm kiếm hoặc thử lại sau."
        
        response_parts = [f"Dựa trên vị trí của bạn, tôi tìm thấy {len(shops)} cửa hàng gần đây:\n"]
        
        for i, shop in enumerate(shops, 1):
            promo = shop.get('notes', '')
            response_parts.append(
                f"{i}. **{shop.get('name', 'N/A')}** ({shop.get('distance_km', '?')}km)\n"
                f"   Danh mục: {shop.get('category', 'N/A')}\n"
                f"   Mức giá: {shop.get('price_range', 'N/A')}\n"
                f"   {'🎁 ' + promo if promo else ''}\n"
            )
        
        response_parts.append(f"\nVề câu hỏi của bạn: \"{user_query}\" - Tôi khuyên bạn nên ghé cửa hàng gần nhất để được tư vấn trực tiếp!")
        
        return "\n".join(response_parts)
    
    def generate_item_suggestions(self, shops: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Sinh gợi ý sản phẩm cho từng cửa hàng
        
        Args:
            shops: Danh sách cửa hàng
        
        Returns:
            Danh sách gợi ý cho từng cửa hàng
        """
        suggestions = []
        
        for shop in shops:
            category = shop.get('category', '').lower()
            suggestion = self._get_suggestion_by_category(category)
            
            suggestions.append({
                "shop_name": shop.get('name', ''),
                "item_suggestion": suggestion,
                "promo_text": shop.get('notes', '')
            })
        
        return suggestions
    
    def _get_suggestion_by_category(self, category: str) -> str:
        """Lấy gợi ý sản phẩm dựa trên danh mục"""
        if 'nữ' in category:
            return "Đầm công sở, áo kiểu thanh lịch"
        elif 'nam' in category:
            return "Áo sơ mi cao cấp, quần tây"
        elif 'streetwear' in category or 'phong cách' in category:
            return "Áo thun oversize, quần jogger"
        elif 'gia đình' in category or 'trẻ em' in category:
            return "Set đồ đôi, đồ trẻ em cute"
        elif 'giày' in category or 'túi' in category or 'phụ kiện' in category:
            return "Giày cao gót, túi xách thời trang"
        else:
            return "Nhiều mẫu mới 2024"


# Singleton instance
_gemini_instance = None

def get_gemini_service(api_key: str = None) -> GeminiService:
    """Lấy instance GeminiService (Singleton pattern)"""
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiService(api_key)
    return _gemini_instance
