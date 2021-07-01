import boto3
import essential
from botocore.exceptions import ClientError

def delete(del_dict,id):
    try:
        # list에서 id index 설정
        i=list(del_dict['instance-id']).index(id)
        # resource가 RDS일 경우
        if del_dict['resource'][i] == 'RDS':
            # RDS 클라이언트 설정
            client = boto3.client(
                'rds',
                region_name = del_dict['region'][i]
            )
            # RDS Instance 상태 검색
            response = client.describe_db_instances(
                DBInstanceIdentifier=id,
            )
            # 삭제 방지가 되어 있는 상태라면
            if response['DBInstances'][0]['DeletionProtection'] == True:
                print('DeletionProtection=True')
                
                # 삭제 방지 해제
                mod = client.modify_db_instance(
                    DBInstanceIdentifier=id,
                    DeletionProtection=False
                )
                print(mod)
                essential.step_result["status"]="FAILED"
            else:
                print("DeletionProtection=False")
            # 삭제
            del_result=client.delete_db_instance(
                DBInstanceIdentifier=id,
                SkipFinalSnapshot=True
            )
            print(del_result)
        # resource가 AURORA일 경우
        elif del_dict['resource'][i] == 'AURORA':
            # RDS 클라이언트 설정
            client = boto3.client(
                'rds',
                region_name = del_dict['region'][i]
            )
            # AURORA Cluster 상태 검색
            response = client.describe_db_clusters(
                DBClusterIdentifier=id,
            )
            # 삭제 방지가 되어 있는 상태라면
            if response['DBClusters'][0]['DeletionProtection'] == True:
                print('DeletionProtection=True')
                
                # 삭제 방지 해제
                mod = client.modify_db_cluster(
                    DBClusterIdentifier=id,
                    DeletionProtection=False
                )
                print(mod)
                essential.step_result["status"]="FAILED"
            else:
                print("DeletionProtection=False")
            # 실행 중인 상태이라면 
            if response['DBClusters'][0]['Status'] == 'available':
                # Aurora member 확인
                cluster_member = client.describe_db_clusters(
                    DBClusterIdentifier=id,
                )['DBClusters'][0]['DBClusterMembers']
                # member가 있으면
                if len(cluster_member)>0:
                    # 루프 돌며 삭제
                    for memberid in cluster_member:
                        del_result=client.delete_db_instance(
                            DBInstanceIdentifier=memberid['DBInstanceIdentifier'],
                            SkipFinalSnapshot=True
                        )
                        print(del_result)
                # 삭제
                del_result=client.delete_db_cluster(
                    DBClusterIdentifier=id,
                    SkipFinalSnapshot=True
                )
                print(del_result)
            else:
                print("status:FAILED")
                # 상태 변경
                essential.step_result["status"]="FAILED"
                # 실행
                client.start_db_cluster(
                    DBClusterIdentifier=id
                )
        else:
            # EC2 클라이언트 설정
            ec2 = boto3.client(
                'ec2',
                region_name = del_dict['region'][i]
            )

            # EC2 Instance의 삭제 방지 정보 검색
            response = ec2.describe_instance_attribute(
                Attribute='disableApiTermination',
                InstanceId=id
            )
            print(response)
            # 삭제 방지가 되어 있는 상태라면
            if response['DisableApiTermination']['Value'] == True:
                print('DeletionProtection=True')
                # 상태 변경
                essential.step_result["status"]="FAILED"
                # 삭제 방지 해제
                mod = ec2.modify_instance_attribute(
                    DisableApiTermination={
                        'Value': False
                    },
                    InstanceId=id,
                )
                print(mod)
            else:
                print("DeletionProtection=False")
            # 삭제
            del_result=ec2.terminate_instances(
                InstanceIds=[id],
                DryRun=False
            )
            print(del_result)   
    except Exception as e:
        print(e)
        # 오류 발생시 상태 변경
        essential.step_result["status"]="FAILED"