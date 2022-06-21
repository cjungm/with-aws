#!/usr/bin/env python3

from aws_cdk import core
from cw_dashboard.cw_dashboard_stack import CwDashboardStack
import boto3

session = boto3.Session(profile_name='default')
account_id = session.resource('iam').CurrentUser().arn.split(':')[4]
env_US = core.Environment(account=account_id,region="us-west-2")
app = core.App()
CwDashboardStack(app, "es-dashboard-stack", env=env_US)

app.synth()
