# Description

I installed at my home the heat pump. This kind of device consumes some electrical energy to transfer heat to my home. I am really curious how much electrical energy needs this device daily. So I decided to monitor main electricity meter of my home. I bought raspberry pi zero W, picamera version 1.3. I am capturing frames of electricity meter digit display by CRON in defined period. Every image is digitally preprocessed. It is recognised position of the display in the frame and seven digits as you can see on images bellow.
The really nice article about digits recognition with opencv and python is [here](https://www.pyimagesearch.com/2017/02/13/recognizing-digits-with-opencv-and-python/). The article inspired me a lot and I only modified the described code to fit to my project. After is image digits recognized to number, the number is stored to mongodb with timestamp. The rpi Zero W is used only for processing images and calling some mongoDB client to store data to other CentOs server. The Centos Server is used for running mongoDB and web server, where web presentation of energy results is hosted.   

## Physical Setup
<p align="left"> <img title="electricity meter" src="images/image001.jpg" alt="electricity meter"></p>
<p align="left"> <img title="front view installation of picamera and rpi Zero W" src="images/IMG-3604.jpg" alt="front view installation of picamera and rpi Zero W"></p>
<p align="left"> <img title="side view installation of picamera and rpi Zero W" src="images/IMG_3602.jpg" alt="side view installation of picamera and rpi Zero W"></p>
<p align="left"> <img title="pic from picamera" src="images/test6.jpg" alt="pic from picamera"></p>

# Installation

## OpenCv and Python
For installation opencv I followed [these](https://yoursunny.com/t/2018/install-OpenCV3-PiZero/) instructions.

```javascript
#Enable my Pi Zero repository:
echo 'deb [trusted=yes] http://dl.bintray.com/yoursunny/PiZero stretch-backports main' |\
  sudo tee  /etc/apt/sources.list.d/bintray-yoursunny-PiZero.list

#Update package lists:
sudo apt update

#Install OpenCV package:
sudo apt install python3-opencv

#Depending on the speed of your Internet connection, this may take between 15 and 30 minutes.
#Verify the installation:
python3 -c 'import cv2; print(cv2.__version__)'

#It will take around 30 seconds, and then you should see:
#3.2.0
```
After that I installed some missing python libraries 
```
sudo apt-get install libatlas-base-dev
sudo pip3 install scipy
sudo pip3 install imutils
```
## MongoDB
I use my Centos server for storing data and web presentation of results. I followed instructions [here](https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-centos-7) to install.

Create repo file for MongoDB [last stable version]() 
```
sudo vi /etc/yum.repos.d/mongodb-org.repo
```
Content of file should be similar to this
```
[mongodb-org-4.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/4.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-4.0.asc
```
Install command

```
sudo yum install mongodb-org
```
Enable and start mongodb service
```
sudo systemctl enable mongod
sudo systemctl start mongod
```
I wanted to access mongodb also with different places than localhost.
I open mongodb port to public zone by firewall

```
sudo firewall-cmd --permanent --zone=public --add-port=27017/tcp
```
Also don't forget changed Net part in file /etc/mongod.conf to bindIpAll
```
sudo vi /etc/mongod.conf
net:
  port: 27017
  bindIpAll: true  # Enter 0.0.0.0,:: to bind to all IPv4 and IPv6 addresses or, alternatively, use the net.bindIpAll setting.
```
For add new user to mongodb Follow [these](https://docs.mongodb.com/manual/reference/method/db.createUser/#db.createUser) instractions

# Run

```
python3 capture_digits.py
```

Results should be look similar this

```
# segments recognition
[1, 1, 1, 1, 0, 1, 1]
[1, 1, 1, 1, 1, 1, 1]
[1, 0, 1, 1, 1, 0, 1]
[1, 1, 1, 0, 1, 1, 1]
[1, 1, 1, 0, 1, 1, 1]
[1, 1, 1, 0, 1, 1, 1]
[1, 1, 1, 0, 1, 1, 0]

# digits recognition
[9, 8, 2, 0, 0, 0, 0]
```


