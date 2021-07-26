from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from pprint import pprint
import json

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_xcom',
    default_args=args,
    schedule_interval=None,
    render_template_as_native_obj=True,
    tags=['Jungmin']
)

def push_xcom(**kwargs):
    data_string = {"key1": 1, "key2": 2, "key3": 3}
    kwargs['task_instance'].xcom_push(key='pushed_value', value=data_string)

task_push = PythonOperator(
    task_id="task_push",
    provide_context=True,
    python_callable=push_xcom,
    dag=dag
)

def pull_xcom(**kwargs):
    order_data = kwargs['task_instance'].xcom_pull("task_push", key='pushed_value')
    pprint(order_data)

task_pull = PythonOperator(
    task_id="task_pull", 
    provide_context=True,
    python_callable=pull_xcom,
    dag=dag
)

def pull_xcom_template(order_data):
    pprint(order_data)


task_pull_template = PythonOperator(
    task_id="task_pull_template", 
    op_kwargs={"order_data": "{{ti.xcom_pull('task_push', key='pushed_value')}}"},
    provide_context=True,
    python_callable=pull_xcom_template,
    dag=dag
)

task_push >> [task_pull, task_pull_template]