import os
import os.path
import glob
import time
from datetime import datetime
import httplib, urllib#http and url libs used for HTTP POSTs
import socket# socket used to get host name/IP
#################
## Phant Stuff ##
#################
server = "data.sparkfun.com" # base URL of your feed
publicKey = "n11ZzGN8LYhOX5xo2wM0" # public key, everyone can see this
privateKey = "Moo7eqJ5RdfBmdxDzvqA"# private key, only you should know
fields = ["date", "time", "temp"]#Your feed's data fields

publicKey2 = "QGGzAN7d34unM2EKD51d"#public key, everyone can see this
privateKey2 = "JqqdZR9lG8Uj9qvlEDBz"#private key, only you should know
fields2 = ["H2O_temp", "room_temp"]#Your feed's data fields

#These lines connect to the DS18B20 Temp Sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#base_dir = '/sys/bus/w1/devices/'
#device_folder = glob.glob(base_dir + '28*')[0]
#device_file = device_folder + '/w1_slave'

device_file = '/sys/bus/w1/devices/28-0000052688c3/w1_slave'
device_file2 = '/sys/bus/w1/devices/28-000005313015/w1_slave'

###########
#Functions#
###########
def read_temp_raw(temp_choice):
    if temp_choice == 0:
        f = open(device_file, 'r')
    else:
        f = open(device_file2, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(read_choice):
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
        return "%.2f" %  temp_f

    
def post_data():
    temp = read_temp(0)
    print("Sending an update!")
    # Our first job is to create the data set. Should turn into
    # something like "light=1234&switch=0&name=raspberrypi"
    data = {} # Create empty set, then fill in with our three fields:
    # Field 0, light, gets the local time:
    data[fields[0]] = time.strftime("%m-%d-%y")
    # Field 1, switch, gets the switch status:
    data[fields[1]] = time.strftime("%H:%M:%S")
    # Field 2, name, gets the pi's local name:
    data[fields[2]] = temp
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
    r = c.getresponse() # Get the server's response and print print r.status, r.reason

def post_data2():
    temp0 = read_temp(0)
    temp1 = read_temp(1)
    print("Sending an update!")
    # Our first job is to create the data set. Should turn into
    # something like "light=1234&switch=0&name=raspberrypi"
    data = {} # Create empty set, then fill in with our three fields:
    # Field 0, light, gets the local time:
    data[fields2[0]] = temp0
    # Field 1, switch, gets the switch status:
    data[fields2[1]] = temp1
    # Next, we need to encode that data into a url format:
    params = urllib.urlencode(data)
    # Now we need to set up our headers:
    headers = {} # start with an empty set
    # These are static, should be there every time:
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Connection"] = "close"
    headers["Content-Length"] = len(params) # length of data
    headers["Phant-Private-Key"] = privateKey2 # private key header
    # Now we initiate a connection, and post the data
    c = httplib.HTTPConnection(server)
    # Here's the magic, our reqeust format is POST, we want
    # to send the data to data.sparkfun.com/input/PUBLIC_KEY.txt
    # and include both our data (params) and headers
    c.request("POST", "/input/" + publicKey2 + ".txt", params, headers)
    r = c.getresponse() # Get the server's response and print print r.status, r.reason
           


while True:
	try:
    	print("H2O temp = " + read_temp(0) + "F")
    	print("Room temp = " + read_temp(1) + "F")
    	post_data()
    	post_data2()
    	time.sleep(600)

	except Exception as E:
		print("Error" + str(E))