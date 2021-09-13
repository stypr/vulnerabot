#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""
vultr.py

Helper class for vultr
"""
from .vendor import vultr

def list_server():
    """
    List instances in json

    {"instances": [{...}, {...}, ...]}
    """
    return vultr.list_instances()

def delete_server(instance_name):
    """ (str) -> bool

    Delete server
    """
    for _instance in list_server()['instances']:
        if _instance['label'] == instance_name:
            vultr.delete_instance(_instance['id'])
            return True
    return False

def add_server(name, snapshot_id):
    """ (str, str) ->json()
    Add server based on given snapshot
    """
    return vultr.create_instance(name, snapshot_id)
