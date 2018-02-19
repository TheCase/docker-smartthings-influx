#!/usr/bin/env python

import time, sys, os
import requests
from influxdb import InfluxDBClient
import datetime

from pprint import pprint

maps = { "Root Cellar": "cellar",
         "Root Cellar old": "deadcellar",
         "Porch": "porch",
         "Mailbox": "mailbox",
         "Greenhouse": "greenhouse",
         "Ejector Pump": "ejector",
         "Leaf Charger": "leaf"
}

# define the capabilities we want to capture
capabilites = { "temperatureMeasurement":       "temperature",
                "relativeHumidityMeasurement":  "humidity",
                "battery":                      "battery",
                "acceleration":                 "active",
                "powerMeter":                   "power",  #watts
                "energyMeter":                  "energy", #kWh
                "accelerationSensor":            "acceleration"
}

def reformat(name):
    name = name.replace(" ","_")
    name = name.replace("/","-")
    name = name.replace(":","")
    return name.lower()

def convert(item):
    if isinstance(item, basestring):
        item = 0
        if item == "active":
            item = 1
    return(item)

def retag(item,item_type):
    for tag in ['Sensor','Lock']:
        if tag in item_type:
            item = "{0}-{1}".format(item,tag.lower())
    return(item)

def influx(measurement, location, value):
    client = InfluxDBClient(os.environ['INFLUXHOST'], os.environ['INFLUXPORT'], os.environ['INFLUXUSER'], os.environ['INFLUXPASS'], os.environ['INFLUXDB'])
    json_body = [
        {
            "measurement": str(measurement),
            "tags": {
                "source": "zwave",
                "location": str(location)
            },
            "fields": {
                "value": float(value)
            }
        }
    ]
    client.write_points(json_body)

def get(url):
    token  = os.environ['ST_TOKEN']
    headers = { 'Authorization': 'Bearer {0}'.format(token) }
    r = requests.get(url,headers=headers)
    check_error(r)
    data = r.json()
    if ('_links' in data and data['_links']['next'] != None):
        print "fix this code for paging: https://smartthings.developer.samsung.com/develop/api-ref/st-api.html#section/Paging"
        sys.exit(1)
    return(data)

def check_error(r):
    if r.status_code != 200:
        print("OAuth error: {0}\n{1}").format(r.status_code,r.text)
        sys.exit(1)

def push(metrics):
    for item in metrics:
        ts = datetime.datetime.now().isoformat()
        (name,meas,value) = item.split(",")
        print("{0} influx: {1} {2}: {3}").format(ts,name,meas,value)
        influx(meas, name, value)

def main():
    metrics = list()
    d_url = 'https://api.smartthings.com/v1/devices'
    for device in get(d_url)['items']:
        label = retag(device['label'],device['name'])
        process = False
        for cap in device['components'][0]['capabilities']:
            if cap.values()[0] in capabilites:
                process = True
        if process:
            url = '{0}/{1}/status'.format(d_url,device['deviceId'])
            for cap,info in get(url)['components']['main'].iteritems():
                if cap in capabilites:
                    name = reformat(label)
                    meas = capabilites[cap]
                    value = convert(info[meas]['value'])
                    ts = datetime.datetime.now().isoformat()
                    print("{0} smartthings: {1} {2}: {3}").format(ts,name,meas,value)
                    metrics.append("{0},{1},{2}".format(name,meas,value))
    push(metrics)

if __name__ == '__main__':
    while True:
        main()
        ts = datetime.datetime.now().isoformat()
        print("{0} sleeping for {1} seconds").format(ts,os.environ['POLL_INTERVAL'])
        time.sleep(int(os.environ['POLL_INTERVAL']))
