from aws_cdk import core
from aws_cdk import aws_cloudwatch as cw
from aws_cdk.aws_cloudwatch import GraphWidget
import boto3

session = boto3.Session(profile_name='default')
account_id = session.resource('iam').CurrentUser().arn.split(':')[4]

# Returns CloudWatch Metrics on each functions
def get_metrics(_metricName, _statistic):
    metrics = []
    metrics.append(
        cw.Metric(
            metric_name = _metricName,
            namespace = 'AWS/ES',
            dimensions={
                "DomainName" :'managed-es',
                "ClientId" : account_id
            },
            statistic = _statistic,
        )
    )

    return metrics

# Returns GraphicWidget
def get_GrapthWidget(_title, _metricName, _statistic, _width, _height):
    return GraphWidget(
                title=_title,
                left=get_metrics(_metricName, _statistic),
                width=_width,
                height=_height
            )



class Elasticsearch(core.Construct):
    
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        dashboard = cw.Dashboard(self, id, dashboard_name=id) # 3rd Arg is the name of dashboard.
        dashboard.add_widgets(
            GraphWidget(title='ClusterStatus',
            left=[
                cw.Metric(metric_name='ClusterStatus.green', namespace='AWS/ES', color='#2ca02c', dimensions={"DomainName":'managed-es', "ClientId":account_id}, statistic='Sum'),
                cw.Metric(metric_name='ClusterStatus.yellow', namespace='AWS/ES', color='#FFFF33', dimensions={"DomainName":'managed-es', "ClientId":account_id}, statistic='Sum'),
                cw.Metric(metric_name='ClusterStatus.red', namespace='AWS/ES', color='#FF0000', dimensions={"DomainName": 'managed-es', "ClientId": account_id}, statistic='Sum')
            ],
            width=6,
            height=6),
            get_GrapthWidget('ClusterIndexWritesBlocked','ClusterIndexWritesBlocked','Maximum',6,6),
            get_GrapthWidget('Nodes','Nodes','Maximum',6,6),
            get_GrapthWidget('FreeStorageSpace','FreeStorageSpace','Sum',6,6),
            get_GrapthWidget('AutomatedSnapshotFailure','AutomatedSnapshotFailure','Maximum',6,6),
            get_GrapthWidget('KibanaHealthyNodes','KibanaHealthyNodes','Average',6,6),
            get_GrapthWidget('SearchableDocuments','SearchableDocuments','Average',6,6),
            get_GrapthWidget('CPUUtilization','CPUUtilization','Maximum',6,6),
        )
