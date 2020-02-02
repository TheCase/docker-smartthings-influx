#!/usr/bin/env python3

import time
import sys
import os
import requests
from influxdb import InfluxDBClient
import datetime

import logging
fmt="%(asctime)s - %(levelname)-s - %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt)
log = logging.getLogger(__name__)

from pprint import pprint

# define the capabilities we want to capture
capabilites = {"temperatureMeasurement":       "temperature",
               "relativeHumidityMeasurement":  "humidity",
               "battery":                      "battery",
               "acceleration":                 "active",
               "powerMeter":                   "power",  # watts
               "energyMeter":                  "energy",  # kWh
               "accelerationSensor":            "acceleration"
               }


def reformat(name, item_type):
  name = name.replace(" ", "_")
  name = name.replace("/", "-")
  name = name.replace(":", "")
  for tag in ['Lock']:
    if tag in item_type:
      name = "{0}-{1}".format(name, tag)
  return name.lower()


def convert(item):
  if isinstance(item, str):
    item = 0
    if item == "active":
      item = 1
  if item == None:
    item = 0
  return(item)


def influx(measurement, location, value):
  client = InfluxDBClient(os.getenv('INFLUXHOST', 'localhost'),
                          os.getenv('INFLUXPORT', '8086' ),
                          os.getenv('INFLUXUSER', 'root'),
                          os.getenv('INFLUXPASS', 'root'),
                          os.getenv('INFLUXDB',   'smartthings')
                         )
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
  token = os.getenv('ST_TOKEN', 'null')
  headers = {'Authorization': 'Bearer {0}'.format(token)}
  r = requests.get(url, headers=headers)
  check_error(r)
  data = r.json()
  if ('_links' in data and 'next' in data['_links']):
    log.error("fix this code for paging: https://smartthings.developer.samsung.com/develop/api-ref/st-api.html#section/Paging")
    sys.exit(1)
  return(data)


def check_error(r):
  if r.status_code != 200:
    log.error("OAuth error: {0}\n{1}".format(r.status_code, r.text))
    sys.exit(1)


def push(metrics):
  for item in metrics:
    ts = datetime.datetime.now().isoformat()
    (name, meas, value) = item.split(",")
    log.info("{0} influx: {1} {2}: {3}".format(ts, name, meas, value))
    influx(meas, name, value)


def main():
  sleep_interval = os.getenv('POLL_INTERVAL', 60)
  while True:
    metrics = list()
    d_url = 'https://api.smartthings.com/v1/devices'
    for device in get(d_url)['items']:
      process = False
      for cap in device['components'][0]['capabilities']:
        if cap['id'] in capabilites:
          process = True
      if process:
        url = '{0}/{1}/status'.format(d_url, device['deviceId'])
        for cap, info in get(url)['components']['main'].items():
          if cap in capabilites:
            name = reformat(device['label'], device['name'])
            meas = capabilites[cap]
            value = convert(info[meas]['value'])
            ts = datetime.datetime.now().isoformat()
            log.info("{0} smartthings: {1} {2}: {3}".format(ts, name, meas, value))
            metrics.append("{0},{1},{2}".format(name, meas, value))
    push(metrics)
    log.info("sleeping for {0} seconds".format(sleep_interval))
    time.sleep(sleep_interval)

if __name__ == '__main__':
  main()
