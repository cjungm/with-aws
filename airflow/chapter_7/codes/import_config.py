from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Connection
from airflow import settings
from airflow.hooks.base_hook import BaseHook
from datetime import datetime, timedelta
import boto3
import json

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='import_config',
    default_args=args,
    schedule_interval=None,
    # 하단 옵션으로 dag에 대한 scheduler를 기본적으로 on 상태 시킵니다.
    # web ui에서 toggle 버튼을 킬 필요가 없습니다.
    is_paused_upon_creation=False,
    tags=['Jungmin']
)

def list_connections(**context):
    session = settings.Session()
    query_result = session.query(Connection).all()
    conn_list = [result.conn_id for result in query_result]
    with open('/tmp/conn_all.json') as json_file:
        import_conn = json.load(json_file)
        for conn_id, conn in zip(list(import_conn.keys()), query_result):
            session = settings.Session()
            if conn_id in conn_list:
                print("already exist. delete first.")
                # update api가 따로 존재하지 않으므로 query를 통해 meta db에 직접 update하면 됩니다.
                new_query = """
UPDATE connection
SET conn_type={conn_type}, description={description}, host={host}, login={login}, password={password}, schema={schema}, port={port}, extra={extra} 
WHERE conn_id={conn_id}""" .format(
    conn_type=import_conn[conn_id]["conn_type"],
    description=import_conn[conn_id]["description"],
    host=import_conn[conn_id]["host"],
    login=import_conn[conn_id]["login"],
    password=import_conn[conn_id]["password"],
    schema=import_conn[conn_id]["schema"],
    port=import_conn[conn_id]["port"],
    extra=import_conn[conn_id]["extra"],
    conn_id=conn_id)
                session.query(new_query)
                session.commit()
                print(conn_id, " deleted")
            else:
                new_conn = Connection(
                    conn_id=conn_id,
                    conn_type=import_conn[conn_id]["conn_type"],
                    description=import_conn[conn_id]["description"],
                    host=import_conn[conn_id]["host"],
                    login=import_conn[conn_id]["login"],
                    password=import_conn[conn_id]["password"],
                    schema=import_conn[conn_id]["schema"],
                    port=import_conn[conn_id]["port"],
                    extra=import_conn[conn_id]["extra"]
                )

                session.add(new_conn)
                session.commit()

task_var_down = BashOperator(
    task_id="task_var_down",
    bash_command="""aws s3 cp s3://cjm-oregon/champion/mwaa/dags/var_all.json /tmp/
aws s3 cp s3://cjm-oregon/champion/mwaa/dags/conn_all.json /tmp/""",
    dag=dag
)

task_var_import = BashOperator(
    task_id="task_var_import",
    bash_command= "airflow variables import /tmp/var_all.json",
    dag=dag
)

list_conn = PythonOperator(
    task_id='list_conn',
    python_callable=list_connections,
    provide_context=True,
    dag=dag
)

task_var_down >> task_var_import >> list_conn