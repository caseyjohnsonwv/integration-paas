from datetime import datetime
import importlib
from re import sub as regex_sub
import sys
from typing import List, Dict
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.models.variable import Variable
import requests

def etl(dag_json:dict):

    source = dag_json['source']
    transformer = dag_json['transformer']
    destination = dag_json['destination']
    importlib.invalidate_caches()
    importlib.import_module(f"transformers.{dag['transformer']['py_file_name']}")

    def extract():
        print('<<<< BEGIN EXTRACT >>>>')
        url = source['url']
        headers = {h['name'] : h['value'] for h in source['headers']}
        resp = requests.get(url, headers=headers)
        print(f"Received status code {resp.status_code} from {url}")
        resp.raise_for_status()
        source_data = resp.json()
        print(f"Source data: {source_data}")
        transform(source_data)

    def transform(source_data:List[Dict]):
        print('<<<< BEGIN TRANSFORM >>>>')
        dest_data = getattr(sys.modules[f"transformers.{transformer['py_file_name']}"], transformer['function_name'])(source_data)
        print(f"Transformed data: {dest_data}")
        load(dest_data)

    def load(payload:List[Dict]):
        print('<<<< BEGIN LOAD >>>>')
        url = destination['url']
        headers = {h['name'] : h['value'] for h in destination['headers']}
        resp = requests.post(url, json=payload, headers=headers)
        print(f"Received status code {resp.status_code} from {url}")
        print(resp.json())
        resp.raise_for_status()

    # kick off etl
    # airflow kinda forces this spaghetti code unfortunately
    extract()



# get current state + target state
dags_json = Variable.get('master_dag_definition', default_var=[], deserialize_json=True)



# create dags from json document
for dag in dags_json:
    dag_id = f"{regex_sub('[^A-Za-z0-9_]+', '_', dag['name'])}_dag"
    with DAG(
        dag_id = dag_id,
        start_date = datetime(2023, 1, 1, 0, 0, 0),
        schedule_interval = dag['cron_schedule'],
        catchup = False,
        max_active_runs = 1,
    ) as _ :
        start_task = EmptyOperator(task_id = 'start_task')
        end_task = EmptyOperator(task_id = 'end_task')
        etl_task = PythonOperator(
            task_id = 'etl_task',
            python_callable = etl,
            op_kwargs = {'dag_json' : dag},
        )
        start_task >> etl_task >> end_task