import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import json

# Querying SQL Database inside Streamlit
st.set_page_config(page_title = 'Olist Business Performance Dashboard', layout = 'wide')
from olist_db_setup import create_database
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "olist.db"

if not DB_PATH.exists():
    with st.spinner("Preparing the dashboard data. This may take a moment..."):
        create_database()

conn = sqlite3.connect(DB_PATH)

# Setting Up Dashboard Title and Description
st.title('Olist Business Performance Dashboard')
st.markdown("Olist is a Brazilian e-commerce technology company\n" \
"that acts as an intermediary platform for business to major online marketplaces.\n" \
"This dashboard showcases the yearly financial performance, operational efficiency\n" \
"and logistical challenges of Olist's marketplace model. By analysing over 100,000 orders across Brazil\n" \
"from October 2016 to September 2018, it tracks Key Performance Indicators such as\n" \
"Total Orders, Total Revenue and On-Time Rate.")

# Filtering by year
year_query = """
SELECT DISTINCT strftime('%Y', o.order_purchase_timestamp) AS year
FROM orders AS o
ORDER BY year
"""
year_df = pd.read_sql(year_query, conn)
unique_years = list(year_df['year'].unique())
with st.sidebar:
    st.title('Olist Business Performance 2016-2018')
    selected_year = st.selectbox('Year', unique_years)
    st.markdown('Note: 2016 and 2018 contain partial-year data. 2016 includes data from October–December, while 2018 includes data from January–September. Direct comparisons of annual totals across years should therefore be interpreted with caution.')

# KPI by year
if selected_year:
    st.header('KPI Overview')
    kpi_query = """
    SELECT COUNT(DISTINCT o.order_id) AS total_orders,
            SUM(p.payment_value) AS total_revenue,
            SUM(p.payment_value) / COUNT(p.order_id) AS avg_order_value,
            AVG(CASE
                WHEN julianday(o.order_delivered_customer_date) <= julianday(o.order_estimated_delivery_date)
                THEN 1.0
                ELSE 0.0
            END)* 100 AS on_time_rate
    FROM orders AS o
    JOIN payments AS p
    ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
        AND strftime('%Y', o.order_purchase_timestamp) = ?
"""
    df_filtered_metrics = pd.read_sql(kpi_query, conn, params = (selected_year,))

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label = 'Total Orders', value = f'{df_filtered_metrics["total_orders"][0]:,}')
with col2:
    st.metric(label = 'Total Revenue', value = f'${df_filtered_metrics["total_revenue"][0]:,.2f}')
with col3:
    st.metric(label = 'Average Order Value', value = f'${df_filtered_metrics["avg_order_value"][0]:,.2f}')

col4, col5, col6, col7 = st.columns(4)
with col5:
    st.metric(label = 'On-Time Rate', value = f'{df_filtered_metrics["on_time_rate"][0]: .1f}%')

if selected_year:
    kpi_query = """
    SELECT COUNT(customer_unique_id) AS number_of_customers
    FROM customers AS c
    JOIN orders AS o
    ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
        AND strftime('%Y', o.order_purchase_timestamp) = ?
"""
    df_filtered_metrics = pd.read_sql(kpi_query, conn, params = (selected_year,))

with col4:
    st.metric(label = 'Number of Customers', value = f'{df_filtered_metrics["number_of_customers"][0]}')

if selected_year:
    kpi_query = """
    SELECT AVG(review_score) AS avg_review_score
    FROM reviews AS r
    JOIN orders AS o
    ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered'
        AND strftime('%Y', o.order_purchase_timestamp) = ?
"""
    df_filtered_metrics = pd.read_sql(kpi_query, conn, params = (selected_year,))
with col6:
    st.metric(label = 'Average Review Score', value = f'{df_filtered_metrics["avg_review_score"][0]:.2f} / 5.00')

if selected_year:
    kpi_query = """
    SELECT 100.0 * SUM(
        CASE WHEN order_status = 'canceled' THEN 1
        ELSE 0 END
    ) / COUNT(*) AS cancellation_rate
    FROM orders AS o
    WHERE strftime('%Y', o.order_purchase_timestamp) = ?
"""
    df_filtered_metrics = pd.read_sql(kpi_query, conn, params = (selected_year,))
with col7:
    st.metric(label = 'Cancellation Rate', value = f'{df_filtered_metrics["cancellation_rate"][0]:.2f}%')

