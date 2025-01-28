from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

from src.utils import *

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

dag = DAG(
    'ecommerce_metrics_dag-v1',
    default_args=default_args,
    schedule_interval='@daily',
    max_active_runs=3,
    tags=['ecommerce', 'data-pipeline'],
    concurrency=3,      # limite à 10 tâches en parallèle pour ce DAG

)

# List of tables to extract
tables = [
    'categories','users','addresses','products','orders','order_items',
    'payments','shipments','reviews','product_views'    ]

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