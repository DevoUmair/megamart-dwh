import json
import os
from typing import List, Dict, Any

class DataManager:
    def __init__(self):
        self.competitor_data = []
        # Try multiple possible file locations
        self.possible_paths = [
            "sources/competitor_pricing.json",  # From your data generation
            "data/competitor_pricing.json",     # Your current path
            "output/competitor_pricing.json",   # Original path
            "../sources/competitor_pricing.json"  # If running from different directory
        ]
        self.data_file = None
        self.load_data()
    
    def find_data_file(self):
        """Find the competitor pricing JSON file in possible locations"""
        for path in self.possible_paths:
            if os.path.exists(path):
                print(f"✅ Found data file at: {path}")
                return path
        return None
    
    def load_data(self):
        try:
            self.data_file = self.find_data_file()
            
            if self.data_file:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.competitor_data = json.load(f)
                print(f"✅ Loaded {len(self.competitor_data)} competitor pricing records from {self.data_file}")
            else:
                print("❌ Competitor pricing file not found in any expected location")
                print("📁 Current directory:", os.getcwd())
                print("📁 Available directories:")
                for item in os.listdir('.'):
                    if os.path.isdir(item):
                        print(f"   - {item}/")
                self.create_sample_data()
                
        except Exception as e:
            print(f"❌ Error loading competitor data: {e}")
            self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample competitor pricing data"""
        print("📝 Creating sample competitor pricing data...")
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
                    },
                    {
                        "product_name": "Dozen Eggs",
                        "competitor_price": 2.99,
                        "our_price": 2.79,
                        "price_difference": -0.20,
                        "promotion_flag": False
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
                        "product_name": "Organic Apples per lb",
                        "competitor_price": 2.99,
                        "our_price": 2.79,
                        "price_difference": -0.20,
                        "promotion_flag": False
                    },
                    {
                        "product_name": "Bananas per lb",
                        "competitor_price": 0.69,
                        "our_price": 0.59,
                        "price_difference": -0.10,
                        "promotion_flag": True
                    }
                ],
                "overall_price_index": 1.05
            },
            {
                "competitor_id": "COMP003",
                "competitor_name": "MarketPlus",
                "scrape_date": "2024-01-16",
                "scrape_time": "09:30:00",
                "product_category": "meat",
                "products_monitored": [
                    {
                        "product_name": "Chicken Breast per lb",
                        "competitor_price": 5.99,
                        "our_price": 5.49,
                        "price_difference": -0.50,
                        "promotion_flag": True
                    }
                ],
                "overall_price_index": 1.09
            }
        ]
        print(f"✅ Created {len(self.competitor_data)} sample competitor records")
    
    def reload_data(self):
        """Reload data from file"""
        self.load_data()
        return {
            "message": "Competitor data reloaded successfully",
            "records": len(self.competitor_data),
            "source_file": self.data_file or "sample_data"
        }
    
    def get_competitors(self) -> List[str]:
        """Get unique competitor names"""
        return sorted(list(set(item['competitor_name'] for item in self.competitor_data)))
    
    def get_categories(self) -> List[str]:
        """Get unique product categories"""
        return sorted(list(set(item['product_category'] for item in self.competitor_data)))
    
    def get_dates(self) -> List[str]:
        """Get unique scrape dates"""
        return sorted(list(set(item['scrape_date'] for item in self.competitor_data)))

# Global data manager instance
data_manager = DataManager()