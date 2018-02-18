ENV VARS:

INFLUXHOST - influxdb host
INFLUXPORT - influxdb port
INFLUXDB -   influxdb database
POLL_INTERVAL - # seconds between API connections

ST_TOKEN - smartthings API token
ST_CLIENT - smartthings API client_id

docker run -d e ST_TOKEN=<token> -e ST_CLIENT=<clientid> --restart=always --name zwave thecase/smartthings-influx
