import cv2
import numpy
from flask import Flask, render_template,jsonify, Response, stream_with_context, request
import time
import RPi.GPIO as GPIO
import time
import sys
from flask_cors import CORS
from threading import Thread
import json
import subprocess
from pymongo import MongoClient



GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pin1 = 17
pin2 = 18
pin3 = 22
#pin4 = 27
# pin5 = 
GPIO.setup(pin1,GPIO.OUT)
GPIO.setup(pin2,GPIO.OUT)
GPIO.setup(pin3,GPIO.OUT)
GPIO.setup(pin4,GPIO.OUT)
GPIO.setup(pin5,GPIO.OUT)

light1 = "off"
fan = "off"
app = Flask(__name__)
CORS(app)
app.debug = True
 
# ##################################################################
@app.route('/light1_on', methods=['POST'])
def light1_on():
    light1="on"
    print(light1, file=sys.stderr)
    GPIO.output(pin1, GPIO.HIGH)
    return jsonify({"light1":"on"})

@app.route('/light1_off', methods=['POST'])
def light1_off():
    light1="off"
    print(light1, file=sys.stderr)
    GPIO.output(pin1, GPIO.LOW)
    return jsonify({"light1":"off"})

@app.route('/light1_automateon', methods=['POST'])
def light1_automateon():
    global stop_task2
    task_thread2 = Thread(target=print_time)
    task_thread2.start()
    return jsonify({"light1":"autoon"})


@app.route('/light1_automateoff', methods=['POST'])
def light1_automateoff():
    global stop_task2
    stop_task2 = True
    return jsonify({"light1":"sutooff"})

def print_time():

   while True:
      GPIO.output(pin1, GPIO.HIGH)
      print("light1 on", file=sys.stderr)
      time.sleep(2)
      GPIO.output(pin1, GPIO.LOW)
      print("light1 off", file=sys.stderr)
      time.sleep(2)
      if stop_task2:
            break












# ##################################################################
@app.route('/fan_on', methods=['POST'])
def fan_on():
    fan="on"
    print(fan, file=sys.stderr)
    GPIO.output(pin5, GPIO.HIGH)
    return jsonify({"fan":"on"})

@app.route('/fan_off', methods=['POST'])
def fan_off():
    fan="off"
    print(fan, file=sys.stderr)
    GPIO.output(pin5, GPIO.LOW)
    return jsonify({"fan":"off"})

@app.route('/fan_automateon', methods=['POST'])
def fan_automateon():
    global stop_task6
    task_thread2 = Thread(target=print_time)
    task_thread2.start()
    return jsonify({"fan":"autoon"})


@app.route('/fan_automateoff', methods=['POST'])
def fan_automateoff():
    global stop_task6
    stop_task6 = True
    return jsonify({"fan":"sutooff"})

def print_time():

   while True:
      GPIO.output(pin5, GPIO.HIGH)
      print("fan on", file=sys.stderr)
      time.sleep(2)
      GPIO.output(pin5, GPIO.LOW)
      print("fan off", file=sys.stderr)
      time.sleep(2)
      if stop_task6:
            break









#####################################################################################################

@app.route('/all_automateon', methods=['POST'])
def all_automateon():
    global stop_task4
    task_thread4 = Thread(target=print_all)
    task_thread4.start()
    return jsonify({"all":"autoon"})


@app.route('/all_automateoff', methods=['POST'])
def all_automateoff():
    global stop_task4
    stop_task4 = True
    return jsonify({"all":"autooff"})

def print_all():

   while True:
       GPIO.output(pin1, GPIO.HIGH)
       GPIO.output(pin2, GPIO.HIGH)
   
       print("all on", file=sys.stderr)
       time.sleep(2)
       GPIO.output(pin1, GPIO.LOW)
       GPIO.output(pin2, GPIO.LOW)
       time.sleep(2)
       print("all off", file=sys.stderr)
       GPIO.output(pin1, GPIO.HIGH)
       GPIO.output(pin2, GPIO.HIGH)
       print("all on", file=sys.stderr)
       time.sleep(2)
       GPIO.output(pin1, GPIO.LOW)
       GPIO.output(pin2, GPIO.LOW)
       time.sleep(2)
       print("all off", file=sys.stderr)
       time.sleep(1)
       if stop_task4:
            break




# ///////////////////////////////////

@app.route('/')
def execute_other_file():
    result = subprocess.check_output(['python', 'server.py'])
    return result





@app.route('/data', methods=['GET'])
def lastfiv():
    client = MongoClient('mongodb+srv://mugilan:mugilan@cluster0.dosw1iz.mongodb.net/')
    db = client['mydatabase']
    collection = db['mycollection']

    data = collection.find().sort('_id', -1).limit(5)
    result = []
    for doc in data:
        result.append(doc)
    client.close()
    return jsonify(result), 200

stop_task2 = False
stop_task4 = False
stop_task6 = False

if __name__=="__main__":
 app.run(threaded=True)
