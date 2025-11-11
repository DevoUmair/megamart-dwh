from datetime import datetime
import hashlib

class DataTransformer:
    def __init__(self):
        pass
    
    def transform_all(self, extracted_data):
        """Transform all data for single fact table schema"""
        print("\n" + "="*50)
        print("🔄 TRANSFORMATION PHASE")
        print("="*50)
        
        transformed_data = {}
        
        # Transform dimensions from MongoDB data
        transformed_data['dim_customer'] = self.transform_customers(extracted_data.get('customers', []))
        transformed_data['dim_product'] = self.transform_products(extracted_data.get('products', []))
        transformed_data['dim_store'] = self.transform_stores(extracted_data.get('store_locations', []))
        transformed_data['dim_employee'] = self.transform_employees(extracted_data.get('employee_schedules', []))
        transformed_data['dim_promotion'] = self.transform_promotions(extracted_data.get('promotions', []))
        transformed_data['dim_supplier'] = self.transform_suppliers(extracted_data.get('suppliers', []))
        
        # Transform fact data for single fact_sales table
        transformed_data['fact_sales'] = self.transform_fact_sales(
            sales_transactions=extracted_data.get('sales_transactions', []),
            sales_items=extracted_data.get('sales_items', []),
            inventory_movements=extracted_data.get('inventory_movements', []),
            competitor_pricing=extracted_data.get('competitor_pricing', []),
            employee_schedules=extracted_data.get('employee_schedules', [])
        )
        
        print("✅ Data transformation completed")
        return transformed_data
    
    def transform_customers(self, customers):
        """Transform customer dimension data from MongoDB"""
        transformed = []
        for customer in customers:
            transformed.append({
                'customer_id': customer.get('customer_id'),
                'first_name': customer.get('first_name', '').title(),
                'last_name': customer.get('last_name', '').title(),
                'full_name': f"{customer.get('first_name', '').title()} {customer.get('last_name', '').title()}",
                'email': customer.get('email', 'unknown@email.com').lower(),
                'phone': customer.get('phone', '555-0000'),
                'loyalty_tier': customer.get('loyalty_tier', 'bronze').lower(),
                'join_date': self.parse_date(customer.get('join_date')),
                'preferred_store': customer.get('preferred_store'),
                'city': customer.get('city', 'Unknown'),
                'state': customer.get('state', 'Unknown'),
                'customer_segment': self.determine_customer_segment(customer.get('loyalty_tier'), customer.get('total_spent', 0)),
                'is_active': True
            })
        print(f"✅ Transformed {len(transformed)} customers")
        return transformed
    
    def transform_products(self, products):
        """Transform product dimension data from MongoDB"""
        transformed = []
        for product in products:
            transformed.append({
                'product_id': product.get('product_id'),
                'product_name': product.get('product_name', 'Unknown Product'),
                'category': product.get('category', 'unknown').lower(),
                'subcategory': product.get('subcategory', 'general').lower(),
                'brand': product.get('brand', 'MegaBrand'),
                'base_price': float(product.get('base_price', 0)),
                'cost_price': float(product.get('cost_price', 0)),
                'supplier_id': product.get('supplier_id'),
                'is_perishable': self.is_perishable(product.get('category')),
                'is_active': True
            })
        print(f"✅ Transformed {len(transformed)} products")
        return transformed
    
    def transform_stores(self, stores):
        """Transform store dimension data from MongoDB"""
        transformed = []
        for store in stores:
            transformed.append({
                'store_id': store.get('store_id'),
                'store_name': store.get('store_name', 'Unknown Store'),
                'address': store.get('address', ''),
                'city': store.get('city', '').title(),
                'state': store.get('state', '').upper(),
                'zip_code': store.get('zip_code', ''),
                'size_sqft': int(store.get('size_sqft', 0)),
                'manager_id': store.get('manager_id'),
                'opening_date': self.parse_date(store.get('opening_date')),
                'weekly_visitors': int(store.get('weekly_visitors', 0)),
                'store_type': self.determine_store_type(store.get('size_sqft', 0)),
                'is_active': True
            })
        print(f"✅ Transformed {len(transformed)} stores")
        return transformed
    
    def transform_employees(self, employee_schedules):
        """Transform employee dimension data from flat files"""
        transformed = []
        employee_cache = {}
        
        for schedule in employee_schedules:
            employee_id = schedule.get('employee_id')
            if employee_id and employee_id not in employee_cache:
                employee_name = schedule.get('employee_name', 'Unknown Employee')
                name_parts = employee_name.split()
                first_name = name_parts[0] if name_parts else 'Unknown'
                last_name = name_parts[-1] if len(name_parts) > 1 else 'Employee'
                
                employee_cache[employee_id] = {
                    'employee_id': employee_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': employee_name,
                    'department': schedule.get('department', 'unknown'),
                    'position': schedule.get('position', 'staff'),
                    'hire_date': self.parse_date(schedule.get('shift_date')),  # Approximate hire date
                    'store_id': schedule.get('store_id'),
                    'salary_band': self.determine_salary_band(schedule.get('position', 'staff')),
                    'is_active': True
                }
        
        transformed = list(employee_cache.values())
        print(f"✅ Transformed {len(transformed)} employees")
        return transformed
    
    def transform_promotions(self, promotions):
        """Transform promotion dimension data from flat files"""
        transformed = []
        for promo in promotions:
            transformed.append({
                'promotion_id': promo.get('promo_id'),
                'promotion_name': promo.get('promo_name', 'Unknown Promotion'),
                'product_category': promo.get('product_category', 'unknown').lower(),
                'discount_pct': float(promo.get('discount_pct', 0)),
                'start_date': self.parse_date(promo.get('start_date')),
                'end_date': self.parse_date(promo.get('end_date')),
                'budget': float(promo.get('budget', 0)),
                'promotion_type': self.determine_promotion_type(promo.get('promo_name', '')),
                'status': promo.get('status', 'unknown').lower()
            })
        print(f"✅ Transformed {len(transformed)} promotions")
        return transformed
    
    def transform_suppliers(self, suppliers):
        """Transform supplier dimension data from MongoDB"""
        transformed = []
        for supplier in suppliers:
            transformed.append({
                'supplier_id': supplier.get('supplier_id'),
                'supplier_name': supplier.get('supplier_name', 'Unknown Supplier'),
                'category': supplier.get('category', 'unknown').lower(),
                'contact_email': supplier.get('contact_email', 'contact@unknown.com').lower(),
                'phone': supplier.get('phone', '555-0000'),
                'rating': float(supplier.get('rating', 4.0)),
                'lead_time_days': int(supplier.get('lead_time_days', 7)),
                'reliability_score': min(float(supplier.get('rating', 4.0)) / 5.0, 1.0),
                'is_active': True
            })
        print(f"✅ Transformed {len(transformed)} suppliers")
        return transformed
    
    def transform_fact_sales(self, sales_transactions, sales_items, inventory_movements, competitor_pricing, employee_schedules):
        """Transform all data into single fact_sales table"""
        print("🔄 Transforming data for single fact_sales table...")
        
        fact_records = []
        
        # Process sales transactions and items from MongoDB
        items_by_transaction = {}
        for item in sales_items:
            transaction_id = item.get('transaction_id')
            if transaction_id not in items_by_transaction:
                items_by_transaction[transaction_id] = []
            items_by_transaction[transaction_id].append(item)
        
        # Create inventory lookup from MongoDB
        inventory_lookup = {}
        for movement in inventory_movements:
            key = (movement.get('product_id'), movement.get('store_id'), movement.get('movement_date'))
            if key not in inventory_lookup:
                inventory_lookup[key] = []
            inventory_lookup[key].append(movement)
        
        # Create competitor pricing lookup from API
        competitor_lookup = {}
        for comp in competitor_pricing:
            key = (comp.get('product_category', ''), comp.get('scrape_date', ''))
            if key not in competitor_lookup:
                competitor_lookup[key] = []
            competitor_lookup[key].extend(comp.get('products_monitored', []))
        
        # Create employee schedule lookup from flat files
        employee_lookup = {}
        for schedule in employee_schedules:
            key = (schedule.get('store_id'), schedule.get('shift_date'))
            if key not in employee_lookup:
                employee_lookup[key] = []
            employee_lookup[key].append(schedule)
        
        processed_count = 0
        for transaction in sales_transactions:
            transaction_id = transaction.get('transaction_id')
            transaction_items = items_by_transaction.get(transaction_id, [])
            
            sale_datetime = self.parse_datetime(transaction.get('sale_datetime'))
            if not sale_datetime:
                continue
            
            date_key = int(sale_datetime.strftime('%Y%m%d'))
            time_key = sale_datetime.strftime('%H%M')
            
            for item in transaction_items:
                # Calculate profit
                cost_price = float(item.get('unit_price', 0)) * 0.6  # Estimate cost price
                profit = (float(item.get('unit_price', 0)) - cost_price - float(item.get('discount_amount', 0))) * int(item.get('quantity', 1))
                
                # Get inventory info
                inventory_info = self.get_inventory_info(
                    item.get('product_id'),
                    transaction.get('store_id'),
                    sale_datetime.date(),
                    inventory_lookup
                )
                
                # Get competitor pricing info
                competitor_info = self.get_competitor_info(
                    item.get('category', ''), 
                    sale_datetime.date(), 
                    competitor_lookup
                )
                
                # Get employee info
                employee_info = self.get_employee_info(
                    transaction.get('store_id'),
                    sale_datetime.date(),
                    employee_lookup
                )
                
                fact_record = {
                    # Foreign Keys
                    'date_key': date_key,
                    'time_key': time_key,
                    'customer_id': transaction.get('customer_id'),
                    'product_id': item.get('product_id'),
                    'store_id': transaction.get('store_id'),
                    'employee_id': employee_info.get('employee_id'),
                    'promotion_id': None,  # Would need promotion mapping
                    'supplier_id': None,   # Would need product-supplier mapping
                    
                    # Transaction details
                    'transaction_id': transaction_id,
                    'line_item_id': item.get('line_item_id'),
                    
                    # Sales measures
                    'quantity': int(item.get('quantity', 1)),
                    'unit_price': float(item.get('unit_price', 0)),
                    'discount_amount': float(item.get('discount_amount', 0)),
                    'line_total': float(item.get('line_total', 0)),
                    'tax_amount': float(transaction.get('tax_amount', 0)),
                    'total_amount': float(item.get('line_total', 0)),
                    'profit': round(profit, 2),
                    
                    # Additional measures from inventory
                    'stock_level': inventory_info.get('stock_level', 0),
                    'restock_quantity': inventory_info.get('restock_quantity', 0),
                    'waste_quantity': inventory_info.get('waste_quantity', 0),
                    
                    # Competitor measures
                    'competitor_price': competitor_info.get('competitor_price'),
                    'price_difference': competitor_info.get('price_difference'),
                    'price_competitiveness_score': competitor_info.get('competitiveness_score'),
                    
                    # Business context
                    'payment_method': transaction.get('payment_method'),
                    'category': item.get('category'),
                    'movement_type': 'sale',
                    'shift_type': employee_info.get('shift_type'),
                    'department': employee_info.get('department')
                }
                
                fact_records.append(fact_record)
                processed_count += 1
        
        print(f"✅ Transformed {processed_count} fact sales records")
        return fact_records
    
    # Helper methods
    def parse_date(self, date_str):
        """Parse date string from MongoDB data"""
        if not date_str:
            return None
        try:
            if isinstance(date_str, datetime):
                return date_str.date()
            # Handle different date formats from MongoDB
            if 'T' in str(date_str):
                return datetime.fromisoformat(str(date_str).replace('Z', '+00:00')).date()
            return datetime.strptime(str(date_str), '%Y-%m-%d').date()
        except:
            return None
    
    def parse_datetime(self, datetime_str):
        """Parse datetime string from MongoDB data"""
        if not datetime_str:
            return None
        try:
            if isinstance(datetime_str, datetime):
                return datetime_str
            # Handle different datetime formats from MongoDB
            if 'T' in str(datetime_str):
                return datetime.fromisoformat(str(datetime_str).replace('Z', '+00:00'))
            formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']
            for fmt in formats:
                try:
                    return datetime.strptime(str(datetime_str), fmt)
                except:
                    continue
            return None
        except:
            return None
    
    def determine_customer_segment(self, loyalty_tier, total_spent):
        """Determine customer segment based on loyalty and spending"""
        if loyalty_tier == 'platinum' or total_spent > 5000:
            return 'premium'
        elif loyalty_tier == 'gold' or total_spent > 2000:
            return 'frequent'
        elif loyalty_tier == 'silver' or total_spent > 500:
            return 'regular'
        else:
            return 'occasional'
    
    def is_perishable(self, category):
        """Determine if product is perishable"""
        perishable_categories = ['dairy', 'produce', 'meat', 'bakery', 'frozen']
        return category.lower() in perishable_categories
    
    def determine_store_type(self, size_sqft):
        """Determine store type based on size"""
        if size_sqft > 60000:
            return 'supercenter'
        elif size_sqft > 40000:
            return 'standard'
        else:
            return 'express'
    
    def determine_salary_band(self, position):
        """Determine salary band based on position"""
        if 'manager' in position.lower():
            return 'A'
        elif 'specialist' in position.lower():
            return 'B'
        else:
            return 'C'
    
    def determine_promotion_type(self, promo_name):
        """Determine promotion type based on name"""
        promo_name_lower = promo_name.lower()
        if 'seasonal' in promo_name_lower:
            return 'seasonal'
        elif 'holiday' in promo_name_lower:
            return 'holiday'
        elif 'clearance' in promo_name_lower:
            return 'clearance'
        else:
            return 'regular'
    
    def get_inventory_info(self, product_id, store_id, date, inventory_lookup):
        """Get inventory information for product and date"""
        key = (product_id, store_id, date.strftime('%Y-%m-%d'))
        movements = inventory_lookup.get(key, [])
        
        stock_level = 0
        restock_quantity = 0
        waste_quantity = 0
        
        for movement in movements:
            movement_type = movement.get('movement_type')
            quantity = int(movement.get('quantity', 0))
            
            if movement_type == 'restock':
                stock_level += quantity
                restock_quantity += quantity
            elif movement_type == 'sale':
                stock_level -= quantity
            elif movement_type == 'waste':
                stock_level -= quantity
                waste_quantity += quantity
        
        return {
            'stock_level': max(stock_level, 0),
            'restock_quantity': restock_quantity,
            'waste_quantity': waste_quantity
        }
    
    def get_competitor_info(self, category, date, competitor_lookup):
        """Get competitor pricing information"""
        key = (category, date.strftime('%Y-%m-%d'))
        competitor_products = competitor_lookup.get(key, [])
        
        if competitor_products:
            # Use first product as sample
            product = competitor_products[0]
            return {
                'competitor_price': product.get('competitor_price'),
                'price_difference': product.get('price_difference'),
                'competitiveness_score': 0.8 if product.get('price_difference', 0) < 0 else 0.5
            }
        
        return {'competitor_price': None, 'price_difference': None, 'competitiveness_score': None}
    
    def get_employee_info(self, store_id, date, employee_lookup):
        """Get employee information for shift"""
        key = (store_id, date.strftime('%Y-%m-%d'))
        schedules = employee_lookup.get(key, [])
        
        if schedules:
            # Use first schedule as sample
            schedule = schedules[0]
            return {
                'employee_id': schedule.get('employee_id'),
                'shift_type': schedule.get('shift_type'),
                'department': schedule.get('department')
            }
        
        return {'employee_id': None, 'shift_type': None, 'department': None}