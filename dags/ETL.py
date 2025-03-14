from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
import pandas as pd
import psycopg2
from pymongo import MongoClient
from decouple import config

# Default arguments for the DAG
default_args = {
    'owner': 'payam',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Create a DAG instance
with DAG(
    'postgres_to_mongodb',
    default_args=default_args,
    description='Extract data from PostgreSQL, transform it, and load it into MongoDB',
    schedule_interval='@once',
    start_date=datetime(2023, 3, 14),
    catchup=False,
) as dag:

    # PostgreSQL connection parameters from environment variables
    pg_conn_params = {
        'dbname': config('PG_DBNAME'),
        'user': config('PG_USER'),
        'password': config('PG_PASSWORD'),
        'host': config('PG_HOST'),
        'port': config('PG_PORT')
    }

    # MongoDB connection parameters from environment variables
    mongo_client = MongoClient(config('MONGO_URI'))
    mongo_db = mongo_client[config('MONGO_DB')]  # Use MongoDB database name from .env
    mongo_collection = mongo_db[config('MONGO_COLLECTION')]  # Use MongoDB collection name from .env

    @task
    def extract_data():
        """Extract data from PostgreSQL."""
        conn = psycopg2.connect(**pg_conn_params)
        query = """
        SELECT p.name, p.main_category, p.sub_category, p.image, p.link, 
               pp.discount_price, pp.actual_price, s.ratings, s.no_of_ratings, s.date
        FROM Product p
        JOIN Product_Price pp ON p.product_id = pp.product_id
        JOIN Sales s ON p.product_id = s.product_id;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    @task
    def transform_data(df):
        """Transform the data according to specified requirements."""
        # Format float values to one decimal place
        df['discount_price'] = df['discount_price'].astype(float).round(1)
        df['actual_price'] = df['actual_price'].astype(float).round(1)
        df['ratings'] = df['ratings'].astype(float).round(1)
        df['no_of_ratings'] = df['no_of_ratings'].astype(int)

        # Format date to "YYYY-MM-DD"
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')

        # Return transformed DataFrame
        return df

    @task
    def load_data(df):
        """Load the transformed data into MongoDB."""
        records = df.to_dict('records')  # Convert DataFrame to a list of dictionaries
        mongo_collection.insert_many(records)  # Insert records into MongoDB

    # Define task dependencies using the TaskFlow API
    extracted_data = extract_data()
    transformed_data = transform_data(extracted_data)
    load_data(transformed_data)