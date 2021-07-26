from airflow.models import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from datetime import datetime, timedelta
import boto3

'''
1. S3로부터 Data Download (s3://cjm-oregon/champion/data/Mall_Customers.csv)
2. DAG_2 호출 (External Trigger)
3. DAG_2 완료 시까지 상태 체크 (External Sensor)
4. DAG_2에서 생성한 CSV 파일 S3에 Upload (s3://cjm-oregon/champion/data/, `topic_1.csv` 라는 이름으로 수행)
'''

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='topic_1_s3',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

def download_data(**kwargs):
    s3 = S3Hook('aws_conn')
    obj = s3.get_key(
        key='champion/data/Mall_Customers.csv',
        bucket_name='cjm-oregon'
    )
    obj.download_file('/home/ec2-user/data.csv')

def upload_data(**kwargs):
    s3 = S3Hook('aws_conn')
    s3.load_file(
        '/home/ec2-user/topic_1.csv',
        key='champion/output/topic_1.csv',
        bucket_name='cjm-oregon'
    )

task_download = PythonOperator(
    task_id='task_download',
    provide_context=True,
    python_callable=download_data,
    dag=dag
)

task_trigger = TriggerDagRunOperator(
    task_id="task_trigger",
    trigger_dag_id="topic_1_ddb",
    execution_date="{{ execution_date }}",
    dag=dag
)

task_dag_sensor = ExternalTaskSensor(
    task_id='task_dag_sensor',
    external_dag_id='topic_1_ddb',
    execution_date_fn=lambda dt: dt,
    timeout=3600,
    dag=dag
)

task_upload = PythonOperator(
    task_id='task_upload',
    provide_context=True,
    python_callable=upload_data,
    dag=dag
)

task_download >> task_trigger >> task_dag_sensor >> task_upload