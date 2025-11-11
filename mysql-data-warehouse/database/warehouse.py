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
        """Create Single Fact Table Star Schema in MySQL"""
        print("🔄 Creating Single Fact Table Star Schema in MySQL...")
        
        # Drop tables if they exist (for clean setup)
        drop_queries = [
            "DROP TABLE IF EXISTS fact_sales",
            "DROP TABLE IF EXISTS dim_time",
            "DROP TABLE IF EXISTS dim_promotion",
            "DROP TABLE IF EXISTS dim_employee",
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
        
        # Dimension Tables for Single Fact Table Schema
        dimension_tables = [
            """
            CREATE TABLE dim_date (
                date_key INT PRIMARY KEY,
                full_date DATE NOT NULL,
                year INT NOT NULL,
                quarter INT NOT NULL,
                month INT NOT NULL,
                month_name VARCHAR(10) NOT NULL,
                week INT NOT NULL,
                day INT NOT NULL,
                day_name VARCHAR(10) NOT NULL,
                day_of_year INT NOT NULL,
                day_of_week INT NOT NULL,
                is_weekend BOOLEAN NOT NULL,
                is_holiday BOOLEAN NOT NULL,
                fiscal_year INT NOT NULL,
                fiscal_quarter INT NOT NULL,
                UNIQUE KEY unique_date (full_date)
            )
            """,
            """
            CREATE TABLE dim_time (
                time_key VARCHAR(4) PRIMARY KEY,
                hour INT NOT NULL,
                minute INT NOT NULL,
                time_of_day VARCHAR(8) NOT NULL,
                day_period VARCHAR(10) NOT NULL,
                is_business_hour BOOLEAN NOT NULL
            )
            """,
            """
            CREATE TABLE dim_customer (
                customer_key INT AUTO_INCREMENT PRIMARY KEY,
                customer_id VARCHAR(20) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                full_name VARCHAR(100),
                email VARCHAR(100),
                phone VARCHAR(20),
                loyalty_tier VARCHAR(20),
                join_date DATE,
                preferred_store VARCHAR(20),
                city VARCHAR(50),
                state VARCHAR(10),
                customer_segment VARCHAR(20),
                is_active BOOLEAN NOT NULL,
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
                brand VARCHAR(50),
                base_price DECIMAL(10,2),
                cost_price DECIMAL(10,2),
                supplier_id VARCHAR(20),
                is_perishable BOOLEAN NOT NULL,
                is_active BOOLEAN NOT NULL,
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
                store_type VARCHAR(20),
                is_active BOOLEAN NOT NULL,
                UNIQUE KEY unique_store (store_id)
            )
            """,
            """
            CREATE TABLE dim_employee (
                employee_key INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(20) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                full_name VARCHAR(100),
                department VARCHAR(50),
                position VARCHAR(50),
                hire_date DATE,
                store_id VARCHAR(20),
                salary_band VARCHAR(10),
                is_active BOOLEAN NOT NULL,
                UNIQUE KEY unique_employee (employee_id)
            )
            """,
            """
            CREATE TABLE dim_promotion (
                promotion_key INT AUTO_INCREMENT PRIMARY KEY,
                promotion_id VARCHAR(20) NOT NULL,
                promotion_name VARCHAR(100),
                product_category VARCHAR(50),
                discount_pct DECIMAL(5,2),
                start_date DATE,
                end_date DATE,
                budget DECIMAL(10,2),
                promotion_type VARCHAR(20),
                status VARCHAR(20),
                UNIQUE KEY unique_promotion (promotion_id)
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
                reliability_score DECIMAL(3,2),
                is_active BOOLEAN NOT NULL,
                UNIQUE KEY unique_supplier (supplier_id)
            )
            """
        ]
        
        # Single Fact Table
        fact_tables = [
            """
            CREATE TABLE fact_sales (
                sales_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                date_key INT NOT NULL,
                time_key VARCHAR(4) NOT NULL,
                customer_key INT,
                product_key INT NOT NULL,
                store_key INT NOT NULL,
                employee_key INT,
                promotion_key INT,
                supplier_key INT,
                
                -- Transaction details
                transaction_id VARCHAR(20) NOT NULL,
                line_item_id VARCHAR(20) NOT NULL,
                
                -- Sales measures
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                discount_amount DECIMAL(10,2) NOT NULL,
                line_total DECIMAL(10,2) NOT NULL,
                tax_amount DECIMAL(10,2) NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                profit DECIMAL(10,2) NOT NULL,
                
                -- Additional measures from other sources
                stock_level INT,
                restock_quantity INT,
                waste_quantity INT,
                competitor_price DECIMAL(10,2),
                price_difference DECIMAL(10,2),
                price_competitiveness_score DECIMAL(5,2),
                
                -- Business context
                payment_method VARCHAR(20),
                category VARCHAR(50),
                movement_type VARCHAR(20),
                shift_type VARCHAR(20),
                department VARCHAR(50),
                
                FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
                FOREIGN KEY (time_key) REFERENCES dim_time(time_key),
                FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
                FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
                FOREIGN KEY (store_key) REFERENCES dim_store(store_key),
                FOREIGN KEY (employee_key) REFERENCES dim_employee(employee_key),
                FOREIGN KEY (promotion_key) REFERENCES dim_promotion(promotion_key),
                FOREIGN KEY (supplier_key) REFERENCES dim_supplier(supplier_key)
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
        print("✅ Single Fact Table Star Schema created successfully in MySQL")
    
    def create_indexes(self):
        """Create performance indexes for faster queries"""
        print("🔄 Creating performance indexes...")
        
        indexes = [
            # Fact table indexes
            "CREATE INDEX idx_fact_sales_date ON fact_sales(date_key)",
            "CREATE INDEX idx_fact_sales_time ON fact_sales(time_key)",
            "CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key)",
            "CREATE INDEX idx_fact_sales_product ON fact_sales(product_key)",
            "CREATE INDEX idx_fact_sales_store ON fact_sales(store_key)",
            "CREATE INDEX idx_fact_sales_employee ON fact_sales(employee_key)",
            "CREATE INDEX idx_fact_sales_promotion ON fact_sales(promotion_key)",
            "CREATE INDEX idx_fact_sales_transaction ON fact_sales(transaction_id)",
            "CREATE INDEX idx_fact_sales_category ON fact_sales(category)",
            
            # Dimension table indexes
            "CREATE INDEX idx_dim_customer_id ON dim_customer(customer_id)",
            "CREATE INDEX idx_dim_customer_tier ON dim_customer(loyalty_tier)",
            "CREATE INDEX idx_dim_customer_city ON dim_customer(city)",
            
            "CREATE INDEX idx_dim_product_id ON dim_product(product_id)",
            "CREATE INDEX idx_dim_product_category ON dim_product(category)",
            "CREATE INDEX idx_dim_product_supplier ON dim_product(supplier_id)",
            
            "CREATE INDEX idx_dim_store_id ON dim_store(store_id)",
            "CREATE INDEX idx_dim_store_city ON dim_store(city)",
            "CREATE INDEX idx_dim_store_type ON dim_store(store_type)",
            
            "CREATE INDEX idx_dim_employee_id ON dim_employee(employee_id)",
            "CREATE INDEX idx_dim_employee_dept ON dim_employee(department)",
            "CREATE INDEX idx_dim_employee_store ON dim_employee(store_id)",
            
            "CREATE INDEX idx_dim_promotion_id ON dim_promotion(promotion_id)",
            "CREATE INDEX idx_dim_promotion_category ON dim_promotion(product_category)",
            "CREATE INDEX idx_dim_promotion_status ON dim_promotion(status)",
            
            "CREATE INDEX idx_dim_supplier_id ON dim_supplier(supplier_id)",
            "CREATE INDEX idx_dim_supplier_category ON dim_supplier(category)"
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
                date_key = int(current_date.strftime('%Y%m%d'))
                self.cursor.execute("""
                    INSERT IGNORE INTO dim_date 
                    (date_key, full_date, year, quarter, month, month_name, week, day, 
                     day_name, day_of_year, day_of_week, is_weekend, is_holiday, 
                     fiscal_year, fiscal_quarter)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    date_key,
                    current_date.date(),
                    current_date.year,
                    (current_date.month - 1) // 3 + 1,
                    current_date.month,
                    current_date.strftime('%B'),
                    current_date.isocalendar()[1],
                    current_date.day,
                    current_date.strftime('%A'),
                    current_date.timetuple().tm_yday,
                    current_date.weekday() + 1,
                    current_date.weekday() >= 5,
                    False,  # Simplified holiday logic
                    current_date.year,
                    (current_date.month - 1) // 3 + 1
                ))
                records_inserted += 1
            except Error as e:
                print(f"Error inserting date {current_date.date()}: {e}")
            
            current_date += timedelta(days=1)
        
        self.connection.commit()
        print(f"✅ Populated {records_inserted} dates in dimension table")
    
    def populate_time_dimension(self):
        """Populate time dimension table"""
        print("⏰ Populating Time Dimension...")
        
        records_inserted = 0
        for hour in range(0, 24):
            for minute in range(0, 60, 15):  # 15-minute intervals
                time_key = f"{hour:02d}{minute:02d}"
                time_of_day = f"{hour:02d}:{minute:02d}"
                
                # Determine day period
                if hour < 6:
                    day_period = "Night"
                elif hour < 12:
                    day_period = "Morning"
                elif hour < 18:
                    day_period = "Afternoon"
                else:
                    day_period = "Evening"
                
                # Business hours: 6 AM to 10 PM
                is_business_hour = 6 <= hour <= 22
                
                try:
                    self.cursor.execute("""
                        INSERT IGNORE INTO dim_time 
                        (time_key, hour, minute, time_of_day, day_period, is_business_hour)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (time_key, hour, minute, time_of_day, day_period, is_business_hour))
                    records_inserted += 1
                except Error as e:
                    print(f"Error inserting time {time_key}: {e}")
        
        self.connection.commit()
        print(f"✅ Populated {records_inserted} time periods in dimension table")
    
    def verify_schema(self):
        """Verify the star schema creation"""
        print("\n🔍 Verifying Star Schema...")
        
        # Get table counts
        tables = [
            'dim_date', 'dim_time', 'dim_customer', 'dim_product', 'dim_store',
            'dim_employee', 'dim_promotion', 'dim_supplier', 'fact_sales'
        ]
        
        for table in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"   {table}: {count} rows")
            except Error as e:
                print(f"   {table}: Error - {e}")
        
        # Verify foreign key relationships
        print("\n🔗 Verifying relationships...")
        try:
            self.cursor.execute("""
                SELECT 
                    TABLE_NAME,
                    COLUMN_NAME,
                    CONSTRAINT_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
            """, (self.database,))
            
            relationships = self.cursor.fetchall()
            print(f"   Found {len(relationships)} foreign key relationships")
            
        except Error as e:
            print(f"   Error checking relationships: {e}")
    
    def generate_erd_script(self):
        """Generate SQL script for MySQL Workbench ERD"""
        erd_script = """
-- MegaMart Data Warehouse - Single Fact Table Star Schema SQL Script
-- Generated for MySQL Workbench ERD

-- Dimension Tables

CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    week INT NOT NULL,
    day INT NOT NULL,
    day_name VARCHAR(10) NOT NULL,
    day_of_year INT NOT NULL,
    day_of_week INT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL,
    fiscal_year INT NOT NULL,
    fiscal_quarter INT NOT NULL,
    UNIQUE KEY unique_date (full_date)
);

