from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import json

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_render_true',
    default_args=args,
    schedule_interval=None,
    render_template_as_native_obj=True,
    tags=['Jungmin']
)

def return_dict():
    data_string = '{"key1": 1, "key2": 2, "key3": 3}'
    return json.loads(data_string)

task_delivery = PythonOperator(
    task_id="task_delivery",
    provide_context=True,
    python_callable=return_dict,
    dag=dag
)

def print_type(order_data):
    print(type(order_data))

task_print = PythonOperator(
    task_id="task_print", 
    op_kwargs={"order_data": "{{ti.xcom_pull('task_delivery')}}"},
    provide_context=True,
    python_callable=print_type,
    dag=dag
)

task_delivery >> task_print