#! /usr/bin/env python3
import serial
import time
import datetime
import shutil
import os.path

port = 'COM3'   #COM port to which the Mythic machine is connected
baud = 9600     #Set baud rate from documentation 
remoteFilePath = "Z:\\M18\\"   #Path to network drive to store the files
localFilePath  = "D:\\M18\\"   #Path to local directory to save files when network drive is down

#Scan all ports that are active
def scan():
    """scan for available ports. return a list of tuples (num, name)"""
    available = []
    for i in range(256):
        try:
            portName = "COM" + str(i)
            s = serial.Serial(portName)
            available.append( (i, s.portstr))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available

#Move files from local directory to remote server drive 
def MoveLocalFiles(localFilePath,remoteFilePath):
    files = os.listdir(localFilePath)
    for f in files:
       shutil.move(f, remoteFilePath)

#Print all active ports 
if __name__=='__main__':
    print ("Found ports:")
    for n,s in scan():
        print ("(%d) %s" % (n,s))

#Open Mythic port and init some flag variables
ser = serial.Serial(port, baud, timeout=1)
isComplete = 1
resultID = 1
resultLine = ''

while 1:
  tdata = ser.read()           # Wait forever for anything
  data_left = ser.inWaiting()  # Get the number of characters ready to be read
  tdata += ser.read(data_left) # Do the read and combine it with the first character
  print("Reading " + str(data_left) + "bytes.") 
  line = tdata.decode('utf-8') # Convert raw bytes to ascii data  
  line = line.strip()          # Remove leading and trailing whitespace characters 
  if line:                     # If it isn't a blank line
     isComplete = 0
     resultLine += line        # Add to result line 

  if isComplete==0 and data_left==0:  # Check if communication has finished and push result to file
      
     filename = datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S') + '_ID_' + str(resultID) + '.csv'
     if os.path.exists(remoteFilePath):          # Check is network drive is available or not
        absolutefilename = remoteFilePath + filename
        f = open(absolutefilename, 'a+')
        f.write(resultLine)
        f.close()
        MoveLocalFiles(localFilePath,remoteFilePath)  # Move files from local drive to network drive 
     else:                                            # If network drive is down save result in local location 
        absolutefilename = localFilePath + filename
        f = open(absolutefilename, 'a+')
        f.write(resultLine)
        f.close()
     #Re-initialize varialbe for next communication 
     isComplete = 1           
     resultLine = ''
     resultID += 1
     
ser.close()


