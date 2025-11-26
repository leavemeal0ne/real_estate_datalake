import os
from airflow import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.standard.operators.python import PythonOperator
from datetime import date, timedelta, datetime
from FlatParser.FlatParser import FlatsParser
from airflow.models import XCom

def ingest_data(**context):
    logic_date = context['ds'] # str in format `YYYY-MM-DD`
    # transform data in text format to date object
    logic_date_transformed = date.fromisoformat(logic_date) - timedelta(days=1)
    filepath = FlatsParser().create_Kyiv_realty_data_by_date(logic_date_transformed)
    ti = context['ti']
    ti.xcom_push(key='filepath', value=filepath)


def load_file_to_s3(**context):
    hook = S3Hook(aws_conn_id='amazon_s3')
    ti = context['ti']
    filepath = ti.xcom_pull(key='filepath', task_ids='ingest_realty_data')
    hook.load_file(
        filename=filepath,
        bucket_name='realty-datalake',
        key=os.path.basename(filepath),
        replace=True,
    )


def delete_file(**context):
    ti = context['ti']
    filepath = ti.xcom_pull(key='filepath', task_ids='ingest_realty_data')
    os.remove(filepath)


default_args = {
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'realty_datalake_dag',
    start_date=datetime(2025, 11, 15),
    schedule=timedelta(days=1),
    catchup=True,
    default_args=default_args,
    tags=['dev','s3','lake_house']
) as dag:

    ingest_realty_task = PythonOperator(
        task_id='ingest_realty_data',
        python_callable=ingest_data,
    )

    upload_data_task = PythonOperator(
        task_id='upload_realty_data_to_s3',
        python_callable=load_file_to_s3,
    )

    delete_local_data_task = PythonOperator(
        task_id='delete_local_file',
        python_callable=delete_file,
    )

    ingest_realty_task >> upload_data_task >> delete_local_data_task

