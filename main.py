import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class EnhancedDataAnalytics:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="UMRlfr1$",
            database="megamart_warehouse",
            port=3306
        )
        # Set modern styling
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
    
    def get_business_kpis(self):
        """Get comprehensive business KPIs from single fact table"""
        query = """
        SELECT 
            COUNT(*) as total_operations,
            SUM(CASE WHEN operation_type = 'SALE' THEN total_amount ELSE 0 END) as total_revenue,
            AVG(CASE WHEN operation_type = 'SALE' THEN total_amount ELSE 0 END) as avg_transaction_value,
            COUNT(DISTINCT CASE WHEN operation_type = 'SALE' THEN customer_key END) as unique_customers,
            SUM(CASE WHEN operation_type = 'SALE' THEN quantity ELSE 0 END) as total_units_sold,
            SUM(CASE WHEN operation_type = 'INVENTORY' AND movement_type = 'restock' THEN quantity * unit_cost ELSE 0 END) as inventory_cost,
            SUM(CASE WHEN operation_type = 'PROMOTION' THEN actual_spend ELSE 0 END) as total_promo_spend
        FROM fact_business_operations
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def get_daily_business_trend(self, days=30):
        """Get daily business trends across all operation types"""
        query = """
        SELECT 
            d.full_date,
            SUM(CASE WHEN fbo.operation_type = 'SALE' THEN fbo.total_amount ELSE 0 END) as daily_revenue,
            SUM(CASE WHEN fbo.operation_type = 'SALE' THEN fbo.quantity ELSE 0 END) as daily_units_sold,
            SUM(CASE WHEN fbo.operation_type = 'INVENTORY' AND fbo.movement_type = 'restock' 
                THEN fbo.quantity * fbo.unit_cost ELSE 0 END) as daily_inventory_cost,
            COUNT(CASE WHEN fbo.operation_type = 'SALE' THEN 1 END) as sales_count,
            COUNT(CASE WHEN fbo.operation_type = 'INVENTORY' THEN 1 END) as inventory_movements
        FROM fact_business_operations fbo
        JOIN dim_date d ON fbo.date_key = d.date_key
        WHERE d.full_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY d.full_date
        ORDER BY d.full_date
        """
        
        df = pd.read_sql(query, self.conn, params=(days,))
        return df
    
    def get_operation_type_breakdown(self):
        """Breakdown of different business operations"""
        query = """
        SELECT 
            operation_type,
            COUNT(*) as operation_count,
            SUM(total_amount) as total_amount,
            AVG(total_amount) as avg_amount
        FROM fact_business_operations
        GROUP BY operation_type
        ORDER BY total_amount DESC
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def get_top_performing_products(self, limit=15):
        """Get top performing products with enhanced metrics"""
        query = """
        SELECT 
            p.product_name,
            p.category,
            p.brand,
            SUM(CASE WHEN fbo.operation_type = 'SALE' THEN fbo.quantity ELSE 0 END) as total_quantity_sold,
            SUM(CASE WHEN fbo.operation_type = 'SALE' THEN fbo.total_amount ELSE 0 END) as total_revenue,
            SUM(CASE WHEN fbo.operation_type = 'SALE' THEN fbo.quantity * (fbo.unit_price - p.cost_price) ELSE 0 END) as total_profit,
            AVG(CASE WHEN fbo.operation_type = 'SALE' THEN fbo.unit_price ELSE NULL END) as avg_selling_price
        FROM fact_business_operations fbo
        JOIN dim_product p ON fbo.product_key = p.product_key
        WHERE fbo.operation_type = 'SALE'
        GROUP BY p.product_name, p.category, p.brand
        ORDER BY total_revenue DESC
        LIMIT %s
        """
        
        df = pd.read_sql(query, self.conn, params=(limit,))
        return df
    
    def get_customer_analytics(self):
        """Comprehensive customer analytics"""
        query = """
        SELECT 
            c.loyalty_tier,
            c.customer_segment,
            COUNT(DISTINCT c.customer_key) as customer_count,
            AVG(fbo.total_amount) as avg_transaction_value,
            SUM(fbo.total_amount) as total_revenue,
            COUNT(fbo.operation_key) as total_transactions
        FROM fact_business_operations fbo
        JOIN dim_customer c ON fbo.customer_key = c.customer_key
        WHERE fbo.operation_type = 'SALE'
        GROUP BY c.loyalty_tier, c.customer_segment
        ORDER BY total_revenue DESC
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def get_inventory_analytics(self):
        """Enhanced inventory analytics"""
        query = """
        SELECT 
            p.category,
            p.subcategory,
            SUM(CASE WHEN fbo.movement_type = 'restock' THEN fbo.quantity ELSE 0 END) as units_restocked,
            SUM(CASE WHEN fbo.movement_type = 'sale' THEN fbo.quantity ELSE 0 END) as units_sold,
            SUM(CASE WHEN fbo.movement_type = 'restock' THEN fbo.quantity * fbo.unit_cost ELSE 0 END) as restock_cost,
            SUM(CASE WHEN fbo.movement_type = 'sale' THEN fbo.quantity * fbo.unit_price ELSE 0 END) as sales_value,
            ROUND(
                SUM(CASE WHEN fbo.movement_type = 'sale' THEN fbo.quantity ELSE 0 END) * 1.0 / 
                NULLIF(SUM(CASE WHEN fbo.movement_type = 'restock' THEN fbo.quantity ELSE 0 END), 0), 2
            ) as turnover_ratio
        FROM fact_business_operations fbo
        JOIN dim_product p ON fbo.product_key = p.product_key
        WHERE fbo.operation_type = 'INVENTORY'
        GROUP BY p.category, p.subcategory
        ORDER BY sales_value DESC
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def get_promotion_effectiveness(self):
        """Analyze promotion effectiveness"""
        query = """
        SELECT 
            pd.promo_name,
            pd.promo_type,
            pd.product_category,
            pd.discount_pct,
            pd.budget,
            pd.actual_spend,
            COUNT(fbo.operation_key) as redemption_count,
            SUM(fbo.total_amount) as revenue_generated,
            ROUND(pd.actual_spend / NULLIF(SUM(fbo.total_amount), 0) * 100, 2) as cost_per_revenue_percent
        FROM fact_business_operations fbo
        JOIN dim_promotion_details pd ON fbo.promotion_key = pd.promotion_key
        WHERE fbo.operation_type = 'PROMOTION'
        GROUP BY pd.promo_name, pd.promo_type, pd.product_category, pd.discount_pct, pd.budget, pd.actual_spend
        ORDER BY revenue_generated DESC
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def get_competitor_intelligence(self):
        """Enhanced competitor intelligence"""
        query = """
        SELECT 
            cp.competitor_name,
            cp.product_category,
            cp.location,
            AVG(cp.overall_price_index) as avg_price_index,
            AVG(cp.base_price) as avg_base_price,
            AVG(cp.promo_price) as avg_promo_price,
            COUNT(*) as data_points,
            ROUND(AVG(cp.price_variance_pct), 2) as avg_price_variance
        FROM dim_competitor_pricing cp
        GROUP BY cp.competitor_name, cp.product_category, cp.location
        ORDER BY avg_price_index DESC
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def get_store_performance_metrics(self):
        """Comprehensive store performance metrics"""
        query = """
        SELECT 
            s.store_name,
            s.city,
            s.region,
            s.store_type,
            COUNT(DISTINCT CASE WHEN fbo.operation_type = 'SALE' THEN fbo.customer_key END) as unique_customers,
            COUNT(CASE WHEN fbo.operation_type = 'SALE' THEN 1 END) as sales_count,
            SUM(CASE WHEN fbo.operation_type = 'SALE' THEN fbo.total_amount ELSE 0 END) as total_revenue,
            AVG(CASE WHEN fbo.operation_type = 'SALE' THEN fbo.total_amount ELSE NULL END) as avg_transaction_value,
            SUM(CASE WHEN fbo.operation_type = 'SALE' THEN fbo.quantity ELSE 0 END) as total_units_sold
        FROM fact_business_operations fbo
        JOIN dim_store s ON fbo.store_key = s.store_key
        WHERE fbo.operation_type = 'SALE'
        GROUP BY s.store_name, s.city, s.region, s.store_type
        ORDER BY total_revenue DESC
        """
        
        df = pd.read_sql(query, self.conn)
        return df
    
    def create_interactive_dashboard(self):
        """Create interactive dashboard using Plotly"""
        print("📊 Generating Interactive Analytics Dashboard...")
        
        try:
            # Get all data
            kpis = self.get_business_kpis()
            daily_trend = self.get_daily_business_trend()
            operation_breakdown = self.get_operation_type_breakdown()
            top_products = self.get_top_performing_products(10)
            customer_analytics = self.get_customer_analytics()
            inventory_analytics = self.get_inventory_analytics()
            promotion_effectiveness = self.get_promotion_effectiveness()
            competitor_intel = self.get_competitor_intelligence()
            store_performance = self.get_store_performance_metrics()
            
            # Create subplots
            fig = make_subplots(
                rows=4, cols=3,
                subplot_titles=(
                    'Daily Business Trends', 'Operation Type Breakdown', 'Top Products by Revenue',
                    'Customer Revenue by Loyalty Tier', 'Inventory Turnover by Category', 
                    'Promotion Effectiveness', 'Competitor Price Analysis', 'Store Performance',
                    'Customer Segmentation', 'Profit Margin Analysis', 'Regional Performance', 'Sales Distribution'
                ),
                specs=[
                    [{"type": "scatter", "colspan": 2}, None, {"type": "pie"}],
                    [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
                    [{"type": "heatmap"}, {"type": "bar"}, {"type": "pie"}],
                    [{"type": "bar"}, {"type": "bar"}, {"type": "box"}]
                ],
                vertical_spacing=0.08,
                horizontal_spacing=0.08
            )
            
            # 1. Daily Business Trends
            if not daily_trend.empty:
                fig.add_trace(
                    go.Scatter(x=daily_trend['full_date'], y=daily_trend['daily_revenue'],
                              name='Revenue', line=dict(color='#2E86AB'), yaxis='y1'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=daily_trend['full_date'], y=daily_trend['daily_units_sold'],
                              name='Units Sold', line=dict(color='#A23B72'), yaxis='y2'),
                    row=1, col=1
                )
                fig.update_layout(
                    yaxis=dict(title='Revenue ($)', side='left', showgrid=False),
                    yaxis2=dict(title='Units Sold', side='right', overlaying='y', showgrid=False)
                )
            
            # 2. Operation Type Breakdown
            if not operation_breakdown.empty:
                fig.add_trace(
                    go.Pie(labels=operation_breakdown['operation_type'], 
                          values=operation_breakdown['total_amount'],
                          name='Operation Types'),
                    row=1, col=3
                )
            
            # 3. Top Products
            if not top_products.empty:
                fig.add_trace(
                    go.Bar(x=top_products['total_revenue'], y=top_products['product_name'],
                          orientation='h', marker_color='#F18F01'),
                    row=2, col=1
                )
            
            # 4. Customer Revenue by Loyalty Tier
            if not customer_analytics.empty:
                fig.add_trace(
                    go.Bar(x=customer_analytics['loyalty_tier'], y=customer_analytics['total_revenue'],
                          marker_color='#C73E1D'),
                    row=2, col=2
                )
            
            # 5. Inventory Turnover
            if not inventory_analytics.empty:
                fig.add_trace(
                    go.Bar(x=inventory_analytics['category'], y=inventory_analytics['turnover_ratio'],
                          marker_color='#3BB273'),
                    row=2, col=3
                )
            
            # 6. Promotion Effectiveness
            if not promotion_effectiveness.empty:
                fig.add_trace(
                    go.Scatter(x=promotion_effectiveness['discount_pct'], 
                              y=promotion_effectiveness['revenue_generated'],
                              mode='markers', marker=dict(size=promotion_effectiveness['redemption_count']/10,
                                                         color=promotion_effectiveness['cost_per_revenue_percent'],
                                                         colorscale='Viridis', showscale=True),
                              text=promotion_effectiveness['promo_name']),
                    row=3, col=1
                )
            
            # 7. Competitor Price Analysis
            if not competitor_intel.empty:
                competitor_pivot = competitor_intel.pivot_table(
                    values='avg_price_index', 
                    index='competitor_name', 
                    columns='product_category', 
                    aggfunc='mean'
                ).fillna(0)
                
                fig.add_trace(
                    go.Heatmap(z=competitor_pivot.values,
                              x=competitor_pivot.columns,
                              y=competitor_pivot.index,
                              colorscale='RdBu_r'),
                    row=3, col=2
                )
            
            # 8. Store Performance
            if not store_performance.empty:
                fig.add_trace(
                    go.Bar(x=store_performance['store_name'], y=store_performance['total_revenue'],
                          marker_color='#7768AE'),
                    row=3, col=3
                )
            
            # Update layout
            fig.update_layout(
                height=1200,
                showlegend=True,
                title_text="Megamart Business Intelligence Dashboard",
                template="plotly_white"
            )
            
            fig.show()
            
            # Print comprehensive KPIs
            self.print_comprehensive_kpis(kpis, store_performance, customer_analytics)
            
        except Exception as e:
            print(f"❌ Error generating dashboard: {e}")
    
    def create_matplotlib_dashboard(self):
        """Create static dashboard using matplotlib"""
        print("📊 Generating Static Analytics Dashboard...")
        
        try:
            # Get data
            kpis = self.get_business_kpis()
            daily_trend = self.get_daily_business_trend()
            top_products = self.get_top_performing_products(8)
            customer_analytics = self.get_customer_analytics()
            inventory_analytics = self.get_inventory_analytics()
            store_performance = self.get_store_performance_metrics()
            
            # Create figure with subplots
            fig = plt.figure(figsize=(20, 16))
            
            # Define grid
            gs = fig.add_gridspec(4, 4)
            
            # 1. KPI Summary
            ax1 = fig.add_subplot(gs[0, :2])
            self.create_kpi_summary(ax1, kpis)
            
            # 2. Daily Trends
            ax2 = fig.add_subplot(gs[0, 2:])
            self.create_daily_trends(ax2, daily_trend)
            
            # 3. Top Products
            ax3 = fig.add_subplot(gs[1, :2])
            self.create_top_products_chart(ax3, top_products)
            
            # 4. Customer Analytics
            ax4 = fig.add_subplot(gs[1, 2:])
            self.create_customer_analytics_chart(ax4, customer_analytics)
            
            # 5. Inventory Analysis
            ax5 = fig.add_subplot(gs[2, :2])
            self.create_inventory_analysis(ax5, inventory_analytics)
            
            # 6. Store Performance
            ax6 = fig.add_subplot(gs[2, 2:])
            self.create_store_performance(ax6, store_performance)
            
            # 7. Operation Metrics
            ax7 = fig.add_subplot(gs[3, :])
            operation_breakdown = self.get_operation_type_breakdown()
            self.create_operation_metrics(ax7, operation_breakdown)
            
            plt.tight_layout()
            plt.savefig('enhanced_business_dashboard.png', dpi=300, bbox_inches='tight')
            plt.show()
            
        except Exception as e:
            print(f"❌ Error generating static dashboard: {e}")
    
    def create_kpi_summary(self, ax, kpis):
        """Create KPI summary visualization"""
        if kpis.empty:
            ax.text(0.5, 0.5, 'No KPI data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Business KPIs', fontsize=14, fontweight='bold')
            return
        
        metrics = [
            ('Total Revenue', f"${kpis['total_revenue'].iloc[0]:,.0f}", '#2E86AB'),
            ('Avg Transaction', f"${kpis['avg_transaction_value'].iloc[0]:.0f}", '#A23B72'),
            ('Unique Customers', f"{kpis['unique_customers'].iloc[0]:,}", '#F18F01'),
            ('Units Sold', f"{kpis['total_units_sold'].iloc[0]:,}", '#3BB273')
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            y_pos = 0.8 - i * 0.2
            ax.text(0.1, y_pos, label, fontsize=12, transform=ax.transAxes, alpha=0.7)
            ax.text(0.7, y_pos, value, fontsize=16, fontweight='bold', 
                   color=color, transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('Key Business Metrics', fontsize=16, fontweight='bold', pad=20)
    
    def create_daily_trends(self, ax, daily_trend):
        """Create daily trends visualization"""
        if daily_trend.empty:
            ax.text(0.5, 0.5, 'No trend data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Daily Business Trends', fontsize=14, fontweight='bold')
            return
        
        ax.plot(daily_trend['full_date'], daily_trend['daily_revenue'], 
               label='Revenue', color='#2E86AB', linewidth=2.5)
        ax.set_ylabel('Revenue ($)', color='#2E86AB')
        ax.tick_params(axis='y', labelcolor='#2E86AB')
        
        ax2 = ax.twinx()
        ax2.plot(daily_trend['full_date'], daily_trend['daily_units_sold'],
                label='Units Sold', color='#A23B72', linewidth=2.5, linestyle='--')
        ax2.set_ylabel('Units Sold', color='#A23B72')
        ax2.tick_params(axis='y', labelcolor='#A23B72')
        
        ax.set_title('Daily Business Trends', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
    
    def create_top_products_chart(self, ax, top_products):
        """Create top products visualization"""
        if top_products.empty:
            ax.text(0.5, 0.5, 'No product data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Top Products', fontsize=14, fontweight='bold')
            return
        
        bars = ax.barh(range(len(top_products)), top_products['total_revenue'], 
                      color=self.colors[:len(top_products)])
        ax.set_yticks(range(len(top_products)))
        ax.set_yticklabels(top_products['product_name'], fontsize=9)
        ax.set_xlabel('Revenue ($)')
        ax.set_title('Top Products by Revenue', fontsize=14, fontweight='bold')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, f'${width:,.0f}', 
                   ha='left', va='center', fontsize=8)
    
    def create_customer_analytics_chart(self, ax, customer_analytics):
        """Create customer analytics visualization"""
        if customer_analytics.empty:
            ax.text(0.5, 0.5, 'No customer data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Customer Analytics', fontsize=14, fontweight='bold')
            return
        
        # Pie chart for revenue distribution
        ax.pie(customer_analytics['total_revenue'], labels=customer_analytics['loyalty_tier'],
              autopct='%1.1f%%', colors=self.colors)
        ax.set_title('Revenue by Loyalty Tier', fontsize=14, fontweight='bold')
    
    def create_inventory_analysis(self, ax, inventory_analytics):
        """Create inventory analysis visualization"""
        if inventory_analytics.empty:
            ax.text(0.5, 0.5, 'No inventory data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Inventory Analysis', fontsize=14, fontweight='bold')
            return
        
        x = np.arange(len(inventory_analytics))
        width = 0.35
        
        ax.bar(x - width/2, inventory_analytics['units_restocked'], width, label='Restocked', alpha=0.7)
        ax.bar(x + width/2, inventory_analytics['units_sold'], width, label='Sold', alpha=0.7)
        
        ax.set_xlabel('Product Category')
        ax.set_ylabel('Units')
        ax.set_title('Inventory Movement by Category', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(inventory_analytics['category'], rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def create_store_performance(self, ax, store_performance):
        """Create store performance visualization"""
        if store_performance.empty:
            ax.text(0.5, 0.5, 'No store data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Store Performance', fontsize=14, fontweight='bold')
            return
        
        bars = ax.bar(store_performance['store_name'], store_performance['total_revenue'],
                     color=self.colors[:len(store_performance)])
        ax.set_ylabel('Revenue ($)')
        ax.set_title('Store Performance by Revenue', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:,.0f}', ha='center', va='bottom', fontsize=8)
    
    def create_operation_metrics(self, ax, operation_breakdown):
        """Create operation metrics visualization"""
        if operation_breakdown.empty:
            ax.text(0.5, 0.5, 'No operation data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Operation Metrics', fontsize=14, fontweight='bold')
            return
        
        # Stacked bar chart for operation types
        x = range(len(operation_breakdown))
        ax.bar(x, operation_breakdown['operation_count'], 
               color=self.colors[:len(operation_breakdown)], alpha=0.7)
        
        ax.set_xlabel('Operation Type')
        ax.set_ylabel('Count')
        ax.set_title('Business Operations Distribution', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(operation_breakdown['operation_type'])
        ax.grid(True, alpha=0.3)
    
    def print_comprehensive_kpis(self, kpis, store_performance, customer_analytics):
        """Print comprehensive KPI summary"""
        print("\n" + "="*60)
        print("📈 COMPREHENSIVE BUSINESS INTELLIGENCE REPORT")
        print("="*60)
        
        if not kpis.empty:
            print(f"\n💰 FINANCIAL KPIs:")
            print(f"   Total Revenue: ${kpis['total_revenue'].iloc[0]:,.2f}")
            print(f"   Average Transaction Value: ${kpis['avg_transaction_value'].iloc[0]:.2f}")
            print(f"   Total Promotion Spend: ${kpis['total_promo_spend'].iloc[0]:,.2f}")
            print(f"   Inventory Cost: ${kpis['inventory_cost'].iloc[0]:,.2f}")
        
        if not store_performance.empty:
            print(f"\n🏪 STORE PERFORMANCE:")
            top_store = store_performance.iloc[0]
            print(f"   Top Performing Store: {top_store['store_name']} (${top_store['total_revenue']:,.2f})")
            print(f"   Total Stores: {len(store_performance)}")
            print(f"   Average Store Revenue: ${store_performance['total_revenue'].mean():,.2f}")
        
        if not customer_analytics.empty:
            print(f"\n👥 CUSTOMER INSIGHTS:")
            print(f"   Total Customer Segments: {len(customer_analytics)}")
            top_segment = customer_analytics.iloc[0]
            print(f"   Most Valuable Segment: {top_segment['loyalty_tier']} (${top_segment['total_revenue']:,.2f})")
    
    def generate_detailed_report(self):
        """Generate detailed analytics report"""
        print("\n📋 GENERATING DETAILED ANALYTICS REPORT...")
        
        try:
            # Get comprehensive data
            kpis = self.get_business_kpis()
            top_products = self.get_top_performing_products(20)
            customer_analytics = self.get_customer_analytics()
            inventory_analytics = self.get_inventory_analytics()
            promotion_effectiveness = self.get_promotion_effectiveness()
            competitor_intel = self.get_competitor_intelligence()
            store_performance = self.get_store_performance_metrics()
            operation_breakdown = self.get_operation_type_breakdown()
            
            # Create detailed report
            report = f"""
ENHANCED MEGAMART BUSINESS INTELLIGENCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

EXECUTIVE SUMMARY:
{'-'*30}
"""
            if not kpis.empty:
                report += f"""Total Business Operations: {kpis['total_operations'].iloc[0]:,}
Total Revenue Generated: ${kpis['total_revenue'].iloc[0]:,.2f}
Average Transaction Value: ${kpis['avg_transaction_value'].iloc[0]:.2f}
Unique Customers: {kpis['unique_customers'].iloc[0]:,}
Total Units Sold: {kpis['total_units_sold'].iloc[0]:,}

"""

            report += "OPERATION BREAKDOWN:\n" + "-"*30 + "\n"
            if not operation_breakdown.empty:
                for _, op in operation_breakdown.iterrows():
                    report += f"{op['operation_type']}: {op['operation_count']:,} operations, ${op['total_amount']:,.2f} total\n"
                report += "\n"

            report += "TOP PERFORMING PRODUCTS:\n" + "-"*30 + "\n"
            if not top_products.empty:
                for i, product in top_products.iterrows():
                    profit_margin = (product['total_profit'] / product['total_revenue'] * 100) if product['total_revenue'] > 0 else 0
                    report += f"{i+1}. {product['product_name']} ({product['category']})\n"
                    report += f"   Revenue: ${product['total_revenue']:,.2f} | Profit: ${product['total_profit']:,.2f} | Margin: {profit_margin:.1f}%\n"
                report += "\n"

            report += "STORE PERFORMANCE RANKING:\n" + "-"*30 + "\n"
            if not store_performance.empty:
                for i, store in store_performance.iterrows():
                    report += f"{i+1}. {store['store_name']} ({store['city']})\n"
                    report += f"   Revenue: ${store['total_revenue']:,.2f} | Transactions: {store['sales_count']:,}\n"
                report += "\n"

            report += "COMPETITOR INTELLIGENCE:\n" + "-"*30 + "\n"
            if not competitor_intel.empty:
                for _, comp in competitor_intel.iterrows():
                    report += f"{comp['competitor_name']} - {comp['product_category']}\n"
                    report += f"   Price Index: {comp['avg_price_index']:.2f} | Variance: {comp['avg_price_variance']}%\n"
                report += "\n"

            # Save report
            with open('enhanced_analytics_report.txt', 'w') as f:
                f.write(report)
            
            print("✅ Enhanced analytics report saved as 'enhanced_analytics_report.txt'")
            
        except Exception as e:
            print(f"❌ Error generating detailed report: {e}")
    
    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()

def main():
    analytics = EnhancedDataAnalytics()
    try:
        print("🚀 MegaMart Enhanced Business Intelligence Dashboard")
        print("=" * 60)
        
        # Create interactive dashboard
        analytics.create_interactive_dashboard()
        
        # Create static dashboard
        analytics.create_matplotlib_dashboard()
        
        # Generate detailed report
        analytics.generate_detailed_report()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure:")
        print("   - MySQL is running")
        print("   - Database 'megamart_warehouse' exists") 
        print("   - Single fact table schema is populated with data")
    finally:
        analytics.close()

if __name__ == "__main__":
    main()