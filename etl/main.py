# main.py
import time
from extractor import DataExtractor
from transformer import DataTransformer
from loader import DataLoader

def main():
    print("🚀 MEGAMART ETL PIPELINE - SINGLE FACT TABLE SCHEMA")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Initialize ETL components
        extractor = DataExtractor()
        transformer = DataTransformer()
        loader = DataLoader()
        
        # ETL Process
        print("\nStarting ETL Process...")
        
        # Extract
        extracted_data = extractor.extract_all()
        
        # Transform
        transformed_data = transformer.transform_all(extracted_data)
        
        # Load
        loader.load_all(transformed_data)
        
        # Summary
        elapsed_time = time.time() - start_time
        print("\n" + "="*60)
        print("🎉 ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"⏱️  Total Time: {elapsed_time:.2f} seconds")
        print(f"📊 Records Processed:")
        print(f"   Customers: {len(transformed_data['customers'])}")
        print(f"   Products: {len(transformed_data['products'])}")
        print(f"   Stores: {len(transformed_data['stores'])}")
        print(f"   Suppliers: {len(transformed_data['suppliers'])}")
        print(f"   Competitors: {len(transformed_data['competitors'])}")
        print(f"   Inventory Movements: {len(transformed_data['inventory_movements'])}")
        print(f"   Promotion Details: {len(transformed_data['promotion_details'])}")
        print(f"   Business Operations: {len(transformed_data['business_operations'])}")
        
    except Exception as e:
        print(f"\n❌ ETL Pipeline Failed: {e}")
    
    finally:
        try:
            loader.close()
        except:
            pass

if __name__ == "__main__":
    main()