import pandas as pd
import requests
from pymongo import MongoClient
from urllib.parse import quote_plus
import os
from config.settings import MONGODB_CONFIG, API_CONFIG, FILE_PATHS

class DataExtractor:
    def __init__(self):
        self.setup_mongodb()
    
    def setup_mongodb(self):
        """Setup MongoDB connections"""
        try:
            username = MONGODB_CONFIG['username']
            password = MONGODB_CONFIG['password']
            encoded_password = quote_plus(password)
            cluster = MONGODB_CONFIG['cluster']
            
            connection_string = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority"
            client = MongoClient(connection_string)
            
            self.mongo_oltp1 = client[MONGODB_CONFIG['databases']['oltp1']]
            self.mongo_oltp2 = client[MONGODB_CONFIG['databases']['oltp2']]
            
            print("✅ Connected to MongoDB")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    def extract_mongodb_data(self):
        """Extract data from MongoDB"""
        print("📥 Extracting MongoDB data...")
        
        data = {}
        
        # OLTP System 1 - Sales
        data['sales_transactions'] = list(self.mongo_oltp1.sales_transactions.find())
        data['sales_items'] = list(self.mongo_oltp1.sales_items.find())
        data['inventory_movements'] = list(self.mongo_oltp1.inventory_movements.find())
        
        # OLTP System 2 - Customer
        data['customers'] = list(self.mongo_oltp2.customers.find())
        data['suppliers'] = list(self.mongo_oltp2.suppliers.find())
        data['store_locations'] = list(self.mongo_oltp2.store_locations.find())
        
        # Remove MongoDB _id fields
        for key in data:
            for item in data[key]:
                item.pop('_id', None)
        
        print(f"✅ MongoDB: {len(data['sales_transactions'])} transactions, {len(data['customers'])} customers")
        return data
    
    def extract_api_data(self):
        """Extract data from API"""
        print("🌐 Extracting API data...")
        
        try:
            url = f"{API_CONFIG['base_url']}{API_CONFIG['endpoints']['competitor_pricing']}"
            response = requests.get(f"{url}?limit=1000")
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                print(f"✅ API: {len(data)} competitor records")
                return data
            else:
                print(f"❌ API request failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ API extraction failed: {e}")
            return []
    
    def extract_flat_files(self, folder_path="flat_files"):
        """Extract all CSV files from a folder"""
        print(f"📁 Extracting CSV files from folder: {folder_path}...")
        
        data = {}
        
        if not os.path.exists(folder_path):
            print(f"❌ Folder '{folder_path}' does not exist")
            return data
        
        # Loop through all CSV files in the folder
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(folder_path, file_name)
                df = pd.read_csv(file_path)
                key = file_name.replace(".csv", "")  # e.g., promotions.csv -> promotions
                data[key] = df.to_dict('records')
                print(f"✅ {key}: {len(data[key])} records")
        
        if not data:
            print("⚠️ No CSV files found in the folder.")
        
        return data
    
    def extract_all(self):
        """Extract data from all sources"""
        print("\n" + "="*50)
        print("📥 EXTRACTION PHASE")
        print("="*50)
        
        mongo_data = self.extract_mongodb_data()
        api_data = self.extract_api_data()
        file_data = self.extract_flat_files()
        
        # Combine all data
        extracted_data = {
            **mongo_data,
            'competitor_data': api_data,
            **file_data
        }
        
        return extracted_data