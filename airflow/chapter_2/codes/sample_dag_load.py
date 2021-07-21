from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
import random

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag_1 = DAG(
    dag_id='sample_dag_load',
    default_args=args,
    schedule_interval=None,
    tags=['dag_load']
)

dag_2 = DAG(
    dag_id='sample_dag_load_2',
    default_args=args,
    schedule_interval=None,
    tags=['dag_load_2']
)

task_follow_dag_1 = DummyOperator(task_id='task_follow_dag_1', dag=dag_1)
task_follow_dag_2 = DummyOperator(task_id='task_follow_dag_2', dag=dag_2)

task_follow_dag_1 >> task_follow_dag_2