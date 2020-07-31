#!/usr/bin/env python
import requests
import paho.mqtt.client as mqtt
import sys, fcntl, time
import json
import math
gh_mappings = {'greenhouse/control1/POWER1' : "WaterPump",
                'greenhouse/control1/POWER2' :"Vent",
                'greenhouse/control1/POWER3' : "CO2Valve",
                'greenhouse/control1/POWER4' : "Lights",
                'greenhouse/control2/POWER1' : "Swamp"}
def calc_svp(temp_c):
    return 610.78 *  math.exp(temp_c / (temp_c + 238.3) * 17.2694)

def calc_vpd(temp_c,humidity):
    return calc_svp(temp_c) * (1 - humidity/100)
def on_message_cb(client,userdata,message):
    the_time = str(int(time.time()))+"000000000"
    if message.topic == "greenhouse/control2/SENSOR":
        print(message.topic)
        payload = json.loads(message.payload)["AM2301"]
        vpd = float(payload["VPD"])*100 # convert from hPa to Pa
        print(requests.post("http://localhost:8086/write?db=greenhouse",
                            "temp_c,host=clarissa,region=baker30s,room=gh2 temp_c=%2f %s"  % (payload["Temperature"], the_time)))
        print(requests.post("http://localhost:8086/write?db=greenhouse",
                            "humidity,host=clarissa,region=baker30s,room=gh2 humidity=%2f %s"  % (payload["Humidity"], the_time)))
        print(requests.post("http://localhost:8086/write?db=greenhouse",
                            "dewpoint,host=clarissa,region=baker30s,room=gh2 dewpoint=%2f %s"  % (payload["DewPoint"], the_time)))
        print(requests.post("http://localhost:8086/write?db=greenhouse",
                            "vpd,host=clarissa,region=baker30s,room=gh2 vpd=%2f %s" % (vpd,the_time)))
    if message.topic in gh_mappings.keys():
        name = gh_mappings[message.topic]
        status = 1 if message.payload == "ON" else 0
        print(requests.post("http://localhost:8086/write?db=greenhouse",
                            "%s,host=clarissa,region=baker30s,room=gh2 %s=%d %s" % (name,name,status,the_time)))
        

class SonoffTHDevice:
    def __init__(self):
        self.client = mqtt.Client("greenho1")
        self.client.connect("localhost")

        for topic in gh_mappings.keys():
            self.client.subscribe(topic)
        self.client.subscribe("greenhouse/control2/SENSOR")
        self.client.on_message = on_message_cb
        self.client.loop_start()
        self.poll_sensors()
        
    def poll_sensors(self):
        for topic in gh_mappings.keys():
            tok = topic.split("/")
            tok.insert(2,"cmnd")
            self.client.publish("/".join(tok))
            
class CO2Detector:
    def __init__(self,devicefilename):
        self.key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]
        self.fp = open(devicefilename, "a+b",  0)
        HIDIOCSFEATURE_9 = 0xC0094806
        set_report = "\x00" + "".join(chr(e) for e in self.key)
        fcntl.ioctl(self.fp, HIDIOCSFEATURE_9, set_report)
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
            data = list(ord(e) for e in self.fp.read(8))
            decrypted = self.decrypt(self.key, data)
            if decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]:
                print(self.hd(data), " => ", self.hd(decrypted),  "Checksum error")
            else:
                op = decrypted[0]
                val = decrypted[1] << 8 | decrypted[2]
                values[op] = val
                if 0x50 in values and 0x42 in values:
                    co2ppm = int(values[0x50])
                    tempc = float(values[0x42]/16.0-273.15)
                    return (co2ppm, tempc)

if __name__ == '__main__':
    device = SonoffTHDevice()
    detector = CO2Detector("/dev/hidraw0")
    while True:
        co2,temp_c = detector.fetch()
        device.poll_sensors()
        the_time = str(int(time.time()))+"000000000"
        print(requests.post("http://localhost:8086/write?db=greenhouse",
              "temp_c,host=clarissa,region=baker30s,room=gh1 temp_c=%2f %s"  % (temp_c, the_time)))
        print(requests.post("http://localhost:8086/write?db=greenhouse",
                            "co2_ppm,host=clarissa,region=baker30s,room=gh1 co2_ppm=%2f %s" % (co2, the_time)))
