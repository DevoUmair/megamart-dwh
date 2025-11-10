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
            print(f"   Host: {self.host}")
            print(f"   User: {self.user}")
            print(f"   Database: {self.database}")
            
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print("✅ Connected to MySQL Server")
            
            # Create database if not exists
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.cursor.execute(f"USE {self.database}")
            print(f"✅ Using database: {self.database}")
            
        except Error as e:
            print(f"❌ MySQL Connection failed: {e}")
            raise
    
    def create_star_schema(self):
        """Create Star Schema tables in MySQL"""
        print("🔄 Creating Star Schema Tables in MySQL...")
        
        # Drop tables if they exist (for clean setup)
        drop_queries = [
            "DROP TABLE IF EXISTS fact_sales",
            "DROP TABLE IF EXISTS fact_inventory",
            "DROP TABLE IF EXISTS fact_promotions",
            "DROP TABLE IF EXISTS dim_competitor",
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
        
        # Dimension Tables (exactly as in original working code)
        dimension_tables = [
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
            """
            CREATE TABLE dim_competitor (
                competitor_key INT AUTO_INCREMENT PRIMARY KEY,
                competitor_id VARCHAR(20) NOT NULL,
                competitor_name VARCHAR(50),
                product_category VARCHAR(50),
                scrape_date DATE,
                overall_price_index DECIMAL(5,2),
                UNIQUE KEY unique_competitor (competitor_id, scrape_date, product_category)
            )
            """
        ]
        
        # Fact Tables (exactly as in original working code)
        fact_tables = [
            """
            CREATE TABLE fact_sales (
                sales_key INT AUTO_INCREMENT PRIMARY KEY,
                date_key INT NOT NULL,
                customer_key INT,
                product_key INT NOT NULL,
                store_key INT NOT NULL,
                transaction_id VARCHAR(20) NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                discount_amount DECIMAL(10,2) NOT NULL,
                line_total DECIMAL(10,2) NOT NULL,
                tax_amount DECIMAL(10,2) NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                payment_method VARCHAR(20),
                category VARCHAR(50),
                FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
                FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
                FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
                FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
            )
            """,
            """
            CREATE TABLE fact_inventory (
                inventory_key INT AUTO_INCREMENT PRIMARY KEY,
                date_key INT NOT NULL,
                product_key INT NOT NULL,
                store_key INT NOT NULL,
                supplier_key INT,
                movement_id VARCHAR(20) NOT NULL,
                movement_type VARCHAR(20) NOT NULL,
                quantity INT NOT NULL,
                unit_cost DECIMAL(10,2) NOT NULL,
                reason VARCHAR(50),
                FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
                FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
                FOREIGN KEY (store_key) REFERENCES dim_store(store_key),
                FOREIGN KEY (supplier_key) REFERENCES dim_supplier(supplier_key)
            )
            """,
            """
            CREATE TABLE fact_promotions (
                promotion_key INT AUTO_INCREMENT PRIMARY KEY,
                date_key INT NOT NULL,
                promo_id VARCHAR(20) NOT NULL,
                promo_name VARCHAR(100),
                product_category VARCHAR(50),
                discount_pct DECIMAL(5,2),
                budget DECIMAL(10,2),
                actual_spend DECIMAL(10,2),
                status VARCHAR(20),
                FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
            )
            """
        ]
        
        # Create all tables
        for table_sql in dimension_tables + fact_tables:
            try:
                self.cursor.execute(table_sql)
                table_name = table_sql.split('(')[0].split()[-1]
                print(f"✅ Created table: {table_name}")
            except Error as e:
                print(f"❌ Error creating table: {e}")
        
        self.connection.commit()
        print("✅ Star Schema tables created successfully in MySQL")
    
    def create_indexes(self):
        """Create performance indexes for faster queries"""
        print("🔄 Creating performance indexes...")
        
        indexes = [
            "CREATE INDEX idx_fact_sales_date ON fact_sales(date_key)",
            "CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key)",
            "CREATE INDEX idx_fact_sales_product ON fact_sales(product_key)",
            "CREATE INDEX idx_fact_sales_store ON fact_sales(store_key)",
            "CREATE INDEX idx_fact_sales_transaction ON fact_sales(transaction_id)",
            
            "CREATE INDEX idx_fact_inventory_date ON fact_inventory(date_key)",
            "CREATE INDEX idx_fact_inventory_product ON fact_inventory(product_key)",
            "CREATE INDEX idx_fact_inventory_store ON fact_inventory(store_key)",
            
            "CREATE INDEX idx_fact_promotions_date ON fact_promotions(date_key)",
            
            "CREATE INDEX idx_dim_customer_id ON dim_customer(customer_id)",
            "CREATE INDEX idx_dim_customer_tier ON dim_customer(loyalty_tier)",
            
            "CREATE INDEX idx_dim_product_id ON dim_product(product_id)",
            "CREATE INDEX idx_dim_product_category ON dim_product(category)",
            
            "CREATE INDEX idx_dim_store_id ON dim_store(store_id)",
            "CREATE INDEX idx_dim_store_city ON dim_store(city)",
            
            "CREATE INDEX idx_dim_supplier_id ON dim_supplier(supplier_id)",
            "CREATE INDEX idx_dim_supplier_category ON dim_supplier(category)",
            
            "CREATE INDEX idx_dim_competitor_date ON dim_competitor(scrape_date)",
            "CREATE INDEX idx_dim_competitor_category ON dim_competitor(product_category)"
        ]
        
        for index_sql in indexes:
            try:
                self.cursor.execute(index_sql)
            except Error as e:
                print(f"Note: {e}")
        
        self.connection.commit()
        print("✅ Performance indexes created")
    
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
                    False  # Simplified holiday logic
                ))
                records_inserted += 1
            except Error as e:
                print(f"Error inserting date {current_date.date()}: {e}")
            
            current_date += timedelta(days=1)
        
        self.connection.commit()
        print(f"✅ Populated {records_inserted} dates in dimension table")
    
    def verify_schema(self):
        """Verify the star schema creation"""
        print("\n🔍 Verifying Star Schema...")
        
        # Get table counts
        tables = [
            'dim_date', 'dim_customer', 'dim_product', 'dim_store', 
            'dim_supplier', 'dim_competitor', 'fact_sales', 'fact_inventory', 'fact_promotions'
        ]
        
        for table in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"   {table}: {count} rows")
            except Error as e:
                print(f"   {table}: Error - {e}")
    
    def generate_erd_script(self):
        """Generate SQL script for MySQL Workbench ERD"""
        erd_script = """
-- MegaMart Data Warehouse - Star Schema SQL Script
-- Generated for MySQL Workbench ERD

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

CREATE TABLE dim_competitor (
    competitor_key INT AUTO_INCREMENT PRIMARY KEY,
    competitor_id VARCHAR(20) NOT NULL,
    competitor_name VARCHAR(50),
    product_category VARCHAR(50),
    scrape_date DATE,
    overall_price_index DECIMAL(5,2),
    UNIQUE KEY unique_competitor (competitor_id, scrape_date, product_category)
);

-- Fact Tables

CREATE TABLE fact_sales (
    sales_key INT AUTO_INCREMENT PRIMARY KEY,
    date_key INT NOT NULL,
    customer_key INT,
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    transaction_id VARCHAR(20) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20),
    category VARCHAR(50),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
);

CREATE TABLE fact_inventory (
    inventory_key INT AUTO_INCREMENT PRIMARY KEY,
    date_key INT NOT NULL,
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    supplier_key INT,
    movement_id VARCHAR(20) NOT NULL,
    movement_type VARCHAR(20) NOT NULL,
    quantity INT NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    reason VARCHAR(50),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key),
    FOREIGN KEY (supplier_key) REFERENCES dim_supplier(supplier_key)
);

CREATE TABLE fact_promotions (
    promotion_key INT AUTO_INCREMENT PRIMARY KEY,
    date_key INT NOT NULL,
    promo_id VARCHAR(20) NOT NULL,
    promo_name VARCHAR(100),
    product_category VARCHAR(50),
    discount_pct DECIMAL(5,2),
    budget DECIMAL(10,2),
    actual_spend DECIMAL(10,2),
    status VARCHAR(20),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- Performance Indexes

CREATE INDEX idx_fact_sales_date ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_store ON fact_sales(store_key);

CREATE INDEX idx_fact_inventory_date ON fact_inventory(date_key);
CREATE INDEX idx_fact_inventory_product ON fact_inventory(product_key);
CREATE INDEX idx_fact_inventory_store ON fact_inventory(store_key);

CREATE INDEX idx_dim_customer_id ON dim_customer(customer_id);
CREATE INDEX idx_dim_product_id ON dim_product(product_id);
CREATE INDEX idx_dim_store_id ON dim_store(store_id);
"""
        
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        # Save to file
        with open('output/megamart_star_schema.sql', 'w') as f:
            f.write(erd_script)
        print("✅ ERD SQL script saved as 'output/megamart_star_schema.sql'")
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
        print("🔌 MySQL connection closed")