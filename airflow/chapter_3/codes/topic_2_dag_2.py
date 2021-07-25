from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.models import Variable
from airflow.exceptions import AirflowFailException
import argparse
import boto3
import csv
import time

'''
1. DAG_1에서 생성한 Glue_Catalog_Table 을 glue job으로 `Spending Score (1-100)`을 오름차순으로 하는 데이터 추출
2. 추출한 Data를 Local File System에 CSV 형태로 저장
'''

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='topic_2_dag_2',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

client = boto3.client('glue', region_name="us-west-2")

def create_job(**kwargs):
    role_arn = Variable.get("ROLE_ARN")
    job_name = client.create_job(
        Name='cjm-champ',
        Description='Catalog Data Transform',
        Role=role_arn,
        Command={
            'Name': 'glueetl',
            'ScriptLocation': 's3://cjm-oregon/champion/glue/sort_data_by_glue.py'
        },
        DefaultArguments={
            '--S3_KEY': 's3://cjm-oregon/champion/glue/output/'
        },
        Tags={
            'Owner': 'champion'
        },
        GlueVersion='2.0',
    )['Name']

    return job_name

def start_job(**kwargs):
    job_name = kwargs['ti'].xcom_pull(key='return_value', task_ids='task_create_job')
    job_run_id = client.start_job_run(
        JobName=job_name,
    )['JobRunId']

    return job_run_id

def check_job(**kwargs):
    job_name = kwargs['ti'].xcom_pull(key='return_value', task_ids='task_create_job')
    job_id = kwargs['ti'].xcom_pull(key='return_value', task_ids='task_start_job')
    status = client.get_job_run(
        JobName=job_name,
        RunId=job_id,
        PredecessorsIncluded=True|False
    )['JobRun']['JobRunState']
    
    while status not in ['STOPPED', 'SUCCEEDED', 'FAILED', 'TIMEOUT']:
        time.sleep(10)
        status = client.get_job_run(
            JobName=job_name,
            RunId=job_id,
            PredecessorsIncluded=True|False
        )['JobRun']['JobRunState']
    
    if status != 'SUCCEEDED':
        raise AirflowFailException('Glue Job Failed')

task_create_job = PythonOperator(
    task_id='task_create_job',
    provide_context=True,
    python_callable=create_job,
    dag=dag
)

task_start_job = PythonOperator(
    task_id='task_start_job',
    provide_context=True,
    python_callable=start_job,
    dag=dag
)

task_check_job = PythonOperator(
    task_id='task_check_job',
    provide_context=True,
    python_callable=check_job,
    dag=dag
)

task_create_job >> task_start_job >> task_check_job