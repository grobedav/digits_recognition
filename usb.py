import io 
import serial
serialPort = serial.Serial(port = '/dev/ttyUSB0', baudrate=300,bytesize=serial.SEVENBITS,parity=serial.PARITY_EVEN,timeout=2)
serialString = "" # Used to hold data coming over UART 
serialPort.write(b"/?!\r\n")
#serialPort.write(b"/?!\r\n")
    # Wait until there is data waiting in the serial buffer
while True:
  if(serialPort.in_waiting > 0):
        # Read data out of the buffer until a carraige return / new line is found
        serialString = serialPort.readline()
        # Print the contents of the serial data print(serialString.decode('Ascii'))
	try:
         print(serialString)
         break;
    	except (UnicodeDecodeError):
    	 print("Problem")
        # Tell the device connected over the serial port that we recevied the data! The b at the beginning is used to indicate bytes!
#serialPort.flush()
   
serialPort.write(b'\x06') #ACK 
serialPort.write(b'000') #baudrate 000 - 300, 010 - 600, 020 - 1200, 030 - 2400, 040 - 4800, 050 - 9600, 060 - 19200 
serialPort.write(b'\x0D') #CR 
serialPort.write(b'\x0A') #LF
#serialPort.write(b"6000\r\n") 
serialString = "" 
while True:
  if b'\x03' in serialString:
        break;
  if(serialPort.in_waiting > 0):
        # Read data out of the buffer until a carraige return / new line is found
        serialString = serialPort.readline()
	try:
         print(serialString)
    	except (UnicodeDecodeError):
    	 print("")

serialPort.close()
