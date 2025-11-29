# places_service.py - Module tìm kiếm cửa hàng từ OpenStreetMap
# Sử dụng Overpass API (miễn phí, không cần API key)

import os
import httpx
import logging
from typing import List, Dict, Any, Optional
from geofilter import calculate_distance
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Cấu hình logging
logger = logging.getLogger(__name__)

# Overpass API endpoint (miễn phí)
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"

# Constants
MAX_RADIUS_METERS = 50000  # 50km
TIMEOUT_SECONDS = 30
SHOP_TAGS = ["clothes", "fashion", "boutique", "department_store", "mall"]
SHOP_TYPES = ["node", "way"]

# Category mapping
CATEGORY_MAP = {
    'clothes': 'Quần áo',
    'fashion': 'Thời trang',
    'boutique': 'Boutique',
    'department_store': 'Trung tâm thương mại',
    'mall': 'Trung tâm thương mại'
}

# Bật/tắt tính năng tìm kiếm
PLACES_API_ENABLED = os.getenv('PLACES_API_ENABLED', 'true').lower() == 'true'


def _build_overpass_query(lat: float, lon: float, radius_meters: int) -> str:
    """Xây dựng Overpass QL query để tìm cửa hàng"""
    shop_queries = []
    for shop_type in SHOP_TYPES:
        for tag in SHOP_TAGS:
            shop_queries.append(f'{shop_type}["shop"="{tag}"](around:{radius_meters},{lat},{lon});')
    
    query = f"""
    [out:json][timeout:25];
    (
      {"".join(shop_queries)}
    );
    out center;
    """
    return query


def _extract_coordinates(element: dict) -> Optional[tuple]:
    """Trích xuất tọa độ từ element OpenStreetMap"""
    if element.get('type') == 'node':
        lat = element.get('lat')
        lon = element.get('lon')
    else:
        center = element.get('center', {})
        lat = center.get('lat')
        lon = center.get('lon')
    
    return (lat, lon) if lat and lon else None


def _extract_address(tags: dict) -> str:
    """Trích xuất địa chỉ từ tags"""
    address_parts = []
    
    if tags.get('addr:housenumber'):
        address_parts.append(tags.get('addr:housenumber'))
    if tags.get('addr:street'):
        address_parts.append(tags.get('addr:street'))
    if tags.get('addr:district'):
        address_parts.append(tags.get('addr:district'))
    if tags.get('addr:city'):
        address_parts.append(tags.get('addr:city'))
    
    return ', '.join(address_parts) if address_parts else tags.get('addr:full', 'Không có địa chỉ')


def _normalize_shop_data(element: dict, lat: float, lon: float, user_lat: float, user_lon: float) -> dict:
    """Chuẩn hóa dữ liệu cửa hàng từ OSM element"""
    tags = element.get('tags', {})
    shop_type = tags.get('shop', 'clothes')
    
    distance_km = calculate_distance(user_lat, user_lon, lat, lon)
    category = CATEGORY_MAP.get(shop_type, 'Quần áo')
    name = tags.get('name') or tags.get('brand') or f'Cửa hàng {category}'
    
    return {
        'name': name,
        'address': _extract_address(tags),
        'lat': lat,
        'lon': lon,
        'distance_km': round(distance_km, 2),
        'category': category,
        'price_range': '',
        'notes': tags.get('opening_hours', ''),
        'phone': tags.get('phone') or tags.get('contact:phone', ''),
        'website': tags.get('website') or tags.get('contact:website', ''),
        'osm_id': element.get('id'),
        'source': 'openstreetmap'
    }


def search_nearby_shops(
    lat: float, 
    lon: float, 
    radius_meters: int = 5000, 
    keyword: str = "cửa hàng quần áo"
) -> List[Dict[str, Any]]:
    """
    Tìm kiếm cửa hàng quần áo gần đây từ OpenStreetMap (Overpass API)
    Miễn phí, không cần API key
    
    Args:
        lat: Vĩ độ vị trí người dùng
        lon: Kinh độ vị trí người dùng
        radius_meters: Bán kính tìm kiếm (mét), tối đa 50km
        keyword: Từ khóa (không dùng, giữ để tương thích)
    
    Returns:
        Danh sách cửa hàng tìm được từ OpenStreetMap
    """
    if not PLACES_API_ENABLED:
        logger.info("[OSM] Tìm kiếm chưa được kích hoạt")
        return []
    
    # Validate và giới hạn bán kính
    radius_meters = min(max(radius_meters, 100), MAX_RADIUS_METERS)
    
    try:
        logger.info(f"[OSM] Đang tìm kiếm cửa hàng trong bán kính {radius_meters}m...")
        
        # Xây dựng query
        query = _build_overpass_query(lat, lon, radius_meters)
        
        # Gọi Overpass API
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.post(OVERPASS_API_URL, data={'data': query})
            response.raise_for_status()
            data = response.json()
        
        elements = data.get('elements', [])
        logger.info(f"[OSM] Tìm thấy {len(elements)} địa điểm từ OpenStreetMap")
        
        # Xử lý và chuẩn hóa dữ liệu
        shops = []
        for element in elements:
            coords = _extract_coordinates(element)
            if not coords:
                continue
            
            shop_lat, shop_lon = coords
            shop = _normalize_shop_data(element, shop_lat, shop_lon, lat, lon)
            shops.append(shop)
        
        # Sắp xếp theo khoảng cách
        shops.sort(key=lambda x: x['distance_km'])
        
        logger.info(f"[OSM] Trả về {len(shops)} cửa hàng")
        return shops
        
    except httpx.HTTPError as e:
        logger.error(f"[OSM] Lỗi HTTP khi gọi Overpass API: {str(e)}")
        return _get_sample_places(lat, lon)
    except Exception as e:
        logger.error(f"[OSM] Lỗi khi tìm kiếm: {str(e)}", exc_info=True)
        return _get_sample_places(lat, lon)


def _get_sample_places(lat: float, lon: float) -> List[Dict[str, Any]]:
    """Trả về dữ liệu mẫu khi có lỗi hoặc không tìm được"""
    import random
    
    sample_names = [
        "Uniqlo", "H&M", "Zara", "Cotton On", "Canifa",
        "Ivy Moda", "Elise", "BOO", "Routine", "Owen",
        "Format", "Yame", "Nem Fashion", "Juno", "Vascara"
    ]
    
    sample_categories = ["Thời trang nam", "Thời trang nữ", "Quần áo", "Phụ kiện"]
    sample_price_ranges = ["Bình dân", "Trung cấp", "Cao cấp"]
    
    shops = []
    for i, name in enumerate(sample_names):
        # Tạo tọa độ ngẫu nhiên trong bán kính 5km
        offset_lat = random.uniform(-0.045, 0.045)
        offset_lon = random.uniform(-0.045, 0.045)
        
        shop_lat = lat + offset_lat
        shop_lon = lon + offset_lon
        distance_km = calculate_distance(lat, lon, shop_lat, shop_lon)
        
        shops.append({
            'name': f"{name} - Chi nhánh {i+1}",
            'address': f"Số {random.randint(1, 200)} Đường ABC, Quận {random.randint(1, 12)}",
            'lat': shop_lat,
            'lon': shop_lon,
            'distance_km': round(distance_km, 2),
            'category': random.choice(sample_categories),
            'price_range': random.choice(sample_price_ranges),
            'notes': '',
            'source': 'sample_data'
        })
    
    shops.sort(key=lambda x: x['distance_km'])
    logger.info(f"[OSM] Trả về {len(shops)} cửa hàng mẫu (fallback)")
    return shops
