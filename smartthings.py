#!/usr/bin/env python

import requests, sys, os

def states():
    token  = os.environ['ST_TOKEN']
    client = os.environ['ST_CLIENT']
    headers = { 'Authorization': 'Bearer {0}'.format(token) }
    url = 'https://graph.api.smartthings.com/api/smartapps/endpoints/{0}?access_token={1}'.format(client,token)
    uri = requests.get(url).json()[0]['uri']
    readings = []
    for dType in ['power','temperature','humidity','battery']:
        url = '{0}/{1}'.format(uri,dType)
        r = requests.get(url, headers=headers)
        data = r.json()
        for item in data:
            readings.append(item)

    return readings

