# Description

I installed at my home the heat pump. This kind of device consumes some electrical energy to transfer heat to my home. I am really curious how much electrical energy needs this device daily. So I decided to monitor main electricity meter of my home. I bought raspberry pi zero W, picamera version 1.3. I am capturing frames of electricity meter digit display by CRON in defined period. Every image is digitally preprocessed. It is recognised position of the display in the frame and seven digits as you can see on images bellow.
The really nice article about digits recognition with opencv and python is [here](https://www.pyimagesearch.com/2017/02/13/recognizing-digits-with-opencv-and-python/). The article inspired me a lot and I only modified the described code to fit to my project. After is image digits recognized to number, the number is stored to mongodb with timestamp. The rpi Zero W is used only for processing images and calling some mongoDB client to store data to other CentOs server. The Centos Server is used for running mongoDB and web server, where web presentation of energy results is hosted.   

## Physical Setup
<p align="left"> <img title="electricity meter" src="images/image001.jpg" alt="electricity meter"></p>
<p align="left"> <img title="front view installation of picamera and rpi Zero W" src="images/IMG-3604.jpg" alt="front view installation of picamera and rpi Zero W"></p>
<p align="left"> <img title="side view installation of picamera and rpi Zero W" src="images/IMG_3602.jpg" alt="side view installation of picamera and rpi Zero W"></p>
<p align="left"> <img title="pic from picamera" src="images/test6.jpg" alt="pic from picamera"></p>

# Upgrade

I started use optical electricity meter reader for reading energy values from electricity meter.
I am using serial communication between reader and electricity meter according to norm ČSN EN IEC 62056-8-4.
Thats mean that I am not using CAMERA picture parsing anymore. But I like Camera solution because it is cheaper and interesting. So I am keeping the information about that also here.

# Installation
## Optical electricity meter
Main script which I am using now is called
```
usb.py
```
This script is based on three parts. 
Firstly
Serial communication between reader and meter. 
I started 7 bit, even parity, 300 baud serial communication. The serial request is sent and response is parsed and stored in the memory.
Secondly
Background time period scheduler is used because IR receiver/transmitter communication takes some time to have data available.
Thirdly
Flask library for creation HTTP REST service. REST service can be read with any other application for results visualisation.
```
curl http://192.168.0.100:5000/electricity_meter/api/v1.0/energy
{"energy":{"highTarif":"0004200.177","lowTarif":"0021209.409","suma":"0025409.587"}}

```

I am using python 3.9.1.

Guide is from 

https://webcache.googleusercontent.com/search?q=cache:8M8wBAk5bEIJ:https://installvirtual.com/how-to-install-python-3-8-on-raspberry-pi-raspbian/+&cd=1&hl=cs&ct=clnk&gl=cz

```
#Download
wget https://www.python.org/ftp/python/3.9.1/Python-3.9.1.tgz

#Extract and install
sudo tar zxf Python-3.9.1.tgz
cd Python-3.9.1
sudo ./configure --enable-optimizations
sudo make -j 4
sudo make altinstall

#Make as default
echo "alias python=/usr/local/bin/python3.9" >> ~/.bashrc
source ~/.bashrc
```

Install and upgrade pip
```
python -m pip install --upgrade pip
```

Install virtual env
```
pip install virtualenv
```

Create virtual env
```
virtualenv venv
```

Activate virtual env
```
source venv/bin/activate
```

Install necessary libraries

```
pip install pyserial
pip install flask
pip install apscheduler
```
Create system service
```
sudo nano optical_sensor.service
```

```
[Unit]
Description=Optical Sensor Service

[Service]
User=pi
WorkingDirectory=/home/pi/power_meter
ExecStart=/home/pi/power_meter/usb.py

[Install]
WantedBy=multi-user.target
```
Enable Service
```
sudo systemctl daemon-reload
sudo systemctl enable optical_sensor.service
sudo systemctl start optical_sensor.service
```
### CRON
```
*/30 * * * * /usr/bin/sh /home/ubuntu/add_energy_to_elastic/run.sh
```

## --- Camera solution ---
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
For add new user to mongodb Follow [these](https://docs.mongodb.com/manual/reference/method/db.createUser/#db.createUser) instructions

Install python library pymongo for CRUD operations
```
sudo pip3 install pymongo
```
Nice tutorial is [here](https://www.mongodb.com/blog/post/getting-started-with-python-and-mongodb)

My Mongo client for storing necessary data looks like this
```
try:
	client = MongoClient('mongodb://x.xxx.xxx.xx:27017',
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
```
## CRON
I want to store current values to mongodb every 15 minutes
```
crontab -e
```
This command open the file with scheduler
Write this similar schedule to the file with right path

```
*/15 * * * *    python3 ~/power_meter/digits_recognition/capture_digits.py
```
For cron trouble shooting use
```
grep CRON /var/log/syslog
```
You should have installed postfix for more info about issue
```
sudo aptitude install postfix
```
Look here after postfix is correctly set up
```
sudo tail -f /var/mail/<user>
```

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


