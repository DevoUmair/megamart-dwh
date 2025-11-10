import json
import os

class DataManager:
    def __init__(self):
        self.competitor_data = []
        # Change this path to match your actual file location
        self.data_file = "data/competitor_pricing.json"  # Changed from output/ to data/
        self.load_data()
    
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.competitor_data = json.load(f)
                print(f"✅ Loaded {len(self.competitor_data)} records from {self.data_file}")
            else:
                print(f"❌ File not found: {self.data_file}")
                print(f"📁 Current directory: {os.getcwd()}")
                print(f"📁 Files in current directory: {os.listdir('.')}")
                self.create_sample_data()
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.create_sample_data()
    
    def create_sample_data(self):
        self.competitor_data = [
            {
                "competitor_id": "COMP001",
                "competitor_name": "QuickMart",
                "scrape_date": "2024-01-15",
                "scrape_time": "10:00:00",
                "product_category": "dairy",
                "products_monitored": [
                    {
                        "product_name": "Whole Milk 1 Gallon",
                        "competitor_price": 3.49,
                        "our_price": 3.29,
                        "price_difference": -0.20,
                        "promotion_flag": True
                    }
                ],
                "overall_price_index": 1.06
            },
            {
                "competitor_id": "COMP002",
                "competitor_name": "SuperValue",
                "scrape_date": "2024-01-15",
                "scrape_time": "11:00:00",
                "product_category": "produce",
                "products_monitored": [
                    {
                        "product_name": "Organic Apples",
                        "competitor_price": 2.99,
                        "our_price": 2.79,
                        "price_difference": -0.20,
                        "promotion_flag": False
                    }
                ],
                "overall_price_index": 1.02
            }
        ]
        print("📝 Created sample data")
    
    def reload_data(self):
        self.load_data()
        return {"message": "Data reloaded", "records": len(self.competitor_data)}

data_manager = DataManager()