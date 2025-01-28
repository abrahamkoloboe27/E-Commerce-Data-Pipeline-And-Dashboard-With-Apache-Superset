import psycopg2
from minio import Minio
import sys
import polars as pl
import io
import logging
import time
logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('airflow_logs.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

# MinIO configuration
MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "ecommerce-data"

def get_minio_client():
    connection = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    return connection

def extract_table(table_name: str, **kwargs):
    execution_date = kwargs['execution_date']
    logging.info(f"Extracting data from {table_name} on {execution_date}")
    date_column_mapping = {
        'users': 'created_at',
        'addresses': 'created_at',
        'products': 'created_at',
        'orders': 'order_date',
        'payments': 'payment_date',
        'shipments': 'shipment_date',
        'reviews': 'review_date',
        'product_views': 'view_date'
    }
    
    # Get the appropriate date column for the table
    date_column = date_column_mapping.get(table_name)
    logging.info(f"Date column for {table_name}: {date_column}")
    # Create PostgreSQL hook
    postgres_connection =  psycopg2.connect(
            dbname="e_commerce_database",
            user="postgres",
            password="postgres",
            host="postgres-prod",
            port="5432"
        )
    
    # Construct query based on whether table has date column
    if date_column:
        query = f"""
            SELECT * FROM {table_name} 
            WHERE DATE({date_column}) = DATE('{execution_date}')
        """
    else:
        # For tables without date columns (like categories), get all records
        query = f"SELECT * FROM {table_name}"

    # Execute query and get data as Polars DataFrame
    df = pl.read_database(query=query, connection=postgres_connection)
    logging.info(f"Extracted {len(df)} records from {table_name}")
    logging.info(f"Extracted data: {df.head()}")
    
    if len(df) > 0:
        # Convert to parquet bytes
        parquet_buffer = io.BytesIO()
        logging.info(f"Writing {len(df)} records to parquet")
        df.write_parquet(parquet_buffer)
        logging.info(f"Finished writing {len(df)} records to parquet")
        parquet_buffer.seek(0)
        
        # Save to MinIO
        minio_client = get_minio_client()
        logging.info(f"Uploading {len(df)} records to MinIO")
        
        # Create bucket if it doesn't exist
        if not minio_client.bucket_exists(MINIO_BUCKET):
            logging.info(f"Creating bucket {MINIO_BUCKET}")
            minio_client.make_bucket(MINIO_BUCKET)
        
        # Define the object path in MinIO
        object_path = f"{table_name}/{execution_date.strftime('%Y/%m/%d')}/{table_name}.parquet"
        logging.info(f"Uploading to {object_path}")
        
        # Upload to MinIO
        try:
            minio_client.put_object(
                bucket_name=MINIO_BUCKET,
                object_name=object_path,
                data=parquet_buffer,
                length=parquet_buffer.getbuffer().nbytes,
                content_type='application/octet-stream'
            )
        except Exception as e:
            time.sleep(5)
            logging.error(f"Connection failed: {e}. Retrying...")
            minio_client = get_minio_client()
            minio_client.put_object(
                bucket_name=MINIO_BUCKET,
                object_name=object_path,
                data=parquet_buffer,
                length=parquet_buffer.getbuffer().nbytes,
                content_type='application/octet-stream'
            )
        logging.info(f"Uploaded {len(df)} records to MinIO")
        
        return f"Extracted and saved {len(df)} records from {table_name}"
    else : 
        return f"No data found for {table_name} on {execution_date}"
