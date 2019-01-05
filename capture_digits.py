from io import BytesIO
from time import sleep
from picamera import PiCamera
import cv2
import numpy as np
import imutils
from imutils.perspective import four_point_transform
from imutils import contours


# Create an in-memory stream
my_stream = BytesIO()
camera = PiCamera()
camera.resolution = (1024, 768)
camera.rotation = 180
camera.start_preview()
# Camera warm-up time
sleep(2)
camera.capture(my_stream, 'jpeg')
camera.stop_preview()


# Take each frame
my_stream.seek(0)
file_bytes = np.asarray(bytearray(my_stream.read()), dtype=np.uint8)
frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
cv2.destroyAllWindows()
#frame = cv2.imread(my_stream)
#frame = imutils.resize(frame, height=800)

# Convert BGR to HSV
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
res = frame.copy()
# define range of blue color in HSV
def update(color, low_green, high_green):
    sensitivity = 10
    lower_green = np.array([color - sensitivity, low_green, low_green])
    upper_green = np.array([color + sensitivity, high_green, high_green])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Bitwise-AND mask and original image
    response = cv2.bitwise_and(frame, frame, mask=mask)

    return response

res = update(70, 100, 255)

# define the dictionary of digit segments so we can identify
# each digit on the digit meter
DIGITS_LOOKUP = {
	(1, 1, 1, 0, 1, 1, 1): 0,
    	(1, 1, 1, 0, 1, 1, 0): 0, # corrupted segment
    	(0, 1, 1, 0, 1, 1, 0): 0, # corrupted segment
    	(0, 1, 1, 0, 1, 1, 1): 0, # corrupted segment
	(0, 0, 1, 0, 0, 1, 0): 1,
	(1, 0, 1, 1, 1, 0, 1): 2,
	(1, 0, 1, 1, 0, 1, 1): 3,
	(0, 1, 1, 1, 0, 1, 0): 4,
	(1, 1, 0, 1, 0, 1, 1): 5,
	(1, 1, 0, 1, 1, 1, 1): 6,
	(1, 0, 1, 0, 0, 1, 0): 7,
	(1, 1, 1, 1, 1, 1, 1): 8,
	(1, 1, 1, 1, 0, 1, 1): 9
}
# load the example image
#HSV color filter, only display
image = res.copy()

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(blurred, 50, 200, 255)

# find contours in the edge map, then sort them by their
# size in descending order


_, contours0, hierarchy = cv2.findContours(gray.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours1 = [];
maximumArea = 0
displayCnt = contours0[0]

for cnt in contours0:
	# length of presicion to aproximate contours
	epsilon = 0.05 * cv2.arcLength(cnt, True)
	#approximation of contour
	approx = cv2.approxPolyDP(cnt, epsilon, True)
	contours1.append(approx)
	localMax = cv2.contourArea(approx)
	if maximumArea < localMax:
		maximumArea = localMax
		displayCnt = approx
h, w = edged.shape[:2]
vis = np.zeros((h, w, 3), np.uint8)

# extract the thermostat display, apply a perspective transform
# to it

# loop over the contours

warped = four_point_transform(gray, displayCnt.reshape(4, 2))
output = four_point_transform(image, displayCnt.reshape(4, 2))


# threshold the warped image, then apply a series of morphological
# operations to cleanup the thresholded image
warped = cv2.medianBlur(warped, 1)
thresh = cv2.adaptiveThreshold(warped,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)
kernel = np.ones((5, 3), np.uint8)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

hh, ww = thresh.shape[:2]
# number of the meter digits
digitCnts = [1,2,3,4,5,6,7]
digits = []

# loop over each of the digits

for c in digitCnts:
    # extract the digit ROI
    h = int(0.5 * hh)
    w = int(0.066 * ww)
    y = 10 + int(0.05 * hh)
    x = ww - c * int(0.024 * ww + w)
    roi = thresh[y:y + h, x:x + w]
    # compute the width and height of each of the 7 segments
    # we are going to examine
    (roiH, roiW) = roi.shape
    (dW, dH) = (int(roiW * 0.4), int(roiH * 0.1))
    

    # define the set of 7 segments
    segments = [
        ((0, 0), (w,dH)),	# top
        ((0, dH), (dW, (h - dH) // 2)),	# top-left
        ((w - dW, dH), (w, (h - dH) // 2)),	# top-right
        ((0, (h - dH) // 2) , (w, (h + dH) // 2)), # center
        ((0, (h + dH) // 2), (dW, h - dH)),	# bottom-left
        ((w - dW, (h + dH) // 2), (w, h - dH)),	# bottom-right
        ((0, h - dH), (w, h)) 	# bottom
    ]
	# segments array whis is on
    on = [1] * len(segments)

    # loop over the segments
    for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
            # extract the segment ROI, count the total number of
            # thresholded pixels in the segment, and then compute
            # the area of the segment
           
            segROI = thresh[y + yA : y + yB, x + xA : x + xB]
            total = cv2.countNonZero(segROI)
            area = (xB - xA) * (yB - yA)
                      
            # if the total number of non-zero pixels is greater than
            # 85% of the area, mark the segment as "on"

            if  float (total) / area > 0.85:
                on[i] = 0


            # lookup the digit and draw it on the image
    print(on)
    if tuple(on) in DIGITS_LOOKUP:
        digit = DIGITS_LOOKUP[tuple(on)]
        digits.append(digit)
        

# display the digits
print(digits)

my_stream.close()
camera.close()
