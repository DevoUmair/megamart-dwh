
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
