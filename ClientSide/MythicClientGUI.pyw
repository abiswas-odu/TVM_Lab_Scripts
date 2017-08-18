#! /usr/bin/env python3
import serial
import time
import datetime
import shutil
import os.path
import threading
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory
from PIL import Image
from PIL import ImageTk
from tkinter import messagebox
##GLOBAL DECLARATIONS
port = 'COM3'   #COM port to which the Mythic machine is connected
baud = 9600     #Set baud rate from documentation 
remoteFilePath = "E:\\lab_results"   #Path to network drive to store the files
localFilePath  = "E:\\M18"   #Path to local directory to save files when network drive is down
success_rel_path='success.gif'
failure_rel_path='failure.gif'
loading_rel_path='loading.gif'
currentTestCount = 0
last_date = datetime.datetime.now()
ser = serial.Serial()
top = Tk()

#Move files from local directory to remote server drive 
def MoveLocalFiles(localFilePath,remoteFilePath):
    files = os.listdir(localFilePath)
    for f in files:
       filePath = os.path.join(localFilePath,f)
       shutil.move(filePath, remoteFilePath)

class Screen:
    def __init__(self,master):
        master.wm_title("SRL Mythic Machine Reader")
        master.minsize(width=400, height=150)
        master.resizable(width=False, height=False)
        self.frame = Frame(master)
        self.frame.pack(side="top", fill="both", expand = True)

        Photo = ImageTk.PhotoImage(Image.open(loading_rel_path))
        self.pic_label = Label(self.frame, image=Photo)
        self.pic_label.image = Photo
        self.pic_label.grid(row=0, column=0, columnspan=2, rowspan=2,sticky=W+E+N+S, padx=5, pady=5)

        self.msgFrame = Frame(self.frame)
        self.msgFrame.grid(row=0,column=2, columnspan=2)
        
        self.msg_label = Label(self.msgFrame, text="Connecting...",width=45, wraplength=330)
        self.msg_label.grid(row=0,column=0, sticky=N)
        
        now = datetime.datetime.now()
        self.count_label = Label(self.msgFrame, text=str(currentTestCount)+" test results processed on "+now.strftime("%d/%m/%Y"),font=("Courier", 15),width=40, height=5, wraplength=330)
        self.count_label.grid(row=1,column=0, sticky=S)

        self.dataFrame = Frame(self.frame)
        self.dataFrame.grid(row=1,column=2, columnspan=2, sticky=W+E+N+S)

        portDataLabel = Label(self.dataFrame)
        portDataLabel["text"] = 'Mythic COM port: '
        self.varPort = StringVar(master)
        self.varPort.set(port)
        portDataLabel.grid(row=0,column=0,sticky=E)
        portText = Entry(self.dataFrame, textvariable=self.varPort,width=50)
        portText.grid(row=0,column=1)
		
        localDataLabel = Label(self.dataFrame)
        localDataLabel["text"] = 'Local Data Directory: '
        localDataLabel.grid(row=1,column=0,sticky=E)
        self.varLocal = StringVar(master)
        self.varLocal.set(localFilePath)
        w = Entry(self.dataFrame, textvariable= self.varLocal,width=50)
        w.grid(row=1,column=1)
        dirButLocal = Button(self.dataFrame, text='...', command = self.askdirectoryLocal)
        dirButLocal.grid(row=1,column=2)

        remoteDataLabel = Label(self.dataFrame)
        remoteDataLabel["text"] = 'Network Data Directory: '
        remoteDataLabel.grid(row=2,column=0, sticky=E)
        self.varRemote = StringVar(master)
        self.varRemote.set(remoteFilePath)
        w1 = Entry(self.dataFrame, textvariable= self.varRemote,width=50)
        w1.grid(row=2,column=1, sticky=E)
        dirButRemote = Button(self.dataFrame, text='...', command = self.askdirectoryRemote)
        dirButRemote.grid(row=2,column=2, sticky=E)
        
        self.con_button = Button(self.frame, text="Connect to Mythic", command=self.Connected,width=30)
        #self.close_button = Button(self.frame, text="Close",command=quit)
        self.con_button.grid(row=2, column=0, columnspan=4, padx=15, pady=15)
        #self.close_button.grid(row=2, column=2, columnspan=2, padx=15, pady=15)

        self.readThreadStop = threading.Event()
        self.readThread = threading.Thread(target=self.ReadMythic, args=(1,self.readThreadStop))
        self.Connected()

    def ReadMythic(self, arg1, stop_event):
        global currentTestCount
        global ser
        global last_date
        isComplete = 1
        resultID = 1
        resultLine = ''
        try:
            while (not stop_event.is_set()):
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
                  # Save result in local location
                  absolutefilename = os.path.join(self.varLocal.get(),filename)
                  f = open(absolutefilename, 'a+')
                  f.write(resultLine)
                  f.close()
                  if os.path.exists(self.varRemote.get()): # Check is network drive is available or not
                     MoveLocalFiles(self.varLocal.get(),self.varRemote.get())  # Move files from local drive to network drive
                  #Re-initialize varialbe for next communication 
                  isComplete = 1           
                  resultLine = ''
                  resultID += 1
                  now = datetime.datetime.now()
                  if last_date.strftime("%d/%m/%Y") != now.strftime("%d/%m/%Y"):
                      last_date=now
                      currentTestCount=0
                  currentTestCount += 1
                  self.count_label.configure(text=str(currentTestCount)+" test results processed on "+now.strftime("%d/%m/%Y"))
        except serial.SerialException:
            self.DisConnected()

    def Connected(self):
        global currentTestCount
        global ser
        global last_date
        try:
           ser = serial.Serial(self.varPort.get(), baud, timeout=1)
        except serial.SerialException:
           self.DisConnected()
           return
        Photo = ImageTk.PhotoImage(Image.open(success_rel_path))
        self.pic_label.configure(image=Photo)
        self.pic_label.image = Photo
        self.msg_label.config(text='Connected Successfully.')
        self.con_button.config(text='Disconnect from Mythic',command=self.DisConnected, width=30)
        now = datetime.datetime.now()
        if last_date.strftime("%d/%m/%Y") != now.strftime("%d/%m/%Y"):
            last_date=now
            currentTestCount=0
        self.count_label.configure(text=str(currentTestCount)+" test results processed on "+now.strftime("%d/%m/%Y"))

        self.readThreadStop = threading.Event()
        self.readThread = threading.Thread(target=self.ReadMythic, args=(1,self.readThreadStop))
        self.readThread.start()

    def DisConnected(self):
        global ser
        global currentTestCount
        self.readThreadStop.set()
        time.sleep(2)
        try:
           ser.close()
        except serial.SerialException:
           pass
        Photo = ImageTk.PhotoImage(Image.open(failure_rel_path))
        self.pic_label.configure(image=Photo)
        self.pic_label.image = Photo
        self.msg_label.configure(text='Mythic disconnected. Please check if Mythic is switched on and connected.') 
        self.con_button.config(text="Connect to Mythic",command=self.Connected, width=30)
        now = datetime.datetime.now()
        if last_date.strftime("%d/%m/%Y") != now.strftime("%d/%m/%Y"):
            currentTestCount=0
        self.count_label.configure(text=str(currentTestCount)+" test results processed on "+now.strftime("%d/%m/%Y"))

    def askdirectoryLocal(self):
       dirname = askdirectory()
       if dirname:
          self.varLocal.set(dirname)
    def askdirectoryRemote(self):
       dirname = askdirectory()
       if dirname:
          self.varRemote.set(dirname)
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.readThreadStop.set()
            time.sleep(2)
            top.destroy()

app = Screen(top)
top.protocol("WM_DELETE_WINDOW",lambda: app.on_closing())
top.mainloop()
