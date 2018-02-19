ENV VARS:

INFLUXHOST - influxdb host
INFLUXPORT - influxdb port
INFLUXDB -   influxdb database
POLL_INTERVAL - # seconds between API connections

ST_TOKEN - smartthings API token

You can get a personal access token from https://account.smartthings.com/tokens

docker run -d e ST_TOKEN=<token> --restart=always --name zwave thecase/smartthings-influx
