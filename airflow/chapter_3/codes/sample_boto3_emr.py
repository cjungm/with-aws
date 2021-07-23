from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import boto3

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='sample_boto3_emr',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

today = datetime.now().strftime("%Y-%m-%d")

def create_emr(**kwargs):
    client = boto3.client('emr', region_name = "us-west-2")
    response = client.run_job_flow(
        Name= "cjm-emr-from-airflow",
        LogUri= 's3://cjm-oregon/emr/',
        ReleaseLabel= 'emr-5.28.1',
        Instances= {
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
        Applications= [{'Name': 'Spark'}, {'Name': 'Hadoop'}, {'Name': 'Hive'}],
        JobFlowRole= 'EMR_EC2_DefaultRole',
        ServiceRole= 'EMR_DefaultRole',
        StepConcurrencyLevel= 10,
        Tags= [
            {
                'Key': 'owner',
                'Value': 'cjm'
            },
            {
                'Key': 'Name',
                'Value': 'cjm-airflow'
            },
            {
                'Key': 'expiry-date',
                'Value': today
            }
        ],
        BootstrapActions= [],
        VisibleToAllUsers= True
    )

    return response['JobFlowId']


task_create_emr = PythonOperator(
    task_id='task_create_emr',
    provide_context=True,
    python_callable=create_emr,
    dag=dag
)
