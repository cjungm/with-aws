from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.operators.emr_create_job_flow import EmrCreateJobFlowOperator
from airflow.providers.amazon.aws.operators.emr_terminate_job_flow import EmrTerminateJobFlowOperator
from airflow.providers.amazon.aws.sensors.emr_job_flow import EmrJobFlowSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='assign_emr_1',
    default_args=args,
    schedule_interval=None,
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

task_create_emr >> task_trigger >> task_dag_sensor >> task_cluster_terminate >> task_sensor