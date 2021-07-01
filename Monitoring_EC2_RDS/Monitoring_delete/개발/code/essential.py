import boto3
import datetime
import pandas as pd
import json
import time
import copy
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

# 금일
def date():
    dt=datetime.datetime.now() + datetime.timedelta(hours=9)
    return dt
# 삭제 예정일
def modified_date(n):
    dt=date() + datetime.timedelta(days=n)
    dt = dt.strftime('%Y-%m-%d')
    return dt
# 삭제 예정 목록 data 일자
# 월요일이면 금요일 목록 받아오기
def getdate():
    if datetime.datetime.now().weekday()==0:
        check_date = date() - datetime.timedelta(days=3)
    # 그 외에는 작일 목록 받아오기
    else:
        check_date = date() - datetime.timedelta(days=1)
    check_date = check_date.strftime('%Y-%m-%d')
    return check_date

def expiration_time():
    # 만료일
    expiration_date = date() + datetime.timedelta(days=30)
    return int(time.mktime(expiration_date.timetuple()))

# 리스트 filtering을 위한 함수 정의
def listpop(ilist, ind):
    for key in ilist.keys():
        ilist[key].pop(ind)
        
# table에 item put 
def putintable(table, ilist, ind):
    item = {}
    for key in ilist.keys():
        item[key]=ilist[key][ind]
    table.put_item(
        Item=item
        )

# Tag 조회한 정보를 담을 dict
instance_lists = {
    'Date' : [],
    'resource' : [],
    'region' : [],
    'instance-name': [],
    'instance-id': [],
    'expiry-date': [],
    'deletion-date': [],
    'deletion': [],
    'expiration-time': []
    }

# Step function 다음 task에 넘길 파라미터 정보
step_result = {
    "status":"SUCCEEDED",
    "SENDER":"",
    "RECIPIENT":"",
    "AWS_REGION":"",
    "SUBJECT":"",
    "CHARSET":"",
    "BUCKET":"",
    "EXTENSION":"",
    "EXCEPT-KEY":"",
    "TableName": ""
    }