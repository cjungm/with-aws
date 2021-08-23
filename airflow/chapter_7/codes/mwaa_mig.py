# https://docs.aws.amazon.com/mwaa/latest/userguide/access-policies.html#console-full-access
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from pprint import pprint
import json
import argparse
import boto3
import time
import requests
import base64
import re

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='mwaa_mig',
    default_args=args,
    schedule_interval=None,
    render_template_as_native_obj=True,
    tags=['Jungmin']
)

cfn = boto3.client('cloudformation', region_name='us-west-2')
Import_stackname = 'Import-Exist-Resource'
MWAA_stackname = "cjm-cdf"

def get_status(id, stackname):
    status = cfn.describe_change_set(
        ChangeSetName=id,
        StackName=stackname
    )['Status']

    while status != 'CREATE_COMPLETE':
        time.sleep(5)
        status = cfn.describe_change_set(
            ChangeSetName=id,
            StackName=stackname
        )['Status']

def create_stack(**kwargs):
    capabilities = ['CAPABILITY_IAM', 'CAPABILITY_AUTO_EXPAND']
    template_url = Variable.get("FIRST_TEMPLATE_URL")
    stack_param = json.loads(Variable.get("STACK_PARAM"))
    current_ts = datetime.now().isoformat().split('.')[0].replace(':','-')
    try:
        stackdata = cfn.create_change_set(
            StackName=Import_stackname,
            TemplateURL=template_url,
            Capabilities=capabilities,
            ChangeSetName=Import_stackname+"-"+current_ts,
            Description='Import Existing Resource For MWAA',
            ChangeSetType='IMPORT',
            ResourcesToImport=[
                {
                    'ResourceType': 'AWS::EC2::VPC',
                    'LogicalResourceId': 'ImportedVPC',
                    'ResourceIdentifier': {
                        'VpcId': stack_param['VpcId']
                    }
                },
                {
                    'ResourceType': 'AWS::EC2::Subnet',
                    'LogicalResourceId': 'ImportedSubnet1',
                    'ResourceIdentifier': {
                        'SubnetId': stack_param['SubnetId1']
                    }
                },
                {
                    'ResourceType': 'AWS::EC2::Subnet',
                    'LogicalResourceId': 'ImportedSubnet2',
                    'ResourceIdentifier': {
                        'SubnetId': stack_param['SubnetId2']
                    }
                },
                {
                    'ResourceType': 'AWS::EC2::SecurityGroup',
                    'LogicalResourceId': 'ImportedSecurityGroup',
                    'ResourceIdentifier': {
                        'GroupId': stack_param['GroupId']
                    }
                },
                {
                    'ResourceType': 'AWS::S3::Bucket',
                    'LogicalResourceId': 'ImportedBucket',
                    'ResourceIdentifier': {
                        'BucketName': stack_param['BucketName']
                    }
                },
                {
                    'ResourceType': 'AWS::IAM::Role',
                    'LogicalResourceId': 'ImportedRole',
                    'ResourceIdentifier': {
                        'RoleName': stack_param['RoleName']
                    }
                },
            ]
        )
    except Exception as e:
        print(str(e))
    return stackdata
  
def launch_first_stack(**kwargs):
    stackdata = kwargs['task_instance'].xcom_pull("task_create_stack", key='return_value')
    pprint(stackdata)

    get_status(stackdata['Id'], Import_stackname)

    response = cfn.execute_change_set(
        ChangeSetName=stackdata['Id'],
        StackName=Import_stackname
    )
    return response

def update_stack(**kwargs):
    stackdata = kwargs['task_instance'].xcom_pull("task_create_stack", key='return_value')

    stack_status = cfn.describe_stacks(
        StackName=stackdata['StackId']
    )['Stacks'][0]['StackStatus']

    while stack_status != 'IMPORT_COMPLETE':
        stack_status = cfn.describe_stacks(
            StackName=stackdata['StackId']
        )['Stacks'][0]['StackStatus']

    capabilities = ['CAPABILITY_IAM', 'CAPABILITY_AUTO_EXPAND']
    template_url = Variable.get("SECOND_TEMPLATE_URL")
    current_ts = datetime.now().isoformat().split('.')[0].replace(':','-')
    try:
        stackdata = cfn.create_change_set(
            StackName=Import_stackname,
            TemplateURL=template_url,
            Capabilities=capabilities,
            ChangeSetName=Import_stackname+"-"+current_ts,
            Description='Import Existing Resource For MWAA',
            ChangeSetType='UPDATE'
        )
    except Exception as e:
        print(str(e))
    return stackdata

def launch_second_stack(**kwargs):
    
    stackdata = kwargs['task_instance'].xcom_pull("task_update_stack", key='return_value')
    pprint(stackdata)

    get_status(stackdata['Id'], Import_stackname)
        
    response = cfn.execute_change_set(
        ChangeSetName=stackdata['Id'],
        StackName=Import_stackname
    )
    return response

