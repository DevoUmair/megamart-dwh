import mysql.connector
from mysql.connector import Error
from config.settings import MYSQL_WAREHOUSE_CONFIG

class DataLoader:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(**MYSQL_WAREHOUSE_CONFIG)
            self.cursor = self.conn.cursor()
            print("✅ Connected to data warehouse")
        except Error as e:
            print(f"❌ Data warehouse connection failed: {e}")
            raise
    
    def load_all(self, transformed_data):
        """Load all transformed data into single fact table schema"""
        print("\n" + "="*50)
        print("📤 LOADING PHASE")
        print("="*50)
        
        try:
            # Disable foreign key checks for faster loading
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Load dimensions first
            self.load_dimensions(transformed_data)
            
            # Load single fact table
            self.load_fact_sales(transformed_data['fact_sales'])
            
            # Re-enable foreign key checks
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            print("✅ Data loading completed successfully")
            
        except Error as e:
            print(f"❌ Loading failed: {e}")
            self.conn.rollback()
            raise
    
    def load_dimensions(self, transformed_data):
        """Load all dimension tables"""
        print("📊 Loading dimension tables...")
        
        dimension_tables = [
            ('dim_customer', transformed_data.get('dim_customer', [])),
            ('dim_product', transformed_data.get('dim_product', [])),
            ('dim_store', transformed_data.get('dim_store', [])),
            ('dim_employee', transformed_data.get('dim_employee', [])),
            ('dim_promotion', transformed_data.get('dim_promotion', [])),
            ('dim_supplier', transformed_data.get('dim_supplier', []))
        ]
        
        for table_name, data in dimension_tables:
            if data:
                self.load_dimension_table(table_name, data)
            else:
                print(f"⚠️  No data for {table_name}")
    
    def load_dimension_table(self, table_name, data):
        """Load a single dimension table"""
        if not data:
            return
        
        # Get the ID column name
        id_column = table_name.replace('dim_', '') + '_id'
        columns = list(data[0].keys())
        
        # Create placeholders and update clause
        placeholders = ', '.join(['%s'] * len(columns))
        update_cols = [f"{col} = VALUES({col})" for col in columns if col != id_column]
        update_clause = ', '.join(update_cols)
        
        # Build the INSERT ... ON DUPLICATE KEY UPDATE query
        columns_str = ', '.join(columns)
        sql = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
        """
        
        values = [tuple(item.values()) for item in data]
        
        try:
            self.cursor.executemany(sql, values)
            self.conn.commit()
            print(f"✅ {table_name}: {len(data)} records")
        except Error as e:
            print(f"❌ Error loading {table_name}: {e}")
            self.conn.rollback()
            raise
    
    def load_fact_sales(self, fact_data):
        """Load the single fact_sales table"""
        if not fact_data:
            print("⚠️  No fact sales data to load")
            return
        
        print("📈 Loading fact_sales table...")
        
        # Define the columns for fact_sales - using foreign KEYS, not IDs
        columns = [
            'date_key', 'time_key', 'customer_key', 'product_key', 'store_key', 
            'employee_key', 'promotion_key', 'supplier_key', 'transaction_id', 
            'line_item_id', 'quantity', 'unit_price', 'discount_amount', 
            'line_total', 'tax_amount', 'total_amount', 'profit', 
            'stock_level', 'restock_quantity', 'waste_quantity', 
            'competitor_price', 'price_difference', 'price_competitiveness_score',
            'payment_method', 'category', 'movement_type', 'shift_type', 'department'
        ]
        
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        sql = f"INSERT INTO fact_sales ({columns_str}) VALUES ({placeholders})"
        
        # Transform data to match column order and resolve foreign keys
        processed_count = 0
        batch_size = 1000
        batch = []
        
        for fact in fact_data:
            try:
                # Resolve foreign keys - get the actual foreign key values from dimension tables
                customer_key = self.get_foreign_key('dim_customer', 'customer_id', fact.get('customer_id'))
                product_key = self.get_foreign_key('dim_product', 'product_id', fact.get('product_id'))
                store_key = self.get_foreign_key('dim_store', 'store_id', fact.get('store_id'))
                employee_key = self.get_foreign_key('dim_employee', 'employee_id', fact.get('employee_id'))
                promotion_key = self.get_foreign_key('dim_promotion', 'promotion_id', fact.get('promotion_id'))
                supplier_key = self.get_foreign_key('dim_supplier', 'supplier_id', fact.get('supplier_id'))
                
                # Prepare values in correct order - using foreign KEYS, not IDs
                values = (
                    fact.get('date_key'),
                    fact.get('time_key'),
                    customer_key,  # This should be the foreign key (int), not customer_id (string)
                    product_key,   # This should be the foreign key (int), not product_id (string)
                    store_key,     # This should be the foreign key (int), not store_id (string)
                    employee_key,  # This should be the foreign key (int), not employee_id (string)
                    promotion_key, # This should be the foreign key (int), not promotion_id (string)
                    supplier_key,  # This should be the foreign key (int), not supplier_id (string)
                    fact.get('transaction_id'),
                    fact.get('line_item_id'),
                    fact.get('quantity'),
                    fact.get('unit_price'),
                    fact.get('discount_amount'),
                    fact.get('line_total'),
                    fact.get('tax_amount'),
                    fact.get('total_amount'),
                    fact.get('profit'),
                    fact.get('stock_level'),
                    fact.get('restock_quantity'),
                    fact.get('waste_quantity'),
                    fact.get('competitor_price'),
                    fact.get('price_difference'),
                    fact.get('price_competitiveness_score'),
                    fact.get('payment_method'),
                    fact.get('category'),
                    fact.get('movement_type'),
                    fact.get('shift_type'),
                    fact.get('department')
                )
                
                # Only add to batch if we have the required foreign keys
                if all([fact.get('date_key'), product_key, store_key]):
                    batch.append(values)
                    processed_count += 1
                else:
                    continue
                
                # Insert in batches for performance
                if len(batch) >= batch_size:
                    self.cursor.executemany(sql, batch)
                    self.conn.commit()
                    batch = []
                    print(f"   ↳ Processed {processed_count} records...")
                    
            except Error as e:
                print(f"   ↳ Skipping record due to error: {e}")
                continue
        
        # Insert remaining records
        if batch:
            try:
                self.cursor.executemany(sql, batch)
                self.conn.commit()
            except Error as e:
                print(f"❌ Error inserting final batch: {e}")
                self.conn.rollback()
        
        print(f"✅ fact_sales: {processed_count} records loaded")
    
    def get_foreign_key(self, table_name, id_column, value):
        """Get foreign key value from dimension table"""
        if not value:
            return None
        
        try:
            key_column = table_name.replace('dim_', '') + '_key'
            query = f"SELECT {key_column} FROM {table_name} WHERE {id_column} = %s"
            self.cursor.execute(query, (value,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"   ↳ Error getting foreign key for {table_name}.{id_column}={value}: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()
        print("🔌 Data warehouse connection closed")