from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server, Summary
import requests
import paho.mqtt.client as mqtt
import sys, fcntl, time
import json
import math
import subprocess
import json
import time
from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily




class RTLCollector(object):
    def __init__(self,rtldetector):
        self.detector = rtldetector
    def collect(self):
        g = GaugeMetricFamily("temp_c_rtl1", 'Temperature detected by my lightning detector', labels=['greenhouse'])
        g.add_metric(["greenhouse"], self.detector.temp_c_rtl1)
        yield g
        g = GaugeMetricFamily("relhum_rtl1", 'Humidity detected by my lightning detector.', labels=['greenhouse'])
        g.add_metric(["greenhouse"], self.detector.relhum_rtl1)
        yield g
        
        
        
class RTLDetector:
    def __init__(self,mqtt_client):
        self.client = mqtt_client
        #cli_args = ['rtl_433', '-F','json','-C','si']
        cli_args = ["bash","testme.bash"]
        self.rtl_433 = subprocess.Popen(cli_args, stdout=subprocess.PIPE)
        for _ in range(1,50):
            print("fetching initial data..")
            self.fetch()
        start_http_server(8000)
        REGISTRY.register(RTLCollector(self))

    def fetch(self):
        line = self.rtl_433.stdout.readline()
        if line == b'':
            raise EOFError()
        print(line)
        self.update_state(line)
        self.client.publish('stat/greenhouse/rtl433',self.format_mqtt_payload())

    def format_mqtt_payload(self):
        json.dumps({"temp_c":self.temp_c_rtl1,
         "relhum":self.relhum_rtl1})
        
    def update_state(self,payload):
        self.last_message = json.loads(payload)
        if self.last_message["model"] == "Acurite-6045M":
            self.temp_c_rtl1 = self.last_message["temperature_C"]
            self.relhum_rtl1 = self.last_message["humidity"]
        if self.last_message["model"] == "Acurite-5n1" and self.last_message["message_type"] == 56:
            self.temp_c_rtl1_roof = self.last_message["temperature_C"]
            self.relhum_rtl1_roof = self.last_message["humidity"]
            self.windavg_rtl1_roof = self.last_message["wind_avg_km_h"]
        
def main():
    mqttc = mqtt.Client("greenho_rtldetector")
    mqttc.username_pw_set(username="greenho_rtldetector",password="cheese")
    mqttc.connect("192.168.1.38")
    detector = RTLDetector(mqttc)
    while True:
        detector.fetch()
        
if __name__ == '__main__':
    main()
