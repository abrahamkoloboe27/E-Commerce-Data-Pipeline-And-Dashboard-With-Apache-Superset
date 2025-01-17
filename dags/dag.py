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

# Extract the tables 
def extract_table(table_name:str , **kwargs):
    execution_date = kwargs['execution_date']
    query = f"SELECT * FROM {table_name} WHERE date = '{execution_date}'"

with dag:
    pass