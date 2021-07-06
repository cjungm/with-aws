import boto3
import datetime
import pandas as pd
import tagging
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

# expiry-date 기준 날짜
date = datetime.datetime.now() + datetime.timedelta(hours=9)
# expiry-date 수정이 필요한 날짜
modified_date = date + datetime.timedelta(days=3)
# 비교대상이 월요일일 경우 지난 주 금요일 조회
if datetime.datetime.now().weekday()==0:
    checked_date = date - datetime.timedelta(days=3)
# 그 외에는 작일 목록 받아오기
else:
    checked_date = date - datetime.timedelta(days=1)


def lambda_handler(event, context):
    # 발신자
    SENDER=event['SENDER']
    # 수신자 endpoint
    RECIPIENT=event['RECIPIENT']
    # region
    AWS_REGION=event['AWS_REGION']
    # 제목.
    SUBJECT=event['SUBJECT']
    # Encoding type
    CHARSET=event['CHARSET']
    # Table 이름
    Table=event["TableName"]

    # resource 만들기
    client = boto3.client('ses',region_name=AWS_REGION)
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
    table = dynamodb.Table(Table)

    # 체크된 tag 정보 받아오기
    try:
        resources = table.scan(
            FilterExpression=Attr('Date').eq(date.strftime('%Y-%m-%d'))
        )
        df = pd.DataFrame(resources['Items'])
        if len(df) > 0:
            df = df[['resource', 'region', 'instance-name', 'instance-id', 'expiry-date', 'deletion-date', 'deletion', 'expiration-time', 'Date']]
    except ClientError as e:
        df = pd.DataFrame()
    
    try:
        del_resource = table.scan(
            FilterExpression=Attr('Date').eq(checked_date.strftime('%Y-%m-%d'))
        )
        gone_df = pd.DataFrame(del_resource['Items'])
        if len(gone_df) > 0:
        # print(gone_df)
            gone_df = gone_df[['resource', 'region', 'instance-name', 'instance-id', 'expiry-date', 'deletion-date', 'deletion', 'expiration-time', 'Date']]
    except ClientError as e:
        gone_df = pd.DataFrame()
    
    tag_df=tagging.tag_state()
    
    # 삭제된 목록
    if len(gone_df) > 0:
        deletion_df = gone_df[gone_df['deletion'] == 'Y']
        deletion_df.drop(['deletion-date', 'deletion', 'expiration-time', 'Date'], axis='columns', inplace=True)
    else:
        deletion_df = pd.DataFrame()

    # 조건에 맞게 각각의 dataframe filtering
    if len(df) > 0:
        del_df = df[df['expiry-date'] < date.strftime('%Y-%m-%d')]
        del_df.drop(['deletion', 'expiration-time', 'Date'], axis='columns', inplace=True)
        mod_df = df[df['expiry-date'] > modified_date.strftime('%Y-%m-%d')]
        mod_df.drop(['deletion-date', 'deletion', 'expiration-time', 'Date'], axis='columns', inplace=True)
    else:
        del_df = pd.DataFrame()
        mod_df = pd.DataFrame()
    tag_df = tag_df[(tag_df['expiry-date'] == 'X') | (tag_df['name'] == 'X') | (tag_df['owner'] == 'X')]
    
    # 삭제된 instance가 있으면
    if len(deletion_df) > 0:
        index_1=list(range(1,len(deletion_df.index)+1))
        deletion_df.index=index_1
        print(deletion_df)
        deletion_msg=deletion_df.to_html()
    # 삭제된 instance가 없으면
    else:
        deletion_msg = "금일은 삭제된 Instance가 없습니다."
        
    # 삭제할 instance가 있으면
    if len(del_df) > 0:
        index_1=list(range(1,len(del_df.index)+1))
        del_df.index=index_1
        print(del_df)
        del_msg=del_df.to_html()
    # 삭제할 instance가 없으면
    else:
        del_msg = "금일은 삭제할 Instance가 없습니다."
    
    # 수정할 instance가 있으면
    if len(mod_df) > 0:
        index_2=list(range(1,len(mod_df.index)+1))
        mod_df.index=index_2
        print(mod_df)
        mod_msg=mod_df.to_html()
    # 수정할 instance가 없으면
    else:
        mod_msg = "금일은 수정할 Instance가 없습니다."
    
    # tag 수정할 instance가 있으면
    if len(tag_df) > 0:
        index_2=list(range(1,len(tag_df.index)+1))
        tag_df.index=index_2
        print(tag_df)
        tag_msg=tag_df.to_html()
    # tag 수정할 instance가 없으면
    else:
        tag_msg = "tag 수정할 Instance가 없습니다."

    BODY_HTML  = """\
    <html>
    <head></head>
    <body>
    <h2>안녕하세요.<br> DMS AWS 계정 담당자입니다.</h2><br>
    <p>본 메일은 자동으로 발송되는 메일로 DMS 계정내에 리소스 생성 정책과 맞지 않은 리소스에 대해 모니터링 결과를 취합하여 전달드립니다.
    <br>
    아래 내용을 확인하시어 본인이 생성한 서비스에 대해 조치해주시기 바랍니다. (단, MSP 서비스에서 활용 또는 본부장님 승인하에 사용하는 리소스는 무시하셔도 됩니다.)</p>
    <h3>1) 삭제 목록</h3>
    <hr>
        {0}
    <br>
    <h3>2) 삭제 권고 - expiry-date 만료</h3>
    <hr>
        {1}
    <br>
    <h3>3) 수정 권고 - expiry-date 3일 이상</h3>
    <hr>
        {2}
    <br>
    <h3>4) tagging 처리 필요 - Name, expiry-date, owner</h3>
    <hr>
        {3}
    <br>

    <h2>감사합니다.<h/2>
    </body>
    </html>
    """.format(deletion_msg, del_msg, mod_msg,tag_msg) 

    # E-mail 전송
    try:
        # 전송할 내용이 있으면
        if len(del_df) > 0 or len(mod_df) > 0 or len(tag_df) > 0:
            # E-mail 내용
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        }
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER
            )
    # E-mail 전송시 오류가 발생할 경우
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print(date)
        print(modified_date)
        print("Email sent! Message ID: " + response['MessageId'])