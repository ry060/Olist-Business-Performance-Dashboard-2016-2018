# 📊 Olist Business Performance Dashboard (2016–2018)

An interactive Streamlit dashboard that analyzes the financial performance, customer satisfaction, and operational efficiency of Olist, a Brazilian e-commerce marketplace, using over 100,000 orders from October 2016 to December 2018.

🔗 **Live Demo:** *https://olist-business-performance-dashboard-2016-2018.streamlit.app/*

---

## Overview

Olist is a Brazilian e-commerce technology company that connects merchants to major online marketplaces. This dashboard provides an overview of Olist's marketplace performance from 2016 to 2018 by analysing key business metrics, sales trends, customer reviews and delivery performance.

Users can explore the dashboard by selecting different years to compare business performance across time.

---

## Dashboard Features

### 📈 Business Performance
- Total Orders
- Total Revenue
- Average Order Value
- Number of Customers
- On-Time Delivery Rate
- Average Review Score
- Cancellation Rate

### 📊 Revenue Analysis
- Monthly Revenue Trend
- Top Revenue-Generating Product Categories
- Revenue by Brazilian State (Interactive Choropleth Map)

### 🚚 Operational Efficiency
- Order Status Distribution
- Top 10 Cities with Longest Average Delivery Lead Times

### 📅 Interactive Filtering
- Filter all visualisations by year (2016–2018)

---

## Technologies Used

- Python
- Streamlit
- SQLite
- Pandas
- Plotly Express
- SQL
- JSON (GeoJSON for Brazil state map)

---

## Dataset

This project uses the **Brazilian E-Commerce Public Dataset by Olist**, containing over 100,000 real e-commerce orders made between 2016 and 2018.

Dataset includes:
- Orders
- Customers
- Products
- Payments
- Reviews
- Sellers
- Geolocation
- Product Category Translations

---

## Project Structure

```
Olist-Business-Performance-Dashboard-2016-2018
│
├── data/
│   ├── olist_customers_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   └── product_category_name_translation.csv
│
├── olist_dashboard.py          # Streamlit application
├── olist_db_setup.py           # Creates SQLite database from CSV files
├── br_states.json              # Brazil GeoJSON boundaries
├── requirements.txt
└── README.md
```

---

## Database

To avoid uploading a large SQLite database to GitHub, the application automatically creates `olist.db` during the first run.

`olist_db_setup.py` reads the CSV datasets and loads them into SQLite tables before the dashboard executes its SQL queries.

---

## Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Olist-Business-Performance-Dashboard-2016-2018.git
cd Olist-Business-Performance-Dashboard-2016-2018
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the dashboard

```bash
streamlit run olist_dashboard.py
```

The database will be generated automatically if it does not already exist.
