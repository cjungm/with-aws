from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import time

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_dependency',
    default_args=args,
    schedule_interval=None,
    tags=['wait']
)

def wait_20_sec():
    time.sleep(60)
    
wait_20_sec = PythonOperator(
    task_id='wait_20_sec',
    provide_context=True,
    python_callable=wait_20_sec,
    dag=dag
)