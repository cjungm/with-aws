from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_jinja_macro',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

task_id = "{{ task_instance.task_id }}"

task_print_id = BashOperator(
    task_id='task_print_id',
    bash_command='echo $TASK_ID',
    dag=dag,
    env={'TASK_ID': task_id}
)

task_print_id