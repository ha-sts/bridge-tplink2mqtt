#!/bin/sh

. venv/bin/activate

export HASTS_MQTT_SERVER_PASS=xxx
export HASTS_ALWAYS_PUBLISH=true
export HASTS_MQTT_SERVER_USER=xxx
export HASTS_MQTT_SERVER_HOST=xxx
export HASTS_MQTT_SERVER_PORT=1883
export HASTS_TPLINK_TARGET_BROADCAST=xxx

python run.py
