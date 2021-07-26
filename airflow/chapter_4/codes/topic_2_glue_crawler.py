from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import boto3
import time

'''
1. Glue Crawler 생성 및 실행 (S3 Data File)
2. DAG_2 호출 (External Trigger)
3. DAG_2 완료 시까지 상태 체크 (External Sensor)
4. DAG_2에서 생성한 CSV 파일 S3에 Upload (s3://cjm-oregon/champion/data/, `topic_2.csv` 라는 이름으로 수행)
'''

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='topic_2_glue_crawler',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

def create_glue(**kwargs):
    db_name = 'topic-2'
    Variable.set("DB_NAME", db_name)
    client = boto3.client('glue', region_name="us-west-2")
    role_arn = Variable.get("ROLE_ARN")
    crawler_name = 'topic-2-crawler'
    client.create_crawler(
        Name=crawler_name,
        Role=role_arn,
        DatabaseName=db_name,
        Description='Crawler Champion',
        Targets={
            'S3Targets': [
                {
                    'Path': 's3://cjm-oregon/champion/glue/data/'
                }
            ]
        }
    )

    return crawler_name

def start_crawler(**kwargs):
    crawler_name = kwargs['ti'].xcom_pull(key='return_value', task_ids='task_create_glue')
    client = boto3.client('glue', region_name="us-west-2")
    client.start_crawler(
        Name=crawler_name
    )

    Variable.set("CRAWLER_NAME", crawler_name)

    crawler_status = client.get_crawler(
        Name=crawler_name
    )['Crawler']['State']

    while crawler_status != 'READY':
        crawler_status = client.get_crawler(
            Name=crawler_name
        )['Crawler']['State']
        time.sleep(10)
    


task_create_glue = PythonOperator(
    task_id='task_create_glue',
    provide_context=True,
    python_callable=create_glue,
    dag=dag
)

task_start_glue = PythonOperator(
    task_id='task_start_glue',
    provide_context=True,
    python_callable=start_crawler,
    dag=dag
) 

task_trigger = TriggerDagRunOperator(
    task_id="task_trigger",
    trigger_dag_id="topic_2_glue_job",
    execution_date="{{ execution_date }}",
    dag=dag
)

task_dag_sensor = ExternalTaskSensor(
    task_id='task_dag_sensor',
    external_dag_id='topic_2_glue_job',
    execution_date_fn=lambda dt: dt,
    timeout=3600,
    dag=dag
)

task_upload = BashOperator(
    task_id="task_upload",
    bash_command="""COMMIT_LIST=$(aws s3 ls s3://cjm-oregon/champion/glue/output/)
    SAVEIFS=$IFS
    IFS=$' '
    COMMIT_LIST=($COMMIT_LIST)
    IFS=$SAVEIFS
    OBJ='s3://cjm-oregon/champion/glue/output/'${COMMIT_LIST[-1]}
    aws s3 cp $OBJ 's3://cjm-oregon/champion/glue/output/topic-2.csv'""",
    dag=dag
)

task_create_glue >> task_start_glue >> task_trigger >> task_dag_sensor >> task_upload
