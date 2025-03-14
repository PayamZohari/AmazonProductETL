import pandas as pd
from sqlalchemy import create_engine, text
import re
import numpy as np
from pymongo import MongoClient
from decouple import config

# Read database connection details from environment variables using decouple
POSTGRES_HOST = config("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = config("POSTGRES_PORT", default="5436")
POSTGRES_USER = config("POSTGRES_USER", default="daria")
POSTGRES_PASS = config("POSTGRES_PASS", default="daria1234")
POSTGRES_DB = config("POSTGRES_DB", default="products")

MONGO_HOST = config("MONGO_HOST", default="localhost")
MONGO_PORT = config("MONGO_PORT", default="27017")
MONGO_USER = config("MONGO_USER", default="daria")
MONGO_PASS = config("MONGO_PASS", default="daria1234")
MONGO_DB = config("MONGO_DB", default="Amazon")
MONGO_COLLECTION = config("MONGO_COLLECTION", default="Products")

# Create PostgreSQL database connection
engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

# Load the Excel file
file_path = "../Amazon-Products - online.xlsx"  # Replace with actual file path
df = pd.read_excel(file_path)

# Data Cleaning: Convert column names to match the database schema
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Function to clean price values
def clean_price(price):
    if isinstance(price, str):  # Ensure price is a string before cleaning
        return float(re.sub(r"[^\d.]", "", price)) if re.search(r"\d", price) else None
    return price  # Return original if already a float

# Apply the cleaning function to price columns
df["discount_price"] = df["discount_price"].apply(clean_price)
df["actual_price"] = df["actual_price"].apply(clean_price)

# Handle NaN values for numerical columns
df["ratings"] = df["ratings"].replace({np.nan: None})
df["no_of_ratings"] = df["no_of_ratings"].replace({np.nan: None})

# Establish a database connection to PostgreSQL
with engine.connect() as conn:
    # Truncate tables before inserting new data
    conn.execute(text("TRUNCATE TABLE sales, product_price, product RESTART IDENTITY CASCADE;"))
    conn.commit()

# Insert into Product table
product_df = df[['name', 'main_category', 'sub_category', 'image', 'link']].drop_duplicates().copy()
product_df.insert(0, 'product_id', range(1, len(product_df) + 1))  # Generating primary key
product_df.to_sql('product', engine, if_exists='append', index=False)

# Create a mapping of product_id for foreign key relations
product_mapping = product_df.set_index('name')['product_id'].to_dict()

# Insert into Product Price table
price_df = df[['name', 'discount_price', 'actual_price']].copy()
price_df['product_id'] = price_df['name'].map(product_mapping)
price_df.drop(columns=['name'], inplace=True)
price_df.insert(0, 'price_id', range(1, len(price_df) + 1))

# Use ON CONFLICT DO NOTHING to avoid duplicate key errors
with engine.connect() as conn:
    for _, row in price_df.iterrows():
        conn.execute(
            text("""
                INSERT INTO product_price (price_id, product_id, discount_price, actual_price)
                VALUES (:price_id, :product_id, :discount_price, :actual_price)
                ON CONFLICT DO NOTHING;
            """),
            row.to_dict()
        )
    conn.commit()

# Insert into Sales table
sales_df = df[['name', 'ratings', 'no_of_ratings', 'date']].copy()
sales_df['product_id'] = sales_df['name'].map(product_mapping)
sales_df.drop(columns=['name'], inplace=True)
sales_df.insert(0, 'sales_id', range(1, len(sales_df) + 1))

# Use ON CONFLICT DO NOTHING to avoid duplicate key errors
with engine.connect() as conn:
    for _, row in sales_df.iterrows():
        conn.execute(
            text("""
                INSERT INTO sales (sales_id, product_id, ratings, no_of_ratings, date)
                VALUES (:sales_id, :product_id, :ratings, :no_of_ratings, :date)
                ON CONFLICT DO NOTHING;
            """),
            row.to_dict()
        )
    conn.commit()

print("Data successfully loaded into PostgreSQL")

# Now, insert the cleaned data into MongoDB
mongo_client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}")
mongo_db = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]

# Prepare data for MongoDB
mongo_data = df.copy()
mongo_data['product_id'] = mongo_data['name'].map(product_mapping)
mongo_data = mongo_data.drop(columns=['name'])  # Drop name column if not needed

# Insert into MongoDB
mongo_collection.insert_many(mongo_data.to_dict('records'))

print("Data successfully loaded into MongoDB")