from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server, Summary
import requests
import paho.mqtt.client as mqtt
import sys, fcntl, time
import json
import math


import time
from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily




class CO2PromCollector(object):
    def __init__(self,co2detector):
        self.detector = co2detector
    def collect(self):
        g = GaugeMetricFamily("co2ppm", 'Detect parts per million of co2 in the atmosphere.', labels=['greenhouse'])
        g.add_metric(["greenhouse"], self.detector.co2ppm)
        yield g
        g = GaugeMetricFamily("temp_c", 'Detect parts per million of co2 in the atmosphere.', labels=['greenhouse'])
        g.add_metric(["greenhouse"], self.detector.temp_c)
        yield g
        
        
        
class CO2Detector:
    def __init__(self,devicefilename,mqtt_client):
        self.client = mqtt_client
        self.key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]
        self.fp = open(devicefilename, "r+b",  0)
        HIDIOCSFEATURE_9 = 0xC0094806
        set_report = b'\x00' + bytes(self.key)#"".join(chr(e) for e in self.key)
        fcntl.ioctl(self.fp, HIDIOCSFEATURE_9, set_report)        
        self.co2ppm,self.temp_c  =  self.fetch()
        start_http_server(8001)
        REGISTRY.register(CO2PromCollector(self))

    def decrypt(self, key, data):
        cstate = [0x48,  0x74,  0x65,  0x6D,  0x70,  0x39,  0x39,  0x65]
        shuffle = [2, 4, 0, 7, 1, 6, 5, 3]
        phase1 = [0] * 8
        for i, o in enumerate(shuffle):
            phase1[o] = data[i]

        phase2 = [0] * 8
        for i in range(8):
            phase2[i] = phase1[i] ^ key[i]

        phase3 = [0] * 8
        for i in range(8):
            phase3[i] = ( (phase2[i] >> 3) | (phase2[ (i-1+8)%8 ] << 5) ) & 0xff

        ctmp = [0] * 8
        for i in range(8):
            ctmp[i] = ( (cstate[i] >> 4) | (cstate[i]<<4) ) & 0xff

        out = [0] * 8
        for i in range(8):
            out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xff

        return out

    def hd(self,d):
        return " ".join("%02X" % e for e in d)

    def fetch(self):
        values = {}
        while True:
            data = list(e for e in self.fp.read(8))
            decrypted = self.decrypt(self.key, data)
            if decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]:
                print(self.hd(data), " => ", self.hd(decrypted),  "Checksum error")
                raise Exception
            else:
                op = decrypted[0]
                val = decrypted[1] << 8 | decrypted[2]
                values[op] = val
                if 0x50 in values and 0x42 in values:
                    co2ppm = int(values[0x50])
                    tempc = float(values[0x42]/16.0-273.15)
                    the_time = str(int(time.time()))+"000000000"
                    print(f"{co2ppm} {tempc} {the_time}")
                    self.client.publish('stat/greenhouse/co2sens',"{\"co2ppm\":%d,\"temp_c\":%2f}" % (co2ppm,tempc))
                    self.co2ppm = co2ppm
                    self.temp_c = tempc
                    return (co2ppm, tempc)

def main():
    hid_device= sys.argv[1] if len(sys.argv) > 1 else "/dev/co2sens"
    mqttc = mqtt.Client("greenho_co2detector")
    mqttc.username_pw_set(username="greenho_co2detector",password="cheese")
    mqttc.connect("localhost")
    detector = CO2Detector(hid_device,mqttc)
    while True:
        detector.fetch()
        
if __name__ == '__main__':
    main()
