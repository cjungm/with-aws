from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
import random

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_subdag',
    default_args=args,
    tags=['subdag']
)

for option in range(1,7):
    DummyOperator(task_id='task_' + str(option), dag=dag)
