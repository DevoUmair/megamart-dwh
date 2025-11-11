from database.warehouse import MySQLDataWarehouse

def main():
    print("🚀 MegaMart Data Warehouse Setup - MySQL")
    print("=" * 50)
    
    # Database configuration
    db_config = {
        "host": "localhost",
        "user": "root", 
        "password": "UMRlfr1$",
        "port": 3306,
        "database": "megamart_warehouse"
    }
    
    print("📊 Using configuration:")
    print(f"   Host: {db_config['host']}")
    print(f"   User: {db_config['user']}")
    print(f"   Database: {db_config['database']}")
    
    # Initialize data warehouse
    dw = MySQLDataWarehouse(**db_config)
    
    try:
        # Connect to MySQL
        dw.connect()
        
        # Create star schema
        dw.create_star_schema()
        
        # Create indexes
        dw.create_indexes()
        
        # Populate date dimension
        dw.populate_date_dimension()
        
        # Populate time dimension
        dw.populate_time_dimension()
        
        # Verify schema
        dw.verify_schema()
        
        # Generate ERD script
        dw.generate_erd_script()
        
        print("\n🎉 MySQL Data Warehouse Setup Completed!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
    finally:
        dw.close()

if __name__ == "__main__":
    main()