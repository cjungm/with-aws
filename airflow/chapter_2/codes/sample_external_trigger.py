from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from datetime import datetime, timedelta
import random

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_external_trigger',
    default_args=args,
    schedule_interval=None,
    tags=['external_trigger']
)

task_start = DummyOperator(task_id='start_task', dag=dag)

task_trigger = TriggerDagRunOperator(
    task_id="task_trigger",
    trigger_dag_id="sample_dependency",
    execution_date="{{ execution_date }}",
    dag=dag
)

task_sensor = ExternalTaskSensor(
    task_id='task_sensor',
    external_dag_id='sample_dependency',
    external_task_id='wait_20_sec',
    execution_date_fn=lambda x: x,
    timeout=3600,
    dag=dag
)

task_start >> task_trigger >> task_sensor
