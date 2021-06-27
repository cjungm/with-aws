import json
import boto3
import datetime

# 금일 날짜 획득
date = datetime.datetime.now() + datetime.timedelta(hours=9) - datetime.timedelta(days=1)

# 중지 프로세스이기 때문에 현재 실행중인 인스턴스만 조회
filters = [ 
    {
        'Name': 'instance-state-name', 
        'Values': ['running']
    }
]


# EC2 Instance별로 security group의 inbound내에 전체 IP 오픈 여부
# aws 정책상 security group inbound source를 anywhere로 설정하는 것을 지양
# 따라서 security group이 anywhere로 되어 있는지 확인
def check_security_group(ec2_list, instance):
    for security_group in instance.security_groups:
        security_group_ingress = ec2_list.SecurityGroup(security_group['GroupId']).ip_permissions
        for sg_ingress in security_group_ingress:
            for ip_range in sg_ingress['IpRanges']:
                if ip_range['CidrIp'] == '0.0.0.0/0':
                    return True
    
    return False

# 모든 EC2 인스턴스의 tag 규칙
# Key : [Name, Owner, Expiry-date]
# Value : [Instance_Name, User_Name, End-date(YYYY-mm-dd)]
# Expiry-date를 초과하면 중지
def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    # 모든 region에 대해 monitoring 수행
    # 전체 region name 획득
    regions_list = ec2.describe_regions()

    # 모든 region loop
    for region in regions_list['Regions']:
        print(region['RegionName'] + '의 중지 대상 EC2의 info')
        ec2_list = boto3.resource('ec2', region_name = region['RegionName'])
        # region마다 running중인 Instance 추출
        instances = ec2_list.instances.filter(Filters=filters)
        for instance in instances:
            try:
                # 필수 Tag 확인 변수
                tag_count = 0
                tag_list = list()
                
                # security group 확인
                if check_security_group(ec2_list, instance):
                    print("security group내에 전체 IP 오픈 :" + instance.id)
                    instance.stop()
                else:
                    # 필수 Tag 없을 시
                    if instance.tags is None:
                        print("Tag가 없는 EC2 :" + instance.id)
                        instance.stop()
                    else:
                        # tag의 key 값만 추출
                        for i in range(len(instance.tags)):
                            tag_list.append(instance.tags[i]['Key'].strip().lower())
                        # 반복된 key 제거
                        tag_list = list(set(tag_list))
                        for tag in instance.tags:
                            if 'expiry-date' in tag['Key'].strip().lower():
    
                                if tag['Value'].strip() <= date.strftime('%Y-%m-%d'):
                                    print("기한 만료된 EC2 (past expiration date) : " + instance.id)
                                    instance.stop()
                                    break 
                        # 필수 tag 유무 판별   
                        for tag in tag_list:
                            if 'expiry-date' == tag:
                                tag_count = tag_count + 1
                            elif 'name' == tag:
                                tag_count = tag_count + 1
                            elif 'owner' == tag:
                                tag_count = tag_count + 1
                        if tag_count < 3:
                            print("필수 tag가 부족한 EC2 (not enough tag) : " + instance.id)
                            print("현재 tag의 key값 : {}".format(tag_list))
                            instance.stop()
            except Exception as e:
                print(e)
    return { "statusCode": 200 }