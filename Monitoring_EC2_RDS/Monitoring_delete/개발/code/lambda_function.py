import boto3
import datetime
import pandas as pd
import json
import time
import copy
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

# 다른 file
import ec2
import rds
import deletion
import essential

# 금일
date = essential.date()
# 수정 대상 일자
modified_date = essential.modified_date(3)
# 삭제 예정 목록 data 일자
check_date = essential.getdate()
# 만료시간
expiration_time = essential.expiration_time()

def lambda_handler(event, context):
    # 체크된 tag 정보 받아오기
    ec2_list=ec2.check_state()
    rds_list=rds.check_state()
    
    # 상수 정의
    Bucket=event["BUCKET"]
    ExceptKey= event["EXCEPT-KEY"] + event["EXTENSION"]
    # Table 이름
    Table=event["TableName"]

    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
    table = dynamodb.Table(Table)

    # 반환값 설정
    essential.step_result["SENDER"] = event["SENDER"]
    essential.step_result["RECIPIENT"] = event["RECIPIENT"]
    essential.step_result["AWS_REGION"] = event["AWS_REGION"]
    essential.step_result["SUBJECT"] = event["SUBJECT"]
    essential.step_result["CHARSET"] = event["CHARSET"]
    essential.step_result["BUCKET"] = Bucket
    essential.step_result["EXTENSION"] = event["EXTENSION"]
    essential.step_result["EXCEPT-KEY"] = event["EXCEPT-KEY"]
    essential.step_result["TableName"] = Table

    # EC2와 RDS 정보 결합()
    for key in ec2_list.keys():
        ec2_list[key].extend(rds_list[key])

    print("ec2_list")
    print(pd.DataFrame(ec2_list))

    # 조건에 맞게 filtering
    index=0
    len_list=len(ec2_list['resource'])
    while index < len_list:
        if ec2_list['expiry-date'][index] >= date.strftime('%Y-%m-%d') and ec2_list['expiry-date'][index] <= modified_date:
            essential.listpop(ec2_list,index)
            index-=1
            len_list-=1
        index+=1
    print("ec2_list")
    print(pd.DataFrame(ec2_list))

    # 예외 대상 목록 불러오기
    read_file = s3_client.get_object(Bucket=Bucket, Key=ExceptKey)
    exceptdf = pd.read_csv(read_file['Body'])

    # 예외 대상 목록과 금일 삭제 대상 목록이 모두 길이가 1이상이면 
    if len(ec2_list['resource'])>0 and len(exceptdf)>0:
        # 루프를 돌아서
        for id in list(ec2_list['instance-id']):
            # 예외 대상 목록 instance id에 동일 id가 있다면
            if id in list(exceptdf['instance-id']):
                ui=ec2_list['instance-id'].index(id)
                # 금일 목록 업데이트
                essential.listpop(ec2_list,ui)

    # 금일 삭제 대상 목록
    to_list=copy.deepcopy(ec2_list)

    index=0
    len_list=len(to_list['resource'])
    while index < len_list:
        if to_list['expiry-date'][index] >= date.strftime('%Y-%m-%d'):
            essential.listpop(to_list,index)
            index-=1
            len_list-=1
        index+=1

    print("exceptdf\n", exceptdf)
    print("to_list\n", pd.DataFrame(to_list))
    print("ec2_list\n", pd.DataFrame(ec2_list))

    # 작일 삭제 대상 목록 불러오기
    try:
        resources = table.scan(
            FilterExpression=Attr('Date').eq(check_date)
        )
        resources = pd.DataFrame(resources['Items'])
        print("resources\n", resources)
        
        # 작일 등록된 대상 있다면
        if len(resources.index) > 0:
            resources=resources.sort_values(by=['resource'], axis=0, ascending=False)
        print("resources\n",resources)
        del_list = resources.to_dict('list')
        if len(to_list['resource'])>0 and len(del_list)>0:
        # 루프를 돌아서
            for id in list(del_list['instance-id']):
                # 작일과 금일 instance id에 동일 id가 있는지 확인
                if id in list(to_list['instance-id']):
                    # 삭제 예정일이 지났다면
                    ti = ec2_list['instance-id'].index(id)
                    yi = del_list['instance-id'].index(id)
                    if del_list['deletion-date'][yi] < date.strftime('%Y-%m-%d'):
                        # 삭제 id
                        print(id)
                        deletion.delete(del_list,id)
                        # 작일 삭제 대상 목록 업데이트
                        del_list['deletion'][yi]='Y'
                        # 금일 삭제 대상 목록 업데이트
                        essential.listpop(ec2_list,ti)
                        # 테이블에 insert
                        essential.putintable(table, del_list, yi)
                    # 삭제 예정일이 지나지 않았다면
                    else:
                        # 금일 목록에서 삭제 예정일을 기존 삭제 예정일로 변경
                        ec2_list['deletion-date'][ti]=del_list['deletion-date'][yi]
                        # 기존 만료 시간은 현재로 최신화
                        del_list['expiration-time'][yi]=expiration_time
                        # 테이블에 insert
                        essential.putintable(table, del_list, yi)
        print("Clear Uploading")
    except ClientError as e:
        print(e.response['Error']['Message'])

    # 금일 등록할 대상이 있다면
    if len(ec2_list['resource'])>0 and essential.step_result['status']=="SUCCEEDED":
        for i in range(len(ec2_list['resource'])):
            essential.putintable(table, ec2_list, i)

    print(pd.DataFrame(ec2_list))
    return essential.step_result