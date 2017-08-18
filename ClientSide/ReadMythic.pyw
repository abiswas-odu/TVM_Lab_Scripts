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



