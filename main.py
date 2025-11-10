import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

class DataAnalytics:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="UMRlfr1$",
            database="megamart_warehouse",
            port=3306
        )
    
    def get_sales_kpis(self):
        """Get key sales performance indicators"""
        query = """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_transaction_value,
            COUNT(DISTINCT customer_key) as unique_customers,
            SUM(quantity) as total_units_sold
        FROM fact_sales
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def get_daily_sales_trend(self, days=30):
        """Get daily sales trend"""
        query = """
        SELECT 
            d.full_date,
            SUM(fs.total_amount) as daily_revenue,
            COUNT(fs.sales_key) as transaction_count
        FROM fact_sales fs
        JOIN dim_date d ON fs.date_key = d.date_key
        WHERE d.full_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY d.full_date
        ORDER BY d.full_date
        """
        
        df = pd.read_sql(query, self.conn, params=(days,))
        return df
    
    def get_top_products(self, limit=10):
        """Get top selling products"""
        query = """
        SELECT 
            p.product_name,
            p.category,
            SUM(fs.quantity) as total_quantity,
            SUM(fs.total_amount) as total_revenue
        FROM fact_sales fs
        JOIN dim_product p ON fs.product_key = p.product_key
        GROUP BY p.product_name, p.category
        ORDER BY total_revenue DESC
        LIMIT %s
        """
        
        df = pd.read_sql(query, self.conn, params=(limit,))
        return df
    
    def get_customer_segmentation(self):
        """Segment customers by spending"""
        query = """
        SELECT 
            c.loyalty_tier,
            COUNT(DISTINCT c.customer_key) as customer_count,
            AVG(fs.total_amount) as avg_spend,
            SUM(fs.total_amount) as total_revenue
        FROM fact_sales fs
        JOIN dim_customer c ON fs.customer_key = c.customer_key
        GROUP BY c.loyalty_tier
        ORDER BY total_revenue DESC
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def get_inventory_turnover(self):
        """Calculate inventory turnover by category"""
        query = """
        SELECT 
            p.category,
            SUM(CASE WHEN im.movement_type = 'sale' THEN im.quantity ELSE 0 END) as units_sold,
            SUM(CASE WHEN im.movement_type = 'restock' THEN im.quantity ELSE 0 END) as units_restocked,
            ROUND(
                SUM(CASE WHEN im.movement_type = 'sale' THEN im.quantity ELSE 0 END) * 1.0 / 
                NULLIF(SUM(CASE WHEN im.movement_type = 'restock' THEN im.quantity ELSE 0 END), 0), 2
            ) as turnover_ratio
        FROM fact_inventory im
        JOIN dim_product p ON im.product_key = p.product_key
        GROUP BY p.category
        ORDER BY turnover_ratio DESC
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def get_competitor_pricing_analysis(self):
        """Analyze competitor pricing data"""
        query = """
        SELECT 
            competitor_name,
            product_category,
            AVG(overall_price_index) as avg_price_index,
            COUNT(*) as data_points
        FROM dim_competitor
        GROUP BY competitor_name, product_category
        ORDER BY avg_price_index DESC
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def get_store_performance(self):
        """Analyze store performance"""
        query = """
        SELECT 
            s.store_name,
            s.city,
            COUNT(fs.sales_key) as transaction_count,
            SUM(fs.total_amount) as total_revenue,
            AVG(fs.total_amount) as avg_transaction_value
        FROM fact_sales fs
        JOIN dim_store s ON fs.store_key = s.store_key
        GROUP BY s.store_name, s.city
        ORDER BY total_revenue DESC
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def create_sales_dashboard(self):
        """Create comprehensive sales dashboard"""
        print("📊 Generating Sales Analytics Dashboard...")
        
        try:
            # Get all metrics
            kpis = self.get_sales_kpis()
            daily_trend = self.get_daily_sales_trend()
            top_products = self.get_top_products()
            customer_segments = self.get_customer_segmentation()
            inventory_turnover = self.get_inventory_turnover()
            competitor_analysis = self.get_competitor_pricing_analysis()
            store_performance = self.get_store_performance()
            
            # Create visualizations
            plt.style.use('seaborn-v0_8')
            fig, axes = plt.subplots(3, 2, figsize=(18, 15))
            
            # Daily Sales Trend
            if not daily_trend.empty:
                axes[0, 0].plot(daily_trend['full_date'], daily_trend['daily_revenue'], marker='o')
                axes[0, 0].set_title('Daily Sales Trend (Last 30 Days)')
                axes[0, 0].set_xlabel('Date')
                axes[0, 0].set_ylabel('Revenue ($)')
                axes[0, 0].tick_params(axis='x', rotation=45)
            else:
                axes[0, 0].text(0.5, 0.5, 'No data available', ha='center', va='center')
                axes[0, 0].set_title('Daily Sales Trend')
            
            # Top Products
            if not top_products.empty:
                axes[0, 1].barh(top_products['product_name'].head(8), top_products['total_revenue'].head(8))
                axes[0, 1].set_title('Top Products by Revenue')
                axes[0, 1].set_xlabel('Revenue ($)')
            else:
                axes[0, 1].text(0.5, 0.5, 'No data available', ha='center', va='center')
                axes[0, 1].set_title('Top Products')
            
            # Customer Segmentation
            if not customer_segments.empty:
                axes[1, 0].pie(customer_segments['total_revenue'], labels=customer_segments['loyalty_tier'], autopct='%1.1f%%')
                axes[1, 0].set_title('Revenue by Customer Loyalty Tier')
            else:
                axes[1, 0].text(0.5, 0.5, 'No data available', ha='center', va='center')
                axes[1, 0].set_title('Customer Segmentation')
            
            # Inventory Turnover
            if not inventory_turnover.empty:
                axes[1, 1].bar(inventory_turnover['category'], inventory_turnover['turnover_ratio'])
                axes[1, 1].set_title('Inventory Turnover by Category')
                axes[1, 1].set_xlabel('Category')
                axes[1, 1].set_ylabel('Turnover Ratio')
                axes[1, 1].tick_params(axis='x', rotation=45)
            else:
                axes[1, 1].text(0.5, 0.5, 'No data available', ha='center', va='center')
                axes[1, 1].set_title('Inventory Turnover')
            
            # Competitor Pricing
            if not competitor_analysis.empty:
                competitor_pivot = competitor_analysis.pivot(index='competitor_name', columns='product_category', values='avg_price_index')
                sns.heatmap(competitor_pivot, annot=True, cmap='YlOrRd', ax=axes[2, 0])
                axes[2, 0].set_title('Competitor Price Index Heatmap')
            else:
                axes[2, 0].text(0.5, 0.5, 'No data available', ha='center', va='center')
                axes[2, 0].set_title('Competitor Analysis')
            
            # Store Performance
            if not store_performance.empty:
                axes[2, 1].bar(store_performance['store_name'], store_performance['total_revenue'])
                axes[2, 1].set_title('Store Performance by Revenue')
                axes[2, 1].set_xlabel('Store')
                axes[2, 1].set_ylabel('Revenue ($)')
                axes[2, 1].tick_params(axis='x', rotation=45)
            else:
                axes[2, 1].text(0.5, 0.5, 'No data available', ha='center', va='center')
                axes[2, 1].set_title('Store Performance')
            
            plt.tight_layout()
            plt.savefig('sales_dashboard.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            # Print KPIs
            print("\n📈 KEY PERFORMANCE INDICATORS:")
            if not kpis.empty:
                print(f"   Total Transactions: {kpis['total_transactions'].iloc[0]:,}")
                print(f"   Total Revenue: ${kpis['total_revenue'].iloc[0]:,.2f}")
                print(f"   Average Transaction: ${kpis['avg_transaction_value'].iloc[0]:.2f}")
                print(f"   Unique Customers: {kpis['unique_customers'].iloc[0]:,}")
                print(f"   Total Units Sold: {kpis['total_units_sold'].iloc[0]:,}")
            else:
                print("   No sales data available")
                
            print("\n🏪 Store Performance Summary:")
            if not store_performance.empty:
                for _, store in store_performance.iterrows():
                    print(f"   {store['store_name']} ({store['city']}): ${store['total_revenue']:,.2f}")
            else:
                print("   No store performance data available")
                
        except Exception as e:
            print(f"❌ Error generating dashboard: {e}")
            print("💡 Make sure you have populated the data warehouse with sample data")
    
    def generate_analytics_report(self):
        """Generate a comprehensive analytics report"""
        print("\n📋 GENERATING ANALYTICS REPORT...")
        
        try:
            # Get all data
            kpis = self.get_sales_kpis()
            top_products = self.get_top_products(15)
            customer_segments = self.get_customer_segmentation()
            inventory_turnover = self.get_inventory_turnover()
            competitor_analysis = self.get_competitor_pricing_analysis()
            store_performance = self.get_store_performance()
            
            # Create report
            report = f"""
