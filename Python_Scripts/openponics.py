import os
import os.path
import serial
import glob
import time
from datetime import datetime
import httplib, urllib#http and url libs used for HTTP POSTs
import socket# socket used to get host name/IP
import serial
import RPi.GPIO as GPIO

# Grab the current datetime which will be used to generate dynamic folder names
d = datetime.now()
initYear = "%04d" % (d.year) 
initMonth = "%02d" % (d.month) 
initDate = "%02d" % (d.day)
initHour = "%02d" % (d.hour)
initMins = "%02d" % (d.minute)

# Define the location where you wish to save files. Set to HOME as default. 
# If you run a local web server on Apache you could set this to /var/www/ to make them 
# accessible via web browser.
folderToSave = "/media/MORDOR/timelapse/timelapse_" + str(initYear) + str(initMonth) + str(initDate) + str(initHour) + str(initMins)
os.mkdir(folderToSave)

# Set the initial serial for saved images to 1
fileSerial = 1

#UART info for pH probe
#make sure python serial is installed: sudo apt-get install python-serial
#Also make sure serial port info is turned off:
#sudo nano /boot/cmdline.txt -> delete AMA0 parts
#sudo nano /etc/inittab  -> comment out last line

usbport = '/dev/ttyAMA0'
ser = serial.Serial(usbport, 38400)

#################
## Phant Stuff ##
#################
server = "data.sparkfun.com" # base URL of your feed
publicKey = "KJJ1rarEx3Irg7JRyaG4" # public key, everyone can see this
privateKey = "vzzRywyMAeu6158ZjBVE"# private key, only you should know
fields = ["H2O_temp","ph","room_temp"]#Your feed's data fields

#These lines connect to the DS18B20 Temp Sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#base_dir = '/sys/bus/w1/devices/'
#device_folder = glob.glob(base_dir + '28*')[0]
#device_file = device_folder + '/w1_slave'

device_file = '/sys/bus/w1/devices/28-0000060756fc/w1_slave'
device_file2 = '/sys/bus/w1/devices/28-00000530b9d3/w1_slave'

###########
#Functions#
###########
def read_temp_raw(temp_choice):
    if temp_choice == 0:
        f = open(device_file, 'r')
    else:
        f = open(device_file2, 'r')
    lines = f.readlines()
    f.close
    return lines

def read_temp(read_choice, return_choice):
    if read_choice == 0:
         lines = read_temp_raw(0)
    else:
         lines = read_temp_raw(1)

    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
	if return_choice == 0:
            return "%.2f" % temp_f
	else:
	    return "%.2f" % temp_c
        
def get_ph():
    line =""
    temp = read_temp(1,1)
    ser.write(temp + "\r")#calibrate with the current H2O temp in C
    ser.write("R\r")#take a single reading
    while ser.inWaiting()!=0:
        data = ser.read()
        if(data == "\r"):
            return line
            line = ""
        else:
            line = line + data

def post_data():
    temp0 = read_temp(0,0)
    temp1 = read_temp(1,0)
    ph = get_ph()
    print("Sending an update!")
    # Our first job is to create the data set. Should turn into
    # something like "light=1234&switch=0&name=raspberrypi"
    data = {} # Create empty set, then fill in with our three fields:
    # Field 0, h2o temp
    data[fields[0]] = temp0
    # Field 1, pH
    data[fields[1]] = ph
    # Field 2, room temp
    data[fields[2]] = temp1
    # Next, we need to encode that data into a url format:
    params = urllib.urlencode(data)
    # Now we need to set up our headers:
    headers = {} # start with an empty set
    # These are static, should be there every time:
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Connection"] = "close"
    headers["Content-Length"] = len(params) # length of data
    headers["Phant-Private-Key"] = privateKey # private key header
    # Now we initiate a connection, and post the data
    c = httplib.HTTPConnection(server)
    # Here's the magic, our reqeust format is POST, we want
    # to send the data to data.sparkfun.com/input/PUBLIC_KEY.txt
    # and include both our data (params) and headers
    c.request("POST", "/input/" + publicKey + ".txt", params, headers)
    r = c.getresponse() # Get the server's response and print
    print r.status, r.reason

while True:
    try:
        #ser.write("L1\r")#Uncomment to turn LEDs ON
        #ser.write("L0\r")#Uncomment to turn LEDs OFF

        #Take initial readings in case they're off
        get_ph()
        read_temp(0,0)
        read_temp(1,0)

        #print data to local termial
        print(get_ph())
        print("H2O temp = " + read_temp(0,0) + "F, " + read_temp(0,1) + "C" )
        print("Room temp = " + read_temp(1,0) + "F, " + read_temp(1,1) + "C" )
   
        #post data to data.sparkfun.com
        post_data()
		
		d = datetime.now()
		if d.hour > 6 and d.hour < 21:
		
			# Set FileSerialNumber to 000X using four digits
			fileSerialNumber = "%04d" % (fileSerial)
		
			# Capture the CURRENT time (not start time as set above) to insert into each capture image filename
			hour = "%02d" % (d.hour)
			mins = "%02d" % (d.minute)
		
			# Define the size of the image you wish to capture. 
			imgWidth = 2592 # Max = 2592 
			imgHeight = 1944 # Max = 1944
			print " ====================================== Saving file at " + hour + ":" + mins
		
			# Capture the image using raspistill. Set to capture with added sharpening, auto white balance and average metering mode
			# Change these settings where you see fit and to suit the conditions you are using the camera in
			os.system("raspistill -w " + str(imgWidth) + " -h " + str(imgHeight) + " -o " + str(folderToSave) + "/" + str(fileSerialNumber) + "_" + str(hour) + str(mins) +  ".jpg -awb fluorescent -mm average -rot 270 -v -n")

			# Increment the fileSerial
			fileSerial += 1
		
			# Wait 60 seconds (10 minute) before next capture
		time.sleep(600)

    except Exception as E:
	print("Error" + str(E)) 
