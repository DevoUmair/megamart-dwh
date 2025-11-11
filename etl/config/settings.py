# MongoDB Configuration
MONGODB_CONFIG = {
    'username': 'umair',
    'password': 'UMRlfr1$',
    'cluster': 'megamart-sales-cluster.noqdmks.mongodb.net',
    'databases': {
        'oltp1': 'megamart_sales_oltp1',
        'oltp2': 'megamart_customer_oltp2'
    }
}

# MySQL Data Warehouse Configuration
MYSQL_WAREHOUSE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'abeer123',
    'database': 'megamart_warehouse',
    'port': 3306
}

# API Configuration
API_CONFIG = {
    'base_url': 'http://127.0.0.1:8000',
    'endpoints': {
        'competitor_pricing': '/api/competitor-pricing'
    }
}

# File Paths
FILE_PATHS = {
    'flat_files_folder': 'flat_files',
    'promotions': 'flat_files/promotions.csv',
    'employee_schedules': 'flat_files/employee_schedules.csv'
}