## Revenue & Sales
# Revenue Trend by Month
st.header('Revenue & Sales')
col7, col8 = st.columns(2)
if selected_year:
    month_map = {
    "01": "Jan", "02": "Feb", "03": "Mar",
    "04": "Apr", "05": "May", "06": "Jun",
    "07": "Jul", "08": "Aug", "09": "Sep",
    "10": "Oct", "11": "Nov", "12": "Dec"
    }
    revenue_trend_query = """
        SELECT SUM(oi.price) AS Revenue, o.order_purchase_timestamp, strftime('%m', o.order_purchase_timestamp) AS Month
        FROM order_items AS oi
        JOIN orders AS o
        ON o.order_id = oi.order_id
        WHERE strftime('%Y', o.order_purchase_timestamp) = ?
        GROUP BY Month
        ORDER BY Month
"""
    with col7:
        df_revenue_trend = pd.read_sql(revenue_trend_query, conn, params = (selected_year,))
        df_revenue_trend["Month"] = df_revenue_trend["Month"].map(month_map)
        fig = px.line(df_revenue_trend, x = 'Month', y = 'Revenue',
                    title = 'Revenue by Month', markers = True, 
                    template = 'plotly_white')
        st.plotly_chart(fig, use_container_width = True)

# Revenue by Product Category
if selected_year:
    product_by_category = """
        SELECT SUM(oi.price) AS Revenue, t.product_category_name_english AS Category
        FROM orders AS o
        JOIN order_items AS oi
        ON o.order_id = oi.order_id

        JOIN products
        ON oi.product_id = products.product_id

        JOIN translation AS t
        ON products.product_category_name = t.product_category_name

        WHERE strftime('%Y', o.order_purchase_timestamp) = ?
            AND o.order_status = 'delivered'

        GROUP BY Category
        ORDER BY Revenue
        LIMIT 10
"""
    with col8:
        df_product_by_category = pd.read_sql(product_by_category, conn, params = (selected_year,))
        fig = px.bar(df_product_by_category, x = 'Revenue', y = 'Category',
                     title = 'Revenue by Product Category',
                     template = 'plotly_white')
        st.plotly_chart(fig, use_container_width = True)

# Revenue by State
with open("br_states.json", "r", encoding="utf-8") as f:
    brazil = json.load(f)
if selected_year:
    revenue_by_state = """
        SELECT c.customer_state AS State, 
        AVG(g.geolocation_lat) AS Latitude,
        AVG(g.geolocation_lng) AS Longitude,
        SUM(oi.price) AS Revenue
        FROM orders AS o

        JOIN customers AS c
        ON o.customer_id = c.customer_id

        JOIN order_items AS oi
        ON o.order_id = oi.order_id

        JOIN geolocation AS g
        ON c.customer_zip_code_prefix = g.geolocation_zip_code_prefix

        WHERE strftime('%Y', o.order_purchase_timestamp) = ?
            AND o.order_status = 'delivered'

        GROUP BY State
        ORDER BY Revenue DESC
"""
    df_revenue_by_state = pd.read_sql(revenue_by_state, conn, params = (selected_year,))
    fig.update_geos(fitbounds="locations", visible=False)
    fig = px.choropleth(
        df_revenue_by_state,
        geojson = brazil,
        locations = 'State',
        featureidkey = 'id',
        color = 'Revenue',
        color_continuous_scale = 'Blues',
        projection = 'mercator',
        title = 'Revenue by State')

fig.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig, use_container_width=True)

## Operational Efficiency
# Average Delivery Lead Time by city
st.header('Operational Efficiency')
col9, col10 = st.columns(2)
with col9:
    if selected_year:
        if selected_year == '2016':
            order_threshold = 1
        else:
            order_threshold = 50

        delivery_time_query = """
            SELECT c.customer_city, COUNT(o.order_status) AS total_orders,
                AVG(julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)) AS average_delivery 
            FROM orders AS o
            JOIN customers AS c
            ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
                AND strftime('%Y', o.order_purchase_timestamp) = ?
            GROUP BY c.customer_city
            HAVING total_orders >= ?
            ORDER BY average_delivery DESC
        """
        df_avg_lead_time = pd.read_sql(delivery_time_query, conn, params = (selected_year, order_threshold))
        df_avg_lead_time['customer_city'] = df_avg_lead_time['customer_city'].str.title()
        df_top_10 = df_avg_lead_time.head(10)

        fig = px.bar(df_top_10, x = 'customer_city', y = 'average_delivery',
                    labels = {'customer_city': 'City', 'average_delivery': 'Avg Delivery Lead Time in Days'},
                    title = 'Top 10 Cities with Longest Delivery Lead Times in Days',
                    template = 'plotly_white')
        fig.update_layout(xaxis_tickangle = -30, margin = dict(b = 100))
        st.plotly_chart(fig, use_container_width = True)

        if selected_year == '2016':
            st.info('Olist launched late in the year (October 2016), resulting in very low initial order volume. Only data from October to December 2016 onwards is available.')

