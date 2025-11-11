from database.warehouse import MySQLDataWarehouse

def main():
    print("🚀 MegaMart Enhanced Data Warehouse Setup - 9-Table Schema")
    print("=" * 65)
    
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
        
        # Create enhanced 9-table schema
        dw.create_enhanced_star_schema()
        
        # Create indexes
        dw.create_enhanced_indexes()
        
        # Populate date dimension
        dw.populate_date_dimension()
        
        # Verify schema
        dw.verify_enhanced_schema()
        
        # Generate comprehensive ERD script
        dw.generate_comprehensive_erd_script()
        
        print("\n🎉 Enhanced 9-Table Data Warehouse Setup Completed!")
        print("📊 Single Fact Table with 8 Dimensions Ready for Analytics!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
    finally:
        dw.close()

if __name__ == "__main__":
    main()