from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models.baseoperator import chain
from airflow.operators.subdag import SubDagOperator
from airflow.models.baseoperator import cross_downstream
from airflow.exceptions import AirflowSkipException
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

task_start = DummyOperator(task_id='start_task', dag=dag)

task_list = [DummyOperator(task_id='task_success_' + str(option), dag=dag) for option in range(1,5)]

def make_skip(**kwargs):
    raise AirflowSkipException("Skip this task and individual downstream tasks while respecting trigger rules.")

def make_fail(**kwargs):
    raise ValueError('Make Error Force')

def subdag(parent_dag_name, child_dag_name, args):

    dag_subdag = DAG(
        dag_id=f'{parent_dag_name}.{child_dag_name}',
        default_args=args,
        start_date=datetime(2021,2,22),
        schedule_interval=None
    )

    task_skipped = PythonOperator(task_id='task_skipped', provide_context=True, python_callable=make_skip, dag=dag_subdag)
    task_failed = PythonOperator(task_id='task_failed', provide_context=True, python_callable=make_fail, dag=dag_subdag)
    task_all_success = DummyOperator(task_id='task_all_success', trigger_rule='all_success', dag=dag_subdag)
    task_all_failed = DummyOperator(task_id='task_all_failed', trigger_rule='all_failed', dag=dag_subdag)
    task_one_success = DummyOperator(task_id='task_one_success', trigger_rule='one_success', dag=dag_subdag)
    task_none_failed = DummyOperator(task_id='task_none_failed', trigger_rule='none_failed', dag=dag_subdag)
    task_none_failed_or_skipped = DummyOperator(task_id='task_none_failed_or_skipped', trigger_rule='none_failed_or_skipped', dag=dag_subdag)
    task_one_failed = DummyOperator(task_id='task_one_failed', trigger_rule='one_failed', dag=dag_subdag)

    cross_downstream(from_tasks=[task_all_success, task_skipped, task_failed, task_one_success], \
        to_tasks=[task_none_failed, task_none_failed_or_skipped, task_all_failed, task_one_failed])

    return dag_subdag

task_subdag = SubDagOperator(
    task_id='task_subdag',
    subdag=subdag("sample_subdag", 'task_subdag', args),
    dag=dag
)

task_all_done = DummyOperator(task_id='task_all_done', trigger_rule='all_done', dag=dag)

chain(task_start, task_list, task_subdag, task_all_done)
