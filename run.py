#!/usr/bin/env python3

### IMPORTS ###
import argparse
import asyncio
import logging
import os

from hasts.bridges.tplink2mqtt import MethodTickler
from hasts.bridges.tplink2mqtt import MqttClient
from hasts.bridges.tplink2mqtt import TPLinkDeviceManager

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###

### MAIN ###
def main():
    # Parse Arguments
    parser = argparse.ArgumentParser(
        description = "Bridge program for allowing TPLink devices to be controlled via MQTT.",
        epilog = "Thank you for using the HA-STS project."
    )
    parser.add_argument("--verbose", action = "store_true", help = "Enable debug logging.")
    parser.add_argument("--username", help = "Username for MQTT server", default = os.getenv("HASTS_MQTT_SERVER_USER"))
    parser.add_argument("--password", help = "Password for MQTT server", default = os.getenv("HASTS_MQTT_SERVER_PASS"))
    parser.add_argument(
        "--mqtt-port",
        help = "MQTT server network port.  Defaults to '1883'.",
        default = os.getenv("HASTS_MQTT_SERVER_PORT", "1883")
    )
    parser.add_argument(
        "--mqtt-host",
        help = "MQTT server hostname or IP address.  Defaults to 'localhost'.",
        default = os.getenv("HASTS_MQTT_SERVER_HOST", "localhost")
    )
    parser.add_argument(
        "--tplink-target-broadcast",
        help = "Broadcast address of the network containing the TPLink devices.  Defaults to '255.255.255.255'.",
        default = os.getenv("HASTS_TPLINK_TARGET_BROADCAST")
    )
    parser.add_argument(
        "--always-publish",
        action = "store_true",
        help = "Always publish the state information when performing the heartbeat updates.",
        default = os.getenv("HASTS_ALWAYS_PUBLISH", "false") in ['TRUE', 'True', 'true']
    )
    args = parser.parse_args()

    # Setup Logging
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(
        format = log_format,
        level = logging.DEBUG if args.verbose else logging.INFO
    )

    logging.debug("args: %s", args)

    # Setup the async tasks
    loop = asyncio.get_event_loop()

    mqttc = MqttClient(
        host = args.mqtt_host,
        port = args.mqtt_port,
        user = args.username,
        password = args.password
    )
    tpldm = TPLinkDeviceManager(
        mqtt_client = mqttc,
        tnba = args.tplink_target_broadcast,
        always_publish = bool(args.always_publish)
    )
    # Run the discovery every day and the heartbeat for state update every five minutes.
    ddt = MethodTickler(seconds = 86400, corofunc = tpldm.discover_devices)
    hbt = MethodTickler(seconds = 300, corofunc = tpldm.heartbeat)

    tasks = []
    task_mqtt_listener = loop.create_task(mqttc.run())
    tasks.append(task_mqtt_listener)
    task_tpldmr = loop.create_task(tpldm.register_coroutines())
    tasks.append(task_tpldmr)
    task_ddt = loop.create_task(ddt.run())
    tasks.append(task_ddt)
    task_hbt = loop.create_task(hbt.run())
    tasks.append(task_hbt)

    # Run the tasks
    loop.run_forever()

    # Catch and clean-up
    # FIXME: Should make this catch the keyboard interrupt (and possibly others)
    #        and make this shutdown gracefully, waiting for tasks and then
    #        disconnecting MQTT

if __name__ == "__main__":
    main()
