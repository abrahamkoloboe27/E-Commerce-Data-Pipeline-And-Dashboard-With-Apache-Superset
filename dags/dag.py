from airflow import DAG
from src.utils import *
from airflow.operators.python_operator import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'catchup': True,
    'start_date': datetime(2025, 1, 10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# List of tables to extract
tables = [
    'categories','users','addresses','products','orders','order_items',
    'payments','shipments','reviews','product_views'    ]

with DAG(
    'ecommerce_metrics_dag-v2',
    default_args=default_args,
    schedule_interval='@daily',
    max_active_runs=3,
    tags=['ecommerce', 'data-pipeline'],
    concurrency=3,      # limite à 10 tâches en parallèle pour ce DAG
    ) as dag:
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
    
    insert_date_dim = PythonOperator(
        task_id='insert_date_dim',
        python_callable=insert_date_dim,
        provide_context=True,
        depends_on_past=True
    )   
    
    tables = ['categories', 'users', 'addresses', 'products',
              'orders', 'order_items', 'payments', 'shipments',
              'reviews', 'product_views']
    def create_cleaning_task(table):
        return PythonOperator(
        task_id=f'clean_{table}',
        python_callable=clean_data,
        op_kwargs={'table_name': table},
        provide_context=True,
        )
    with TaskGroup('clean_data') as clean_group:
        cleaning_tasks = [
            create_cleaning_task(table) for table in tables
        ]
    aggregate_daily_data = PythonOperator(
        task_id='aggregate_daily_data',
        python_callable=aggregate_daily_data,
        provide_context=True,
        depends_on_past=True
    )
    end_task = EmptyOperator(task_id ='end_task')
    
    start_task >> extract_data >>cleaning_tasks >>aggregate_daily_data >> insert_date_dim >> end_task