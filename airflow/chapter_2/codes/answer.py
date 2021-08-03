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

# CF_1
# =====================================
# task_list = [DummyOperator(task_id='task_' + str(option), dag=dag) for option in range(1,7)]
# from airflow.models.baseoperator import chain
# chain(task_list[0], [task_list[1], task_list[2]], [task_list[3], task_list[4]], task_list[5])
# =====================================

# CF_2
# =====================================
# task_list = [DummyOperator(task_id='task_' + str(option), dag=dag) for option in range(1,7)]
# from airflow.models.baseoperator import cross_downstream
# task_list[0] >> [task_list[1], task_list[2]]
# cross_downstream([task_list[1], task_list[2]], [task_list[3], task_list[4]])
# [task_list[3], task_list[4]] >> task_list[5]
# =====================================

# CF_3
# Cannot make Taskgroup with defined task
# =====================================
# from airflow.utils.task_group import TaskGroup

# with TaskGroup("case_group", dag=dag) as tasks_group:
#     for idx in range(5, 1, -1):
#         DummyOperator(task_id='task_' + str(idx), dag=dag)

# DummyOperator(task_id='task_1', dag=dag) >> tasks_group >> DummyOperator(task_id='task_6', dag=dag)
# =====================================

# CF_4
# Cannot make Subdag with defined task
# =====================================
from airflow.operators.subdag import SubDagOperator
def subdag(parent_dag_name, child_dag_name, args):
    
    dag_subdag = DAG(
        dag_id=f'{parent_dag_name}.{child_dag_name}',
        default_args=args,
        start_date=datetime(2021,2,22),
        schedule_interval=None
    )

    [DummyOperator(task_id='task_' + str(idx), dag=dag_subdag) for idx in range(5, 1, -1)]

    return dag_subdag

task_subdag = SubDagOperator(
    task_id='task_subdag',
    subdag=subdag("chap_2_assign_1", 'task_subdag', args),
    dag=dag
)

DummyOperator(task_id='task_1', dag=dag) >> task_subdag >> DummyOperator(task_id='task_6', dag=dag)
# =====================================