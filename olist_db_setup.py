import sqlite3
import pandas as pd

connection = sqlite3.connect('olist.db')
customers = pd.read_csv('../data/olist_customers_dataset.csv')
orders = pd.read_csv('../data/olist_orders_dataset.csv')
order_items = pd.read_csv('../data/olist_order_items_dataset.csv')
geolocation = pd.read_csv('../data/olist_geolocation_dataset.csv')
payments = pd.read_csv('../data/olist_order_payments_dataset.csv')
reviews = pd.read_csv('../data/olist_order_reviews_dataset.csv')
products = pd.read_csv('../data/olist_products_dataset.csv')
sellers = pd.read_csv('../data/olist_sellers_dataset.csv')
translation = pd.read_csv('../data/product_category_name_translation.csv')


customers.to_sql('customers', connection, if_exists = 'replace', index = False)
orders.to_sql('orders', connection, if_exists = 'replace', index = False)
order_items.to_sql('order_items', connection, if_exists = 'replace', index = False)
geolocation.to_sql('geolocation', connection, if_exists = 'replace', index = False)
payments.to_sql('payments', connection, if_exists = 'replace', index = False)
reviews.to_sql('reviews', connection, if_exists = 'replace', index = False)
products.to_sql('products', connection, if_exists = 'replace', index = False)
sellers.to_sql('sellers', connection, if_exists = 'replace', index = False)
translation.to_sql('translation', connection, if_exists = 'replace', index = False)


connection.close()
print('Database created successfully.')