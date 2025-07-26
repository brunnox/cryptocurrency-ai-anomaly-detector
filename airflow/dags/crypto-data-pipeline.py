from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

sys.path.insert(0, '/opt/airflow/dags')

coingecko_token = os.environ.get('COINGECKO_KEY')
endpoint_url = 'http://172.18.0.3:9000'
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

from src.data_lake.data_collector import CryptoDataCollector
from src.data_lake.lake_manager import BucketManager

default_args = {
    'owner': 'crypto-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'crypto_data_pipeline',
    default_args=default_args,
    description='Cryptocurrency data collection and inserting in data lake pipeline',
    schedule_interval='*/5 * * * *', 
    catchup=False,
    max_active_runs=1,
    tags=['crypto', 'data-lake', 'pipeline'],
)

def collect_data_task(**context):
    
    collector = CryptoDataCollector(
    url="https://api.coingecko.com/api/v3/",
    token=coingecko_token
)
    print(f"Starting data collection at {context['execution_date']}")
    
    data = collector.collect_crypto_data()
    return data

def insert_data_lake_task(**context):

    print(f"Starting lake management at {context['execution_date']}")
    
    data = context['task_instance'].xcom_pull(task_ids='my_collect_task')

    bucket_manager = BucketManager(
        endpoint_url=endpoint_url,
        access_key=aws_access_key_id,
        secret_key=aws_secret_access_key
    )

    result = bucket_manager.store_crypto_data('crypto-data-lake', data)

    return result

collect_data = PythonOperator(
    task_id='my_collect_task',
    python_callable=collect_data_task,
    dag=dag,
)

insert_data_lake = PythonOperator(
    task_id='insert_lake_data', 
    python_callable=insert_data_lake_task,
    dag=dag,
)

collect_data >> insert_data_lake