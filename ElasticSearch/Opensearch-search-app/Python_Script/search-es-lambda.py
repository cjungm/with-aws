import boto3
import json
import os
import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection
from pprint import pprint

region = os.environ['AWS_REGION']
credentials = boto3.Session().get_credentials()

host = os.environ['HOST']
index = 'master_product'

client = boto3.client('ssm')
es_master_pw = client.get_parameter(Name='ESMasterPW')['Parameter']['Value']
es_master_user = client.get_parameter(Name='ESMasterUser')['Parameter']['Value']

awsauth = (es_master_user, es_master_pw)

client = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)

# Lambda execution starts here
def lambda_handler(event, context):
    es_action = event['queryStringParameters']['action']

    if es_action == "rank-list":
        # Put the user query into the query DSL for more accurate search results.
        # Note that certain fields are boosted (^).
        query = {
            "size": 10,
            "query": { "term": { "UserName": event['queryStringParameters']['q'] } },
            "aggs": {
                "time_filter": {
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-3h",
                            "lt": "now"
                        }
                    }
                },
                    "aggs": {
                            "product_name": {
                            "terms": {
                                "field": "Name"
                            }
                        }
                    }
                }
            }
        }

        r = {
            "product" : []
        }

        # Make the signed HTTP request
        bucket_list = client.search(
            body = query,
            index = "rank_list"
        )['aggregations']['time_filter']['product_name']['buckets']

        for i in range(10):
            if i < len(bucket_list):
                r["product"].append({"Name":bucket_list[i]['key']})
            else:
                pass

    elif es_action == "login":
        query = {
            "size": 1,
            "query": {
                "multi_match": {
                    "query": event['queryStringParameters']['q'],
                    "fields": ["_id"]
                }
            }
        }

        r = client.search(
            body = query,
            index = "user_account"
        )

    else:
        # Put the user query into the query DSL for more accurate search results.
        # Note that certain fields are boosted (^).
        query = {
            "size": 25,
            "query": {
                "multi_match": {
                    "query": event['queryStringParameters']['q'],
                    "fields": ["Name"]
                }
            },
            "sort" : ["_score"]
        }
        
        # Make the signed HTTP request
        r = client.search(
            body = query,
            index = index
        )

        if es_action == "search":
            id = event['requestContext']['extendedRequestId']
            params=event['queryStringParameters']['q'].split("/")
            document = {
                "UserName": params[1],
                'Name': r['hits']['hits'][0]['_source']['Name'],
                'Search_word': params[0],
                'PrdNo': r['hits']['hits'][0]['_source']['PrdNo'],
                "@timestamp": utc_time()
            }
            client.index(
                index = "rank_list",
                body = document,
                id = id,
                refresh = True
            )

    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    # Add the search results to the response
    response['body'] = json.dumps(r)
    return response

def utc_time():  # @timestamp timezone을 utc로 설정하여 kibana로 index 생성시 참조
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')