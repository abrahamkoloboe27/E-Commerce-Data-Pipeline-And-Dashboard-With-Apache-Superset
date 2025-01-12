from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from minio import Minio
from datetime import datetime, timedelta
import pendulum
import polars as pl

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'catchup': True ,
    'start_date': datetime(2023, 10, 1),
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

# List of metrics with their SQL queries
metrics = {
    'n_user': "SELECT COUNT(*) FROM users WHERE DATE(created_at) = '{{ ds }}';",
    'user_registration_growth': "SELECT DATE_TRUNC('day', created_at) AS registration_date, COUNT(user_id) AS user_count FROM users WHERE DATE(created_at) = '{{ ds }}' GROUP BY registration_date ORDER BY registration_date;",
    # Add all other metrics here...
}

def calculate_and_store_metric(metric_name, sql_query, **context):
    ds = context['ds']
    # Connect to production database
    prod_hook = PostgresHook(postgres_conn_id='prod_db_conn')
    # Execute the query and get the result
    result = prod_hook.get_records(sql_query)
    if result:
        # Connect to analytical database
        analytics_hook = PostgresHook(postgres_conn_id='analytics_db_conn')
        # Prepare the insertion query
        insert_query = f"""
            INSERT INTO {metric_name} (metric_value, date, calculation_time)
            VALUES (%s, %s, CURRENT_TIMESTAMP);
        """
        # Insert the result
        analytics_hook.run(insert_query, parameters=(result[0][0], ds))
    else:
        print(f"No result for metric {metric_name}")

def extract_and_upload_to_minio(**context):
    ds = context['ds']
    # Connect to production database
    prod_hook = PostgresHook(postgres_conn_id='prod_db_conn')
    
    # List of tables to extract
    tables = ['users', 'orders', 'order_items', 'products', 'categories', 'addresses', 'payments', 'shipments', 'reviews', 'product_views']
    
    # Initialize MinIO client
    minio_client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    for table in tables:
        # Extract data from the table
        query = f"SELECT * FROM {table};"
        data = prod_hook.get_pandas_df(query)
        
        # Convert to Polars DataFrame
        df = pl.DataFrame(data)
        
        # Save to Parquet
        parquet_file = f"/dump/{table}_{ds}.parquet"
        df.write_parquet(parquet_file)
        
        # Upload to MinIO
        bucket_name = "ecommerce-data"
        object_name = f"{table}/{ds}.parquet"
        minio_client.fput_object(bucket_name, object_name, parquet_file)
        print(f"Uploaded {object_name} to MinIO bucket {bucket_name}")

# Generate tasks dynamically
metric_tasks = []
for metric, sql in metrics.items():
    task_id = f'calc_{metric}'
    t = PythonOperator(
        task_id=task_id,
        python_callable=calculate_and_store_metric,
        op_kwargs={'metric_name': metric, 'sql_query': sql},
        provide_context=True,
        dag=dag,
    )
    metric_tasks.append(t)

# Task to extract data and upload to MinIO
extract_and_upload_task = PythonOperator(
    task_id='extract_and_upload_to_minio',
    python_callable=extract_and_upload_to_minio,
    provide_context=True,
    dag=dag,
)

# Set task dependencies correctement
for task in metric_tasks:
    task >> extract_and_upload_task