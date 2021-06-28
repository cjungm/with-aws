# EC2, RDS Stop Monitoring

정해진 규칙에 따라 EC2, RDS의 Instance 및 Cluster를 매 시간마다 중지 시키는 Service

1. [규칙](#1.-규칙)
2. [Lambda 생성](#2.-lambda-생성)
3. [Cloudwatch Rule 생성](#3.-cloudwatch-rule-생성)

## 1. 규칙

1. 필수 Tag
   1. Name : "{Instance_Name}"
   2. Owner : "{User_Name}"
   3. Expiry-date : "{End_Date}" (Format : YYYY-mm-dd)
2. 하단의 규칙에 위배될 경우 중지
   1. 모든 EC2, RDS Instance 및 Cluster는 필수 Tag 부착
   2. Expiry-date를 초과 시 중지
3. Monitoring 주기는 매 시간 정각

<div style="page-break-after: always; break-after: page;"></div>

## 2. Lambda 생성

1. [Lambda](https://console.aws.amazon.com/lambda/home#/functions) 열기

2. `함수 생성`
   Region : `us-west-2` 

   ![lambda_function](images\lambda_function.png)

3. 함수 이름 : `Monitoring-EC2`
   런타임 : `Python 3.8`
   실행 역할 : `기본 Lambda 권한을 가진 새 역할 생성`
   고급 설정 : 해당 내용들은 기본값 ( 네트워크 설정은 Code 상에서 모든 Region을 조회하는 로직이기 때문에 VPC 설정 X )

4. Lambda 설정

   1. Code
      EC2 Monitoring 이므로 `ec2_stop` code를 code editor에 복사 붙여넣기
      `Deploy` 로 저장

      ![lambda_code](images\lambda_code.png)

   2. handler

      Handler 설정에 따라 Lambda 함수가 수행되면 lambda_function.py 파일의 lambda_handler method를 제일 먼저 수행

      일반적인 python code의 main method에 해당하므로 자신의 code에 따라 handler를 편집
      ![lambda_handler](images\lambda_handler.png)

   3. config 변경

      설명 : `Monitoring Service for EC2`

      메모리 : `128` (기본값이 128)

      제한 시간 : `3분` (기본값 3초)

      메모리는 기본값이면 충분하지만 제한 시간은 변경 필요
      ![lambda_configuration](images\lambda_configuration.png)

<div style="page-break-after: always; break-after: page;"></div>

## 3. Cloudwatch Rule 생성

1. [Cloudwatch](https://console.aws.amazon.com/cloudwatch/) 열기

2. `Event` tab에서 `규칙 생성`
   ![cloudwatch](images\cloudwatch.png)

3. 규칙 구성

   1. 이벤트 소스 : `일정`
   2. 고정 비율 : `1 시간`
   3. 대상 : `Lambda 함수`
      함수 : `Monitoring-EC2`

   ![cloudwatch_event](images\cloudwatch_event.png)

4. 결과 확인

   트리거에 1시간 단위로 trigger를 걸어줄 cloudwatch event가 추가
   ![lambda_result](images\lambda_result.png)