MEGAMART ANALYTICS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

SALES PERFORMANCE:
{'-'*30}
"""
            if not kpis.empty:
                report += f"""Total Transactions: {kpis['total_transactions'].iloc[0]:,}
Total Revenue: ${kpis['total_revenue'].iloc[0]:,.2f}
Average Transaction Value: ${kpis['avg_transaction_value'].iloc[0]:.2f}
Unique Customers: {kpis['unique_customers'].iloc[0]:,}
Total Units Sold: {kpis['total_units_sold'].iloc[0]:,}

"""
            
            report += "TOP PRODUCTS:\n" + "-"*30 + "\n"
            if not top_products.empty:
                for _, product in top_products.iterrows():
                    report += f"{product['product_name']} ({product['category']}): ${product['total_revenue']:,.2f}\n"
                report += "\n"
            
            report += "STORE PERFORMANCE:\n" + "-"*30 + "\n"
            if not store_performance.empty:
                for _, store in store_performance.iterrows():
                    report += f"{store['store_name']}: ${store['total_revenue']:,.2f} ({store['transaction_count']} transactions)\n"
                report += "\n"
            
            report += "COMPETITOR ANALYSIS:\n" + "-"*30 + "\n"
            if not competitor_analysis.empty:
                for _, competitor in competitor_analysis.iterrows():
                    report += f"{competitor['competitor_name']} - {competitor['product_category']}: Price Index {competitor['avg_price_index']:.2f}\n"
            
            # Save report to file
            with open('analytics_report.txt', 'w') as f:
                f.write(report)
            
            print("✅ Analytics report saved as 'analytics_report.txt'")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()

def main():
    analytics = DataAnalytics()
    try:
        print("🚀 MegaMart Data Analytics Dashboard")
        print("=" * 50)
        
        # Create dashboard
        analytics.create_sales_dashboard()
        
        # Generate report
        analytics.generate_analytics_report()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure:")
        print("   - MySQL is running")
        print("   - Database 'megamart_warehouse' exists")
        print("   - Tables are populated with data")
    finally:
        analytics.close()

if __name__ == "__main__":
    main()