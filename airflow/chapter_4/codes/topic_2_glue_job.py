from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.operators.glue import AwsGlueJobOperator
from airflow.providers.amazon.aws.sensors.glue import AwsGlueJobSensor
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
    dag_id='topic_2_glue_job',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

role_arn = Variable.get("ROLE_NAME")

task_run_job = AwsGlueJobOperator(
    task_id = 'task_run_job',
    job_name ='cjm-champ',
    script_location='s3://cjm-oregon/champion/glue/sort_data_by_glue.py',
    job_desc="Catalog Data Transform",
    script_args={'--S3_KEY': 's3://cjm-oregon/champion/glue/output/'},
    region_name = "us-west-2",
    iam_role_name = role_arn,
    num_of_dpus=10,
    s3_bucket = 'cjm-oregon',
    retry_limit = 2,
    dag = dag
)

task_check_job = AwsGlueJobSensor(
    task_id='task_check_job',
    job_name = 'cjm-champ',
    run_id = "{{ task_instance.xcom_pull('task_run_job', key='return_value') }}",
    dag = dag
)

task_run_job >> task_check_job