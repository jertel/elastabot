import os
import elasticsearch
from elasticsearch.client import Elasticsearch

# Creates an Elasticsearch client via options stored in the provided config file
def createElasticsearchClient(conf):
  auth = None
  username = os.environ.get('ELASTICSEARCH_USERNAME')
  password = os.environ.get('ELASTICSEARCH_PASSWORD')
  if username and password:
    auth = (username, password)
  return Elasticsearch(host=conf['elasticsearch']['host'],
                        port=conf['elasticsearch']['port'],
                        url_prefix=conf['elasticsearch']['urlPrefix'],
                        use_ssl=conf['elasticsearch']['sslEnabled'],
                        verify_certs=conf['elasticsearch']['sslStrictEnabled'],
                        http_auth=auth,
                        timeout=conf['elasticsearch']['timeoutSeconds'])
