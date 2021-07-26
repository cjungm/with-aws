from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import boto3
import time



args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_variable',
    default_args=args,
    schedule_interval=None,
    render_template_as_native_obj=True,
    tags=['Jungmin']
)

def set_var(**kwargs):
    Variable.set("TEST", "set_var")

def get_var(**kwargs):
    get_var = Variable.get("TEST")
    print(get_var)
    get_var = '{"new_var":"var_changed"}'
    Variable.set("TEST", get_var)

def new_var(**kwargs):
    get_var = Variable.get("TEST", deserialize_json=True)
    print(type(get_var))
    new_var = Variable.get("TEST", default_var=None)
    print(new_var)

task_set_var = PythonOperator(
    task_id='task_set_var',
    provide_context=True,
    python_callable=set_var,
    dag=dag
)

print_set_var = BashOperator(
    task_id="print_set_var",
    bash_command="echo {{ var.value.TEST }}",
    dag=dag
)

task_get_var = PythonOperator(
    task_id='task_get_var',
    provide_context=True,
    python_callable=get_var,
    dag=dag
)

print_get_var = BashOperator(
    task_id="print_get_var",
    bash_command="echo {{ var.json.TEST }}",
    dag=dag
)

task_new_var = PythonOperator(
    task_id='task_new_var',
    provide_context=True,
    python_callable=new_var,
    dag=dag
)

task_set_var >> print_set_var >> task_get_var >> print_get_var >> task_new_var
