#!/usr/bin/python

import serial
import time


print "Initiating"

ser = serial.Serial("/dev/ttyAMA0", 38400, timeout=0.5)


#ser.write("L1\r")

#ser.write("E\r")



line = ""

while True:
        
        ser.write("r\r")
        data = ser.read()
	if(data == "\r"):
		print "pH = " + line
		line = ""
		time.sleep(10)
	else:
		line = line + data