import time
from extractor import DataExtractor
from transformer import DataTransformer
from loader import DataLoader

def main():
    print("🚀 MEGAMART ETL PIPELINE - MONGODB TO SINGLE FACT TABLE")
    print("=" * 60)
    
    start_time = time.time()
    extractor = None
    loader = None
    
    try:
        # Initialize ETL components
        extractor = DataExtractor()
        transformer = DataTransformer()
        loader = DataLoader()
        
        # ETL Process
        print("\nStarting ETL Process...")
        
        # Extract phase from MongoDB
        extracted_data = extractor.extract_all()
        
        # Transform phase  
        transformed_data = transformer.transform_all(extracted_data)
        
        # Load phase to MySQL Data Warehouse
        loader.load_all(transformed_data)
        
        # Summary
        elapsed_time = time.time() - start_time
        print("\n" + "="*60)
        print("🎉 ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"⏱️  Total Time: {elapsed_time:.2f} seconds")
        print(f"📊 Records Processed:")
        print(f"   Customers: {len(transformed_data.get('dim_customer', []))}")
        print(f"   Products: {len(transformed_data.get('dim_product', []))}")
        print(f"   Stores: {len(transformed_data.get('dim_store', []))}")
        print(f"   Employees: {len(transformed_data.get('dim_employee', []))}")
        print(f"   Promotions: {len(transformed_data.get('dim_promotion', []))}")
        print(f"   Suppliers: {len(transformed_data.get('dim_supplier', []))}")
        print(f"   Fact Sales: {len(transformed_data.get('fact_sales', []))}")
        
    except Exception as e:
        print(f"\n❌ ETL Pipeline Failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up resources
        try:
            if extractor:
                extractor.close_connections()
            if loader:
                loader.close()
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")

if __name__ == "__main__":
    main()