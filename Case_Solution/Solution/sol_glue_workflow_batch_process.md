# AWS Glue Workflow Batch Process

## 1. Data 수집

1. 쉽게 DataSet을 얻을 수 있는 [Kaggle](https://www.kaggle.com/)을 검색하여 접속합니다.
   ![search_kaggle](images/search_kaggle.png)

2. Data를 선택하고 고객에 대한 data가 필요하므로 customer를 검색, 소규모 dataset이 필요하므로 small을 선택합니다.

   ![search_data_kaggle](images/search_data_kaggle.png)

3. 2 번째 항목을 선택하고 data를 다운로드 합니다.
   ![kaggle_data_download](images/kaggle_data_download.png)

4. dataset의 원본 형태에는 고객 정보와 고객 매출 정보가 함께 있습니다. 용도에 맞게 분류합니다.
   원본: column 5개 row 200개

   - CustomerID
   - Gender
   - Age
   - Annual Income (k$)
   - Spending Score (1-100)

   ![initial_data](images/initial_data.png)

   수정본: 고객 정보 data, 고객 매출 정보 data 로 분할

   고객 정보 data : column 3개 row 100개 (100개씩 2개의 파일로 분할)

   - CustomerID
   - Gender
   - Age

   ![modified_data](images/modified_data.png)

   고객 매출 정보 data : data: column 3개 row 100개 (100개씩 2개의 파일로 분할)

   - CustomerID
   - Annual Income (k$)
   - Spending Score (1-100)

   ![modified_data_2](images/modified_data_2.png)

   분할 결과 : 고객 정보, 고객 매출 정보 csv 파일이 각 2개 씩 존재

   ![modified_data_files](images/modified_data_files.png)

## 2. Dynamodb에 고객 정보 data 적재

1. [AWS Dynamodb](https://console.aws.amazon.com/dynamodb/) 콘솔을 엽니다. **테이블 만들기**를 선택합니다.
   ![create_dynamodb](images/create_dynamodb.png)

   

2. 이름과 기본키를 선택하고 생성합니다.
   ![create_dynamodb_2](images/create_dynamodb_2.png)

   

3. csv파일을 dynamodb에 적재하기 위한 python code 작성

   

   ```python
   # csv 레코드를 dynamo db 테이블에 쓰는 스크립트.
   from __future__ import print_function 
   from __future__ import division 
   import argparse
   import boto3
   import csv
   import time
   
   # command line arguments
   parser = argparse.ArgumentParser(description='Write CSV records to dynamo db table. CSV Header must map to dynamo table field names.')
   parser.add_argument('csvFile', default='{CSV_FILE}', nargs='?', help='Path to csv file location')
   parser.add_argument('table', default='{DynamoDB_Table_Name}', nargs='?', help='Dynamo db table name')
   parser.add_argument('writeRate', default=5, type=int, nargs='?', help='Number of records to write in table per second (default:5)')
   parser.add_argument('delimiter', default=',', nargs='?', help='Delimiter for csv records (default=|)')
   parser.add_argument('region', default='{Region_Name}', nargs='?', help='Dynamo db region name (default=us-west-2')
   args = parser.parse_args()
   print(args)
   
   # dynamodb and table initialization
   endpointUrl = "https://dynamodb." + args.region + ".amazonaws.com"
   dynamodb = boto3.resource('dynamodb', region_name=args.region, endpoint_url=endpointUrl)
   table = dynamodb.Table(args.table)
   
   # write records to dynamo db
   with open(args.csvFile) as csv_file:
       tokens = csv.reader(csv_file, delimiter=args.delimiter)
       # dynamo db 필드 이름을 포함하는 파일의 첫 번째 행을 읽습니다.
       header = next(tokens)
       # 파일의 나머지 부분에는 새로운 레코드가 포함
       for token in tokens:
          item = {}
          for i,val in enumerate(token):
            if val:
              key = header[i]
              item[key] = val
          print(item)
          table.put_item(Item = item)
   
          time.sleep(1/args.writeRate) # 테이블에 대한 최대 쓰기 프로비저닝 용량을 수용
   ```

   

4. 결과 확인
   ![result_input_ddb](images/result_input_ddb.png)

   dynamodb table 확인
   ![check_ddb](images/check_ddb.png)

## 3. IAM role 생성(S3, glue service, Dynamodb)

1. IAM 서비스를 선택합니다. 액세스 관리에 있는 **역할**을 선택하고 **역할 만들기**를 선택합니다.
   ![iam_create](images/iam_create.png)

2. 신뢰할 수 있는 유형의 개체는 AWS 서비스를 선택합니다. 사용 사례 선택에서는 Glue를 선택하고 **다음**을 선택합니다.

   ![iam_create_2](images/iam_create_2.png)

3. S3, Glue, Dynamodb를 차례로 검색하여 정책을 연결합니다.
   ![iam_create_3](images/iam_create_3.png)

   ![iam_create_4](images/iam_create_4.png)

   ![iam_create_5](images/iam_create_5.png)

4. 필요한 태그를 지정합니다.
   ![iam_create_6](images/iam_create_6.png)

5. 역할에 대한 설정을 검토하고 **역할만들기**를 선택합니다.
   ![iam_create_7](images/iam_create_7.png)

## 4. Glue Crawler 생성 (Dynamodb data)

1. 데이터 카탈로그에 있는 **크롤러**을 선택하고 **크롤러 추가**를 선택합니다.
   ![create_crawler](images/create_crawler.png)

2. 이름을 설정하고 다음을 선택합니다.
   ![create_crawler_2](images/create_crawler_2.png)

3. Dynamodb에서 data를 가져올 것이므로 Data stores를 선택하고 다음을 선택합니다.

   ![create_crawler_3](images/create_crawler_3.png)

4. 데이터 스토어와 테이블을 선택합니다.
   ![create_crawler_4](images/create_crawler_4.png)

5. **아니오**를 선택합니다.
   ![create_crawler_5](images/create_crawler_5.png)

6. 기존에 생성한 IAM을 설정합니다.
   ![create_crawler_6](images/create_crawler_6.png)

7. **온디맨드**로 설정
   ![create_crawler_7](images/create_crawler_7.png)

8. data를 저장할 Database를 새롭게 추가합니다.
   ![create_crawler_8](images/create_crawler_8.png)

   ![create_crawler_9](images/create_crawler_9.png)

9. 검토 후 생성
   ![create_crawler_10](images/create_crawler_10.png)

10. 생성된 crawler 실행
    ![create_crawler_result](images/create_crawler_result.png)

    실행중
    ![running_crawler](images/running_crawler.png)

    실행 완료
    ![running_crawler_result](images/running_crawler_result.png)

11. 확인
    Crawler에서 생성한 Database 선택
    ![glue_database](images/glue_database.png)
    테이블 확인
    ![glue_table](images/glue_table.png)![glue_table_schema](images/glue_table_schema.png)
    스키마와 인스턴스 수를 통해 정확하게 crawling되었음을 확인할 수 있습니다.
    ![glue_table_retult](images/glue_table_retult.png)

## 5. Glue Job 생성 (Data S3에 적재)

1. ETL에 있는 **Job**을 선택하고 **작업추가**를 선택합니다.
   ![glue_job_create_1](images/glue_job_create_1.png)

2. 이름과 IAM을 선택, 스크립트가 저장될 경로를 지정합니다.
   ![glue_job_create_2](images/glue_job_create_2.png)

3. Crawling한 테이블을 선택합니다.
   ![glue_job_create_3](images/glue_job_create_3.png)**스키마 변경**을 선택합니다.
   ![glue_job_create_4](images/glue_job_create_4.png)

4. **데이터 대상에서 테이블 생성**합니다. 

   ![glue_job_create_5](images/glue_job_create_5.png)

5. 데이터 대상을 편집합니다.

   ![glue_job_create_6](images/glue_job_create_6.png)

   ```python
   import sys
   from awsglue.transforms import *
   from awsglue.utils import getResolvedOptions
   from pyspark.context import SparkContext
   from awsglue.context import GlueContext
   from awsglue.job import Job
   from pyspark.sql.functions import *
   from awsglue.dynamicframe import DynamicFrame
   from pyspark.sql.types import *
   import os
   
   table_name = "{Catalog Table Name}"
   table = glueContext.create_dynamic_frame.from_options(
     "dynamodb",
     connection_options={
       "dynamodb.input.tableName": table_name
     }
   )
   
   repartition = table.toDF()
   repartition.coalesce(1).write.mode('overwrite').option("header", "true").csv('S3_Key_Path')
   ```

6. 작업 실행
   ![glue_job_create_7](images/glue_job_create_7.png)

   ![glue_job_create_8](images/glue_job_create_8.png)

   ![glue_job_create_9](images/glue_job_create_9.png)

7. 완료 결과 확인
   ![result_glue_job](images/result_glue_job.png)

   ![reslut_glue_job_2](images/reslut_glue_job_2.png)

## 6. Glue 개발 Endpoint 생성

1. ETL에 있는 **개발 엔드포인트**을 선택하고 **엔드포인트 추가**를 선택합니다.
   ![glue_endpoint_1](images/glue_endpoint_1.png)

2. 이름과 IAM을 선택합니다.
   ![glue_endpoint_2](images/glue_endpoint_2.png)

3. 네트워킹은 인터넷 연결이 되어있는 private vpc와 subnet 선택
   ![glue_endpoint_3](images/glue_endpoint_3.png)

4. 준비되는 중(엔드포인트는 요금이 비싸기 때문에 사용 후 **반드시 삭제**합니다.)
   ![glue_endpoint_4](images/glue_endpoint_4.png)

5. 준비가 되면 노트북 생성
   ![glue_endpoint_5](images/glue_endpoint_5.png)

   구성요소들을 설정합니다.
   ![glue_endpoint_6](images/glue_endpoint_6.png)

   ![glue_endpoint_7](images/glue_endpoint_7.png)

   준비되는 중
   ![glue_endpoint_8](images/glue_endpoint_8.png)

6. 노트북 시작하기
   ![start_glue_endpoint](images/start_glue_endpoint.png)

   ![start_glue_endpoint_2](images/start_glue_endpoint_2.png)

   

7. 코드 작성하기

   ```python
   import sys
   from awsglue.transforms import *
   from awsglue.utils import getResolvedOptions
   from pyspark.context import SparkContext
   from awsglue.context import GlueContext
   from awsglue.job import Job
   from pyspark.sql.functions import *
   from awsglue.dynamicframe import DynamicFrame
   from pyspark.sql.types import *
   ```

   Starting Spark application

   |   ID |            YARN Application ID |    Kind | State |                                                     Spark UI |                                                   Driver log | Current session? |
   | ---: | -----------------------------: | ------: | ----: | -----------------------------------------------------------: | -----------------------------------------------------------: | ---------------: |
   |    0 | application_1586965137568_0001 | pyspark |  idle | [Link](http://ip-172-31-15-246.ap-northeast-2.compute.internal:20888/proxy/application_1586965137568_0001/) | [Link](http://ip-172-31-0-4.ap-northeast-2.compute.internal:8042/node/containerlogs/container_1586965137568_0001_01_000001/livy) |                ✔ |

   SparkSession available as 'spark'.

   ```python
   sc = SparkContext.getOrCreate()
   glueContext = GlueContext(sc)
   spark = glueContext.spark_session
   ```

   ```python
   # 2개의 csv 파일 받아오기
   customer_sale_df_csv = spark.read.format("csv").option("header", "true").load("{S3_Sale_Data_Key_Path}")
   customer_info_df_csv = spark.read.format("csv").option("header", "true").load("{S3_User_Data_Key_Path}")
   ```

   ```python
   # 10개의 record씩 확인
   customer_info_df_csv.show(10)
   customer_sale_df_csv.show(10)
   ```

   ```
   +----------+------+---+
   |customerid|gender|age|
   +----------+------+---+
   |        48|Female| 27|
   |        53|Female| 31|
   |       100|  Male| 20|
   |        39|Female| 36|
   |        73|Female| 60|
   |        99|  Male| 48|
   |         9|  Male| 64|
   |        82|  Male| 38|
   |        78|  Male| 40|
   |        45|Female| 49|
   +----------+------+---+
   only showing top 10 rows
   
   +----------+------------------+----------------------+
   |CustomerID|Annual Income (k$)|Spending Score (1-100)|
   +----------+------------------+----------------------+
   |         1|                15|                    39|
   |         2|                15|                    81|
   |         3|                16|                     6|
   |         4|                16|                    77|
   |         5|                17|                    40|
   |         6|                17|                    76|
   |         7|                18|                     6|
   |         8|                18|                    94|
   |         9|                19|                     3|
   |        10|                19|                    72|
   +----------+------------------+----------------------+
   only showing top 10 rows
   ```

   ```python
   # 스키마 확인
   customer_info_df_csv.printSchema
   customer_sale_df_csv.printSchema
   ```

   ```
   <bound method DataFrame.printSchema of DataFrame[customerid: string, gender: string, age: string]>
   <bound method DataFrame.printSchema of DataFrame[CustomerID: string, Annual Income (k$): string, Spending Score (1-100): string]>
   ```

   ```python
   # 두 테이블 join 후 스키마 확인
   new_customer_csv = customer_info_df_csv.join(customer_sale_df_csv, "CustomerID")
   new_customer_csv.printSchema
   ```

   ```
   <bound method DataFrame.printSchema of DataFrame[customerid: string, gender: string, age: string, Annual Income (k$): string, Spending Score (1-100): string]>
   ```

   ```python
   # customerid 컬럼의 타입을 Integer로 변경
   new_customer_csv = new_customer_csv.withColumn("customerid",new_customer_csv["customerid"].cast(IntegerType())).orderBy(asc("customerid"))
   ```

   ```python
   # join된 table 확인
   new_customer_csv.show(10)
   ```

   ```
   +----------+------+---+------------------+----------------------+
   |customerid|gender|age|Annual Income (k$)|Spending Score (1-100)|
   +----------+------+---+------------------+----------------------+
   |         1|  Male| 19|                15|                    39|
   |         2|  Male| 21|                15|                    81|
   |         3|Female| 20|                16|                     6|
   |         4|Female| 23|                16|                    77|
   |         5|Female| 31|                17|                    40|
   |         6|Female| 22|                17|                    76|
   |         7|Female| 35|                18|                     6|
   |         8|Female| 23|                18|                    94|
   |         9|  Male| 64|                19|                     3|
   |        10|Female| 30|                19|                    72|
   +----------+------+---+------------------+----------------------+
   only showing top 10 rows
   ```

   ```python
   # S3에 join된 table 적재
   new_customer_csv.coalesce(1).write.mode('append').option("header", "true").csv('{S3_Data_Key_Path}')
   ```

   ![table_join_result](images/table_join_result.png)

## 7. Glue Job 생성 (S3안의 2 개의 csv join)

1. ETL에 있는 **Job**을 선택하고 **작업추가**를 선택합니다.
   ![glue_job_create_1](images/glue_job_create_1.png)이름과 스크립트 저장 장소 설정 / 사용자가 직접 작성하는 스크립트 선택
   ![glue_job](images/glue_job.png)

2. 개발 엔드포인트에서 작성한 코드를 저장한다.
   
   

   ```python
   import sys
   from awsglue.transforms import *
   from awsglue.utils import getResolvedOptions
   from pyspark.context import SparkContext
   from awsglue.context import GlueContext
   from awsglue.job import Job
   from pyspark.sql.functions import *
   from awsglue.dynamicframe import DynamicFrame
   from pyspark.sql.types import *
   
   sc = SparkContext.getOrCreate()
   glueContext = GlueContext(sc)
   spark = glueContext.spark_session
   
   # 2개의 csv 파일 받아오기
   customer_sale_df_csv = spark.read.format("csv").option("header", "true").load("{S3_Sale_Data_Key_Path}")
   customer_info_df_csv = spark.read.format("csv").option("header", "true").load("{S3_User_Data_Key_Path}")
   
   # 두 테이블 join 
   new_customer_csv = customer_info_df_csv.join(customer_sale_df_csv, "CustomerID")
   
   # customerid 컬럼의 타입을 Integer로 변경
   new_customer_csv = new_customer_csv.withColumn("customerid",new_customer_csv["customerid"].cast(IntegerType())).orderBy(asc("customerid"))
   
   # S3에 join된 table 적재
   new_customer_csv.coalesce(1).write.mode('append').option("header", "true").csv('{S3_Data_Key_Path}')
   ```

## 8. Glue Workflow 생성 및 실행

워크플로우 그래프에 트리거를 추가하고 각 트리거에 대해 감시되는 이벤트와 작업을 정의하여 워크플로우를 구축합니다. 

### 1단계: 생성

1. [AWS Glue](https://console.aws.amazon.com/glue/) 콘솔을 엽니다.

2. 탐색 창의 **ETL** 아래에서 **Workflows(워크플로우)**를 선택합니다.

3. **Add workflow(워크플로우 추가)**를 선택하고 **Add a new ETL workflow(새 ETL 워크플로우 추가)** 양식을 작성합니다.

   추가하는 선택적 기본 실행 속성은 워크플로우의 모든 작업에 대한 인수로 사용할 수 있습니다. 
   ![glue_workflow_create_1](images/glue_workflow_create_1.png)**Add workflow(워크플로우 추가)**를 선택합니다.

   새 워크플로우가 **Workflows(워크플로우)** 페이지의 목록에 나타납니다.
   ![glue_workflow_create_2](images/glue_workflow_create_2.png)

   ![glue_workflow_create_3](images/glue_workflow_create_3.png)

### 2단계: 실행

1. **Workflows(워크플로우)** 페이지에서 새 워크플로우를 선택합니다. 아래쪽의 탭에서 **Graph(그래프)**를 선택합니다.

2. **Add trigger(트리거 추가)**를 선택하고 **Add trigger(트리거 추가)** 대화 상자에서 다음 중 하나를 수행합니다.
   ![glue_workflow_create_4](images/glue_workflow_create_4.png)

   - **Add new(새로 추가)**를 선택하고 **Add trigger(트리거 추가)** 양식을 작성합니다. **Trigger Type(트리거 유형)**에서 **Schedule(일정)** 또는 **On demand(온디맨드)**를 선택합니다. 그런 다음 **추가**를 선택합니다.
     ![glue_workflow_create_5](images/glue_workflow_create_5.png)

     자리 표시자 노드(**Add node(노드 추가)**라고 레이블이 지정됨)와 함께 트리거가 그래프에 나타납니다. 이때 트리거는 아직 저장되어 있지 않습니다.
     ![glue_workflow_create_6](images/glue_workflow_create_6.png)

     * 불완전한 트리거이므로 작업을 추가해야 합니다.

       ![glue_workflow_create_7](images/glue_workflow_create_7.png)

3. 새 트리거를 추가한 경우 다음 단계를 완료합니다.

   1. 다음 중 하나를 수행하십시오.

      - 자리 표시자 노드(**Add node(노드 추가)**)를 선택합니다.
      - 시작 트리거가 선택되어 있는지 확인하고, 그래프 위의 **Action(작업)** 메뉴에서 **Add jobs/crawlers to trigger(트리거할 작업/크롤러 추가)**를 선택합니다.

   2. **Add jobs(s) and crawler(s) to trigger(트리거할 작업 및 크롤러 추가)** 대화 상자에서 작업 또는 크롤러를 하나 이상 선택한 후 **Add(추가)**를 선택합니다.

      트리거가 저장되고, 선택한 작업 또는 크롤러가 트리거의 커넥터와 함께 그래프에 나타납니다.

      실수로 잘못된 작업 또는 크롤러를 추가한 경우, 해당 트리거 또는 커넥터를 선택하고 **Remove(제거)**를 선택하면 됩니다.
      ![glue_workflow_run_1](images/glue_workflow_run_1.png)

   3. 실행확인
      ![glue_workflow_run_2](images/glue_workflow_run_2.png)
      세부정보
      ![glue_workflow_run_3](images/glue_workflow_run_3.png)

      ![glue_workflow_run_4](images/glue_workflow_run_4.png)

## 9. Glue Workflow Trigger

### 1. CloudWatch를 사용하여 워크플로우 실행

#### 1단계: Lambda 함수 생성

1. Lambda 서비스의 함수에서 **함수 생성**을 선택합니다.
   ![lambda_create](images/lambda_create.png)

2. 함수 이름, 사용할 언어와 역할을 선택합니다.
   ![lambda_create_2](images/lambda_create_2.png)

3. 코드를 편집합니다.
   ![lambda_create_3](images/lambda_create_3.png)

   Lambda function code

   ```python
   # Set up logging
   import json
   import os
   import logging
   logger = logging.getLogger()
   logger.setLevel(logging.INFO)
   
   # Import Boto 3 for AWS Glue
   import boto3
   client = boto3.client('glue')
   
   # Variables for the job: 
   glueWorkFlowName = "{Glue_Workflow_Name}"
   
   # Define Lambda function
   def lambda_handler(event, context):
       logger.info('## TRIGGERED BY EVENT: ')
       logger.info(event['detail'])
       # workflow 실행
       response = client.start_workflow_run(Name=glueWorkFlowName)
       logger.info('## STARTED GLUE JOB: ' + glueWorkFlowName)
       logger.info('## GLUE JOB RUN ID: ' + response['RunId'])
       return response
   ```

   

#### 2단계: **CloudWatch Events 규칙 생성**

1. [CloudWatch 콘솔](https://console.aws.amazon.com/cloudwatch/)을 엽니다.

2. 탐색 창에서 [**Rules**]를 선택하고 [**Create rule**]을 선택합니다.
   ![cloudwatch_event](images/cloudwatch_event.png)

3. [**Event Source**] 섹션에서 [**일정**]을 선택합니다. 대상에서 생성한 함수를 선택합니다. (20분마다 cloudwatch에서 Lambda에 trigger를 날리게 된다.)
   ![cloudwatch_envent_2](images/cloudwatch_envent_2.png)

4. 세부 정보 설정
   ![cloudwatch_event_3](images/cloudwatch_event_3.png)
5. 생성 완료

![cloudwatchevent_4](images/cloudwatchevent_4.png)

![cloudwatch_trigger](images/cloudwatch_trigger.png)

6. 호출 확인
   Lambda

   ![lambda_result](images/lambda_result.png)

   Workflow
   ![lambda_result_2](images/lambda_result_2.png)

### 2. Glue Trigger를 사용하여 Scheduling

#### 1단계: 새로운 Job 생성

1. ETL에 있는 **Job**을 선택하고 **작업추가**를 선택합니다.
   ![glue_job_create_1](images/glue_job_create_1.png)

2. 이름과 설명 지정
   ![glue_new_job](images/glue_new_job.png)

3. 코드 작성
   ![glue_new_job_2](images/glue_new_job_2.png)

   ```python
   import sys
   from awsglue.transforms import *
   from awsglue.utils import getResolvedOptions
   from pyspark.context import SparkContext
   from awsglue.context import GlueContext
   from awsglue.job import Job
   from pyspark.sql.functions import *
   from awsglue.dynamicframe import DynamicFrame
   from pyspark.sql.types import *
   import os
   
   sc = SparkContext.getOrCreate()
   glueContext = GlueContext(sc)
   spark = glueContext.spark_session
   
   try:
       cmd = "hdfs dfs -rm -r -skipTrash {S3_URL_KEY}"
       os.system (cmd)
   except Exception as ex:
       pass
   
   table_name = "{Dynamodb_Table_Name}"
   table = glueContext.create_dynamic_frame.from_options(
     "dynamodb",
     connection_options={
       "dynamodb.input.tableName": table_name
     }
   )
   
   repartition = table.toDF()
   repartition.coalesce(1).write.mode('append').option("header", "true").csv('{S3_URL_KEY}')
   ```

   

#### 2단계: Scheduling할 Trigger 생성

1. 트리거 추가하기
   ![glue_trigger](images/glue_trigger.png)

   새로운 트리거를 추가합니다. 유형을 일정으로 선택합니다. 빈도는 사용자 지정으로 cron형식으로 설정가능합니다.
   ***/20 * * * ? *** 으로 설정하면 20분마다 트리거를 일으켜 workflow가 실행됩니다.
   ![glue_trigger_2](images/glue_trigger_2.png)

   두번째 Trigger
   ![glue_trigger_3](images/glue_trigger_3.png)

   ![glue_trigger_4](images/glue_trigger_4.png)

2. 실행하기

   ![glue_trigger_activate](images/glue_trigger_activate.png)

#### 3단계: Trigger와 Job으로 workflow 새롭게 구성

1. **Add workflow(워크플로우 추가)**를 선택하고 **Add a new ETL workflow(새 ETL 워크플로우 추가)** 양식을 작성합니다.

   추가하는 선택적 기본 실행 속성은 워크플로우의 모든 작업에 대한 인수로 사용할 수 있습니다. 

   ![glue_workflow_create_1](images/glue_workflow_create_1.png)

2. 기존의 트리거를 복사 하여 그래프 설정
   ![new_glue_workflow](C:\Users\jungmin.choi\Desktop\git project\with-aws\Case_Solution\Solution\images\new_glue_workflow.png)

3. 결과
   S3에서 객체 확인
   ![s3_result](images/s3_result.png)

   2분 간격으로 csv 2개가 생성된 것을 확인했다.

   EC2로 내용물 확인

   ![data_result](images/data_result.png)

4. **기록**탭에서 20분 단위로 실행되는 것을 확인할 수 있다.
   ![time_check](images/time_check.png)
