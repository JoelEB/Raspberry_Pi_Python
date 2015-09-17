#!/usr/bin/python

import serial

print "Welcome to the Atlas Scientific Raspberry Pi example."

usbport = '/dev/ttyAMA0'
ser = serial.Serial(usbport, 38400)

# turn on the LEDs
ser.write("L1\r")


line = ""

while True:
        ser.write("R\r")
	data = ser.read()
	if(data == "\r"):
		print "Received from sensor:" + line
		line = ""
	else:
		line = line + data
