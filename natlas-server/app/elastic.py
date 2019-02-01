import json
from elasticsearch import Elasticsearch
import random


class Elastic:
    es = ''

    def __init__(self, elasticURL):
        self.es = Elasticsearch(elasticURL)

    def search(self, query, limit, offset):
        if query == '':
            query = 'nmap'

        try:
            result = self.es.search(index="nmap", doc_type="_doc", body={"size": limit, "from": offset, "query": {"query_string": {
                                    'query': query, "fields": ["nmap_data"], "default_operator": "AND"}}, "sort": {"ctime": {"order": "desc"}}})
        except:
            return 0, []  # search borked, return nothing

        #result = es.search(index="nmap", doc_type="_doc", body={"size":limit, "from":offset, "query": {"match": {'nmap_data':query}}})
        count = 1

        results = []  # collate results
        for thing in result['hits']['hits']:
            results.append(thing['_source'])

        return result['hits']['total'], results

    def newhost(self, host):
        ip = str(host['ip'])
        # broken in ES6
        self.es.index(index='nmap_history', doc_type='_doc', body=host)
        self.es.index(index='nmap', doc_type='_doc', id=ip, body=host)

    def gethost(self, ip):
        result = self.es.search(index='nmap_history', doc_type='_doc', body={"size": 1, "query": {"query_string": {
                                'query': ip, "fields": ["nmap_data"], "default_operator": "AND"}}, "sort": {"ctime": {"order": "desc"}}})
        if result['hits']['total'] == 0:
            return 0, None
        return result['hits']['total'], result['hits']['hits'][0]['_source']

    def gethost_history(self, ip, limit, offset):
        result = self.es.search(index='nmap_history', doc_type='_doc', body={"size": limit, "from": offset, "query": {
                                "query_string": {'query': ip, "fields": ["nmap_data"], "default_operator": "AND"}}, "sort": {"ctime": {"order": "desc"}}})

        results = []  # collate results
        for thing in result['hits']['hits']:
            results.append(thing['_source'])

        return result['hits']['total'], results

    def gethost_scan_id(self, scan_id):
        result = self.es.search(index='nmap_history', doc_type='_doc', body={"size": 1, "query": {
                                "query_string": {'query': scan_id, "fields": ["scan_id"], "default_operator": "AND"}}, "sort": {"ctime": {"order": "desc"}}})

        if result['hits']['total'] == 0:
            return 0, None
        return result['hits']['total'], result['hits']['hits'][0]['_source']

    def getwork_mass(self):  # getwork when masscan data is loaded

        # get random ip
        result = self.es.search(index="masscan_hosts", doc_type="_doc", body={"size": 1, "query": {
                                "function_score": {"functions": [{"random_score": {"seed": random.randint(0, 2**60)}}]}}})
        randip = str(result['hits']['hits'][0]['_source']['ip'])

        # get ports
        result = self.es.search(index="masscan_services", doc_type="_doc", body={
                                "size": 1000, "query": {"match": {'ip': randip}}})
        ports = []  # collate results
        for thing in result['hits']['hits']:
            ports.append(thing['_source']['ports'][0]['port'])

        work = {}
        work['type'] = 'nmap'
        work['target'] = randip
        work['ports'] = ports
        return json.dumps(work)