from elasticsearch import Elasticsearch
from pprint import pprint
import csv
import os

def search_api(es, index_name):
    index = index_name
    body = {
        'size':1,
        'query':{
            'match_all':{}
        }
    }
    res = es.search(index=index, body=body)
    return res

es = Elasticsearch(
    # 마스터 계정정보를 이용하여 http로 ES와 통신
    hosts = [{'host': '{host}', 'port': '{port}'}],
    http_auth = ('{username}', '{password}'),
    scheme="http"
)

indices = [""]
csv_columns = list(search_api(es, indices[0])['hits']['hits'][0]['_source'].keys())
csv_file = os.environ['HOME']+'/'+indices[0]+'_export.csv'

for index in indices:
    result = es.search(
        index =index,
        doc_type =index+"_doc",
        scroll ='5m',
        body = {
            'size':10000,
            'query':{
                'match_all':{}
            }
        }
    )
    scroll_id = result['_scroll_id']
    scroll_size = result['hits']['total']['value']
    while scroll_size > 0:
        with open(csv_file, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for doc in result['hits']['hits']:
                writer.writerow(doc['_source'])

        csvfile.close()

        result = es.scroll(scroll_id = scroll_id, scroll ='5m')

        scroll_id = result['_scroll_id']
        scroll_size = len(result['hits']['hits'])