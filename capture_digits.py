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
camera.capture(my_stream, 'jpeg')


# Take each frame
number = i2n.stream_to_number(my_stream) 
print number

camera.stop_preview()
camera.close()
