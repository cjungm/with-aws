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
        # aurora tag 값 기반으로 만료일자가 지난 cluster stop
        try:
            client = boto3.client('rds', region_name = region['RegionName'])
            aurora_clusters = client.describe_db_clusters()['DBClusters']
            rds_instances = client.describe_db_instances()['DBInstances']
            for aurora_cluster in aurora_clusters:
                if aurora_cluster['Engine'] not in ('docdb', 'neptune'):
                    aurora_tags = client.list_tags_for_resource(ResourceName=aurora_cluster['DBClusterArn'])
                    for tag in aurora_tags['TagList']:
                        # 태그가 expiry-date 일때
                        if tag['Key'].strip().lower()=="expiry-date":
                            instance_lists['expiry-date'].append(tag['Value'])
                            instance_lists['Date'].append(date.strftime('%Y-%m-%d'))
                            instance_lists['resource'].append('AURORA')
                            instance_lists['region'].append(region['RegionName'])
                            instance_lists['instance-id'].append(aurora_cluster['DBClusterIdentifier'])
                            instance_lists['deletion-date'].append(modified_date)
                            instance_lists['deletion'].append('N')
                            instance_lists['expiration-time'].append(expiration_time)

                        # 태그가 name 일때
                        elif tag['Key'].strip().lower()=="name":
                            instance_lists['instance-name'].append(tag['Value'])
                            
                    # 루프를 돌았을 때 name tag와 expiry-date 태그의 갯수가 일치하지 않을 경우
                    if len(instance_lists['instance-name']) > len(instance_lists['expiry-date']):
                        # 마지막에 추가된 name tagdhk id를 제거합니다.
                        instance_lists['instance-name'].pop()

                    elif len(instance_lists['instance-name']) < len(instance_lists['expiry-date']):
                        # name tag를 공란으로 추가합니다.
                        instance_lists['instance-name'].append('')

        except Exception as e:
            print(e)
            continue

        # rds tag 값 기반으로 만료일자가 지난 instance stop
        try:
            for rds_instance in rds_instances:
                if rds_instance['Engine'] not in ('docdb', 'neptune'):
                    rds_tags = client.list_tags_for_resource(ResourceName=rds_instance['DBInstanceArn'])
                    for tag in rds_tags['TagList']:
                        # 태그가 expiry-date 일때
                        if tag['Key'].strip().lower()=="expiry-date":
                            instance_lists['expiry-date'].append(tag['Value'])
                            instance_lists['Date'].append(date.strftime('%Y-%m-%d'))
                            instance_lists['resource'].append('RDS')
                            instance_lists['region'].append(region['RegionName'])
                            instance_lists['instance-id'].append(rds_instance['DBInstanceIdentifier'])
                            instance_lists['deletion-date'].append(modified_date)
                            instance_lists['deletion'].append('N')
                            instance_lists['expiration-time'].append(expiration_time)
                        
                        # 태그가 name 일때
                        elif tag['Key'].strip().lower()=="name":
                            instance_lists['instance-name'].append(tag['Value'])

                    # 루프를 돌았을 때 name tag와 expiry-date 태그의 갯수가 일치하지 않을 경우
                    if len(instance_lists['instance-name']) > len(instance_lists['expiry-date']):
                        # 마지막에 추가된 name tagdhk id를 제거합니다.
                        instance_lists['instance-name'].pop()

                    elif len(instance_lists['instance-name']) < len(instance_lists['expiry-date']):
                        # name tag를 공란으로 추가합니다.
                        instance_lists['instance-name'].append('')

        except Exception as e:
            print(e)
            continue
    print(pd.DataFrame(instance_lists))

    return instance_lists