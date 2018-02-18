#!/usr/bin/env python

import sys, os
import smartthings
import time
from influxdb import InfluxDBClient

def fixName(name):
    name = name.replace(" ","_")
    name = name.replace(":","")
    return name.lower()

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

maps = { "Root Cellar": "cellar",
         "Root Cellar old": "deadcellar",
         "Porch": "porch",
         "Mailbox": "mailbox",
         "Greenhouse": "greenhouse",
         "Ejector Pump": "ejector",
         "Leaf Charger": "leaf"
}

measures = { "temperatureMeasurement": "temperature",
             "relativeHumidityMeasurement": "humidity",
             "battery": "battery",
             "acceleration": "active",
             "powerMeter": "power"
}

while True:
    for device in smartthings.states():
       if device['type'] in measures:
           meas =  measures[device['type']]
           if meas == "battery":
               name = fixName(device['label'])
           else:
               name = maps[device['label']]
           val  = device['value']
           print("{0} {1}: {2}").format(name,meas,val)
           if val == None:
              val = -1
         #  influx(meas, name, int(val))
    time.sleep(int(os.environ['POLL_INTERVAL'])) 
