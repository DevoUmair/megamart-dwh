from datetime import datetime

class DataTransformer:
    def __init__(self):
        pass
    
    def transform_all(self, extracted_data):
        """Transform all data"""
        print("\n" + "="*50)
        print("🔄 TRANSFORMATION PHASE")
        print("="*50)
        
        transformed_data = {}
        
        # Transform dimensions
        transformed_data['customers'] = self.transform_customers(extracted_data.get('customers', []))
        transformed_data['products'] = self.transform_products(extracted_data.get('sales_items', []))
        transformed_data['stores'] = self.transform_stores(extracted_data.get('store_locations', []))
        transformed_data['suppliers'] = self.transform_suppliers(extracted_data.get('suppliers', []))
        transformed_data['competitors'] = self.transform_competitors(extracted_data.get('competitor_data', []))
        
        # Transform facts
        transformed_data['sales'] = self.transform_sales(
            extracted_data.get('sales_transactions', []),
            extracted_data.get('sales_items', [])
        )
        transformed_data['inventory'] = self.transform_inventory(extracted_data.get('inventory_movements', []))
        transformed_data['promotions'] = self.transform_promotions(extracted_data.get('promotions', []))
        
        print("✅ Data transformation completed")
        return transformed_data
    
    def transform_customers(self, customers):
        """Transform customer data"""
        transformed = []
        for customer in customers:
            transformed.append({
                'customer_id': customer.get('customer_id'),
                'first_name': customer.get('first_name', '').title(),
                'last_name': customer.get('last_name', '').title(),
                'email': customer.get('email', 'unknown@email.com'),
                'phone': customer.get('phone', '555-0000'),
                'loyalty_tier': customer.get('loyalty_tier', 'bronze'),
                'join_date': self.parse_date(customer.get('join_date')),
                'preferred_store': customer.get('preferred_store'),
                'total_spent': float(customer.get('total_spent', 0)),
                'last_visit': self.parse_date(customer.get('last_visit'))
            })
        return transformed
    
    def transform_products(self, sales_items):
        """Transform product data"""
        products = {}
        for item in sales_items:
            product_id = item.get('product_id')
            if product_id not in products:
                products[product_id] = {
                    'product_id': product_id,
                    'product_name': f"Product {product_id}",
                    'category': item.get('category', 'unknown'),
                    'subcategory': 'general',
                    'base_price': float(item.get('unit_price', 0)),
                    'cost_price': float(item.get('unit_price', 0)) * 0.6
                }
        return list(products.values())
    
    def transform_stores(self, stores):
        """Transform store data"""
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
                'weekly_visitors': int(store.get('weekly_visitors', 0))
            })
        return transformed
    
    def transform_suppliers(self, suppliers):
        """Transform supplier data"""
        transformed = []
        for supplier in suppliers:
            transformed.append({
                'supplier_id': supplier.get('supplier_id'),
                'supplier_name': supplier.get('supplier_name', 'Unknown Supplier'),
                'category': supplier.get('category', 'unknown'),
                'contact_email': supplier.get('contact_email', 'contact@unknown.com'),
                'phone': supplier.get('phone', '555-0000'),
                'rating': float(supplier.get('rating', 4.0)),
                'lead_time_days': int(supplier.get('lead_time_days', 7)),
                'contract_start': self.parse_date(supplier.get('contract_start')),
                'payment_terms': supplier.get('payment_terms', 'net_30')
            })
        return transformed
    
    def transform_competitors(self, competitors):
        """Transform competitor data"""
        transformed = []
        for competitor in competitors:
            transformed.append({
                'competitor_id': competitor.get('competitor_id'),
                'competitor_name': competitor.get('competitor_name'),
                'product_category': competitor.get('product_category'),
                'scrape_date': self.parse_date(competitor.get('scrape_date')),
                'overall_price_index': float(competitor.get('overall_price_index', 1.0))
            })
        return transformed
    
    def transform_sales(self, transactions, items):
        """Transform sales data"""
        transformed = []
        
        # Create items lookup
        items_by_transaction = {}
        for item in items:
            transaction_id = item.get('transaction_id')
            if transaction_id not in items_by_transaction:
                items_by_transaction[transaction_id] = []
            items_by_transaction[transaction_id].append(item)
        
        for transaction in transactions:
            transaction_id = transaction.get('transaction_id')
            transaction_items = items_by_transaction.get(transaction_id, [])
            
            for item in transaction_items:
                sale_datetime = self.parse_datetime(transaction.get('sale_datetime'))
                if sale_datetime:
                    transformed.append({
                        'transaction_id': transaction_id,
                        'sale_date': sale_datetime.date(),
                        'customer_id': transaction.get('customer_id'),
                        'product_id': item.get('product_id'),
                        'store_id': transaction.get('store_id'),
                        'quantity': int(item.get('quantity', 1)),
                        'unit_price': float(item.get('unit_price', 0)),
                        'discount_amount': float(item.get('discount_amount', 0)),
                        'line_total': float(item.get('line_total', 0)),
                        'tax_amount': float(transaction.get('tax_amount', 0)),
                        'total_amount': float(item.get('line_total', 0)),
                        'payment_method': transaction.get('payment_method'),
                        'category': item.get('category')
                    })
        
        return transformed
    
    def transform_inventory(self, movements):
        """Transform inventory data"""
        transformed = []
        for movement in movements:
            movement_date = self.parse_date(movement.get('movement_date'))
            if movement_date:
                transformed.append({
                    'movement_id': movement.get('movement_id'),
                    'movement_date': movement_date,
                    'product_id': movement.get('product_id'),
                    'store_id': movement.get('store_id'),
                    'supplier_id': movement.get('supplier_id'),
                    'movement_type': movement.get('movement_type'),
                    'quantity': int(movement.get('quantity', 0)),
                    'unit_cost': float(movement.get('unit_cost', 0)),
                    'reason': movement.get('reason', 'unknown')
                })
        return transformed
    
    def transform_promotions(self, promotions):
        """Transform promotion data"""
        transformed = []
        for promo in promotions:
            start_date = self.parse_date(promo.get('start_date'))
            if start_date:
                transformed.append({
                    'promo_id': promo.get('promo_id'),
                    'promo_name': promo.get('promo_name'),
                    'product_category': promo.get('product_category'),
                    'discount_pct': float(promo.get('discount_pct', 0)),
                    'start_date': start_date,
                    'budget': float(promo.get('budget', 0)),
                    'actual_spend': float(promo.get('actual_spend', 0)),
                    'status': promo.get('status', 'unknown')
                })
        return transformed
    
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