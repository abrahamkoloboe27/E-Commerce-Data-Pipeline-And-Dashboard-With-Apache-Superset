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
    'start_date': datetime(2024, 10, 23),
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
    'ecommerce_metrics_dag-v1.0.0',
    default_args=default_args,
    schedule_interval='@daily',
    max_active_runs=5,
    tags=['ecommerce', 'data-pipeline'],
    concurrency=5,     
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
    # aggregate_daily_data = PythonOperator(
    #     task_id='aggregate_daily_data',
    #     python_callable=aggregate_daily_data,
    #     provide_context=True,
    #     depends_on_past=True
    # )
    with TaskGroup("prepare_data") as prepare_data:
        # def dimension_pipeline(**kwargs):
        #     execution_date = kwargs['execution_date']
        #     prepare_and_store_dimensions(execution_date)
        prepare_dimensions_task = PythonOperator(
            task_id='prepare_dimensions_tables',
            python_callable=dimension_pipeline,
            provide_context=True
        )
        aggregate_daily_data = PythonOperator(
        task_id='prepare_fact_tables',
        python_callable=aggregate_daily_data,
        provide_context=True,
        depends_on_past=True
        )
        prepare_dimensions_task >> aggregate_daily_data
    with TaskGroup("insert_data_in_data_warehouse") as insert_data_in_data_warehouse:
        insert_data_in_dimension_table = PythonOperator(
             task_id='insert_data_in_dimension_table',
             python_callable=insert_data_in_dim_tables,
             provide_context=True
         )
        insert_data_in_fact_table = PythonOperator(
             task_id='insert_data_in_fact_table',
             python_callable=fact_pipeline,
             provide_context=True
         )
        insert_data_in_dimension_table >> insert_data_in_fact_table
        
        
    end_task = EmptyOperator(task_id ='end_task')
    
    start_task >> extract_data >>cleaning_tasks >> prepare_data >>insert_data_in_data_warehouse>> end_task