from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from minio import Minio
from datetime import datetime, timedelta
import pendulum
import polars as pl
import io

# MinIO configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "ecommerce-data"

def get_minio_client():
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

def extract_table(table_name: str, **kwargs):
    execution_date = kwargs['execution_date']
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
    
    # Create PostgreSQL hook
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    
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
    df = pl.read_database(query=query, connection=pg_hook.get_conn())
    
    if len(df) > 0:
        # Convert to parquet bytes
        parquet_buffer = io.BytesIO()
        df.write_parquet(parquet_buffer)
        parquet_buffer.seek(0)
        
        # Save to MinIO
        minio_client = get_minio_client()
        
        # Create bucket if it doesn't exist
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
        
        # Define the object path in MinIO
        object_path = f"{table_name}/{execution_date.strftime('%Y/%m/%d')}/{table_name}.parquet"
        
        # Upload to MinIO
        minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_path,
            data=parquet_buffer,
            length=parquet_buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )
        
        return f"Extracted and saved {len(df)} records from {table_name}"
    return f"No data found for {table_name} on {execution_date}"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'catchup': True,
    'start_date': datetime(2024, 12, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ecommerce_metrics_dag-v2',
    default_args=default_args,
    schedule_interval='@daily',
)

# List of tables to extract
tables = [
    'categories',
    'users',
    'addresses',
    'products',
    'orders',
    'order_items',
    'payments',
    'shipments',
    'reviews',
    'product_views'
]

with dag:
    start_task = EmptyOperator(task_id = 'start_task')
    # Create extraction tasks for each table
    extraction_tasks = []
    with TaskGroup('extract_data') as extract_data :  
        for table in tables:
            task = PythonOperator(
                task_id=f'extract_{table}',
                python_callable=extract_table,
                op_kwargs={'table_name': table},
                provide_context=True,
            )
            extraction_tasks.append(task)
    
    end_task = EmptyOperator(task_id ='end_task')
    
    start_task >> extract_data >> end_task