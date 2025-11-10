# Database Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'UMRlfr1$',
    'database': 'megamart_warehouse',
    'port': 3306
}

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

# API Configuration
API_CONFIG = {
    'base_url': 'http://127.0.0.1:8000',
    'endpoints': {
        'competitor_pricing': '/api/competitor-pricing'
    }
}

# File Paths
FILE_PATHS = {
    'promotions': 'etl/flat_files/promotions.csv',
    'employee_schedules': 'etl/flat_files/employee_schedules.csv'
}