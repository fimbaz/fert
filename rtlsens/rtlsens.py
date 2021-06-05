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
        g = GaugeMetricFamily("vpd_rtl1", 'Vapor pressure defecit in hPa.', labels=['greenhouse'])
        g.add_metric(["greenhouse"], self.detector.vpd_rtl1)
        
        yield g
        
        
def calc_svp(temp_c):
    return 610.78 *  math.exp(temp_c / (temp_c + 238.3) * 17.2694)

def calc_vpd(temp_c,humidity):
    return calc_svp(temp_c) * (1 - humidity/100)

class RTLDetector:
    def __init__(self,mqtt_client):
        self.client = mqtt_client
        cli_args = ['rtl_433', '-F','json','-C','si']
        #cli_args = ["bash","testme.bash"]
        self.rtl_433 = subprocess.Popen(cli_args, stdout=subprocess.PIPE)
        self.prefetch()
        start_http_server(8001)
        REGISTRY.register(RTLCollector(self))

    def fetch_loop(self):
        while True:
            self.fetch()
            self.client.publish('stat/greenhouse/rtl433',self.format_mqtt_payload())
    def prefetch(self):
        for _ in range(1,50):
            print("fetching initial data..")
            self.fetch()
    def fetch(self):
        line = self.rtl_433.stdout.readline()
        if line == b'':
            raise EOFError()
        print(line)
        self.update_state(line)

    def format_mqtt_payload(self):
        json.dumps({"temp_c":self.temp_c_rtl1,
                    "relhum":self.relhum_rtl1,
                    "VPD":self.vpd_rtl1})
        
    def update_state(self,payload):
        self.last_message = json.loads(payload)
        if self.last_message["model"] == "Acurite-6045M":
            self.temp_c_rtl1 = self.last_message["temperature_C"]
            self.relhum_rtl1 = self.last_message["humidity"]
            self.vpd_rtl1 = calc_vpd(self.temp_c_rtl1,self.relhum.rtl1)
        if self.last_message["model"] == "Acurite-5n1" and self.last_message["message_type"] == 56:
            self.temp_c_rtl1_roof = self.last_message["temperature_C"]
            self.relhum_rtl1_roof = self.last_message["humidity"]
            self.windavg_rtl1_roof = self.last_message["wind_avg_km_h"]
def main():
    mqttc = mqtt.Client("greenho_rtldetector")
    mqttc.username_pw_set(username="greenho_rtldetector",password="cheese")
    mqttc.connect("localhost")
    detector = RTLDetector(mqttc)
    while True:
        detector.fetch_loop()
        
if __name__ == '__main__':
    main()
