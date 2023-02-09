FROM alpine:3.17

RUN apk -u add python3 py3-pip && \
    pip install --upgrade pip && \ 
    pip install requests influxdb

COPY *.py /

ENV INFLUXHOST localhost
ENV INFLUXPORT 8086
ENV INFLUXUSER root
ENV INFLUXPASS root
ENV INFLUXDB   zwave

ENV ST_TOKEN XXXXXXXXXXXX

CMD [ "python3", "smartthings.py" ]
