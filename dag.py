# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator
from airflow.contrib.sensors.file_sensor import FileSensor

import requests
from datetime import datetime
import pendulum

raw_data_file = 'loan_dataset_{}.csv'.format(datetime.today().strftime('%Y%m%d'))
processed_data_file = raw_data_file.replace('.csv','_processed.csv')

def process_data():
    #Process raw data
    url = 'http://host.docker.internal:8000/api/v1/process?data={}'
    response = requests.post(url.format(raw_data_file))
    print(response.status_code)

def train_model():
    #Train model using processed data
    url = 'http://host.docker.internal:8000/api/v1/train?data={}'
    response = requests.post(url.format(processed_data_file))
    print(response.status_code)

with DAG(
    "pbda_dag",
    default_args={"retries": 2},
    description="PBDA Data Pipeline",
    schedule=None,
    start_date=pendulum.datetime(2023, 1, 1, tz="Asia/Singapore"),
    catchup=False,
    tags=["PBDA"],
) as dag:
    
    raw_data_sensor = FileSensor(
        task_id="raw_data_sensor",
        fs_conn_id="data_path",
        filepath=raw_data_file,
        poke_interval=5,
        timeout=60
    )
    
    call_data_process_api = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )
    
    processed_data_sensor = FileSensor(
        task_id="processed_data_sensor",
        fs_conn_id="data_path",
        filepath=processed_data_file,
        poke_interval=5,
        timeout=60
    )
    
    call_train_model_api = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
    )
    
    raw_data_sensor >> call_data_process_api >> processed_data_sensor >> call_train_model_api
    
    