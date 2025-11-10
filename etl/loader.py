import mysql.connector
from mysql.connector import Error
from config.settings import MYSQL_CONFIG

class DataLoader:
    def __init__(self):
        self.conn = mysql.connector.connect(**MYSQL_CONFIG)
        self.cursor = self.conn.cursor()
    
    def load_all(self, transformed_data):
        """Load all transformed data"""
        print("\n" + "="*50)
        print("📤 LOADING PHASE")
        print("="*50)
        
        # Load dimensions
        self.load_dimension('dim_customer', transformed_data['customers'])
        self.load_dimension('dim_product', transformed_data['products'])
        self.load_dimension('dim_store', transformed_data['stores'])
        self.load_dimension('dim_supplier', transformed_data['suppliers'])
        self.load_dimension('dim_competitor', transformed_data['competitors'])
        
        # Load facts
        self.load_fact_sales(transformed_data['sales'])
        self.load_fact_inventory(transformed_data['inventory'])
        self.load_fact_promotions(transformed_data['promotions'])
        
        print("✅ Data loading completed")
    
    def load_dimension(self, table_name, data):
        """Load dimension table"""
        if not data:
            print(f"⚠️  No data for {table_name}")
            return
        
        id_column = table_name.replace('dim_', '') + '_id'
        columns = ', '.join(data[0].keys())
        placeholders = ', '.join(['%s'] * len(data[0].keys()))
        
        # Build update clause
        update_cols = [f"{col} = VALUES({col})" for col in data[0].keys() if col != id_column]
        update_clause = ', '.join(update_cols)
        
        sql = f"""
            INSERT INTO {table_name} ({columns})
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
    
    def load_fact_sales(self, sales_data):
        """Load sales fact table"""
        if not sales_data:
            print("⚠️  No sales data")
            return
        
        count = 0
        for sale in sales_data:
            try:
                date_key = self.get_key('dim_date', 'full_date', sale['sale_date'])
                customer_key = self.get_key('dim_customer', 'customer_id', sale.get('customer_id'))
                product_key = self.get_key('dim_product', 'product_id', sale['product_id'])
                store_key = self.get_key('dim_store', 'store_id', sale['store_id'])
                
                if all([date_key, product_key, store_key]):
                    sql = """
                        INSERT INTO fact_sales 
                        (date_key, customer_key, product_key, store_key, transaction_id, 
                         quantity, unit_price, discount_amount, line_total, tax_amount, 
                         total_amount, payment_method, category)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    self.cursor.execute(sql, (
                        date_key, customer_key, product_key, store_key, sale['transaction_id'],
                        sale['quantity'], sale['unit_price'], sale['discount_amount'], sale['line_total'],
                        sale['tax_amount'], sale['total_amount'], sale.get('payment_method'), sale.get('category')
                    ))
                    count += 1
                    
            except Error as e:
                continue
        
        self.conn.commit()
        print(f"✅ fact_sales: {count} records")
    
    def load_fact_inventory(self, inventory_data):
        """Load inventory fact table"""
        if not inventory_data:
            print("⚠️  No inventory data")
            return
        
        count = 0
        for movement in inventory_data:
            try:
                date_key = self.get_key('dim_date', 'full_date', movement['movement_date'])
                product_key = self.get_key('dim_product', 'product_id', movement['product_id'])
                store_key = self.get_key('dim_store', 'store_id', movement['store_id'])
                supplier_key = self.get_key('dim_supplier', 'supplier_id', movement.get('supplier_id'))
                
                if all([date_key, product_key, store_key]):
                    sql = """
                        INSERT INTO fact_inventory 
                        (date_key, product_key, store_key, supplier_key, movement_id, 
                         movement_type, quantity, unit_cost, reason)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    self.cursor.execute(sql, (
                        date_key, product_key, store_key, supplier_key, movement['movement_id'],
                        movement['movement_type'], movement['quantity'], movement['unit_cost'], movement.get('reason')
                    ))
                    count += 1
                    
            except Error as e:
                continue
        
        self.conn.commit()
        print(f"✅ fact_inventory: {count} records")
    
    def load_fact_promotions(self, promotions_data):
        """Load promotions fact table"""
        if not promotions_data:
            print("⚠️  No promotion data")
            return
        
        count = 0
        for promo in promotions_data:
            try:
                date_key = self.get_key('dim_date', 'full_date', promo['start_date'])
                
                if date_key:
                    sql = """
                        INSERT INTO fact_promotions 
                        (date_key, promo_id, promo_name, product_category, discount_pct, 
                         budget, actual_spend, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    self.cursor.execute(sql, (
                        date_key, promo['promo_id'], promo['promo_name'], promo['product_category'],
                        promo['discount_pct'], promo['budget'], promo['actual_spend'], promo['status']
                    ))
                    count += 1
                    
            except Error as e:
                continue
        
        self.conn.commit()
        print(f"✅ fact_promotions: {count} records")
    
    def get_key(self, table, id_column, value):
        """Get foreign key from dimension table"""
        if not value:
            return None
        
        try:
            self.cursor.execute(f"SELECT {table.replace('dim_', '')}_key FROM {table} WHERE {id_column} = %s", (value,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error:
            return None
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()
        print("🔌 Database connection closed")