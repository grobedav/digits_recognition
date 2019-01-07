from io import BytesIO
from time import sleep
from picamera import PiCamera
import image_to_number as i2n
# Create an in-memory stream
my_stream = BytesIO()
camera = PiCamera()
camera.resolution = (1024, 768)
camera.rotation = 180
camera.start_preview()
# Camera warm-up time
sleep(2)


t1 = 0
t2 = 0
# Take each frame
while t1 == 0 or t2 == 0:
	camera.capture(my_stream, 'jpeg')
	number = i2n.stream_to_number(my_stream)
	sleep(8)
	if number > 1:
		if number > t2:
			t1 = t2
			t2 = number
		else: 
			t1 = number	
			
print(t1)
print(t2)

camera.stop_preview()
camera.close()
