#!/usr/bin/env python

import sys, fcntl, time
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
                print self.hd(data), " => ", self.hd(decrypted),  "Checksum error"
            else:
                op = decrypted[0]
                val = decrypted[1] << 8 | decrypted[2]
                values[op] = val
                if 0x50 in values and 0x42 in values:
                    co2ppm = int(values[0x50])
                    tempc = float(values[0x42]/16.0-273.15)
                    return (co2ppm, tempc)

if __name__ == '__main__':
    detector = CO2Detector("/dev/hidraw2")
    while True:
        print("%4d %2f" % detector.fetch())
