import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import os

class MySQLDataWarehouse:
    def __init__(self, host="localhost", user="root", password="UMRlfr1$", database="megamart_warehouse", port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Connect to MySQL database"""
        try:
            print(f"🔗 Attempting to connect to MySQL...")
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print("✅ Connected to MySQL Server")
            
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.cursor.execute(f"USE {self.database}")
            print(f"✅ Using database: {self.database}")
            
        except Error as e:
            print(f"❌ MySQL Connection failed: {e}")
            raise
    
    def create_enhanced_star_schema(self):
        """Create Enhanced 9-Table Star Schema with One Fact Table"""
        print("🔄 Creating Enhanced 9-Table Star Schema...")
        
        # Drop tables if they exist
        drop_queries = [
            "DROP TABLE IF EXISTS fact_business_operations",
            "DROP TABLE IF EXISTS dim_promotion_details",
            "DROP TABLE IF EXISTS dim_inventory_movements",
            "DROP TABLE IF EXISTS dim_competitor_pricing",
            "DROP TABLE IF EXISTS dim_supplier",
            "DROP TABLE IF EXISTS dim_store",
            "DROP TABLE IF EXISTS dim_product",
            "DROP TABLE IF EXISTS dim_customer",
            "DROP TABLE IF EXISTS dim_date"
        ]
        
        for query in drop_queries:
            try:
                self.cursor.execute(query)
            except Error as e:
                print(f"Note: {e}")
        
        # Enhanced Dimension Tables (8 dimensions + 1 fact)
        dimension_tables = [
            # 1. Date Dimension (Same structure)
            """
            CREATE TABLE dim_date (
                date_key INT AUTO_INCREMENT PRIMARY KEY,
                full_date DATE NOT NULL,
                day INT NOT NULL,
                month INT NOT NULL,
                quarter INT NOT NULL,
                year INT NOT NULL,
                day_of_week INT NOT NULL,
                day_name VARCHAR(10) NOT NULL,
                month_name VARCHAR(10) NOT NULL,
                is_weekend BOOLEAN NOT NULL,
                is_holiday BOOLEAN NOT NULL,
                UNIQUE KEY unique_date (full_date)
            )
            """,
            
            # 2. Customer Dimension (Same structure)
            """
            CREATE TABLE dim_customer (
                customer_key INT AUTO_INCREMENT PRIMARY KEY,
                customer_id VARCHAR(20) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                email VARCHAR(100),
                phone VARCHAR(20),
                loyalty_tier VARCHAR(20),
                join_date DATE,
                preferred_store VARCHAR(20),
                total_spent DECIMAL(10,2),
                last_visit DATE,
                UNIQUE KEY unique_customer (customer_id)
            )
            """,
            
            # 3. Product Dimension (Same structure)
            """
            CREATE TABLE dim_product (
                product_key INT AUTO_INCREMENT PRIMARY KEY,
                product_id VARCHAR(20) NOT NULL,
                product_name VARCHAR(200),
                category VARCHAR(50),
                subcategory VARCHAR(50),
                base_price DECIMAL(10,2),
                cost_price DECIMAL(10,2),
                UNIQUE KEY unique_product (product_id)
            )
            """,
            
            # 4. Store Dimension (Same structure)
            """
            CREATE TABLE dim_store (
                store_key INT AUTO_INCREMENT PRIMARY KEY,
                store_id VARCHAR(20) NOT NULL,
                store_name VARCHAR(100),
                address VARCHAR(200),
                city VARCHAR(50),
                state VARCHAR(10),
                zip_code VARCHAR(10),
                size_sqft INT,
                manager_id VARCHAR(20),
                opening_date DATE,
                weekly_visitors INT,
                UNIQUE KEY unique_store (store_id)
            )
            """,
            
            # 5. Supplier Dimension (Same structure)
            """
            CREATE TABLE dim_supplier (
                supplier_key INT AUTO_INCREMENT PRIMARY KEY,
                supplier_id VARCHAR(20) NOT NULL,
                supplier_name VARCHAR(100),
                category VARCHAR(50),
                contact_email VARCHAR(100),
                phone VARCHAR(20),
                rating DECIMAL(3,2),
                lead_time_days INT,
                contract_start DATE,
                payment_terms VARCHAR(20),
                UNIQUE KEY unique_supplier (supplier_id)
            )
            """,
            
            # 6. Competitor Pricing Dimension (Enhanced from original)
            """
            CREATE TABLE dim_competitor_pricing (
                competitor_key INT AUTO_INCREMENT PRIMARY KEY,
                competitor_id VARCHAR(20) NOT NULL,
                competitor_name VARCHAR(50),
                product_category VARCHAR(50),
                scrape_date DATE,
                overall_price_index DECIMAL(5,2),
                base_price DECIMAL(8,2),
                promo_price DECIMAL(8,2),
                stock_availability VARCHAR(20),
                location VARCHAR(50),
                UNIQUE KEY unique_competitor (competitor_id, scrape_date, product_category)
            )
            """,
            
            # 7. Inventory Movements Dimension (Enhanced from fact_inventory)
            """
            CREATE TABLE dim_inventory_movements (
                movement_key INT AUTO_INCREMENT PRIMARY KEY,
                movement_id VARCHAR(20) NOT NULL,
                movement_type VARCHAR(20) NOT NULL,
                reason VARCHAR(50),
                unit_cost DECIMAL(10,2) NOT NULL,
                supplier_id VARCHAR(20),
                approval_status VARCHAR(20),
                movement_category VARCHAR(30),
                UNIQUE KEY unique_movement (movement_id)
            )
            """,
            
            # 8. Promotion Details Dimension (Enhanced from fact_promotions)
            """
            CREATE TABLE dim_promotion_details (
                promotion_key INT AUTO_INCREMENT PRIMARY KEY,
                promo_id VARCHAR(20) NOT NULL,
                promo_name VARCHAR(100),
                product_category VARCHAR(50),
                discount_pct DECIMAL(5,2),
                budget DECIMAL(10,2),
                actual_spend DECIMAL(10,2),
                status VARCHAR(20),
                start_date DATE,
                end_date DATE,
                target_audience VARCHAR(30),
                promo_type VARCHAR(20),
                UNIQUE KEY unique_promotion (promo_id)
            )
            """
        ]
        
        # Single Comprehensive Fact Table (Combining all original facts)
        fact_table = """
        CREATE TABLE fact_business_operations (
            -- Primary Key
            operation_key BIGINT AUTO_INCREMENT PRIMARY KEY,
            
            -- Dimension Foreign Keys (All 8 dimensions)
            date_key INT NOT NULL,
            customer_key INT,
            product_key INT NOT NULL,
            store_key INT NOT NULL,
            supplier_key INT,
            competitor_key INT,
            movement_key INT,
            promotion_key INT,
            
            -- Sales Metrics (from original fact_sales)
            transaction_id VARCHAR(20),
            quantity INT NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            discount_amount DECIMAL(10,2) NOT NULL,
            line_total DECIMAL(10,2) NOT NULL,
            tax_amount DECIMAL(10,2) NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            payment_method VARCHAR(20),
            category VARCHAR(50),
            
            -- Inventory Metrics (from original fact_inventory)
            movement_id VARCHAR(20),
            movement_type VARCHAR(20),
            unit_cost DECIMAL(10,2),
            reason VARCHAR(50),
            
            -- Promotion Metrics (from original fact_promotions)
            promo_id VARCHAR(20),
            promo_name VARCHAR(100),
            discount_pct DECIMAL(5,2),
            budget DECIMAL(10,2),
            actual_spend DECIMAL(10,2),
            status VARCHAR(20),
            
            -- Competitor Metrics (from original dim_competitor)
            competitor_id VARCHAR(20),
            overall_price_index DECIMAL(5,2),
            
            -- Business Context
            operation_type VARCHAR(30) NOT NULL,  -- 'SALE', 'INVENTORY_IN', 'INVENTORY_OUT', 'PROMOTION', 'COMPETITOR_ANALYSIS'
            
            -- Timestamps
            created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Foreign Key Constraints
            FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
            FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
            FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
            FOREIGN KEY (store_key) REFERENCES dim_store(store_key),
            FOREIGN KEY (supplier_key) REFERENCES dim_supplier(supplier_key),
            FOREIGN KEY (competitor_key) REFERENCES dim_competitor_pricing(competitor_key),
            FOREIGN KEY (movement_key) REFERENCES dim_inventory_movements(movement_key),
            FOREIGN KEY (promotion_key) REFERENCES dim_promotion_details(promotion_key)
        )
        """
        
        # Create all tables
        for table_sql in dimension_tables + [fact_table]:
            try:
                self.cursor.execute(table_sql)
                table_name = table_sql.split('(')[0].split()[-1]
                print(f"✅ Created table: {table_name}")
            except Error as e:
                print(f"❌ Error creating table: {e}")
        
        self.connection.commit()
        print("✅ Enhanced 9-Table Star Schema created successfully")
    
    def create_enhanced_indexes(self):
        """Create comprehensive performance indexes"""
        print("🔄 Creating enhanced performance indexes...")
        
        indexes = [
            # Fact table indexes
            "CREATE INDEX idx_fact_operations_date ON fact_business_operations(date_key)",
            "CREATE INDEX idx_fact_operations_customer ON fact_business_operations(customer_key)",
            "CREATE INDEX idx_fact_operations_product ON fact_business_operations(product_key)",
            "CREATE INDEX idx_fact_operations_store ON fact_business_operations(store_key)",
            "CREATE INDEX idx_fact_operations_type ON fact_business_operations(operation_type)",
            "CREATE INDEX idx_fact_operations_transaction ON fact_business_operations(transaction_id)",
            
            # Dimension indexes
            "CREATE INDEX idx_dim_customer_id ON dim_customer(customer_id)",
            "CREATE INDEX idx_dim_customer_tier ON dim_customer(loyalty_tier)",
            
            "CREATE INDEX idx_dim_product_id ON dim_product(product_id)",
            "CREATE INDEX idx_dim_product_category ON dim_product(category)",
            
            "CREATE INDEX idx_dim_store_id ON dim_store(store_id)",
            "CREATE INDEX idx_dim_store_city ON dim_store(city)",
            
            "CREATE INDEX idx_dim_supplier_id ON dim_supplier(supplier_id)",
            "CREATE INDEX idx_dim_supplier_category ON dim_supplier(category)",
            
            "CREATE INDEX idx_dim_competitor_date ON dim_competitor_pricing(scrape_date)",
            "CREATE INDEX idx_dim_competitor_category ON dim_competitor_pricing(product_category)",
            
            "CREATE INDEX idx_dim_movement_type ON dim_inventory_movements(movement_type)",
            "CREATE INDEX idx_dim_promotion_status ON dim_promotion_details(status)"
        ]
        
        for index_sql in indexes:
            try:
                self.cursor.execute(index_sql)
            except Error as e:
                print(f"Note: {e}")
        
        self.connection.commit()
        print("✅ Enhanced performance indexes created")
    
    def populate_date_dimension(self, start_date='2020-01-01', end_date='2024-12-31'):
        """Populate date dimension table"""
        print("📅 Populating Date Dimension...")
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        current_date = start
        
        records_inserted = 0
        while current_date <= end:
            try:
                self.cursor.execute("""
                    INSERT IGNORE INTO dim_date 
                    (full_date, day, month, quarter, year, day_of_week, day_name, month_name, is_weekend, is_holiday)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    current_date.date(),
                    current_date.day,
                    current_date.month,
                    (current_date.month - 1) // 3 + 1,
                    current_date.year,
                    current_date.weekday(),
                    current_date.strftime('%A'),
                    current_date.strftime('%B'),
                    current_date.weekday() >= 5,
                    False
                ))
                records_inserted += 1
            except Error as e:
                print(f"Error inserting date {current_date.date()}: {e}")
            
            current_date += timedelta(days=1)
        
        self.connection.commit()
        print(f"✅ Populated {records_inserted} dates in dimension table")
    
    def verify_enhanced_schema(self):
        """Verify the enhanced star schema creation"""
        print("\n🔍 Verifying Enhanced Star Schema...")
        
        tables = [
            'dim_date', 'dim_customer', 'dim_product', 'dim_store', 
            'dim_supplier', 'dim_competitor_pricing', 'dim_inventory_movements', 
            'dim_promotion_details', 'fact_business_operations'
        ]
        
        for table in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"   {table}: {count} rows")
            except Error as e:
                print(f"   {table}: Error - {e}")
    
    def generate_comprehensive_erd_script(self):
        """Generate SQL script for MySQL Workbench ERD"""
        erd_script = """
-- MegaMart Data Warehouse - Enhanced 9-Table Star Schema
-- Single Fact Table with Multiple Dimensions

-- Dimension Tables

CREATE TABLE dim_date (
    date_key INT AUTO_INCREMENT PRIMARY KEY,
    full_date DATE NOT NULL,
    day INT NOT NULL,
    month INT NOT NULL,
    quarter INT NOT NULL,
    year INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(10) NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL,
    UNIQUE KEY unique_date (full_date)
);

CREATE TABLE dim_customer (
    customer_key INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    loyalty_tier VARCHAR(20),
    join_date DATE,
    preferred_store VARCHAR(20),
    total_spent DECIMAL(10,2),
    last_visit DATE,
    UNIQUE KEY unique_customer (customer_id)
);

CREATE TABLE dim_product (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL,
    product_name VARCHAR(200),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    base_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    UNIQUE KEY unique_product (product_id)
);

CREATE TABLE dim_store (
    store_key INT AUTO_INCREMENT PRIMARY KEY,
    store_id VARCHAR(20) NOT NULL,
    store_name VARCHAR(100),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(10),
    zip_code VARCHAR(10),
    size_sqft INT,
    manager_id VARCHAR(20),
    opening_date DATE,
    weekly_visitors INT,
    UNIQUE KEY unique_store (store_id)
);

CREATE TABLE dim_supplier (
    supplier_key INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id VARCHAR(20) NOT NULL,
    supplier_name VARCHAR(100),
    category VARCHAR(50),
    contact_email VARCHAR(100),
    phone VARCHAR(20),
    rating DECIMAL(3,2),
    lead_time_days INT,
    contract_start DATE,
    payment_terms VARCHAR(20),
    UNIQUE KEY unique_supplier (supplier_id)
);

CREATE TABLE dim_competitor_pricing (
    competitor_key INT AUTO_INCREMENT PRIMARY KEY,
    competitor_id VARCHAR(20) NOT NULL,
    competitor_name VARCHAR(50),
    product_category VARCHAR(50),
    scrape_date DATE,
    overall_price_index DECIMAL(5,2),
    base_price DECIMAL(8,2),
    promo_price DECIMAL(8,2),
    stock_availability VARCHAR(20),
    location VARCHAR(50),
    UNIQUE KEY unique_competitor (competitor_id, scrape_date, product_category)
);

CREATE TABLE dim_inventory_movements (
    movement_key INT AUTO_INCREMENT PRIMARY KEY,
    movement_id VARCHAR(20) NOT NULL,
    movement_type VARCHAR(20) NOT NULL,
    reason VARCHAR(50),
    unit_cost DECIMAL(10,2) NOT NULL,
    supplier_id VARCHAR(20),
    approval_status VARCHAR(20),
    movement_category VARCHAR(30),
    UNIQUE KEY unique_movement (movement_id)
);

CREATE TABLE dim_promotion_details (
    promotion_key INT AUTO_INCREMENT PRIMARY KEY,
    promo_id VARCHAR(20) NOT NULL,
    promo_name VARCHAR(100),
    product_category VARCHAR(50),
    discount_pct DECIMAL(5,2),
    budget DECIMAL(10,2),
    actual_spend DECIMAL(10,2),
    status VARCHAR(20),
    start_date DATE,
    end_date DATE,
    target_audience VARCHAR(30),
    promo_type VARCHAR(20),
    UNIQUE KEY unique_promotion (promo_id)
);

-- Single Comprehensive Fact Table

CREATE TABLE fact_business_operations (
    operation_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    date_key INT NOT NULL,
    customer_key INT,
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    supplier_key INT,
    competitor_key INT,
    movement_key INT,
    promotion_key INT,
    transaction_id VARCHAR(20),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20),
    category VARCHAR(50),
    movement_id VARCHAR(20),
    movement_type VARCHAR(20),
    unit_cost DECIMAL(10,2),
    reason VARCHAR(50),
    promo_id VARCHAR(20),
    promo_name VARCHAR(100),
    discount_pct DECIMAL(5,2),
    budget DECIMAL(10,2),
    actual_spend DECIMAL(10,2),
    status VARCHAR(20),
    competitor_id VARCHAR(20),
    overall_price_index DECIMAL(5,2),
    operation_type VARCHAR(30) NOT NULL,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key),
    FOREIGN KEY (supplier_key) REFERENCES dim_supplier(supplier_key),
    FOREIGN KEY (competitor_key) REFERENCES dim_competitor_pricing(competitor_key),
    FOREIGN KEY (movement_key) REFERENCES dim_inventory_movements(movement_key),
    FOREIGN KEY (promotion_key) REFERENCES dim_promotion_details(promotion_key)
);

-- Performance Indexes

CREATE INDEX idx_fact_operations_date ON fact_business_operations(date_key);
CREATE INDEX idx_fact_operations_customer ON fact_business_operations(customer_key);
CREATE INDEX idx_fact_operations_product ON fact_business_operations(product_key);
CREATE INDEX idx_fact_operations_store ON fact_business_operations(store_key);
CREATE INDEX idx_fact_operations_type ON fact_business_operations(operation_type);

CREATE INDEX idx_dim_customer_id ON dim_customer(customer_id);
CREATE INDEX idx_dim_product_id ON dim_product(product_id);
CREATE INDEX idx_dim_store_id ON dim_store(store_id);
CREATE INDEX idx_dim_supplier_id ON dim_supplier(supplier_id);
"""
        
        os.makedirs('output', exist_ok=True)
        with open('output/megamart_enhanced_schema.sql', 'w') as f:
            f.write(erd_script)
        print("✅ Enhanced ERD SQL script saved as 'output/megamart_enhanced_schema.sql'")
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
        print("🔌 MySQL connection closed")