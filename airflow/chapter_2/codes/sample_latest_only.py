from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.models.baseoperator import chain
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.utils.dates import days_ago
import random

args = {
    'owner': 'Jungmin',
    'start_date': days_ago(3)
}

dag = DAG(
    dag_id='sample_latest_only',
    default_args=args,
    schedule_interval=None,
    tags=['latest']
)

start_task = DummyOperator(
    task_id='start_task',
    dag=dag
)


latest_only = LatestOnlyOperator(
    task_id='latest_only',
    dag=dag
)

every_task = DummyOperator(
    task_id='every_task',
    dag=dag
)

latest_end_task = BashOperator(
    task_id='latest_end_task',
    bash_command='echo "execution_date={{ execution_date }}"',
    dag=dag
)

every_end_task = BashOperator(
    task_id='every_end_task',
    bash_command='echo "execution_date={{ execution_date }}"',
    dag=dag
)

chain(start_task, [latest_only, every_task], [latest_end_task, every_end_task])

