from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
import random




args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='chap_2_assign_1',
    default_args=args,
    schedule_interval=None,
    tags=['subdag']
)

task_list = [DummyOperator(task_id='task_' + str(option), dag=dag) for option in range(1,7)]
