from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.operators.emr_create_job_flow import EmrCreateJobFlowOperator
from airflow.providers.amazon.aws.sensors.emr_job_flow import EmrJobFlowSensor

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_emr_create',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

today = datetime.now().strftime("%Y-%m-%d")

JOB_FLOW_OVERRIDES = {
    'Name': "cjm-emr-from-airflow",
    'LogUri': 's3://cjm-oregon/emr/',
    'ReleaseLabel': 'emr-5.28.1',
    'Instances': {
        'Ec2KeyName': 'cjm-key',
        'Ec2SubnetId': 'subnet-08f17a12a46396972',
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
 