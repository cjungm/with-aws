# CDK Python project CloudWatch DashBoard

Elasticsearch Metric들로 CloudWatch DashBoard 생성하기

cdk.json : App 실행 방법에 대한 명세

이 프로젝트는 표준 Python 프로젝트처럼 설정
초기화 프로세스는 또한 이 프로젝트 내에 .venv 아래에 저장된 virtualenv를 생성
virtualenv를 생성하려면 경로에`venv`에 대한 액세스 권한이있는`python3` (또는 Windows의 경우`python`) 실행 파일이 있다고 가정
virtualenv 자동 생성이 실패하면 virtualenv를 수동으로 생성 할 수 있습니다.

virtualenv 설치 및 생성

```
pip3 install virtualenv
virtualenv .venv
```

초기화 프로세스가 완료되고 virtualenv가 생성 후 virtualenv 활성화

```
source .venv/Scripts/activate
```

cdk 설치

```
npm install -g aws-cdk
```

종속 library 설치

```
pip3 install -r requirements.txt
```

CloudFormation template 동기화 및 배포

```
cdk synth --profile default
```

```
cdk deploy --profile default
```

종속성 (예 : 다른 CDK 라이브러리)을 추가하려면`setup.py` 파일에 추가하고`pip install -r requirements.txt` 명령을 다시 실행하면됩니다.

## Useful commands

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation
- `cdk destroy` destroy CDK stack


