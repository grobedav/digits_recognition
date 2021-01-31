#!venv/bin/python

import io 
import serial
import logging
import time
import json
from flask import Flask, jsonify
import atexit
import threading
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
#---- cron ---
cron = BackgroundScheduler()
# Explicitly kick off the background thread
class OptData:
 def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

result = OptData()
result.suma = 0
result.highTarif = 0
result.lowTarif = 0

def testJob():
  result.suma += 1
  result.highTarif += 1
  result.lowTarif += 1 
  print(result.toJSON())
  time.sleep(5)

def doJob():
  read_opt_sensor()

#cron.start()
#cron.add_job(testJob, 'interval', seconds = 1, max_instances = 1)

# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: cron.shutdown(wait=False))
#-----cron -----
def read_opt_sensor():
  serialPort = serial.Serial(port = '/dev/ttyUSB0', baudrate=300,bytesize=serial.SEVENBITS,parity=serial.PARITY_EVEN,timeout=2)
  try: 
    serialString = "" # Used to hold data coming over UART 
    serialPort.write(b"/?!\r\n")
        # Wait until there is data waiting in the serial buffer
    while True:
        try:
          if(serialPort.inWaiting() > 0):
            # Read data out of the buffer until a carraige return / new line is found
           serialString = serialPort.readline()
           #print(serialString.decode('ascii'))
           break
        except Exception as e:
          print(e)
          break

          # Tell the device connected over the serial port that we recevied the data! The b at the beginning is used to indicate bytes!
    serialPort.write(b'\x06') #ACK 
    serialPort.write(b'000\r\n') #baudrate 000 - 300, 010 - 600, 020 - 1200, 030 - 2400, 040 - 4800, 050 - 9600, 060 - 19200  change baudrate not working here!
    #serialPort.baudrate = 4800
    numberOfread = 0
    while True:
      numberOfread += 1
      if(numberOfread > 10000): #something goes wrong with reading break
        break
      try:
        if(serialPort.inWaiting() > 0):
            # Read data out of the buffer until a carraige return / new line is found
          serialString = serialPort.readline()
         # print(numberOfread) 
          numberOfread = 0  
          if b'\x03' in serialString: #end of message
            break
          serialString = serialString.decode('ascii')
          if(serialString.startswith("1.8.0(")):
            result.suma = serialString.split("(")[1].split("*")[0]
          if(serialString.startswith("1.8.1(")):
            result.highTarif = serialString.split("(")[1].split("*")[0]
          if(serialString.startswith("1.8.2(")):
            result.lowTarif = serialString.split("(")[1].split("*")[0]
         # print(serialString)
      except Exception as e:
       print(e)
       break
  finally:
    serialPort.close()


@app.route('/electricity_meter/api/v1.0/energy', methods=['GET'])
def get_energie():
  
  return {"energy": {"highTarif":result.highTarif, "lowTarif":result.lowTarif, "suma":result.suma}}

if __name__ == "__main__":
  cron.start()
  cron.add_job(read_opt_sensor, 'interval', seconds = 300, max_instances = 1)
  #read_opt_sensor(result) 
  app.run(host='0.0.0.0')
