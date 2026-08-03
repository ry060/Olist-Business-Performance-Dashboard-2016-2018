from pathlib import Path
import sqlite3
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "olist.db"


def create_database() -> None:
    """Create and populate the SQLite database from the Olist CSV files."""

    tables = {
        "customers": "olist_customers_dataset.csv",
        "orders": "olist_orders_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "geolocation": "olist_geolocation_dataset.csv",
        "payments": "olist_order_payments_dataset.csv",
        "reviews": "olist_order_reviews_dataset.csv",
        "products": "olist_products_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "translation": "product_category_name_translation.csv",
    }

    connection = sqlite3.connect(DB_PATH)

    try:
        for table_name, filename in tables.items():
            csv_path = DATA_DIR / filename

            if not csv_path.exists():
                raise FileNotFoundError(
                    f"Missing required CSV file: {csv_path}"
                )

            print(f"Loading {filename} into table '{table_name}'...")

            dataframe = pd.read_csv(csv_path)

            dataframe.to_sql(
                table_name,
                connection,
                if_exists="replace",
                index=False,
            )

        connection.commit()
        print("Database created successfully.")

    except Exception:
        connection.rollback()

        # Remove an incomplete database so the app can retry cleanly.
        connection.close()

        if DB_PATH.exists():
            DB_PATH.unlink()

        raise

    else:
        connection.close()


if __name__ == "__main__":
    create_database()