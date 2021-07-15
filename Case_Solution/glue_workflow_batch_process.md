# AWS Glue Workflow Batch Process

## 목표 : Glue Workflow및 Glue Job으로 Batch Process 구성

1. Glue Job
   1. Manual 하게 호출
   2. CloudWatch Event 가 Lambda 을 호출, Lambda 는 Glue WorkFlow 을 호출
   3. Glue Trigger 이용하여 호출
2. Glue WorkFlow 
   1. DynamoDB 에서 데이터를 Select 해서 S3 에 저장
   2. 기존에 S3 에 존재하는 데이터와 Join
   3. 두개의 데이터를 조인한 결과를 S3 에 저장
3. Athena 라 조인한 결과 데이터 (S3)를 조회한다.

## Resource

1. Glue Crawler : Dynamodb에서 고객 data를 S3에 적재
2. Glue Job : S3에서 매출 data를 읽고 2개의 data를 join 및 S3에 저장
3. Glue Workflow : Batch Process Ochestartion
4. Dynamodb : Raw Data
5. S3 : Data Source
6. Athena : Data 조회
