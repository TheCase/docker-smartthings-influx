FROM python:3.8.10-slim-buster

RUN pip install --upgrade pip

RUN pip install requests influxdb 

COPY *.py /

ENV INFLUXHOST localhost
ENV INFLUXPORT 8086
ENV INFLUXUSER root
ENV INFLUXPASS root
ENV INFLUXDB   zwave 

ENV ST_TOKEN XXXXXXXXXXXX

CMD [ "python3", "smartthings.py" ]
