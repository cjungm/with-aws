# Amazon과 Elastic Cloud Service 비교



## AWS Elasticsearch 제약 사항

- 수집에 대한 별도의 구성이 필요 ( Logstash, Fluentbeat ... etc)
- 제공되는 plugin의 제한 ( x-pack, nori ... etc) 으로 인한 기능 제한 ( Machine Learning, Maps ... etc )
- Cluster에 대한 확장성이나 구성 변경에 제한적
- Downtime Cluster Upgrade라는 장점이 있지만 [버전에 따라 Index들이 손상될 수 있는 risk 존재 ](https://docs.aws.amazon.com/ko_kr/elasticsearch-service/latest/developerguide/es-version-migration.html)
- [Migration 시 version 호환에 대한 제약 사항](https://www.elastic.co/kr/support/matrix#matrix_compatibility)



## 비교 요약 :

- Elastic Cloud Service는 수집, 정제, 분석, 시각화 등의 일련의 서비스들이 하나의 제품군으로 구성이 되어있기에 연동이나 관리 기능 다양하고 이에 따라 확장 및 관리가 용이
- Aws Elasticsearch 는 Elasticsearch와 Kibana 만을 Managed service로 제공하기 때문에 수집과 관련된 기능은 별도로 구성이 필요하며 제공 plugin 에 대한 제약 사항이 많아 사용할 수 없는 기능들이 다수 존재, 모니터링 또한 Stack에 대한 모니터링이 아닌 Elasticsearch cluster에 대한 모니터링 기능만을 제공. 그 외의 일반적인 기능들은 정상적으로 제공됩니다.



## 비교 표

|                           | AWS ES                                                       | Elastic Cloud Service                                        |
| ------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Elastic Stack 보안        | 외곽 경계 수준 전용 보안 및 표준 IAM 정책                    | ● 전송 암호화 <br />● 인증 <br />● 역할 기반 액세스 제어 <br />● 속성 기반 액세스 제어 <br />● 필드 및 문서 수준 보안 <br />● 휴면 암호화 |
| Alerting                  | 추가 적인 AWS Service들과 함께 Alerting 제공<br />● 규칙 기반 경보 이상으로 이상 징후 알림<br />● 별도로 요금이 청구되는 서비스인 SNS는 이메일, 텍스트, HTTP 또는 Lambda 경보에 필요합니다. | Elasticsearch와 Kibana에 완전히 통합되고 맞춤화됨: <br />● SIEM, APM, Logs, Metrics, Uptime을 위해 설계된 도메인 인식 경보 UI, 각 앱을 떠나지 않고도 이용 가능 <br />● 모든 경보 조회, 검색, 관리를 위한 단일 UI <br />● PagerDuty, JIRA, ServiceNow 같은 서드파티 도구와 기본 통합 <br />● Elasticsearch 인덱스, 서버 로그 등에 이벤트를 전송할 수 있는 기본 기능 <br />● 규칙 기반 경보 이상으로 확장 가능한 지도 및 비지도 머신 러닝 이상 징후 탐색 |
| Machine Learning          | 자체 서비스가 아닌 추가적인 AWS 서비스나 서드파티 서비스를 사용해 생성된 자체 모델을 구축하고 관리<br />● 이상 징후 탐색 (자체 서비스에서 제공) | Elasticsearch의 완전히 통합된 API와 Kibana의 UI를 통해 사용자의 머신 러닝 환경을 간소화하고 성능을 강화. <br />● 이상 징후 탐색 <br />● 회귀, 분류 및 이상값 탐색 모델을 위한 자동화 머신 러닝(AutoML) <br />● 머신 러닝 모델을 위한 유추 프로세서 |
| Stack Monitoring          | 클러스터 상태, 노드 정보 등을 포함하는 몇 가지 메트릭에 적용되는 Amazon Cloudwatch에 따름. <br />Elastic Stack 과 같은 통합적인 모니터링 기능 없음( Elasticsearch 단일 서비스 이기 때문 ) | 모니터링 제품으로 Elasticsearch와 Kibana에 특별히 맞춤 설계됨. <br />● 10초 데이터 단위로 검색<br />● 인덱스 비율 및 대기시간<br />● 가비지 수집 횟수 및 기간<br />● 스레드 풀 대량 거부/대기열<br />● Lucene 메모리 분석 등을 포함하는 광범위한 메트릭을 캡처. <br />● 클러스터 문제에 대한 자동 알림 등 진단 및 문제 해결과 클러스터가 정상적인 상태로 유지되도록 하기 위한 강력한 도구. |
| Kibana 스페이스           | Multi-Tenant 로 Internal User 별 권한 제어                   | 접속자별로 분리된 공간에서 키바나 활용                       |
| 수집기 관리 기능          | Beats, Logstash, Fluentd                                     | Beats, Logstash, Fluentd, Elastic Agent, Fleet               |
| Elastic 에이전트          | 미제공                                                       | 제공                                                         |
| Elastic Maps              | 미제공                                                       | 제공                                                         |
| Graph                     | 미제공                                                       | 제공                                                         |
| Reporting                 | Discover, Dashboard, Visualize Library                       | Discover, Dashboard, Visualize Library, Canvas               |
| Google 계정으로 콘솔 등록 | 사용자 맞춤형 개발 또는 별도로 요금이 청구되는 Cognito 서비스가 필요함 | 사용자 맞춤형 개발이 필요하지 않음                           |
| 기술 지원                 | aws support를 통해 기술 문의 가능                            | 문의내용의 중요 레벨에 따라 아래 규정으로 응대 <br />플래티넘 라이센스 - 1시간, 4시간, 1일 안에 <br />골드 - 4시간, 1일, 일 <br />스탠다드 - 없음 |
| Plugin                    | 제공되는 plugin 및 사용자 정의 package 사용 가능<br />Elastic에 비해 갯수가 적고 제한 사항이 많음 | 다양한 plugin 및 사용자 package 사용 가능                    |

[참고 자료](https://www.elastic.co/kr/blog/hosted-elasticsearch-services-roundup-elastic-cloud-and-amazon-elasticsearch-service)