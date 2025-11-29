# gsheet_connector.py - Module kết nối và đọc dữ liệu từ Google Sheets
# Sử dụng thư viện gspread với xác thực Service Account

import gspread
from gspread.exceptions import WorksheetNotFound
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
import os
import json
import logging

logger = logging.getLogger(__name__)

# Phạm vi quyền truy cập Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
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
                credentials_json = credentials_json.strip()
                
                # Nếu JSON bắt đầu bằng { thì parse trực tiếp
                if credentials_json.startswith('{'):
                    try:
                        # Thử parse JSON trực tiếp (có thể đã là JSON hợp lệ)
                        creds_dict = json.loads(credentials_json)
                    except json.JSONDecodeError:
                        # Nếu fail, thử clean JSON (xử lý multi-line)
                        # Loại bỏ tất cả xuống dòng và tab, chỉ giữ space
                        cleaned = ' '.join(credentials_json.split())
                        # Đảm bảo các string values được giữ nguyên trong quotes
                        creds_dict = json.loads(cleaned)
                else:
                    # Nếu không bắt đầu bằng {, có thể là đường dẫn file
                    raise ValueError("JSON credentials phai bat dau bang {")
                
                credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            elif credentials_path and os.path.exists(credentials_path):
                credentials = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
            else:
                logger.warning("Không tìm thấy credentials, sử dụng dữ liệu mẫu")
                self.client = None
                return
            
            self.client = gspread.authorize(credentials)
            logger.info("Kết nối Google Sheets thành công")
        except Exception as e:
            logger.error(f"Lỗi kết nối Google Sheets: {str(e)}")
            self.client = None
    
    def get_shops_data(self, spreadsheet_id: str, sheet_name: str = "Trang tính 1") -> List[Dict[str, Any]]:
        """
        Đọc dữ liệu cửa hàng từ Google Sheets
        
        Args:
            spreadsheet_id: ID của Google Spreadsheet
            sheet_name: Tên sheet chứa dữ liệu
        
        Returns:
            Danh sách các cửa hàng dưới dạng dictionary
        """
        if not self.client:
            logger.warning("Không có kết nối, trả về dữ liệu mẫu")
            return self._get_sample_data()
        
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Lấy tất cả dữ liệu dưới dạng list of dictionaries
            records = worksheet.get_all_records()
            
            logger.info(f"Đã đọc {len(records)} cửa hàng từ Google Sheets")
            return records
        except Exception as e:
            logger.error(f"Lỗi đọc dữ liệu: {str(e)}")
            return self._get_sample_data()
    
    def add_shop(self, spreadsheet_id: str, shop_data: Dict[str, Any], sheet_name: str = "Trang tính 1") -> bool:
        """
        Thêm cửa hàng mới vào Google Sheet
        
        Args:
            spreadsheet_id: ID của Google Spreadsheet
            shop_data: Thông tin cửa hàng cần thêm
                - name: Tên cửa hàng
                - address: Địa chỉ
                - lat: Vĩ độ
                - lon: Kinh độ
                - category: Danh mục
                - price_range: Mức giá
                - notes: Ghi chú/Khuyến mãi
        
        Returns:
            True nếu thêm thành công, False nếu có lỗi
        """
        if not self.client:
            print("Khong co ket noi, khong the ghi cua hang")
            return False
        
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            
            # Thu mo worksheet, neu khong co thi tao moi hoac lay sheet dau tien
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except WorksheetNotFound:
                # Neu khong tim thay sheet, thu lay sheet dau tien
                try:
                    worksheet_list = spreadsheet.worksheets()
                    if worksheet_list:
                        worksheet = worksheet_list[0]
                        print(f"Sheet '{sheet_name}' khong ton tai, su dung sheet dau tien: '{worksheet.title}'")
                    else:
                        # Neu khong co sheet nao, tao sheet moi
                        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                        # Them header
                        worksheet.append_row(['name', 'address', 'lat', 'lon', 'category', 'price_range', 'notes'])
                        print(f"Da tao sheet moi: '{sheet_name}'")
                except Exception as e:
                    print(f"Loi khi lay hoac tao sheet: {str(e)}")
                    return False
            
            # Kiem tra cua hang da ton tai chua (theo ten)
            existing_shops = worksheet.get_all_records()
            shop_name = shop_data.get('name', '').strip()
            
            # Kiem tra trung ten
            for shop in existing_shops:
                if shop.get('name', '').strip().lower() == shop_name.lower():
                    print(f"Cua hang '{shop_name}' da ton tai, bo qua")
                    return False
            
            # Them cua hang moi vao sheet
            row_data = [
                shop_data.get('name', ''),
                shop_data.get('address', ''),
                shop_data.get('lat', ''),
                shop_data.get('lon', ''),
                shop_data.get('category', ''),
                shop_data.get('price_range', ''),
                shop_data.get('notes', '')
            ]
            
            worksheet.append_row(row_data)
            print(f"Da them cua hang '{shop_name}' vao Google Sheets")
            return True
            
        except Exception as e:
            print(f"Loi them cua hang vao Google Sheets: {str(e)}")
            return False
    
    def add_shops_batch(self, spreadsheet_id: str, shops: List[Dict[str, Any]], sheet_name: str = "Trang tính 1") -> int:
        """
        Thêm nhiều cửa hàng vào Google Sheet (loại bỏ trùng lặp)
        
        Args:
            spreadsheet_id: ID của Google Spreadsheet
            shops: Danh sách cửa hàng cần thêm
            sheet_name: Tên sheet
        
        Returns:
            Số lượng cửa hàng đã thêm thành công
        """
        if not self.client:
            print("[GHI SHEET] Khong co ket noi Google Sheets, khong the ghi cua hang")
            return 0
        
        try:
            print(f"[GHI SHEET] Ket noi den sheet ID: {spreadsheet_id}")
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            
            # Thu mo worksheet, neu khong co thi tao moi hoac lay sheet dau tien
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                print(f"[GHI SHEET] Da mo worksheet: {sheet_name}")
            except WorksheetNotFound:
                # Neu khong tim thay sheet, thu lay sheet dau tien
                try:
                    worksheet_list = spreadsheet.worksheets()
                    if worksheet_list:
                        worksheet = worksheet_list[0]
                        print(f"[GHI SHEET] Sheet '{sheet_name}' khong ton tai, su dung sheet dau tien: '{worksheet.title}'")
                    else:
                        # Neu khong co sheet nao, tao sheet moi
                        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                        # Them header
                        worksheet.append_row(['name', 'address', 'lat', 'lon', 'category', 'price_range', 'notes'])
                        print(f"[GHI SHEET] Da tao sheet moi: '{sheet_name}'")
                except Exception as e:
                    print(f"[GHI SHEET] Loi khi lay hoac tao sheet: {str(e)}")
                    return 0
            
            # Lay danh sach cua hang hien co
            existing_shops = worksheet.get_all_records()
            existing_names = {shop.get('name', '').strip().lower() for shop in existing_shops if shop.get('name')}
            print(f"[GHI SHEET] Hien co {len(existing_names)} cua hang trong sheet")
            
            # Loc cac cua hang moi (chua ton tai)
            new_shops = []
            for shop in shops:
                shop_name = shop.get('name', '').strip()
                if shop_name and shop_name.lower() not in existing_names:
                    new_shops.append([
                        shop.get('name', ''),
                        shop.get('address', ''),
                        shop.get('lat', ''),
                        shop.get('lon', ''),
                        shop.get('category', ''),
                        shop.get('price_range', ''),
                        shop.get('notes', '')
                    ])
                    existing_names.add(shop_name.lower())
            
            # Them hang loat vao sheet
            if new_shops:
                print(f"[GHI SHEET] Dang ghi {len(new_shops)} cua hang vao sheet...")
                worksheet.append_rows(new_shops)
                print(f"[GHI SHEET] THANH CONG: Da them {len(new_shops)} cua hang moi vao Google Sheets")
                return len(new_shops)
            else:
                print("[GHI SHEET] Khong co cua hang moi de them (tat ca da ton tai)")
                return 0
            
        except Exception as e:
            print(f"[GHI SHEET] LOI: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
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
    Lay instance GoogleSheetsConnector (Singleton pattern)
    """
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = GoogleSheetsConnector(credentials_path, credentials_json)
    return _connector_instance

def fetch_all_shops(spreadsheet_id: str = None, sheet_name: str = "Trang tính 1") -> List[Dict[str, Any]]:
    """
    Ham tien ich de lay tat ca du lieu cua hang
    
    Args:
        spreadsheet_id: ID cua Google Spreadsheet
        sheet_name: Ten sheet
    
    Returns:
        Danh sach cua hang
    """
    credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS', '').strip()
    connector = get_connector(credentials_json=credentials_json)
    
    if spreadsheet_id:
        return connector.get_shops_data(spreadsheet_id, sheet_name)
    else:
        return connector._get_sample_data()

def add_shop_to_sheet(spreadsheet_id: str, shop_data: Dict[str, Any], sheet_name: str = "Trang tính 1") -> bool:
    """
    Hàm tiện ích để thêm cửa hàng vào Google Sheet
    
    Args:
        spreadsheet_id: ID của Google Spreadsheet
        shop_data: Thông tin cửa hàng
        sheet_name: Tên sheet (mặc định: Sheet1)
    
    Returns:
        True nếu thành công, False nếu có lỗi
    """
    credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    connector = get_connector(credentials_json=credentials_json)
    
    if spreadsheet_id:
        return connector.add_shop(spreadsheet_id, shop_data, sheet_name)
    else:
        print("Khong co spreadsheet_id, khong the them cua hang")
        return False

def add_shops_to_sheet_batch(spreadsheet_id: str, shops: List[Dict[str, Any]], sheet_name: str = "Trang tính 1") -> int:
    """
    Hàm tiện ích để thêm nhiều cửa hàng vào Google Sheet
    
    Args:
        spreadsheet_id: ID của Google Spreadsheet
        shops: Danh sách cửa hàng
        sheet_name: Tên sheet (mặc định: Sheet1)
    
    Returns:
        Số lượng cửa hàng đã thêm thành công
    """
    credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    connector = get_connector(credentials_json=credentials_json)
    
    if spreadsheet_id:
        return connector.add_shops_batch(spreadsheet_id, shops, sheet_name)
    else:
        print("Khong co spreadsheet_id, khong the them cua hang")
        return 0