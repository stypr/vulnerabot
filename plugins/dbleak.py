#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""
dbleak.py

Translate Format
"""

from elasticsearch import Elasticsearch

# Init connection
_ES_URL = "localhost:9200"
es_client = Elasticsearch(_ES_URL, http_compress=True)

def find_account(account_name, threshold=10):
    """ (str, int) -> dict

    Search on ElasticSearch to find a credential for a given query
    """
    output = ""
    _parts = account_name.split("@", maxsplit=1)
    _query = {}
    if len(_parts) > 1:
        _query = {
            "bool": {
                "must": [
                    {"match": {"username": {"query": _parts[0]}}},
                    {"match": {"hostname": {"query": _parts[1]}}},
                ],
            }
        }
    else:
        _query = {
            "match": {
                "username": {"query": _parts[0]}
            }
        }

    _result = es_client.search(query=_query, size=threshold)
    _result_total = _result['hits']['total']['value']
    _result = _result['hits']['hits']

    for _result_data in _result:
        output += " - **ID:** "
        output += _result_data['_source']['username']
        output += "@"
        output += _result_data['_source']['hostname']
        output += " / **PW:** "
        output += _result_data['_source']['password']
        output += "\n"

    return output

def find_domain(domain_name, threshold=10):
    """ (str) -> str

    Search on ElasticSearch to find a credential for a given query
    """
    output = ""
    _query = {
        "match": {
            "hostname": {"query": domain_name}
        }
    }

    _result = es_client.search(query=_query, size=threshold)
    _result_total = _result['hits']['total']['value']
    _result = _result['hits']['hits']

    i = 0
    output = "id,username,password\n"
    for _result_data in _result:
        i += 1
        output += str(i)
        output += ","
        output += _result_data['_source']['username']
        output += "@"
        output += _result_data['_source']['hostname']
        output += ","
        output += _result_data['_source']['password']
        output += "\n"

    return output
