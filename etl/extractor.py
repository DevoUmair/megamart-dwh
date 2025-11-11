import pandas as pd
import requests
from pymongo import MongoClient
from urllib.parse import quote_plus
import os
import time
from config.settings import MONGODB_CONFIG, API_CONFIG, FILE_PATHS

class DataExtractor:
    def __init__(self):
        self.mongo_oltp1 = None
        self.mongo_oltp2 = None
        self.setup_mongodb()
    
    def setup_mongodb(self):
        """Setup MongoDB connections to OLTP databases with proper timeout settings"""
        try:
            print("🔗 Connecting to MongoDB OLTP databases...")
            
            username = MONGODB_CONFIG['username']
            password = MONGODB_CONFIG['password']
            encoded_password = quote_plus(password)
            cluster = MONGODB_CONFIG['cluster']
            
            # Connection string with timeout settings (correct parameter names)
            connection_string = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority&socketTimeoutMS=30000&connectTimeoutMS=30000&serverSelectionTimeoutMS=30000"
            
            # Use only valid parameters
            client = MongoClient(
                connection_string,
                maxPoolSize=50
                # Removed socketKeepAlive as it's not a valid parameter
            )
            
            # Test connection with timeout
            client.admin.command('ping')
            
            # Connect to OLTP databases
            self.mongo_oltp1 = client[MONGODB_CONFIG['databases']['oltp1']]
            self.mongo_oltp2 = client[MONGODB_CONFIG['databases']['oltp2']]
            
            print("✅ Connected to MongoDB:")
            print(f"   - {MONGODB_CONFIG['databases']['oltp1']}")
            print(f"   - {MONGODB_CONFIG['databases']['oltp2']}")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    def extract_mongodb_collection_batch(self, collection, collection_name, batch_size=1000, max_docs=50000):
        """Extract data from MongoDB collection in batches to avoid timeouts"""
        print(f"   ↳ Extracting {collection_name}...")
        
        try:
            # Get total count first
            total_count = collection.count_documents({})
            print(f"     Total documents: {total_count:,}")
            
            # If collection is too large, limit the extraction
            if total_count > max_docs:
                print(f"     ⚠️  Collection too large, limiting to {max_docs:,} documents")
                cursor = collection.find().limit(max_docs)
            else:
                cursor = collection.find()
            
            data = []
            processed = 0
            
            for doc in cursor:
                # Remove MongoDB _id field
                if '_id' in doc:
                    del doc['_id']
                data.append(doc)
                processed += 1
                
                # Progress indicator
                if processed % batch_size == 0:
                    print(f"       Processed {processed:,}/{min(total_count, max_docs):,} documents...")
                
                # Safety break for very large collections
                if processed >= max_docs:
                    break
            
            print(f"     ✅ Extracted {len(data):,} {collection_name}")
            return data
            
        except Exception as e:
            print(f"     ❌ Error extracting {collection_name}: {e}")
            return []
    
    def extract_mongodb_data(self):
        """Extract data from MongoDB OLTP databases with batch processing"""
        print("📥 Extracting MongoDB OLTP data...")
        
        data = {}
        
        try:
            # OLTP System 1 - Sales data from MongoDB (with limits for large collections)
            print("   OLTP System 1 - Sales Data:")
            data['sales_transactions'] = self.extract_mongodb_collection_batch(
                self.mongo_oltp1.sales_transactions, 
                'sales_transactions',
                max_docs=10000  # Limit transactions to 10K
            )
            
            data['sales_items'] = self.extract_mongodb_collection_batch(
                self.mongo_oltp1.sales_items, 
                'sales_items',
                max_docs=15000  # Limit sales items to 30K
            )
            
            data['inventory_movements'] = self.extract_mongodb_collection_batch(
                self.mongo_oltp1.inventory_movements, 
                'inventory_movements',
                max_docs=5000  # Limit inventory movements to 5K
            )
            
            # OLTP System 2 - Master data from MongoDB (smaller collections, no limits needed)
            print("   OLTP System 2 - Master Data:")
            data['customers'] = self.extract_mongodb_collection_batch(
                self.mongo_oltp2.customers, 
                'customers'
            )
            
            data['products'] = self.extract_mongodb_collection_batch(
                self.mongo_oltp2.products, 
                'products'
            )
            
            data['store_locations'] = self.extract_mongodb_collection_batch(
                self.mongo_oltp2.store_locations, 
                'store_locations'
            )
            
            data['suppliers'] = self.extract_mongodb_collection_batch(
                self.mongo_oltp2.suppliers, 
                'suppliers'
            )
            
            print(f"✅ MongoDB Extraction Summary:")
            print(f"   - Sales Transactions: {len(data['sales_transactions']):,}")
            print(f"   - Sales Items: {len(data['sales_items']):,}")
            print(f"   - Inventory Movements: {len(data['inventory_movements']):,}")
            print(f"   - Customers: {len(data['customers']):,}")
            print(f"   - Products: {len(data['products']):,}")
            print(f"   - Stores: {len(data['store_locations']):,}")
            print(f"   - Suppliers: {len(data['suppliers']):,}")
            
        except Exception as e:
            print(f"❌ MongoDB extraction failed: {e}")
            raise
        
        return data
    
    def extract_api_data(self):
        """Extract data from Competitor Pricing API with error handling"""
        print("🌐 Extracting Competitor Pricing API data...")
        
        try:
            url = f"{API_CONFIG['base_url']}{API_CONFIG['endpoints']['competitor_pricing']}"
            
            # Add timeout to API request
            response = requests.get(f"{url}?limit=1000", timeout=30)
            
            if response.status_code == 200:
                api_response = response.json()
                data = api_response.get('data', [])
                print(f"✅ API: {len(data)} competitor pricing records")
                return data
            else:
                print(f"❌ API request failed: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            print("❌ API request timed out")
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
        """Extract data from all sources with error handling"""
        print("\n" + "="*50)
        print("📥 EXTRACTION PHASE")
        print("="*50)
        
        try:
            mongodb_data = self.extract_mongodb_data()
        except Exception as e:
            print(f"❌ MongoDB extraction failed, continuing with other sources: {e}")
            mongodb_data = {}
        
        try:
            api_data = self.extract_api_data()
        except Exception as e:
            print(f"❌ API extraction failed, continuing with other sources: {e}")
            api_data = []
        
        try:
            file_data = self.extract_flat_files()
        except Exception as e:
            print(f"❌ Flat file extraction failed, continuing with other sources: {e}")
            file_data = {}
        
        # Combine all data
        extracted_data = {
            **mongodb_data,
            'competitor_pricing': api_data,
            **file_data
        }
        
        total_records = sum(len(data) for data in extracted_data.values())
        print(f"📊 Total records extracted: {total_records:,}")
        
        return extracted_data
    
    def close_connections(self):
        """Close MongoDB connections"""
        try:
            if self.mongo_oltp1 is not None:
                self.mongo_oltp1.client.close()
            if self.mongo_oltp2 is not None:
                self.mongo_oltp2.client.close()
            print("🔌 MongoDB connections closed")
        except Exception as e:
            print(f"⚠️  Error closing MongoDB connections: {e}")