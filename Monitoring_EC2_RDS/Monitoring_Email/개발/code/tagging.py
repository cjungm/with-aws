import boto3
import pandas as pd

def tag_state():
    # 인스턴스의 태그 정보를 담을 dict
    instance_lists = {
                'region' : [],
                'resource' : [],
                'instance-name': [],
                'name': [],
                'expiry-date': [],
                'owner' : []
                }


    # 모든 리전을 대상으로 수행
    ec2 = boto3.client(
        'ec2'
        )
    regions_list = ec2.describe_regions()


    for region in regions_list['Regions']:
        print('region : ' + region['RegionName'])
        
        # aurora tag 값 유무 확인하기
        try:
            client = boto3.client('rds', region_name = region['RegionName'])
            # 모든 cluster를 대상으로 수행
            aurora_clusters = client.describe_db_clusters()['DBClusters']
            # 모든 db instance를 대상으로 수행
            rds_instances = client.describe_db_instances()['DBInstances']
            ec2_list = boto3.resource('ec2', region_name = region['RegionName'])
            # 모든 ec2 instance를 대상으로 수행
            instances = ec2_list.instances.all()
            for aurora_cluster in aurora_clusters:
                aurora_tags = client.list_tags_for_resource(ResourceName=aurora_cluster['DBClusterArn'])
                instance_lists['resource'].append('RDS')
                instance_lists['region'].append(region['RegionName'])
                instance_lists['instance-name'].append(aurora_cluster['DBClusterIdentifier'])
                new_aurora_tags=list()
                for i in range(len(aurora_tags['TagList'])):
                    new_aurora_tags.append(aurora_tags['TagList'][i]['Key'].strip().lower())
                
                # expiry-date tag 확인
                if any('expiry-date' in tag for tag in new_aurora_tags):
                    instance_lists['expiry-date'].append('O')
                else:
                    instance_lists['expiry-date'].append('X')

                # name tag 확인
                if any('name' in tag for tag in new_aurora_tags):
                    instance_lists['name'].append('O')
                else:
                    instance_lists['name'].append('X')

                # owner tag 확인
                if any('owner' in tag for tag in new_aurora_tags):
                    instance_lists['owner'].append('O')
                else:
                    instance_lists['owner'].append('X')

        except Exception as e:
            print(e)
            continue

        # rds tag 값 유무 확인하기
        try:
            for rds_instance in rds_instances:
                rds_tags = client.list_tags_for_resource(ResourceName=rds_instance['DBInstanceArn'])
                instance_lists['resource'].append('RDS')
                instance_lists['region'].append(region['RegionName'])
                instance_lists['instance-name'].append(rds_instance['DBInstanceIdentifier'])
                new_rds_tags=list()
                for i in range(len(rds_tags['TagList'])):
                    new_rds_tags.append(rds_tags['TagList'][i]['Key'].strip().lower())

                # expiry-date tag 확인
                if any('expiry-date' in tag for tag in new_rds_tags):
                    instance_lists['expiry-date'].append('O')
                else:
                    instance_lists['expiry-date'].append('X')

                # name tag 확인
                if any('name' in tag for tag in new_rds_tags):
                    instance_lists['name'].append('O')
                else:
                    instance_lists['name'].append('X')

                # owner tag 확인
                if any('owner' in tag for tag in new_rds_tags):
                    instance_lists['owner'].append('O')
                else:
                    instance_lists['owner'].append('X')

        except Exception as e:
            print(e)
            continue
        
        # ec2 tag 값 유무 확인하기
        try:
            for instance in instances:
                instance_lists['resource'].append('EC2')
                instance_lists['region'].append(region['RegionName'])
                
                if instance.tags is None:
                    instance_lists['expiry-date'].append('X')
                    instance_lists['name'].append('X')
                    instance_lists['instance-name'].append('X')
                    instance_lists['owner'].append('X')

                
                new_ec2_tags=list()
                for i in range(len(instance.tags)):
                    new_ec2_tags.append(instance.tags[i]['Key'].strip().lower())

                # expiry-date tag 확인
                if any('expiry-date' in tag for tag in new_ec2_tags):
                    instance_lists['expiry-date'].append('O')
                else:
                    instance_lists['expiry-date'].append('X')

                # name tag 확인
                if any('name' in tag for tag in new_ec2_tags):
                    i=new_ec2_tags.index("name")
                    instance_lists['instance-name'].append(instance.tags[i]['Value'])
                    instance_lists['name'].append('O')
                else:
                    instance_lists['name'].append('X')
                    instance_lists['instance-name'].append('X')

                # owner tag 확인
                if any('owner' in tag for tag in new_ec2_tags):
                    instance_lists['owner'].append('O')
                else:
                    instance_lists['owner'].append('X')
        except Exception as e:
            print(e)
            continue

    print("{}, {}, {}, {}, {}, {}".format(len(instance_lists['region']),len(instance_lists['resource']),len(instance_lists['instance-name']),
    len(instance_lists['name']),len(instance_lists['expiry-date']),len(instance_lists['owner'])))
    df=pd.DataFrame(instance_lists)

    return df