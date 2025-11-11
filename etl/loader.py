# loader.py
import mysql.connector
from mysql.connector import Error
from config.settings import MYSQL_CONFIG

class DataLoader:
    def __init__(self):
        self.conn = mysql.connector.connect(**MYSQL_CONFIG)
        self.cursor = self.conn.cursor(buffered=True)  # Add buffered cursor
    
    def load_all(self, transformed_data):
        """Load all transformed data into single fact table schema"""
        print("\n" + "="*50)
        print("📤 LOADING PHASE")
        print("="*50)
        
        try:
            # Load all dimensions first
            self.load_dimension('dim_customer', transformed_data['customers'])
            self.load_dimension('dim_product', transformed_data['products'])
            self.load_dimension('dim_store', transformed_data['stores'])
            self.load_dimension('dim_supplier', transformed_data['suppliers'])
            self.load_dimension('dim_competitor_pricing', transformed_data['competitors'])
            self.load_dimension('dim_inventory_movements', transformed_data['inventory_movements'])
            self.load_dimension('dim_promotion_details', transformed_data['promotion_details'])
            
            # Load single fact table
            self.load_fact_business_operations(transformed_data['business_operations'])
            
            print("✅ Data loading completed")
            
        except Exception as e:
            print(f"❌ Loading failed: {e}")
            raise
        finally:
            # Clear any unread results
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass

    def load_dimension(self, table_name, data):
        """Load dimension table with upsert logic"""
        if not data:
            print(f"⚠️  No data for {table_name}")
            return
        
        try:
            # Get column names
            columns = list(data[0].keys())
            id_column = f"{table_name.replace('dim_', '')}_id"
            
            # Build SQL
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            
            # Build update clause
            update_cols = [f"{col} = VALUES({col})" for col in columns if col != id_column]
            update_clause = ', '.join(update_cols)
            
            sql = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {update_clause}
            """
            
            values = [tuple(item.values()) for item in data]
            
            self.cursor.executemany(sql, values)
            self.conn.commit()
            print(f"✅ {table_name}: {len(data)} records")
            
        except Error as e:
            print(f"❌ Error loading {table_name}: {e}")
            self.conn.rollback()
            # Clear unread results
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass

    def load_fact_business_operations(self, operations_data):
        """Load single fact table with all business operations"""
        if not operations_data:
            print("⚠️  No business operations data")
            return
        
        count = 0
        error_count = 0
        batch_size = 1000
        
        for i, operation in enumerate(operations_data):
            try:
                # Get foreign keys - handle None values properly
                date_key = self.get_date_key(operation['operation_date'])
                if not date_key:
                    error_count += 1
                    continue
                    
                customer_key = self.get_customer_key(operation.get('customer_id'))
                product_key = self.get_product_key(operation.get('product_id'))
                store_key = self.get_store_key(operation.get('store_id'))
                supplier_key = self.get_supplier_key(operation.get('supplier_id'))
                competitor_key = self.get_competitor_key(operation.get('competitor_id'))
                movement_key = self.get_movement_key(operation.get('movement_id'))
                promotion_key = self.get_promotion_key(operation.get('promo_id'))
                
                # Check required foreign keys
                if not product_key or not store_key:
                    error_count += 1
                    continue
                
                # Insert into fact table
                sql = """
                    INSERT INTO fact_business_operations (
                        date_key, customer_key, product_key, store_key, supplier_key,
                        competitor_key, movement_key, promotion_key,
                        transaction_id, quantity, unit_price, discount_amount,
                        line_total, tax_amount, total_amount, payment_method, category,
                        movement_id, movement_type, unit_cost, reason,
                        promo_id, promo_name, discount_pct, budget, actual_spend, status,
                        competitor_id, overall_price_index, operation_type
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    date_key, customer_key, product_key, store_key, supplier_key,
                    competitor_key, movement_key, promotion_key,
                    operation.get('transaction_id'),
                    operation.get('quantity', 0),
                    operation.get('unit_price', 0),
                    operation.get('discount_amount', 0),
                    operation.get('line_total', 0),
                    operation.get('tax_amount', 0),
                    operation.get('total_amount', 0),
                    operation.get('payment_method'),
                    operation.get('category'),
                    operation.get('movement_id'),
                    operation.get('movement_type'),
                    operation.get('unit_cost', 0),
                    operation.get('reason'),
                    operation.get('promo_id'),
                    operation.get('promo_name'),
                    operation.get('discount_pct', 0),
                    operation.get('budget', 0),
                    operation.get('actual_spend', 0),
                    operation.get('status'),
                    operation.get('competitor_id'),
                    operation.get('overall_price_index', 0),
                    operation.get('operation_type')
                )
                
                self.cursor.execute(sql, values)
                count += 1
                
                # Commit in batches to avoid memory issues
                if count % batch_size == 0:
                    self.conn.commit()
                    print(f"   ↳ Processed {count} operations...")
                
            except Error as e:
                error_count += 1
                if error_count <= 10:  # Only show first 10 errors
                    print(f"⚠️  Skipping operation {i}: {e}")
                elif error_count == 11:
                    print("⚠️  Additional errors suppressed...")
                continue
        
        # Final commit
        self.conn.commit()
        print(f"✅ fact_business_operations: {count} records loaded, {error_count} errors")

    # Foreign key resolution methods with improved error handling
    def get_date_key(self, date_value):
        """Get date key from dim_date"""
        if not date_value:
            return None
        try:
            self.cursor.execute("SELECT date_key FROM dim_date WHERE full_date = %s", (date_value,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"⚠️  Date key lookup failed for {date_value}: {e}")
            return None
        finally:
            # Clear any unread results
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass

    def get_customer_key(self, customer_id):
        """Get customer key from dim_customer"""
        if not customer_id:
            return None
        try:
            self.cursor.execute("SELECT customer_key FROM dim_customer WHERE customer_id = %s", (customer_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error:
            return None
        finally:
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass

    def get_product_key(self, product_id):
        """Get product key from dim_product"""
        if not product_id:
            return None
        try:
            self.cursor.execute("SELECT product_key FROM dim_product WHERE product_id = %s", (product_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error:
            return None
        finally:
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass

    def get_store_key(self, store_id):
        """Get store key from dim_store"""
        if not store_id:
            return None
        try:
            self.cursor.execute("SELECT store_key FROM dim_store WHERE store_id = %s", (store_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error:
            return None
        finally:
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass

    def get_supplier_key(self, supplier_id):
        """Get supplier key from dim_supplier"""
        if not supplier_id:
            return None
        try:
            self.cursor.execute("SELECT supplier_key FROM dim_supplier WHERE supplier_id = %s", (supplier_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error:
            return None
        finally:
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass

    def get_competitor_key(self, competitor_id):
        """Get competitor key from dim_competitor_pricing"""
        if not competitor_id:
            return None
        try:
            self.cursor.execute("SELECT competitor_key FROM dim_competitor_pricing WHERE competitor_id = %s", (competitor_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error:
            return None
        finally:
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass

    def get_movement_key(self, movement_id):
        """Get movement key from dim_inventory_movements"""
        if not movement_id:
            return None
        try:
            self.cursor.execute("SELECT movement_key FROM dim_inventory_movements WHERE movement_id = %s", (movement_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error:
            return None
        finally:
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass

    def get_promotion_key(self, promo_id):
        """Get promotion key from dim_promotion_details"""
        if not promo_id:
            return None
        try:
            self.cursor.execute("SELECT promotion_key FROM dim_promotion_details WHERE promo_id = %s", (promo_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Error:
            return None
        finally:
            try:
                while self.cursor.nextset():
                    pass
            except:
                pass

    def close(self):
        """Close database connection"""
        try:
            # Clear any remaining results
            while self.cursor.nextset():
                pass
        except:
            pass
        self.cursor.close()
        self.conn.close()
        print("🔌 Database connection closed")