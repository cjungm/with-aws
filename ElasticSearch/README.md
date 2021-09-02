# Migration 방법론 - Elasticsearch

1. [Migration Restriction(제약사항) 또는 차이점](compare_ES)
   
   - Self Hosted Service 와 Managed Service의 비교
   - Migration 시 고려사항
   
2. [Self Hosted Service ( on ec2 )](installed_ES)
   
   - Coordinate node 1, Master node 1, Data node 2 형태의 Cluster 구성
   - Metricbeat, Logstash, Elasticsearch, Kibana 의 Elastic Stack 구성
   - Free Trial 사용
   
3. [Data 적재](data_input_ES)
   
   - Kaggle Data 탐색
   - shell 및 python 활용 data 적재
   
4. [Managed Service](managed_ES)
   
   - Managed Elasticsearch 및 Kibana 구성 가이드
   
5. [Migration](migration_ES)
   
   Migration 가이드 ( Backup & Restore )
   
   - Repository & Snapshot
     - FileStorage
     - S3
   - Elasitdump
   
6. [Monitoring](monitoring_ES)

   - Self Hosted Service 와 Managed Service의 Monitoring Guide
   - X-pack
   - CDK

7. [Q&A](additional_ES)

   - 역인덱스에 Document의 count 저장 여부
   - AWS ES는 Domain이 생성된 이후에 인스턴스 type이나 수의 자유성
   - Data를 분할하여 Migration 가능 여부
   - 다른 Version의 ES 끼리 Data Migration 방법
   - ES의 Data를 csv 혹은 Json으로 Export하는 방법
