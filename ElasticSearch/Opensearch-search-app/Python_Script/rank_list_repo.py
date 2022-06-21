import boto3, sys, requests
from requests_aws4auth import AWS4Auth

es_domain = sys.argv[1]
role_arn = sys.argv[2]

host = es_domain
region = 'us-west-2' # e.g. us-west-2
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# Register repository

path = '_snapshot/rank_list_repo' # the Elasticsearch API endpoint
url = host + path

payload = {
  "type": "s3",
  "settings": {
    "bucket": "{YOUR_S3_BUCKET_NAME}",
    "region": region,
    "base_path": "{YOUR_S3_SNAPSHOT_PATH}",
    "role_arn": role_arn
  }
}

headers = {"Content-Type": "application/json"}

r = requests.put(url, auth=awsauth, json=payload, headers=headers)

print(r.status_code)
print(r.text)