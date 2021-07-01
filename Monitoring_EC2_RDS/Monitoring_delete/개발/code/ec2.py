import boto3
import time
import datetime
import pandas as pd
import essential
import copy

# 금일
date = essential.date()
# 삭제 예정일
modified_date = essential.modified_date(7)
# 삭제 예정 목록 data 일자
check_date = essential.getdate()
# 만료시간
expiration_time = essential.expiration_time()

def check_state():

    # 인스턴스의 태그 정보를 담을 dict
    instance_lists = copy.deepcopy(essential.instance_lists)

    ec2 = boto3.client(
        'ec2'
        )
    # 허용 리전을 대상으로 수행
    regions_list = ec2.describe_regions()
    for region in regions_list['Regions']:

        try:
            ec2_list = boto3.resource('ec2', region_name = region['RegionName'])
            instances = ec2_list.instances.all()
            for instance in instances:
                if instance.tags is not None:
                    for tag in instance.tags:
                        # 태그가 expiry-date 일때
                        if tag['Key'].strip().lower()=="expiry-date":
                            instance_lists['expiry-date'].append(tag['Value'])
                            instance_lists['Date'].append(date.strftime('%Y-%m-%d'))
                            instance_lists['resource'].append('EC2')
                            instance_lists['region'].append(region['RegionName'])
                            instance_lists['instance-id'].append(instance.id)
                            instance_lists['deletion-date'].append(modified_date)
                            instance_lists['deletion'].append('N')
                            instance_lists['expiration-time'].append(expiration_time)

                        # 태그가 name 일때
                        elif tag['Key'].strip().lower()=="name":
                            instance_lists['instance-name'].append(tag['Value'])
                            
                    # 루프를 돌았을 때 name tag와 expiry-date 태그의 갯수가 일치하지 않을 경우
                    if len(instance_lists['instance-name']) > len(instance_lists['expiry-date']):
                        # 마지막에 추가된 name tag와 id를 제거합니다.
                        instance_lists['instance-name'].pop()
                        
                    elif len(instance_lists['instance-name']) < len(instance_lists['expiry-date']):
                        # name tag를 공란으로 추가합니다.
                        instance_lists['instance-name'].append('')
                        
        except Exception:
            continue
    print(pd.DataFrame(instance_lists))

    return instance_lists