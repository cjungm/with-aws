# AWS Monitoring 삭제

Monitoring_stop을 응용하여 Monitoring_delete 개발

1. 매일 EC2와 RDS의 Tag status를 조회
   - Tag의 `Expiry-date`를 기준으로 삭제 대상 여부 확인
   - 삭제 대상일 경우 해당 Resource 정보를 DynamoDB Table에 적재
2. 만료일자가 지난 Instance 및 Cluster에 삭제 예정일 부여
   - 삭제 예정일은 만료 일자 +7 days
   - 삭제 대상으로 등록된 Resource는 삭제 예정일 변동없이 삭제 예정일까지 매일 등록
   - 삭제 대상으로 등록된 Resource의 Tag가 update 될 경우 등록 중단
   - Tag update되었던 Resource가 다시 삭제 대상이 될 경우 update된 `Expiry-date`를 기준으로 다시 삭제 대상으로 등록
3. 삭제 예정일이 지난 resource는 삭제
   - DynamoDB를 기준으로 삭제 예정일이 지난 Resource는 삭제
   - 삭제 대상, 삭제 예정일 초과 2가지 모두 충족시 삭제
   - 모든 Resource 정보는 최초 등록 +30 days TTL 부여





