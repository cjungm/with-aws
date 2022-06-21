from aws_cdk import core
from cw_dashboard.cw_dashboard_es import Elasticsearch

class CwDashboardStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        dashboard_es_creation = Elasticsearch(self, 'Managed-Es-DashBoard')  # 2nd Arg is the id of dashboard.
