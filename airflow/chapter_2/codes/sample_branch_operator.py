from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import random

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_branch_operator',
    default_args=args,
    schedule_interval=None,
    tags=['branch']
)

first_task = DummyOperator(
    task_id='first_task',
    dag=dag,
)

options = ['branch_a', 'branch_b', 'branch_c', 'branch_d']
txt_file = '/home/ec2-user/test.txt'

def decide_which_path():
    next_task = random.choice(options)
    if next_task == "end_task":
        f = open(txt_file, mode='wt', encoding='utf-8')
        f.write('Branch by Condition')
        return next_task
    else:
        return next_task

choice_task = BranchPythonOperator(
    task_id='choice_task',
    python_callable=decide_which_path,
    dag=dag,
)

def print_context():
    r = open(txt_file, mode='rt', encoding='utf-8')
    print(r.readline())

end_task = PythonOperator(
    task_id='end_task',
    provide_context=True,
    python_callable=print_context,
    trigger_rule='all_done',
    dag=dag
)

task_list = [BashOperator(task_id=option, bash_command="echo \'" + option + " done\' > " + txt_file, dag=dag) for option in options]

first_task >> choice_task >> task_list >> end_task