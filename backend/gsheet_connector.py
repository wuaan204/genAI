# gsheet_connector.py - Module kết nối và đọc dữ liệu từ Google Sheets
# Sử dụng thư viện gspread với xác thực Service Account

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
import os
import json

# Phạm vi quyền truy cập Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

class GoogleSheetsConnector:
    """
    Lớp kết nối và đọc dữ liệu từ Google Sheets
    """
    
    def __init__(self, credentials_path: str = None, credentials_json: str = None):
        """
        Khởi tạo kết nối Google Sheets
        
        Args:
            credentials_path: Đường dẫn file credentials JSON
            credentials_json: Chuỗi JSON credentials (ưu tiên dùng biến môi trường)
        """
        self.client = None
        self._initialize_client(credentials_path, credentials_json)
    
    def _initialize_client(self, credentials_path: str, credentials_json: str):
        """
        Khởi tạo client gspread với credentials
        """
        try:
            # Ưu tiên sử dụng credentials từ biến môi trường
            if credentials_json:
                creds_dict = json.loads(credentials_json)
                credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            elif credentials_path and os.path.exists(credentials_path):
                credentials = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
            else:
                print("Canh bao: Khong tim thay credentials, su dung du lieu mau")
                self.client = None
                return
            
            self.client = gspread.authorize(credentials)
            print("Ket noi Google Sheets thanh cong")
        except Exception as e:
            print(f"Loi ket noi Google Sheets: {str(e)}")
            self.client = None
    
    def get_shops_data(self, spreadsheet_id: str, sheet_name: str = "Sheet1") -> List[Dict[str, Any]]:
        """
        Đọc dữ liệu cửa hàng từ Google Sheets
        
        Args:
            spreadsheet_id: ID của Google Spreadsheet
            sheet_name: Tên sheet chứa dữ liệu
        
        Returns:
            Danh sách các cửa hàng dưới dạng dictionary
        """
        if not self.client:
            print("Khong co ket noi, tra ve du lieu mau")
            return self._get_sample_data()
        
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Lấy tất cả dữ liệu dưới dạng list of dictionaries
            records = worksheet.get_all_records()
            
            print(f"Da doc {len(records)} cua hang tu Google Sheets")
            return records
        except Exception as e:
            print(f"Loi doc du lieu: {str(e)}")
            return self._get_sample_data()
    
    def _get_sample_data(self) -> List[Dict[str, Any]]:
        """
        Trả về dữ liệu mẫu khi không kết nối được Google Sheets
        Dữ liệu mẫu: 15 cửa hàng quần áo tại Hà Nội và TP.HCM
        """
        return [
            # Cửa hàng tại Hà Nội
            {
                "name": "Elise Fashion Hoan Kiem",
                "address": "42 Trang Tien, Hoan Kiem, Ha Noi",
                "lat": 21.0245,
                "lon": 105.8530,
                "category": "Thoi trang nu cao cap",
                "price_range": "500k - 2tr",
                "notes": "Giam 20% cuoi tuan, mau moi 2024"
            },
            {
                "name": "CANIFA Vincom Ba Trieu",
                "address": "191 Ba Trieu, Hai Ba Trung, Ha Noi",
                "lat": 21.0115,
                "lon": 105.8490,
                "category": "Thoi trang gia dinh",
                "price_range": "200k - 800k",
                "notes": "Mua 2 giam 15%, free ship noi thanh"
            },
            {
                "name": "Routine Store Cau Giay",
                "address": "125 Xuan Thuy, Cau Giay, Ha Noi",
                "lat": 21.0367,
                "lon": 105.7873,
                "category": "Streetwear nam nu",
                "price_range": "300k - 1tr",
                "notes": "BST mua dong moi, tang voucher 100k"
            },
            {
                "name": "YODY Thai Ha",
                "address": "98 Thai Ha, Dong Da, Ha Noi",
                "lat": 21.0145,
                "lon": 105.8215,
                "category": "Thoi trang co ban",
                "price_range": "150k - 500k",
                "notes": "Flash sale thu 6, giam den 50%"
            },
            {
                "name": "NEM Fashion Kim Ma",
                "address": "233 Kim Ma, Ba Dinh, Ha Noi",
                "lat": 21.0305,
                "lon": 105.8145,
                "category": "Thoi trang cong so nu",
                "price_range": "400k - 1.5tr",
                "notes": "Combo 3 mon giam 25%"
            },
            {
                "name": "Owen Hang Bai",
                "address": "88 Hang Bai, Hoan Kiem, Ha Noi",
                "lat": 21.0252,
                "lon": 105.8485,
                "category": "Ao so mi nam cao cap",
                "price_range": "350k - 900k",
                "notes": "Mua 3 tang 1, theu ten mien phi"
            },
            {
                "name": "Ivy Moda Long Bien",
                "address": "Aeon Mall Long Bien, Ha Noi",
                "lat": 21.0507,
                "lon": 105.8913,
                "category": "Thoi trang nu tre trung",
                "price_range": "300k - 1.2tr",
                "notes": "Giam 30% cho khach moi"
            },
            # Cửa hàng tại TP.HCM
            {
                "name": "Routine Store Nguyen Hue",
                "address": "76 Nguyen Hue, Quan 1, TP.HCM",
                "lat": 10.7738,
                "lon": 106.7031,
                "category": "Streetwear nam nu",
                "price_range": "300k - 1tr",
                "notes": "Khai truong giam 25%"
            },
            {
                "name": "JUNO Quan 3",
                "address": "156 Vo Van Tan, Quan 3, TP.HCM",
                "lat": 10.7725,
                "lon": 106.6875,
                "category": "Giay dep & Tui xach nu",
                "price_range": "200k - 600k",
                "notes": "Combo giay + tui giam 20%"
            },
            {
                "name": "Blue Exchange Phu Nhuan",
                "address": "210 Phan Xich Long, Phu Nhuan, TP.HCM",
                "lat": 10.7985,
                "lon": 106.6805,
                "category": "Thoi trang tre",
                "price_range": "150k - 450k",
                "notes": "Hoc sinh sinh vien giam 15%"
            },
            {
                "name": "Nem Fashion Crescent Mall",
                "address": "Crescent Mall, Quan 7, TP.HCM",
                "lat": 10.7295,
                "lon": 106.7195,
                "category": "Thoi trang cong so nu",
                "price_range": "400k - 1.5tr",
                "notes": "Tang scarf khi mua tu 1tr"
            },
            {
                "name": "CANIFA Landmark 81",
                "address": "Landmark 81, Binh Thanh, TP.HCM",
                "lat": 10.7952,
                "lon": 106.7219,
                "category": "Thoi trang gia dinh",
                "price_range": "200k - 800k",
                "notes": "Member giam them 10%"
            },
            {
                "name": "Elise Takashimaya",
                "address": "Takashimaya, Quan 1, TP.HCM",
                "lat": 10.7733,
                "lon": 106.7010,
                "category": "Thoi trang nu cao cap",
                "price_range": "600k - 2.5tr",
                "notes": "BST Xuan He 2024, thiet ke doc quyen"
            },
            {
                "name": "Owen Le Loi",
                "address": "102 Le Loi, Quan 1, TP.HCM",
                "lat": 10.7718,
                "lon": 106.6980,
                "category": "Ao so mi nam cao cap",
                "price_range": "350k - 900k",
                "notes": "In logo cong ty mien phi"
            },
            {
                "name": "YODY Go Vap",
                "address": "458 Quang Trung, Go Vap, TP.HCM",
                "lat": 10.8385,
                "lon": 106.6495,
                "category": "Thoi trang co ban",
                "price_range": "150k - 500k",
                "notes": "Doi tra trong 30 ngay"
            }
        ]


# Singleton instance để sử dụng trong toàn bộ ứng dụng
_connector_instance = None

def get_connector(credentials_path: str = None, credentials_json: str = None) -> GoogleSheetsConnector:
    """
    Lấy instance GoogleSheetsConnector (Singleton pattern)
    """
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = GoogleSheetsConnector(credentials_path, credentials_json)
    return _connector_instance

def fetch_all_shops(spreadsheet_id: str = None, sheet_name: str = "Sheet1") -> List[Dict[str, Any]]:
    """
    Hàm tiện ích để lấy tất cả dữ liệu cửa hàng
    
    Args:
        spreadsheet_id: ID của Google Spreadsheet
        sheet_name: Tên sheet
    
    Returns:
        Danh sách cửa hàng
    """
    credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    connector = get_connector(credentials_json=credentials_json)
    
    if spreadsheet_id:
        return connector.get_shops_data(spreadsheet_id, sheet_name)
    else:
        return connector._get_sample_data()