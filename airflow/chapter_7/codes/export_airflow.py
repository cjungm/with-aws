from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.models import Variable
from datetime import datetime, timedelta


args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='export_airflow',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

task_var_export = BashOperator(
    task_id="task_var_export",
    bash_command="airflow variables export /home/ec2-user/airflow/dags/var_all.json",
    dag=dag
)

task_conn_export = BashOperator(
    task_id="task_conn_export",
    bash_command="airflow connections export --format json /home/ec2-user/airflow/dags/conn_all.json",
    dag=dag
)

task_requirements_export = BashOperator(
    task_id="task_requirements_export",
    bash_command="pip3 freeze > /home/ec2-user/requirements.txt",
    dag=dag
)

task_dag_copy = BashOperator(
    task_id="task_dag_copy",
    bash_command="aws s3 cp /home/ec2-user/airflow/dags/ s3://cjm-oregon/champion/mwaa/dags/ --recursive --exclude '*.pyc'",
    dag=dag
)

task_requirements_copy = BashOperator(
    task_id="task_requirements_copy",
    bash_command="aws s3 cp /home/ec2-user/requirements.txt s3://cjm-oregon/champion/mwaa/requirements/",
    dag=dag
)

task_trigger = TriggerDagRunOperator(
    task_id="task_trigger",
    trigger_dag_id="mwaa_mig",
    execution_date="{{ execution_date }}",
    dag=dag
)

task_var_export >> task_conn_export >> task_requirements_export >> task_dag_copy >> task_requirements_copy >> task_trigger