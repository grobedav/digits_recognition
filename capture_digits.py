from io import BytesIO
from time import sleep
import time
from picamera import PiCamera
from pymongo import MongoClient
import image_to_number as i2n
# Create an in-memory stream

camera = PiCamera()
camera.resolution = (1024, 768)
camera.rotation = 180
camera.start_preview()
# Camera warm-up time
sleep(2)


t1 = 0
t2 = 0
# Take each tarif frame from electricity meter
while t1 == 0 or t2 == 0 or t1 == t2:
	my_stream = BytesIO()
	camera.capture(my_stream, 'jpeg')
	number = i2n.stream_to_number(my_stream)
	sleep(8)
	if number > 1:
		if number > t2:
			t1 = t2
			t2 = number
		else: 
			t1 = number	
			
camera.stop_preview()
camera.close()

# read credentials
with open('/home/pi/power_meter/digits_recognition/mongodb_credentials.txt') as f:
    credentials = [x.strip().split(':') for x in f.readlines()]
# write display results to db
try:
	client = MongoClient('mongodb://' + credentials[0][2] +':27017',
                     username = credentials[0][0],
                      password = credentials[0][1],
                      authSource = 'home',
                      authMechanism = 'SCRAM-SHA-1')
	timestamp = time.time()
	energy = {
        	'T1' : t1,
        	'T2' : t2,
        	'timestamp' : timestamp
	}

	db = client.home
	result = db.energy.insert_one(energy)
finally:
	client.close()






