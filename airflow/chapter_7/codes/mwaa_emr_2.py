import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import datetime as dt
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.operators.emr_add_steps import EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr_step import EmrStepSensor
import boto3
from pprint import pprint
import json
import time

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='mwaa_emr_2',
    default_args=args,
    schedule_interval=None,
    is_paused_upon_creation=False,
    tags=['Jungmin']
)

client = boto3.client('emr', region_name="us-west-2")

def get_cluster_id(**kwargs):
    cluster_id = ""

    response = client.list_clusters(
        CreatedAfter=datetime(2000, 1, 1),
        CreatedBefore=datetime(3000, 1, 1),
        ClusterStates=['STARTING', 'BOOTSTRAPPING', 'RUNNING', 'WAITING']
    )

    for cluster in response['Clusters']:
        if cluster['Name'] == 'cjm-emr-from-airflow':
            cluster_id = cluster['Id']
            break

    emr_status = client.describe_cluster(
        ClusterId=cluster_id
    )['Cluster']['Status']['State']
    
    print(emr_status)
    while emr_status != 'WAITING':
        time.sleep(10)
        emr_status = client.describe_cluster(
            ClusterId=cluster_id
        )['Cluster']['Status']['State']
        print(emr_status)

    return cluster_id

FORMAT_TRANSFORM_STEP = [
    {
        'Name': 'csv_to_parquet',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'spark-submit',
                '--deploy-mode', 'client',
                '--master', 'yarn',
                's3://cjm-oregon/champion/emr/step_script/data_transform_workflow.py'
            ]
        }
    }
]

task_cluster_id = PythonOperator(
    task_id='task_cluster_id',
    provide_context=True,
    python_callable=get_cluster_id,
    dag=dag
)

task_format_transform = EmrAddStepsOperator(
    task_id='task_format_transform',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    aws_conn_id='aws_default',
    steps=FORMAT_TRANSFORM_STEP,
    dag=dag
)

sensor_format_transform = EmrStepSensor(
    task_id='sensor_format_transform',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    step_id="{{ task_instance.xcom_pull('task_format_transform', key='return_value')[0] }}",
    aws_conn_id='aws_default',
    dag=dag
)

task_cluster_id >> task_format_transform >> sensor_format_transform
