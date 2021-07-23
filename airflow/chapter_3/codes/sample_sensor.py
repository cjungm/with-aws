import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import datetime as dt
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.operators.emr_add_steps import EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr_step import EmrStepSensor
from airflow.providers.amazon.aws.operators.emr_terminate_job_flow import EmrTerminateJobFlowOperator
from airflow.providers.amazon.aws.sensors.emr_job_flow import EmrJobFlowSensor
import boto3


args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_sensor',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

def get_cluster_id(**kwargs):
    client = boto3.client('emr', region_name = "us-west-2")

    response = client.list_clusters(
        CreatedAfter=datetime(2000, 1, 1),
        CreatedBefore=datetime(3000, 1, 1),
        ClusterStates=['RUNNING', 'WAITING']
    )

    for cluster in response['Clusters']:
        if cluster['Name'] == 'cjm-emr-from-airflow':
            return cluster['Id']

task_cluster_id = PythonOperator(
    task_id='task_cluster_id',
    provide_context=True,
    python_callable=get_cluster_id,
    dag=dag
)

date = "{{ ds }}"

FIRST_STEP = [
    {
        'Name': 'create test file',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'bash',
                '-c',
                'echo "this is from airflow" > /home/hadoop/' + date + '.txt'
            ]
        }
    }
]

task_step_add_first_step = EmrAddStepsOperator(
    task_id='task_step_add_first_step',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    aws_conn_id='aws_default',
    steps=FIRST_STEP,
    dag=dag
)

task_step_check_first_step = EmrStepSensor(
    task_id='task_step_check_first_step',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    step_id="{{ task_instance.xcom_pull('task_step_add_first_step', key='return_value')[0] }}",
    aws_conn_id='aws_default',
    dag=dag
)

SECOND_STEP = [
    {
        'Name': 'upload test file to s3',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'aws',
                's3',
                'cp',
                '/home/hadoop/' + date + '.txt',
                's3://cjm-oregon/champion/' + date + '.txt'
            ]
        }
    }
]

task_step_add_second_step = EmrAddStepsOperator(
    task_id='task_step_add_second_step',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    aws_conn_id='aws_default',
    steps=SECOND_STEP,
    dag=dag
)

task_step_check_second_step = EmrStepSensor(
    task_id='task_step_check_second_step',
    job_flow_id="{{ task_instance.xcom_pull('task_cluster_id', key='return_value') }}",
    step_id="{{ task_instance.xcom_pull('task_step_add_second_step', key='return_value')[0] }}",
    aws_conn_id='aws_default',
    dag=dag
)

task_cluster_terminate = EmrTerminateJobFlowOperator(
    task_id='task_cluster_terminate',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='task_cluster_id', key='return_value') }}",
    aws_conn_id='aws_default',
    dag=dag
)

task_sensor = EmrJobFlowSensor(
    task_id='task_sensor',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='task_cluster_id', key='return_value') }}",
    aws_conn_id='aws_default',
    dag=dag
)

task_cluster_id >> task_step_add_first_step >> task_step_check_first_step >> task_step_add_second_step >> task_step_check_second_step >> task_cluster_terminate >> task_sensor