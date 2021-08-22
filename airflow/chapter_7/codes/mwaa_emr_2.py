import airflow
from airflow import DAG
from airflow import settings
from airflow.hooks.base_hook import BaseHook
from airflow.models import Connection
from airflow.operators.python_operator import PythonOperator
from airflow.models.baseoperator import chain
from airflow.models.baseoperator import cross_downstream
import datetime as dt
from datetime import datetime, timedelta
from airflow.providers.apache.hive.hooks.hive import HiveServer2Hook
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

conn_id = "hive_connect"
client = boto3.client('emr', region_name="us-west-2")

def get_cluster_id(**kwargs):
    cluster_id = ""
    kwargs['task_instance'].xcom_push(key='hive_conn', value=conn_id)

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

def make_connection(**kwargs):
    master_dns = ""
    conn_type = "hive_cli"
    cluster_id = kwargs['task_instance'].xcom_pull("task_cluster_id", key='return_value')
    master_dns = client.describe_cluster(
        ClusterId=cluster_id
    )['Cluster']['MasterPublicDnsName']

    session = settings.Session() # get the session
    conn = BaseHook.get_connection(conn_id)
    
    if conn:
        pprint(conn)
        new_query = """
UPDATE connection
SET conn_type={conn_type}, host={host}, login={login}, port={port}
WHERE conn_id={conn_id}""".format(
    conn_type=conn_type,
    host=master_dns,
    login="hadoop",
    port=10000,
    conn_id=conn_id)
        session.query(new_query)
        session.commit()
    else:
        conn = Connection(
                conn_id=conn_id,
                conn_type=conn_type,
                login="hadoop",
                host=master_dns,
                port=10000
        )
        session.add(conn)
        session.commit()

def get_table_schema(**kwargs):
    s3 = boto3.client('s3', region_name="us-west-2")

    r = s3.select_object_content(
        Bucket='cjm-oregon',
        Key='champion/data/Mall_Customers.csv',

        Expression='select s.* from S3Object s limit 2',
        ExpressionType='SQL',
        InputSerialization={'CSV': {}}, 
        OutputSerialization={'JSON': {}}
    )
    for rec in r['Payload']:
        if 'Records' in rec:
            columns = list(json.loads(rec['Records']['Payload'].decode('utf-8').split("\n")[0]).values())
            values = list(json.loads(rec['Records']['Payload'].decode('utf-8').split("\n")[1]).values())

    field_schema = {}
    for column, value in zip(columns, values):
        col_name = '_'.join(char for char in column.split(" ") if char.isalpha())
        col_type = str(type(value))

        if col_type == "<class 'str'>":
            field_schema[col_name]="string"
        elif col_type == "<class 'int'>":
            field_schema[col_name]="int"

    table_info = list(field_schema.items())

    table_query=''
    for info in table_info:
        table_query += info[0] + " " + info[1] + ", "
        
    return table_query

def s3_to_hive(**kwargs):
    table_data = kwargs['task_instance'].xcom_pull("task_get_table_schema", key='return_value')[:-2]
    hql = """CREATE TABLE mall_customers (
{table_info}
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS
INPUTFORMAT
  'com.amazonaws.emr.s3select.hive.S3SelectableTextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://cjm-oregon/champion/emr/data/'
TBLPROPERTIES (
  "s3select.format" = "csv",
  "s3select.headerInfo" = "ignore"
)""".format(table_info=table_data)
    hm = HiveServer2Hook(hiveserver2_conn_id = 'hive_connect')
    hm.run(hql)

DOWNLOAD_STEP = [
    {
        'Name': 'download script from s3',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'aws',
                's3',
                'cp',
                's3://cjm-oregon/champion/emr/step_script/bash_command.sh',
                '/home/hadoop/bash_command.sh'
            ]
        }
    }
]

RUN_BASH_STEP = [
    {
        'Name': 'run bash script',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'bash',
                '/home/hadoop/bash_command.sh'
            ]
        }
    }
]

DATA_TRANSFORM_STEP = [
    {
        'Name': 'csv_to_parquet',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'python3',
                '/home/hadoop/transform_python.py'
            ]
        }
    }
]

FORMAT_TRANSFORM_STEP = [
    {
        'Name': 'csv_to_parquet',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'spark-submit',
                '--deploy-mode', 'client',
                '--master', 'yarn',
                's3://cjm-oregon/champion/emr/step_script/transform_pyspark.py'
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

task_make_connection = PythonOperator(
    task_id='task_make_connection',
    provide_context=True,
    python_callable=make_connection,
    dag=dag
)

task_get_table_schema = PythonOperator(
    task_id='task_get_table_schema',
    provide_context=True,
    python_callable=get_table_schema,
    dag=dag
)

task_s3_to_hive = PythonOperator(
    task_id='task_s3_to_hive',
    provide_context=True,
    python_callable=s3_to_hive,
    dag=dag
)

task_download_step = EmrAddStepsOperator(
    task_id='task_download_step',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    aws_conn_id='aws_default',
    steps=DOWNLOAD_STEP,
    dag=dag
)

sensor_download_step = EmrStepSensor(
    task_id='sensor_download_step',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    step_id="{{ task_instance.xcom_pull('task_download_step', key='return_value')[0] }}",
    aws_conn_id='aws_default',
    dag=dag
)

task_run_bash_step = EmrAddStepsOperator(
    task_id='task_run_bash_step',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    aws_conn_id='aws_default',
    steps=RUN_BASH_STEP,
    dag=dag
)

sensor_run_bash_step = EmrStepSensor(
    task_id='sensor_run_bash_step',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    step_id="{{ task_instance.xcom_pull('task_run_bash_step', key='return_value')[0] }}",
    aws_conn_id='aws_default',
    dag=dag
)

task_data_transform = EmrAddStepsOperator(
    task_id='task_data_transform',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    aws_conn_id='aws_default',
    steps=DATA_TRANSFORM_STEP,
    dag=dag
)

sensor_data_transform = EmrStepSensor(
    task_id='sensor_data_transform',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    step_id="{{ task_instance.xcom_pull('task_data_transform', key='return_value')[0] }}",
    aws_conn_id='aws_default',
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

task_cluster_id >> task_make_connection >> task_get_table_schema
task_get_table_schema >> task_s3_to_hive
task_get_table_schema >> task_download_step >> sensor_download_step >> task_run_bash_step >> sensor_run_bash_step
chain([task_s3_to_hive, sensor_run_bash_step], task_data_transform, sensor_data_transform, task_format_transform, sensor_format_transform)
