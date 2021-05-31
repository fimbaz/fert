#!/usr/bin/env python
import requests
import paho.mqtt.client as mqtt
import sys, fcntl, time
import json
import math
gh_mappings = {'stat/greenhouse/control1/POWER1' : "WaterPump",
                'stat/greenhouse/control1/POWER2' :"Vent",
                'stat/greenhouse/control1/POWER3' : "CO2Valve",
                'stat/greenhouse/control3/POWER3' : "Reds",
                'stat/greenhouse/control3/POWER2' : "Lights",
                'stat/greenhouse/control3/POWER4' : "DeHum",
                'stat/greenhouse/control2/POWER1' : "Swamp"}

from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily




class TasmotaPromCollector(object):
    def __init__(self,co2detector):
        self.detector = co2detector
    def collect(self):
        g = GaugeMetricFamily("co2ppm", 'Detect parts per million of co2 in the atmosphere.', labels=['greenhouse'])
        g.add_metric(["greenhouse"], self.detector.co2ppm)
        yield g
        g = GaugeMetricFamily("temp_c", 'Detect parts per million of co2 in the atmosphere.', labels=['greenhouse'])
        g.add_metric(["greenhouse"], self.detector.temp_c)
        yield g

def calc_svp(temp_c):
    return 610.78 *  math.exp(temp_c / (temp_c + 238.3) * 17.2694)

def calc_vpd(temp_c,humidity):
    return calc_svp(temp_c) * (1 - humidity/100)
def on_message_cb(client,userdata,message):
    the_time = str(int(time.time()))+"000000000"
    if message.topic == "tele/greenhouse/control2/SENSOR":
        payload = json.loads(message.payload)["AM2301"]
        self.temp_c = float(payload["Temperature"])
        self.humidity = float(payload["Humidity"])
        self.dewpoint = float(payload["DewPoint"])        
        self.vpd = calc_vpd(float(payload["Temperature"]),float(payload["Humidity"]))
    if message.topic in gh_mappings.keys():
        name = gh_mappings[message.topic]
        status = 1 if message.payload == "ON" else 0
        userdata.gh_last[message.topic] = status
        
class SonoffTHDevice:
    def __init__(self,mqtt_client):
        self.gh_last = {metric:None for metric in gh_mappings.keys()}
        self.client = mqtt_client
        for topic in gh_mappings.keys():
            self.client.subscribe(topic)
        self.client.subscribe("tele/greenhouse/control2/SENSOR")
        self.client.on_message = on_message_cb
        self.client.user_data_set(self)
        self.client.loop_start()
        self.poll_sensors()

    def poll_sensors(self):
        for topic in gh_mappings.keys():
            tok = topic.split("/")
            tok[0] = "stat"
            self.client.publish("/".join(tok))
            
def main():
    client = mqtt.Client("greenho_man")
    client.connect("localhost")
    device = SonoffTHDevice(client)
    while True:
        device.fetch()
        time.sleep(1)

