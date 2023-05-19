import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO
import math
from pymongo import MongoClient
import json
import sys
k= 1.0
from simple_pid import PID
client = MongoClient("mongodb+srv://mugilan:mugilan@cluster0.dosw1iz.mongodb.net/")
db = client.mydatabase
collection = db.mycollection


# Configure the ADS1115 and create analog input objects
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 2/3
ph_chan = AnalogIn(ads, ADS.P0)
tds_chan = AnalogIn(ads, ADS.P1)
temp_channel = AnalogIn(ads, ADS.P2)

# Set up GPIO for TDS sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.output(17, GPIO.LOW)

# Set limit values
ph_limit = [6, 8]
tds_limit = [400, 450]
conductivity_limit = [250, 650]
temp_limit = [28,32]
# PID controller parameters
Kp = 1
Ki = 0.1
Kd = 0.05

pid = PID(Kp, Ki, Kd, setpoint=7)

# Function to read pH sensor
def read_ph():
    # Get pH sensor reading and convert to pH value
    ph_raw = ph_chan.voltage
    ph=(-5.07*ph_raw)+21.55509299
    temp_voltage = temp_channel.voltage
    temp_range = ((temp_voltage - 0.5) * 100)
    temp_celsius = temp_range / 10

    return ph,temp_celsius

# Function to read TDS sensor
def read_tds():
    # Send pulse to TDS sensor
    GPIO.output(17, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(17, GPIO.LOW)

    # Get TDS sensor reading and convert to TDS value
    tds_raw = tds_chan.voltage
    #tds = 1000 * (133.42 * math.exp(6.185 * tds_raw) -0.5)
    #voltage = tds_chan.voltage*5/1024.0
    tds = (((133.42/tds_chan.voltage*tds_chan.voltage*tds_chan.voltage-255.86*tds_chan.voltage*tds_chan.voltage+857.39*tds_chan.voltage)*5)/10)
    return tds

def calc_conductivity(tds_value):
    conductivity = (tds_chan.voltage)*0.5  # convert ppm to mS/cm
    return conductivity

# Main loop to read sensors and print values
while True:
    ph,temp_celsius = read_ph()
    tds = read_tds()
    tds_value = read_tds()
    conductivity = calc_conductivity(tds_value)
    pid.setpoint = 7
    pid_ph =pid(ph)
    pid_temp =pid(temp_celsius)
    pid_tds =pid(tds)
    pid_cond =pid(conductivity)


    # Check if any limit is exceeded and turn on the relay
    if (pid_ph < ph_limit[0] or pid_ph > ph_limit[1] and
        pid_tds < tds_limit[0] or pid_tds > tds_limit[1] and
        pid_cond < conductivity_limit[0] or pid_cond > conductivity_limit[1] and
        pid_temp < temp_limit[0] or pid_temp > temp_limit[1]):
        GPIO.output(22, GPIO.HIGH)
        GPIO.output(27,GPIO.LOW)
        oldest_doc = collection.find_one_and_delete({}, sort=[('_id', 1)])
        document = {"pH":round(ph,2),"Temperature":round(temp_celsius,2),"TDS":round(tds),"Conductivity": conductivity}
        result = collection.insert_one(document)
        print("Open value 1,Close value 2!")
        time.sleep(2)
    else:
        GPIO.output(22,GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        oldest_doc = collection.find_one_and_delete({}, sort=[('_id', 1)])
        document = {"pH":round(ph,2),"Temperature":round(temp_celsius,2),"TDS":round(tds),"Conductivity": conductivity}
        result = collection.insert_one(document)
        print("Open value 2,Close value 1!")
        time.sleep(2)
       

