from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
from airflow.models import TaskInstance
from airflow.providers.amazon.aws.operators.emr_create_job_flow import EmrCreateJobFlowOperator
from airflow.providers.amazon.aws.operators.emr_terminate_job_flow import EmrTerminateJobFlowOperator
from airflow.providers.amazon.aws.sensors.emr_job_flow import EmrJobFlowSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.models import Variable
import boto3
from pprint import pprint

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='mwaa_emr_1',
    default_args=args,
    schedule_interval=None,
    is_paused_upon_creation=False,
    tags=['Jungmin']
)

today = datetime.now().strftime("%Y-%m-%d")

JOB_FLOW_OVERRIDES = {
    'Name': "cjm-emr-from-airflow",
    'LogUri': 's3://cjm-oregon/emr/',
    'ReleaseLabel': 'emr-6.2.0',
    'Instances': {
        'Ec2KeyName': 'cjm-key',
        'Ec2SubnetId': '{Public_Subnet}',
        'KeepJobFlowAliveWhenNoSteps': True,
        'TerminationProtected': False,
        'InstanceGroups': [
            {
                'InstanceRole': 'MASTER',
                "InstanceCount": 1,
                "InstanceType": 'm5.2xlarge',
                "Market": "SPOT",
                "Name": "Master"
            }
        ]
    },
    'Applications': [{'Name': 'Spark'}, {'Name': 'Hadoop'}, {'Name': 'Hive'}],
    'JobFlowRole': 'EMR_EC2_DefaultRole',
    'ServiceRole': 'EMR_DefaultRole',
    'StepConcurrencyLevel': 10,
    'Tags': [
        {
            'Key': 'owner',
            'Value': 'cjm'
        },
        {
            'Key': 'Name',
            'Value': 'cjm-emr-from-airflow'
        },
        {
            'Key': 'expiry-date',
            'Value': today
        }
    ],
    'BootstrapActions': [
        {
            'Name': 'Essential Library Install',
            'ScriptBootstrapAction': {'Path': '{Bootstrap_Script_Path}'}
        }
    ],
    "VisibleToAllUsers": True
}

def check_task(**kwargs):
    # Get execution_date
    execution_date = kwargs['execution_date']
    # Get Dag & Task Info
    dag_instance = kwargs['dag']
    operator_instance = dag_instance.get_task("task_sensor")
    # Task Status
    task_status = TaskInstance(operator_instance, execution_date).current_state()
    if task_status == 'success':
        return "end_task"
    else:
        return "email_task"

def send_email(**kwargs):
    sns = boto3.client('sns', region_name="us-west-2")
    target_arn = Variable.get("SNS_ARN")
    sub = "Airflow Workflow Failed"
    message = "{} EMR WorkFlow Was Failed".format(dag.dag_id)
    # SNS에 게시
    response = sns.publish(
        TargetArn=target_arn,
        Message=message,
        Subject=sub
    )
    pprint(response)

task_create_emr = EmrCreateJobFlowOperator(
    task_id='task_create_emr',
    job_flow_overrides=JOB_FLOW_OVERRIDES,
    aws_conn_id='aws_default',
    emr_conn_id='emr_default',
    dag=dag
)

task_trigger = TriggerDagRunOperator(
    task_id="task_trigger",
    trigger_dag_id="assign_emr_2",
    execution_date="{{ execution_date }}",
    dag=dag
)

task_dag_sensor = ExternalTaskSensor(
    task_id='task_dag_sensor',
    external_dag_id='assign_emr_2',
    execution_date_fn=lambda dt: dt,
    timeout=3600,
    dag=dag
)

task_cluster_terminate = EmrTerminateJobFlowOperator(
    task_id='task_cluster_terminate',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='task_create_emr', key='return_value') }}",
    aws_conn_id='aws_default',
    dag=dag
)

task_sensor = EmrJobFlowSensor(
    task_id='task_sensor',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='task_create_emr', key='return_value') }}",
    aws_conn_id='aws_default',
    dag=dag
)

choice_task = BranchPythonOperator(
    task_id='choice_task',
    python_callable=check_task,
    trigger_rule='one_failed',
    dag=dag,
)

email_task = PythonOperator(
    task_id='email_task',
    provide_context=True,
    python_callable=send_email,
    dag=dag
)

end_task = DummyOperator(
    task_id='end_task',
    dag=dag,
)

task_create_emr >> task_trigger >> task_dag_sensor >> task_cluster_terminate >> task_sensor >> choice_task >> [email_task, end_task]