CREATE TABLE dim_time (
    time_key VARCHAR(4) PRIMARY KEY,
    hour INT NOT NULL,
    minute INT NOT NULL,
    time_of_day VARCHAR(8) NOT NULL,
    day_period VARCHAR(10) NOT NULL,
    is_business_hour BOOLEAN NOT NULL
);

CREATE TABLE dim_customer (
    customer_key INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    loyalty_tier VARCHAR(20),
    join_date DATE,
    preferred_store VARCHAR(20),
    city VARCHAR(50),
    state VARCHAR(10),
    customer_segment VARCHAR(20),
    is_active BOOLEAN NOT NULL,
    UNIQUE KEY unique_customer (customer_id)
);

CREATE TABLE dim_product (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL,
    product_name VARCHAR(200),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    brand VARCHAR(50),
    base_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    supplier_id VARCHAR(20),
    is_perishable BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
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
    store_type VARCHAR(20),
    is_active BOOLEAN NOT NULL,
    UNIQUE KEY unique_store (store_id)
);

CREATE TABLE dim_employee (
    employee_key INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR(100),
    department VARCHAR(50),
    position VARCHAR(50),
    hire_date DATE,
    store_id VARCHAR(20),
    salary_band VARCHAR(10),
    is_active BOOLEAN NOT NULL,
    UNIQUE KEY unique_employee (employee_id)
);

