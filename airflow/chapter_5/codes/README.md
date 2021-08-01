# 과제

시나리오 : S3의 CSV Data를 EMR의 Hive로 Table로 등록 후 pyspark 활용 변형 S3에 Upload

**모든 AWS 관련 작업은 Console 작업 금지**

상단의 Data가 S3에 위치해 있을 때 (s3://cjm-oregon/champion/data/Mall_Customers.csv)

## 1. Library 설치

Airflow에서 Hive Operator나 Hook을 사용하고 싶으면 먼저 Hive관련 Library를 설치하고 Connection을 생성해야합니다.

```sh
sudo yum install -y gcc-c++
sudo pip3 install sasl
sudo pip3 install 'apache-airflow[apache.hive]'
sudo pip3 install apache-airflow-providers-apache-hive
```

## 2. Hive Connection 설정

하단 Script와 같이 PythonOperator로 dynamic하게 Connection 생성 가능

```python
def make_connection(**kwargs):
    master_dns = ""
    conn_type = "hive_cli"
    cluster_id = kwargs['task_instance'].xcom_pull("task_cluster_id", key='return_value')
    master_dns = client.describe_cluster(
        ClusterId=cluster_id
    )['Cluster']['MasterPublicDnsName']

    session = settings.Session() # get the session
    conn = BaseHook.get_connection(conn_id)
    
    if conn:
        pprint(conn)
        session.delete(conn)
        session.commit()

    conn = Connection(
            conn_id=conn_id,
            conn_type=conn_type,
            login="hadoop",
            host=master_dns,
            port=10000
    )
    
    session.add(conn)
    session.commit()
```

## 3. DAG 구성

#### DAG_1

1. EMR 생성

   1. EMR Version : `emr-6.2.0`

   2. Subnet : `{Airflow와 동일 Subnet}

   3. Bootstrap Option : linux package 및 python library 설치

      ```sh
      #!/bin/bash
      
      # yum 최신화
      sudo yum update -y
      
      # python library 설치를 위한 package 설치
      sudo yum install libevent-devel zlib-devel gcc-c++ cyrus-sasl-devel.x86_64 gcc python3-devel.x86_64 -y
      ```

      기존 Numpy 버전 삭제 이유
      기존 버전을 삭제하지 않고 update나 추가 설치할 경우 하단과 같은 Issue 발생

      ```sh
      Traceback (most recent call last):
        File "/home/hadoop/transform_python.py", line 2, in <module>
          import pandas as pd
        File "/usr/local/lib64/python3.7/site-packages/pandas/__init__.py", line 22, in <module>
          from pandas.compat import (
        File "/usr/local/lib64/python3.7/site-packages/pandas/compat/__init__.py", line 15, in <module>
          from pandas.compat.numpy import (
        File "/usr/local/lib64/python3.7/site-packages/pandas/compat/numpy/__init__.py", line 21, in <module>
          f"this version of pandas is incompatible with numpy < {_min_numpy_ver}\n"
      ImportError: this version of pandas is incompatible with numpy < 1.17.3
      your numpy version is 1.16.5.
      Please upgrade numpy to >= 1.17.3 to use this pandas version
      ```

      삭제 하지 않을 경우 두 버전이 공존하며 기존 버전 library만 이용하게 되어 pandas 이용 불가

      ```sh
      [hadoop@ip-10-0-1-178 site-packages]$ ls
      click lxml-4.6.1-py3.7.egg-info numpy-1.21.1.dist-info regex thrift-0.13.0-py3.7.egg-info
      click-7.1.2.dist-info mysqlclient-1.4.2-py3.7.egg-info numpy.libs regex-2020.10.28-py3.7.egg-info  tqdm
      joblib MySQLdb pandas sasl tqdm-4.51.0.dist-info
      joblib-0.17.0.dist-info numpy pandas-1.3.1.dist-info sasl-0.3.1-py3.7.egg-info yaml
      lxml numpy-1.16.5-py3.7.egg-info PyYAML-5.3.1-py3.7.egg-info thrift
      ```

      

2. DAG_2 호출 (External Trigger)

   데이터 변환 및 데이터 형 변환 작업을 위한 DAG 호출

3. DAG_2 완료 시까지 상태 체크 (External Sensor)

4. EMR 종료

5. 수행 여부를 E-mail로 전송

#### DAG_2

1. DAG_1에서 생성한 EMR Hive로 S3의 Data 복사

   1. Hive Table 생성을 위한 Schema 확인
   2. S3 Select를 이용 Hive Table 생성

2. Library 설치 및 수정

   1. 하단 Script를 Add Step으로 작업

      ```sh
      #!/bin/bash
      
      # 기존 Numpy 버전 삭제
      sudo rm -r /usr/local/lib64/python3.7/site-packages/numpy*
      
      # python lib 설치
      sudo pip3 install numpy pandas pyhive thrift sasl thrift_sasl --use-feature=2020-resolver
      ```

      기존 Numpy 버전 삭제 이유 : 
      기존 버전을 삭제하지 않고 update나 추가 설치할 경우 하단과 같은 Issue 발생

      ```sh
      Traceback (most recent call last):
        File "/home/hadoop/transform_python.py", line 2, in <module>
          import pandas as pd
        File "/usr/local/lib64/python3.7/site-packages/pandas/__init__.py", line 22, in <module>
          from pandas.compat import (
        File "/usr/local/lib64/python3.7/site-packages/pandas/compat/__init__.py", line 15, in <module>
          from pandas.compat.numpy import (
        File "/usr/local/lib64/python3.7/site-packages/pandas/compat/numpy/__init__.py", line 21, in <module>
          f"this version of pandas is incompatible with numpy < {_min_numpy_ver}\n"
      ImportError: this version of pandas is incompatible with numpy < 1.17.3
      your numpy version is 1.16.5.
      Please upgrade numpy to >= 1.17.3 to use this pandas version
      ```

      삭제 하지 않을 경우 두 버전이 공존하며 기존 버전 library만 이용하게 되어 pandas 이용 불가

      Bootstrap이 아닌 Add Step으로 작업하는 이유는 Bootstrap이후에 삭제해야하는 Numpy version이 구성되기 때문에 EMR 구성 완료 후에 필요한 작업이기 떄문

      ```sh
      [hadoop@ip-10-0-1-178 site-packages]$ ls
      click lxml-4.6.1-py3.7.egg-info numpy-1.21.1.dist-info regex thrift-0.13.0-py3.7.egg-info
      click-7.1.2.dist-info mysqlclient-1.4.2-py3.7.egg-info numpy.libs regex-2020.10.28-py3.7.egg-info  tqdm
      joblib MySQLdb pandas sasl tqdm-4.51.0.dist-info
      joblib-0.17.0.dist-info numpy pandas-1.3.1.dist-info sasl-0.3.1-py3.7.egg-info yaml
      lxml numpy-1.16.5-py3.7.egg-info PyYAML-5.3.1-py3.7.egg-info thrift
      ```

      

3. 복사한 Data를 `Spending Score (1-100)`을 오름차순으로 변경

   1. python 이용 Data 변경
   2. 변경 된 Data를 Local File Storage에 저장

4. 변경한 Data를 S3에 Parquet로 저장

   1. Local Data를 Load하여 S3에 Parquet로 Write

---

예시 코드)

1. [DAG_1](codes/assign_emr_1.py)
2. [DAG_2](codes/assign_emr_2.py)
3. [Bootstrap](codes/bootstrap.sh)
4. [Bash_Command](codes/bash_command.sh)
5. [Data_Transform](codes/transform_python.py)
6. [Data_Format_Transform](codes/transform_pyspark.py)

