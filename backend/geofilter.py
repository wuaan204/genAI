# geofilter.py - Module lọc cửa hàng theo vị trí địa lý
# Sử dụng thư viện geopy để tính khoảng cách giữa 2 điểm GPS

from geopy.distance import geodesic
from typing import List, Dict, Any

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách giữa 2 điểm GPS (đơn vị: km)
    
    Args:
        lat1, lon1: Tọa độ điểm thứ nhất (vị trí người dùng)
        lat2, lon2: Tọa độ điểm thứ hai (vị trí cửa hàng)
    
    Returns:
        Khoảng cách tính bằng km
    """
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).kilometers

def filter_shops_by_radius(
    user_lat: float, 
    user_lon: float, 
    shops: List[Dict[str, Any]], 
    radius_km: float = 5.0,
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Lọc các cửa hàng trong bán kính cho trước và trả về danh sách gần nhất
    
    Args:
        user_lat: Vĩ độ người dùng
        user_lon: Kinh độ người dùng
        shops: Danh sách tất cả cửa hàng
        radius_km: Bán kính tìm kiếm (mặc định 5km)
        limit: Số lượng cửa hàng tối đa trả về (mặc định 3)
    
    Returns:
        Danh sách các cửa hàng gần nhất, đã sắp xếp theo khoảng cách
    """
    shops_with_distance = []
    
    for shop in shops:
        try:
            shop_lat = float(shop.get('lat', 0))
            shop_lon = float(shop.get('lon', 0))
            
            # Kiểm tra tọa độ hợp lệ
            if shop_lat == 0 and shop_lon == 0:
                continue
            
            distance = calculate_distance(user_lat, user_lon, shop_lat, shop_lon)
            
            # Chỉ lấy các cửa hàng trong bán kính cho phép
            if distance <= radius_km:
                shop_copy = shop.copy()
                shop_copy['distance_km'] = round(distance, 2)
                
                # Tính điểm ưu tiên: cửa hàng gần hơn và có thông tin đầy đủ được ưu tiên
                priority_score = 0
                # Ưu tiên cửa hàng gần (khoảng cách càng nhỏ, điểm càng cao)
                priority_score += max(0, 100 - distance * 10)
                # Ưu tiên cửa hàng có đầy đủ thông tin
                if shop.get('name') and shop.get('address'):
                    priority_score += 10
                if shop.get('category'):
                    priority_score += 5
                if shop.get('price_range'):
                    priority_score += 5
                if shop.get('notes'):  # Có khuyến mãi
                    priority_score += 15
                
                shop_copy['priority_score'] = priority_score
                shops_with_distance.append(shop_copy)
        except (ValueError, TypeError):
            # Bỏ qua các cửa hàng có tọa độ không hợp lệ
            continue
    
    # Sắp xếp: ưu tiên điểm số, sau đó mới đến khoảng cách
    shops_with_distance.sort(key=lambda x: (-x.get('priority_score', 0), x['distance_km']))
    
    # Trả về số lượng giới hạn
    return shops_with_distance[:limit]

def get_nearby_shops_summary(shops: List[Dict[str, Any]]) -> str:
    """
    Tạo chuỗi tóm tắt thông tin các cửa hàng gần đó để gửi cho AI
    
    Args:
        shops: Danh sách cửa hàng đã lọc
    
    Returns:
        Chuỗi mô tả thông tin các cửa hàng
    """
    if not shops:
        return "Khong tim thay cua hang nao gan day."
    
    summary_parts = []
    for i, shop in enumerate(shops, 1):
        part = (
            f"{i}. {shop.get('name', 'N/A')} - "
            f"Dia chi: {shop.get('address', 'N/A')} - "
            f"Khoang cach: {shop.get('distance_km', 'N/A')}km - "
            f"Danh muc: {shop.get('category', 'N/A')} - "
            f"Gia: {shop.get('price_range', 'N/A')} - "
            f"Ghi chu: {shop.get('notes', '')}"
        )
        summary_parts.append(part)
    
    return "\n".join(summary_parts)