CREATE TABLE dim_promotion (
    promotion_key INT AUTO_INCREMENT PRIMARY KEY,
    promotion_id VARCHAR(20) NOT NULL,
    promotion_name VARCHAR(100),
    product_category VARCHAR(50),
    discount_pct DECIMAL(5,2),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(10,2),
    promotion_type VARCHAR(20),
    status VARCHAR(20),
    UNIQUE KEY unique_promotion (promotion_id)
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
    reliability_score DECIMAL(3,2),
    is_active BOOLEAN NOT NULL,
    UNIQUE KEY unique_supplier (supplier_id)
);

-- Single Fact Table

CREATE TABLE fact_sales (
    sales_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    date_key INT NOT NULL,
    time_key VARCHAR(4) NOT NULL,
    customer_key INT,
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    employee_key INT,
    promotion_key INT,
    supplier_key INT,
    
    -- Transaction details
    transaction_id VARCHAR(20) NOT NULL,
    line_item_id VARCHAR(20) NOT NULL,
    
    -- Sales measures
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    profit DECIMAL(10,2) NOT NULL,
    
    -- Additional measures from other sources
    stock_level INT,
    restock_quantity INT,
    waste_quantity INT,
    competitor_price DECIMAL(10,2),
    price_difference DECIMAL(10,2),
    price_competitiveness_score DECIMAL(5,2),
    
    -- Business context
    payment_method VARCHAR(20),
    category VARCHAR(50),
    movement_type VARCHAR(20),
    shift_type VARCHAR(20),
    department VARCHAR(50),
    
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key),
    FOREIGN KEY (employee_key) REFERENCES dim_employee(employee_key),
    FOREIGN KEY (promotion_key) REFERENCES dim_promotion(promotion_key),
    FOREIGN KEY (supplier_key) REFERENCES dim_supplier(supplier_key)
);

