# geofilter.py - Module lọc cửa hàng theo vị trí địa lý
# Sử dụng thư viện geopy để tính khoảng cách giữa 2 điểm GPS

from geopy.distance import geodesic
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách giữa 2 điểm GPS (đơn vị: km)
    
    Args:
        lat1, lon1: Tọa độ điểm thứ nhất (vị trí người dùng)
        lat2, lon2: Tọa độ điểm thứ hai (vị trí cửa hàng)
    
    Returns:
        Khoảng cách tính bằng km
    """
    try:
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        return geodesic(point1, point2).kilometers
    except Exception as e:
        logger.error(f"Lỗi tính khoảng cách: {str(e)}")
        return 999.0  # Trả về giá trị lớn nếu lỗi


def _validate_coordinates(lat: float, lon: float) -> bool:
    """Kiểm tra tọa độ hợp lệ"""
    return -90 <= lat <= 90 and -180 <= lon <= 180


def _calculate_priority_score(shop: Dict[str, Any], distance_km: float) -> float:
    """Tính điểm ưu tiên cho cửa hàng"""
    score = 0.0
    
    # Ưu tiên cửa hàng gần (khoảng cách càng nhỏ, điểm càng cao)
    score += max(0, 100 - distance_km * 10)
    
    # Ưu tiên cửa hàng có đầy đủ thông tin
    if shop.get('name') and shop.get('address'):
        score += 10
    if shop.get('category'):
        score += 5
    if shop.get('price_range'):
        score += 5
    if shop.get('notes'):  # Có khuyến mãi
        score += 15
    
    return score


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
    # Validate tọa độ người dùng
    if not _validate_coordinates(user_lat, user_lon):
        logger.warning(f"Tọa độ người dùng không hợp lệ: lat={user_lat}, lon={user_lon}")
        return []
    
    shops_with_distance = []
    
    for shop in shops:
        try:
            shop_lat = float(shop.get('lat', 0))
            shop_lon = float(shop.get('lon', 0))
            
            # Kiểm tra tọa độ hợp lệ
            if not _validate_coordinates(shop_lat, shop_lon):
                continue
            
            if shop_lat == 0 and shop_lon == 0:
                continue
            
            distance = calculate_distance(user_lat, user_lon, shop_lat, shop_lon)
            
            # Chỉ lấy các cửa hàng trong bán kính cho phép
            if distance <= radius_km:
                shop_copy = shop.copy()
                shop_copy['distance_km'] = round(distance, 2)
                
                # Tính điểm ưu tiên
                priority_score = _calculate_priority_score(shop, distance)
                shop_copy['priority_score'] = priority_score
                
                shops_with_distance.append(shop_copy)
                
        except (ValueError, TypeError) as e:
            logger.debug(f"Bỏ qua cửa hàng có tọa độ không hợp lệ: {str(e)}")
            continue
    
    # Sắp xếp: ưu tiên điểm số, sau đó mới đến khoảng cách
    shops_with_distance.sort(key=lambda x: (-x.get('priority_score', 0), x['distance_km']))
    
    # Trả về số lượng giới hạn
    result = shops_with_distance[:limit]
    logger.info(f"Lọc được {len(result)}/{len(shops)} cửa hàng trong bán kính {radius_km}km")
    
    return result


def get_nearby_shops_summary(shops: List[Dict[str, Any]]) -> str:
    """
    Tạo chuỗi tóm tắt thông tin các cửa hàng gần đó để gửi cho AI
    
    Args:
        shops: Danh sách cửa hàng đã lọc
    
    Returns:
        Chuỗi mô tả thông tin các cửa hàng
    """
    if not shops:
        return "Không tìm thấy cửa hàng nào gần đây."
    
    summary_parts = []
    for i, shop in enumerate(shops, 1):
        part = (
            f"{i}. {shop.get('name', 'N/A')} - "
            f"Địa chỉ: {shop.get('address', 'N/A')} - "
            f"Khoảng cách: {shop.get('distance_km', 'N/A')}km - "
            f"Danh mục: {shop.get('category', 'N/A')} - "
            f"Giá: {shop.get('price_range', 'N/A')} - "
            f"Ghi chú: {shop.get('notes', '')}"
        )
        summary_parts.append(part)
    
    return "\n".join(summary_parts)
