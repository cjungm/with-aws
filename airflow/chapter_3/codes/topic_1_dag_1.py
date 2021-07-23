from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
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
    dag_id='topic_1_dag_1',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

task_download = BashOperator(
    task_id="task_download",
    bash_command= "aws s3 cp s3://cjm-oregon/champion/data/Mall_Customers.csv /home/ec2-user/data.csv",
    dag=dag
)

task_trigger = TriggerDagRunOperator(
    task_id="task_trigger",
    trigger_dag_id="topic_1_dag_2",
    execution_date="{{ execution_date }}",
    dag=dag
)

task_dag_sensor = ExternalTaskSensor(
    task_id='task_dag_sensor',
    external_dag_id='topic_1_dag_2',
    execution_date_fn=lambda dt: dt,
    timeout=3600,
    dag=dag
)

task_upload = BashOperator(
    task_id="task_upload",
    bash_command= "aws s3 cp /home/ec2-user/topic_1.csv s3://cjm-oregon/champion/data/topic_1.csv",
    dag=dag
)

task_download >> task_trigger >> task_dag_sensor >> task_upload