-- Performance Indexes

CREATE INDEX idx_fact_sales_date ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_time ON fact_sales(time_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_store ON fact_sales(store_key);
CREATE INDEX idx_fact_sales_employee ON fact_sales(employee_key);
CREATE INDEX idx_fact_sales_promotion ON fact_sales(promotion_key);
CREATE INDEX idx_fact_sales_transaction ON fact_sales(transaction_id);
CREATE INDEX idx_fact_sales_category ON fact_sales(category);

CREATE INDEX idx_dim_customer_id ON dim_customer(customer_id);
CREATE INDEX idx_dim_customer_tier ON dim_customer(loyalty_tier);
CREATE INDEX idx_dim_product_id ON dim_product(product_id);
CREATE INDEX idx_dim_product_category ON dim_product(category);
CREATE INDEX idx_dim_store_id ON dim_store(store_id);
CREATE INDEX idx_dim_store_city ON dim_store(city);
CREATE INDEX idx_dim_employee_id ON dim_employee(employee_id);
CREATE INDEX idx_dim_promotion_id ON dim_promotion(promotion_id);
CREATE INDEX idx_dim_supplier_id ON dim_supplier(supplier_id);
"""
        
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        # Save to file
        with open('output/megamart_single_fact_schema.sql', 'w') as f:
            f.write(erd_script)
        print("✅ ERD SQL script saved as 'output/megamart_single_fact_schema.sql'")
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
        print("🔌 MySQL connection closed")