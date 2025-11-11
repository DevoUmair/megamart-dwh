# transformer.py
from datetime import datetime
import re
import logging

class DataTransformer:
    def __init__(self):
        self.logger = logging.getLogger('DataTransformer')
        
    def transform_all(self, extracted_data):
        """Transform all data for single fact table schema"""
        print("\n" + "="*50)
        print("🔄 TRANSFORMATION PHASE")
        print("="*50)
        
        transformed_data = {}
        
        try:
            # Transform dimensions
            transformed_data['customers'] = self.transform_customers(extracted_data.get('customers', []))
            transformed_data['products'] = self.transform_products(extracted_data.get('sales_items', []))
            transformed_data['stores'] = self.transform_stores(extracted_data.get('store_locations', []))
            transformed_data['suppliers'] = self.transform_suppliers(extracted_data.get('suppliers', []))
            transformed_data['competitors'] = self.transform_competitors(extracted_data.get('competitor_data', []))
            transformed_data['inventory_movements'] = self.transform_inventory_movements(extracted_data.get('inventory_movements', []))
            transformed_data['promotion_details'] = self.transform_promotion_details(extracted_data.get('promotions', []))
            
            # Transform single fact table data
            transformed_data['business_operations'] = self.transform_business_operations(
                extracted_data.get('sales_transactions', []),
                extracted_data.get('sales_items', []),
                extracted_data.get('inventory_movements', []),
                extracted_data.get('promotions', []),
                extracted_data.get('competitor_data', [])
            )
            
            print("✅ Data transformation completed")
            return transformed_data
            
        except Exception as e:
            print(f"❌ Transformation failed: {e}")
            raise

    def clean_text(self, text):
        """Clean and standardize text data"""
        if not text:
            return "Unknown"
        return str(text).strip().title()

    def clean_email(self, email):
        """Clean email"""
        if not email:
            return "unknown@email.com"
        return str(email).strip().lower()

    def clean_phone(self, phone):
        """Clean phone number"""
        if not phone:
            return "555-0000"
        return str(phone).strip()

    def clean_numeric(self, value, default=0):
        """Clean numeric values"""
        try:
            if value is None or str(value).strip() == '':
                return default
            return float(value)
        except:
            return default

    def parse_date(self, date_str):
        """Parse date string"""
        if not date_str:
            return None
        try:
            if isinstance(date_str, datetime):
                return date_str.date()
            return datetime.strptime(str(date_str), '%Y-%m-%d').date()
        except:
            return None

    def parse_datetime(self, datetime_str):
        """Parse datetime string"""
        if not datetime_str:
            return None
        try:
            if isinstance(datetime_str, datetime):
                return datetime_str
            return datetime.strptime(str(datetime_str), '%Y-%m-%d %H:%M:%S')
        except:
            return None

    # Dimension Transformations
    def transform_customers(self, customers):
        """Transform customer data for dim_customer"""
        transformed = []
        for customer in customers:
            transformed.append({
                'customer_id': customer.get('customer_id', ''),
                'first_name': self.clean_text(customer.get('first_name')),
                'last_name': self.clean_text(customer.get('last_name')),
                'email': self.clean_email(customer.get('email')),
                'phone': self.clean_phone(customer.get('phone')),
                'loyalty_tier': customer.get('loyalty_tier', 'bronze'),
                'join_date': self.parse_date(customer.get('join_date')),
                'preferred_store': customer.get('preferred_store', ''),
                'total_spent': self.clean_numeric(customer.get('total_spent')),
                'last_visit': self.parse_date(customer.get('last_visit'))
            })
        print(f"✅ Transformed {len(transformed)} customers")
        return transformed

    def transform_products(self, sales_items):
        """Transform product data for dim_product"""
        products = {}
        for item in sales_items:
            product_id = item.get('product_id')
            if product_id and product_id not in products:
                base_price = self.clean_numeric(item.get('unit_price'), 10)
                products[product_id] = {
                    'product_id': product_id,
                    'product_name': self.clean_text(item.get('product_name', f"Product {product_id}")),
                    'category': self.clean_text(item.get('category', 'unknown')),
                    'subcategory': self.clean_text(item.get('subcategory', 'general')),
                    'base_price': base_price,
                    'cost_price': base_price * 0.6
                }
        result = list(products.values())
        print(f"✅ Transformed {len(result)} products")
        return result

    def transform_stores(self, stores):
        """Transform store data for dim_store"""
        transformed = []
        for store in stores:
            transformed.append({
                'store_id': store.get('store_id', ''),
                'store_name': self.clean_text(store.get('store_name', 'Unknown Store')),
                'address': self.clean_text(store.get('address', '')),
                'city': self.clean_text(store.get('city', '')),
                'state': self.clean_text(store.get('state', '')).upper(),
                'zip_code': str(store.get('zip_code', '')),
                'size_sqft': int(self.clean_numeric(store.get('size_sqft', 0))),
                'manager_id': store.get('manager_id', ''),
                'opening_date': self.parse_date(store.get('opening_date')),
                'weekly_visitors': int(self.clean_numeric(store.get('weekly_visitors', 0)))
            })
        print(f"✅ Transformed {len(transformed)} stores")
        return transformed

    def transform_suppliers(self, suppliers):
        """Transform supplier data for dim_supplier"""
        transformed = []
        for supplier in suppliers:
            transformed.append({
                'supplier_id': supplier.get('supplier_id', ''),
                'supplier_name': self.clean_text(supplier.get('supplier_name', 'Unknown Supplier')),
                'category': self.clean_text(supplier.get('category', 'unknown')),
                'contact_email': self.clean_email(supplier.get('contact_email')),
                'phone': self.clean_phone(supplier.get('phone')),
                'rating': self.clean_numeric(supplier.get('rating', 4.0)),
                'lead_time_days': int(self.clean_numeric(supplier.get('lead_time_days', 7))),
                'contract_start': self.parse_date(supplier.get('contract_start')),
                'payment_terms': supplier.get('payment_terms', 'net_30')
            })
        print(f"✅ Transformed {len(transformed)} suppliers")
        return transformed

    def transform_competitors(self, competitors):
        """Transform competitor data for dim_competitor_pricing"""
        transformed = []
        for competitor in competitors:
            transformed.append({
                'competitor_id': competitor.get('competitor_id', ''),
                'competitor_name': self.clean_text(competitor.get('competitor_name', 'Unknown Competitor')),
                'product_category': self.clean_text(competitor.get('product_category', 'general')),
                'scrape_date': self.parse_date(competitor.get('scrape_date')),
                'overall_price_index': self.clean_numeric(competitor.get('overall_price_index', 1.0)),
                'base_price': self.clean_numeric(competitor.get('base_price', 0)),
                'promo_price': self.clean_numeric(competitor.get('promo_price', 0)),
                'stock_availability': competitor.get('stock_availability', 'in_stock'),
                'location': self.clean_text(competitor.get('location', 'unknown'))
            })
        print(f"✅ Transformed {len(transformed)} competitors")
        return transformed

    def transform_inventory_movements(self, movements):
        """Transform inventory movements for dim_inventory_movements"""
        transformed = []
        for movement in movements:
            transformed.append({
                'movement_id': movement.get('movement_id', ''),
                'movement_type': self.clean_text(movement.get('movement_type', 'unknown')),
                'reason': self.clean_text(movement.get('reason', 'unknown')),
                'unit_cost': self.clean_numeric(movement.get('unit_cost', 0)),
                'supplier_id': movement.get('supplier_id', ''),
                'approval_status': movement.get('approval_status', 'approved'),
                'movement_category': self.derive_movement_category(movement.get('movement_type'))
            })
        print(f"✅ Transformed {len(transformed)} inventory movements")
        return transformed

    def transform_promotion_details(self, promotions):
        """Transform promotion data for dim_promotion_details"""
        transformed = []
        for promo in promotions:
            transformed.append({
                'promo_id': promo.get('promo_id', ''),
                'promo_name': self.clean_text(promo.get('promo_name', 'Unknown Promotion')),
                'product_category': self.clean_text(promo.get('product_category', 'general')),
                'discount_pct': self.clean_numeric(promo.get('discount_pct', 0)),
                'budget': self.clean_numeric(promo.get('budget', 0)),
                'actual_spend': self.clean_numeric(promo.get('actual_spend', 0)),
                'status': promo.get('status', 'completed'),
                'start_date': self.parse_date(promo.get('start_date')),
                'end_date': self.parse_date(promo.get('end_date')),
                'target_audience': promo.get('target_audience', 'all_customers'),
                'promo_type': self.derive_promo_type(promo.get('discount_pct'))
            })
        print(f"✅ Transformed {len(transformed)} promotion details")
        return transformed

    # Add this method to your existing transformer.py in the DataTransformer class

    def transform_business_operations(self, transactions, items, movements, promotions, competitors):
        """Transform all data into single fact table - fact_business_operations"""
        operations = []
        
        # Process sales operations
        sales_ops = self.transform_sales_operations(transactions, items)
        operations.extend(sales_ops)
        
        # Process inventory operations
        inventory_ops = self.transform_inventory_operations(movements)
        operations.extend(inventory_ops)
        
        # Process promotion operations
        promotion_ops = self.transform_promotion_operations(promotions)
        operations.extend(promotion_ops)
        
        # Process competitor operations
        competitor_ops = self.transform_competitor_operations(competitors)
        operations.extend(competitor_ops)
        
        # Filter out operations with missing required fields
        filtered_operations = []
        for op in operations:
            # Check for required fields based on operation type
            if op['operation_type'] == 'SALE':
                if op.get('product_id') and op.get('store_id') and op.get('operation_date'):
                    filtered_operations.append(op)
            elif op['operation_type'] == 'INVENTORY':
                if op.get('product_id') and op.get('store_id') and op.get('operation_date'):
                    filtered_operations.append(op)
            elif op['operation_type'] == 'PROMOTION':
                if op.get('operation_date'):
                    filtered_operations.append(op)
            elif op['operation_type'] == 'COMPETITOR_ANALYSIS':
                if op.get('operation_date'):
                    filtered_operations.append(op)
        
        print(f"✅ Transformed {len(filtered_operations)} valid business operations (filtered from {len(operations)})")
        return filtered_operations
    
    def transform_sales_operations(self, transactions, items):
        """Transform sales data for fact table"""
        operations = []
        items_by_transaction = {}
        
        # Group items by transaction
        for item in items:
            transaction_id = item.get('transaction_id')
            if transaction_id:
                if transaction_id not in items_by_transaction:
                    items_by_transaction[transaction_id] = []
                items_by_transaction[transaction_id].append(item)
        
        for transaction in transactions:
            transaction_id = transaction.get('transaction_id')
            transaction_items = items_by_transaction.get(transaction_id, [])
            
            for item in transaction_items:
                try:
                    sale_datetime = self.parse_datetime(transaction.get('sale_datetime'))
                    if not sale_datetime:
                        continue
                    
                    quantity = int(self.clean_numeric(item.get('quantity', 1)))
                    unit_price = self.clean_numeric(item.get('unit_price', 0))
                    discount_amount = self.clean_numeric(item.get('discount_amount', 0))
                    line_total = self.clean_numeric(item.get('line_total', quantity * unit_price))
                    
                    operation = {
                        'operation_type': 'SALE',
                        'transaction_id': transaction_id,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'discount_amount': discount_amount,
                        'line_total': line_total,
                        'tax_amount': self.clean_numeric(transaction.get('tax_amount', line_total * 0.08)),
                        'total_amount': line_total,
                        'payment_method': transaction.get('payment_method', 'unknown'),
                        'category': item.get('category', 'unknown'),
                        'unit_cost': unit_price * 0.6,
                        'customer_id': transaction.get('customer_id'),
                        'product_id': item.get('product_id'),
                        'store_id': transaction.get('store_id'),
                        'operation_date': sale_datetime.date()
                    }
                    
                    operations.append(operation)
                    
                except Exception as e:
                    print(f"⚠️ Error transforming sales operation: {e}")
                    continue
        
        return operations

    def transform_inventory_operations(self, movements):
        """Transform inventory data for fact table"""
        operations = []
        
        for movement in movements:
            try:
                movement_date = self.parse_date(movement.get('movement_date'))
                if not movement_date:
                    continue
                
                quantity = int(self.clean_numeric(movement.get('quantity', 0)))
                unit_cost = self.clean_numeric(movement.get('unit_cost', 0))
                
                operation = {
                    'operation_type': 'INVENTORY',
                    'movement_id': movement.get('movement_id'),
                    'movement_type': movement.get('movement_type'),
                    'quantity': abs(quantity),
                    'unit_price': unit_cost,
                    'discount_amount': 0,
                    'line_total': abs(quantity) * unit_cost,
                    'tax_amount': 0,
                    'total_amount': abs(quantity) * unit_cost,
                    'payment_method': None,
                    'category': None,
                    'unit_cost': unit_cost,
                    'reason': movement.get('reason', 'unknown'),
                    'product_id': movement.get('product_id'),
                    'store_id': movement.get('store_id'),
                    'supplier_id': movement.get('supplier_id'),
                    'operation_date': movement_date
                }
                
                operations.append(operation)
                
            except Exception as e:
                print(f"⚠️ Error transforming inventory operation: {e}")
                continue
        
        return operations

    def transform_promotion_operations(self, promotions):
        """Transform promotion data for fact table"""
        operations = []
        
        for promo in promotions:
            try:
                start_date = self.parse_date(promo.get('start_date'))
                if not start_date:
                    continue
                
                operation = {
                    'operation_type': 'PROMOTION',
                    'promo_id': promo.get('promo_id'),
                    'promo_name': promo.get('promo_name'),
                    'discount_pct': self.clean_numeric(promo.get('discount_pct', 0)),
                    'budget': self.clean_numeric(promo.get('budget', 0)),
                    'actual_spend': self.clean_numeric(promo.get('actual_spend', 0)),
                    'status': promo.get('status', 'completed'),
                    'quantity': 0,
                    'unit_price': 0,
                    'discount_amount': 0,
                    'line_total': 0,
                    'tax_amount': 0,
                    'total_amount': 0,
                    'payment_method': None,
                    'category': promo.get('product_category'),
                    'unit_cost': 0,
                    'reason': None,
                    'operation_date': start_date
                }
                
                operations.append(operation)
                
            except Exception as e:
                print(f"⚠️ Error transforming promotion operation: {e}")
                continue
        
        return operations

    def transform_competitor_operations(self, competitors):
        """Transform competitor data for fact table"""
        operations = []
        
        for competitor in competitors:
            try:
                scrape_date = self.parse_date(competitor.get('scrape_date'))
                if not scrape_date:
                    continue
                
                operation = {
                    'operation_type': 'COMPETITOR_ANALYSIS',
                    'competitor_id': competitor.get('competitor_id'),
                    'overall_price_index': self.clean_numeric(competitor.get('overall_price_index', 1.0)),
                    'quantity': 0,
                    'unit_price': 0,
                    'discount_amount': 0,
                    'line_total': 0,
                    'tax_amount': 0,
                    'total_amount': 0,
                    'payment_method': None,
                    'category': competitor.get('product_category'),
                    'unit_cost': 0,
                    'reason': None,
                    'operation_date': scrape_date
                }
                
                operations.append(operation)
                
            except Exception as e:
                print(f"⚠️ Error transforming competitor operation: {e}")
                continue
        
        return operations

    def derive_movement_category(self, movement_type):
        """Derive movement category"""
        movement_type = str(movement_type).lower()
        if 'sale' in movement_type:
            return 'sales'
        elif 'purchase' in movement_type:
            return 'purchases'
        elif 'return' in movement_type:
            return 'returns'
        elif 'transfer' in movement_type:
            return 'transfers'
        else:
            return 'adjustments'

    def derive_promo_type(self, discount_pct):
        """Derive promotion type"""
        discount_pct = float(discount_pct)
        if discount_pct >= 50:
            return 'clearance'
        elif discount_pct >= 25:
            return 'major_sale'
        elif discount_pct >= 10:
            return 'standard_sale'
        else:
            return 'minor_promotion'