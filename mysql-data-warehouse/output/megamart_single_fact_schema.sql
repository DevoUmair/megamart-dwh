
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
