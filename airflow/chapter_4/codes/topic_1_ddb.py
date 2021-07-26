from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import argparse
import boto3
import csv
import time

'''
1. DynamoDB Table 생성
2. DAG_1 에서 Download 받은 Data를 DynamoDB Table 적재
3. Table 에서 `Spending Score (1-100)`을 오름차순으로 하는 데이터 추출 & 추출한 Data를 Local File System에 CSV 형태로 저장
'''

args = {
    'owner': 'Jungmin',
    'start_date': datetime(2021,2,22)
}

dag = DAG(
    dag_id='topic_1_ddb',
    default_args=args,
    schedule_interval=None,
    tags=['Jungmin']
)

def create_ddb(**kwargs):
    client = boto3.client('dynamodb', region_name="us-west-2")
    response = client.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'CustomerID',
                'AttributeType': 'N'
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'CustomerID',
                'KeyType': 'HASH'
            },
        ],
        TableName='topic-1',
        BillingMode='PAY_PER_REQUEST',
        Tags=[
            {
                'Key': 'Name',
                'Value': 'topic-1'
            },
            {
                'Key': 'owner',
                'Value': 'cjm'
            }
        ]
    )

    return response['TableDescription']['TableName']

def data_input(**kwargs):
    time.sleep(10)
    table_name = kwargs['ti'].xcom_pull(key='return_value', task_ids='task_create_ddb')
    endpoint_url = "https://dynamodb.us-west-2.amazonaws.com"
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url=endpoint_url)
    table = dynamodb.Table(table_name)

    with open('/home/ec2-user/data.csv') as csv_file:
        tokens = csv.reader(csv_file, delimiter=',')
        header = next(tokens)
        for token in tokens:
            item = {}
            for i,val in enumerate(token):
                if val:
                    key = header[i]
                    if key == 'Gender':
                        item[key] = val
                    else:
                        item[key] = int(val)

            table.put_item(Item = item)

def create_sort_data(**kwargs):
    table_name = kwargs['ti'].xcom_pull(key='return_value', task_ids='task_create_ddb')
    client = boto3.client('dynamodb', region_name="us-west-2")

    response = client.scan(
        TableName=table_name,
        Limit=200,
        Select='ALL_ATTRIBUTES'
    )

    for items in response['Items']:
        for key, item in items.items():
            if key == 'Gender':
                items[key] = list(item.values())[0]
            else:
                items[key] = int(list(item.values())[0])
            print(items[key])

    sort_data = sorted(response['Items'], key=lambda item: (item['Spending Score (1-100)']))

    with open('/home/ec2-user/topic_1.csv','w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(response['Items'][0].keys()))
        writer.writeheader()
        for data in sort_data:
            writer.writerow(data)


task_create_ddb = PythonOperator(
    task_id='task_create_ddb',
    provide_context=True,
    python_callable=create_ddb,
    dag=dag
)

task_data_input = PythonOperator(
    task_id='task_data_input',
    provide_context=True,
    python_callable=data_input,
    dag=dag
)

task_data_sort = PythonOperator(
    task_id='task_data_sort',
    provide_context=True,
    python_callable=create_sort_data,
    dag=dag
)

task_create_ddb >> task_data_input >> task_data_sort