# Order Status Distribution
with col10:
    if selected_year:
        order_status_query = """
            SELECT o.order_status AS Status, COUNT(o.order_status) AS Count,
            ROUND(100.0 * COUNT(o.order_status) / SUM(COUNT(o.order_status)) OVER (), 2) AS Percentage
            FROM orders AS o
            WHERE strftime('%Y', o.order_purchase_timestamp) = ?
            GROUP BY Status
            ORDER BY Count
        """
    df_order_status = pd.read_sql(order_status_query, conn, params = (selected_year,))
    fig = px.bar(df_order_status, x = 'Percentage', y = 'Status',
                 title = 'Order Status Distribution',
                 template = 'plotly_white',
                 hover_data={"Percentage": ":.2f",
                             "Count": ":,"})
    fig.update_xaxes(title="Percentage", ticksuffix="%")
    st.plotly_chart(fig, use_container_width = True)

st.header('Key Insights')
if selected_year == '2016':
    st.text("• Processed 266 delivered orders, generating $46,586.33 in revenue during the available October–December 2016 period.")
    st.text("• Achieved a 98.9% on-time delivery rate, demonstrating strong delivery performance, although the 7.90% cancellation rate suggests there is room to improve order fulfilment.")
    st.text("• Customers reported a generally positive shopping experience, with an average review score of 4.01/5.00.")
    st.text("• Revenue was concentrated within the available three-month period, with October contributing the highest monthly revenue among the recorded months.")
    st.text("• Revenue was driven by a small number of product categories, with Fashion Bags & Accessories, Industry, Commerce & Business, and Telephony emerging as the highest-performing categories.")
    st.text("• São Paulo (SP) generated the highest revenue among all Brazilian states, indicating that sales were concentrated in one of Brazil's largest economic regions.")
    st.text("• Delivery lead times varied considerably across cities, with the slowest locations averaging over 60 days, highlighting opportunities to improve logistics efficiency in certain regions.")

if selected_year == '2017':
    st.text("• Processed 43,428 delivered orders, generating $6,922,900.24 in revenue with an average order value of $151.40 for the entire year.")
    st.text("• Achieved a 93.4% on-time delivery rate with significantly low cancellation rate of 0.59%, indicating efficient order fulfilment and reliable logistics operations.")
    st.text("• Customers reported a high level of satisfaction, with an average review score of 4.17/5.00, reflecting a generally positive shopping experience.")
    st.text("• Revenue increased steadily throughout the year and peaked in November, before easing slightly in December, suggesting strong seasonal demand towards the end of the year.")
    st.text("• Books Imported, Small Appliances Home Oven & Coffee, and Cine Photo are among the highest-performing categories in revenue generated.")
    st.text("• São Paulo (SP) remains the state which generated the highest revenue among all Brazilian states, highlighting the Southeast as Olist's strongest market.")
    st.text("• Average delivery lead times varied across cities, with Maceió and Manaus recording the longest delivery times among the top 10 cities, indicating opportunities to improve logistics efficiency.")

if selected_year == '2018':
    st.text("• Processed 52,783 delivered orders, generating $8,452,975.20 in revenue with an average order value of $154.40 during the available period.")
    st.text("• Maintained a 90.7% on-time delivery rate with a 0.62% cancellation rate, indicating consistently reliable order fulfilment despite a slight decline in on-time performance compared to 2017.")
    st.text("• Customers remained highly satisfied, with an average review score of 4.14/5.00, demonstrating consistently positive customer experiences.")
    st.text("• Revenue remained strong throughout the year, peaking between March and May, before gradually declining. As 2018 data is only available until September, later months are not included and annual comparisons should be interpreted with caution.")
    st.text("• Revenue was concentrated in a handful of product categories, with Diapers and Hygiene, Tablets Printing Image, and DVDs Blu-ray generating the highest revenue.")
    st.text("• São Paulo (SP) remained the highest-revenue state by a substantial margin, reinforcing its position as Olist's largest market.")
    st.text("• Average delivery lead times in Manaus and Maceió remain the longest delivery times among the top 10 cities with longest average delivery lead times, highlighting a greater urgency to improve logistics performance in these regions.")

st.header('References')
st.markdown('Data Source: Brazilian Olist E-commerce Dataset (Kaggle)')
st.markdown('Built with: Python • SQLite • Pandas • Plotly • Streamlit')