def create_mwaa(**kwargs):
    stackdata = kwargs['task_instance'].xcom_pull("task_update_stack", key='return_value')
    role_arn = Variable.get("ROLE_ARN")

    stack_status = cfn.describe_stacks(
        StackName=stackdata['StackId']
    )['Stacks'][0]['StackStatus']

    while stack_status != 'UPDATE_COMPLETE':
        stack_status = cfn.describe_stacks(
            StackName=stackdata['StackId']
        )['Stacks'][0]['StackStatus']

    capabilities = ['CAPABILITY_IAM', 'CAPABILITY_AUTO_EXPAND']
    template_url = Variable.get("MWAA_TEMPLATE_URL")
    try:
        stackdata = cfn.create_stack(
            StackName=MWAA_stackname,
            DisableRollback=True,
            TemplateURL=template_url,
            Capabilities=capabilities,
            RoleARN=role_arn
        )
    except Exception as e:
        print(str(e))
    return stackdata

def trigger_import_dag(**kwargs):
    stackdata = kwargs['task_instance'].xcom_pull("task_create_mwaa", key='return_value')
    pprint(stackdata)

    status = cfn.describe_stacks(
        StackName=stackdata['StackId']
    )['Stacks'][0]['StackStatus']

    while status != 'CREATE_COMPLETE':
        time.sleep(5)
        status = cfn.describe_stacks(
            StackName=stackdata['StackId']
        )['Stacks'][0]['StackStatus']

    resource_id = cfn.describe_stack_resources(
        StackName=stackdata['StackId']
    )['StackResources'][0]['PhysicalResourceId']
    print(resource_id)

    client = boto3.client('mwaa', region_name='us-west-2')
    token = client.create_cli_token(Name=resource_id)
    url = "https://{0}/aws_mwaa/cli".format(token['WebServerHostname'])
    body = 'dags trigger import_config'
    headers = {
        'Authorization' : 'Bearer '+token['CliToken'],
        'Content-Type': 'text/plain'
        }
    r = requests.post(url, data=body, headers=headers)

    mwaa_std_out_message = base64.b64decode(r.json()['stdout']).decode('utf8')
    print(mwaa_std_out_message)
    d = r'\d{4}-\d?\d-\d?\d (?:2[0-3]|[01]?[0-9]):[0-5]?[0-9]:[0-5]?[0-9]\+\d{2}:\d{2}'
    execution_date=re.search(d, mwaa_std_out_message).group()
    kwargs['task_instance'].xcom_push(key='execution_date', value=execution_date.replace(" ","T"))
    return resource_id

def trigger_mwaa_emr(**kwargs):
    resource_id = kwargs['task_instance'].xcom_pull("task_trigger_import_dag", key='return_value')
    print(resource_id)
    execution_date = kwargs['task_instance'].xcom_pull("task_trigger_import_dag", key='execution_date')
    print(execution_date)

    client = boto3.client('mwaa', region_name='us-west-2')
    token = client.create_cli_token(Name=resource_id)
    url = "https://{0}/aws_mwaa/cli".format(token['WebServerHostname'])
    body = 'dags state import_config {}'.format(execution_date)
    headers = {
        'Authorization' : 'Bearer '+token['CliToken'],
        'Content-Type': 'text/plain'
        }
    r = requests.post(url, data=body, headers=headers)

    mwaa_std_out_message = base64.b64decode(r.json()['stdout']).decode('utf8')
    status = mwaa_std_out_message.split("\n")[-2]
    print(status)

    while status != "success":
        time.sleep(5)
        r = requests.post(url, data=body, headers=headers)
        mwaa_std_out_message = base64.b64decode(r.json()['stdout']).decode('utf8')
        status = mwaa_std_out_message.split("\n")[-2]
        print(status)

    body = 'dags trigger mwaa_emr_1'
    headers = {
        'Authorization' : 'Bearer '+token['CliToken'],
        'Content-Type': 'text/plain'
        }
    r = requests.post(url, data=body, headers=headers)
    mwaa_std_out_message = base64.b64decode(r.json()['stdout']).decode('utf8')
    print(mwaa_std_out_message)        



task_create_stack = PythonOperator(
    task_id='task_create_stack',
    provide_context=True,
    python_callable=create_stack,
    dag=dag
)

task_launch_first_stack = PythonOperator(
    task_id='task_launch_first_stack',
    provide_context=True,
    python_callable=launch_first_stack,
    dag=dag
)

task_update_stack = PythonOperator(
    task_id='task_update_stack',
    provide_context=True,
    python_callable=update_stack,
    dag=dag
)

task_launch_second_stack = PythonOperator(
    task_id='task_launch_second_stack',
    provide_context=True,
    python_callable=launch_second_stack,
    dag=dag
)

task_create_mwaa = PythonOperator(
    task_id='task_create_mwaa',
    provide_context=True,
    python_callable=create_mwaa,
    dag=dag
)

task_trigger_import_dag = PythonOperator(
    task_id="task_trigger_import_dag",
    python_callable=trigger_import_dag,
    provide_context=True,
    dag=dag
)

task_trigger_mwaa_emr = PythonOperator(
    task_id="task_trigger_mwaa_emr",
    python_callable=trigger_mwaa_emr,
    provide_context=True,
    dag=dag
)

task_create_stack >> task_launch_first_stack >> task_update_stack >> task_launch_second_stack >> task_create_mwaa >> task_trigger_import_dag >> task_trigger_mwaa_emr
