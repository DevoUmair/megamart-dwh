import pandas as pd
import requests
from pymongo import MongoClient
from urllib.parse import quote_plus
import os
from config.settings import MONGODB_CONFIG, API_CONFIG, FILE_PATHS

class DataExtractor:
    def __init__(self):
        self.mongo_oltp1 = None
        self.mongo_oltp2 = None
        self.setup_mongodb()
    
    def setup_mongodb(self):
        """Setup MongoDB connections to OLTP databases"""
        try:
            print("🔗 Connecting to MongoDB OLTP databases...")
            
            username = MONGODB_CONFIG['username']
            password = MONGODB_CONFIG['password']
            encoded_password = quote_plus(password)
            cluster = MONGODB_CONFIG['cluster']
            
            connection_string = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority"
            client = MongoClient(connection_string)
            
            # Connect to OLTP databases
            self.mongo_oltp1 = client[MONGODB_CONFIG['databases']['oltp1']]
            self.mongo_oltp2 = client[MONGODB_CONFIG['databases']['oltp2']]
            
            print("✅ Connected to MongoDB:")
            print(f"   - {MONGODB_CONFIG['databases']['oltp1']}")
            print(f"   - {MONGODB_CONFIG['databases']['oltp2']}")
            
            # Test connections
            self.mongo_oltp1.list_collection_names()
            self.mongo_oltp2.list_collection_names()
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    def extract_mongodb_data(self):
        """Extract data from MongoDB OLTP databases"""
        print("📥 Extracting MongoDB OLTP data...")
        
        data = {}
        
        try:
            # OLTP System 1 - Sales data from MongoDB
            data['sales_transactions'] = list(self.mongo_oltp1.sales_transactions.find())
            data['sales_items'] = list(self.mongo_oltp1.sales_items.find())
            data['inventory_movements'] = list(self.mongo_oltp1.inventory_movements.find())
            
            # OLTP System 2 - Master data from MongoDB
            data['customers'] = list(self.mongo_oltp2.customers.find())
            data['products'] = list(self.mongo_oltp2.products.find())
            data['store_locations'] = list(self.mongo_oltp2.store_locations.find())
            data['suppliers'] = list(self.mongo_oltp2.suppliers.find())
            
            # Remove MongoDB _id fields
            for key in data:
                for item in data[key]:
                    if '_id' in item:
                        del item['_id']
            
            print(f"✅ MongoDB Extraction Summary:")
            print(f"   - Sales Transactions: {len(data['sales_transactions'])}")
            print(f"   - Sales Items: {len(data['sales_items'])}")
            print(f"   - Inventory Movements: {len(data['inventory_movements'])}")
            print(f"   - Customers: {len(data['customers'])}")
            print(f"   - Products: {len(data['products'])}")
            print(f"   - Stores: {len(data['store_locations'])}")
            print(f"   - Suppliers: {len(data['suppliers'])}")
            
        except Exception as e:
            print(f"❌ MongoDB extraction failed: {e}")
            raise
        
        return data
    
    def extract_api_data(self):
        """Extract data from Competitor Pricing API"""
        print("🌐 Extracting Competitor Pricing API data...")
        
        try:
            url = f"{API_CONFIG['base_url']}{API_CONFIG['endpoints']['competitor_pricing']}"
            response = requests.get(f"{url}?limit=1000")
            
            if response.status_code == 200:
                api_response = response.json()
                data = api_response.get('data', [])
                print(f"✅ API: {len(data)} competitor pricing records")
                return data
            else:
                print(f"❌ API request failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ API extraction failed: {e}")
            return []
    
    def extract_flat_files(self):
        """Extract data from flat files"""
        print(f"📁 Extracting flat files from {FILE_PATHS['flat_files_folder']}...")
        
        data = {}
        flat_files_path = FILE_PATHS['flat_files_folder']
        
        if not os.path.exists(flat_files_path):
            print(f"❌ Folder '{flat_files_path}' does not exist")
            return data
        
        try:
            # Extract promotions
            if os.path.exists(FILE_PATHS['promotions']):
                df = pd.read_csv(FILE_PATHS['promotions'])
                data['promotions'] = df.to_dict('records')
                print(f"✅ Promotions: {len(data['promotions'])} records")
            else:
                print("⚠️ Promotions file not found")
            
            # Extract employee schedules
            if os.path.exists(FILE_PATHS['employee_schedules']):
                df = pd.read_csv(FILE_PATHS['employee_schedules'])
                data['employee_schedules'] = df.to_dict('records')
                print(f"✅ Employee Schedules: {len(data['employee_schedules'])} records")
            else:
                print("⚠️ Employee schedules file not found")
                
        except Exception as e:
            print(f"❌ Flat file extraction failed: {e}")
        
        return data
    
    def extract_all(self):
        """Extract data from all sources"""
        print("\n" + "="*50)
        print("📥 EXTRACTION PHASE")
        print("="*50)
        
        mongodb_data = self.extract_mongodb_data()
        api_data = self.extract_api_data()
        file_data = self.extract_flat_files()
        
        # Combine all data
        extracted_data = {
            **mongodb_data,
            'competitor_pricing': api_data,
            **file_data
        }
        
        total_records = sum(len(data) for data in extracted_data.values())
        print(f"📊 Total records extracted: {total_records}")
        
        return extracted_data
    
    def close_connections(self):
        """Close MongoDB connections"""
        if self.mongo_oltp1:
            self.mongo_oltp1.client.close()
        if self.mongo_oltp2:
            self.mongo_oltp2.client.close()
        print("🔌 MongoDB connections closed")