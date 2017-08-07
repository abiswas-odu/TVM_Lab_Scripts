# Thiruvananthapuram Hematology and Biochemistry Laboratory Integration Scripts 

### Current Version
* v1.0

### Setup and Installation

### Basic Dependencies

1. Python 3.5 or above. Install from: https://www.python.org
2. Python Package Index (PyPA) version or 9 above. Install from https://pypi.python.org/pypi/pip
3. Python module pyserial. Install using:
```
   pip install pyserial 
   
```
4. Oracle client installed. May need to add client library location to PATH. 
5. Python module cx_Oracle. Install using:
```
   pip install cx_Oracle 
   
```
 
### Client Side Installation Steps for Windows

1. Log into lab host computer to which the machines are connected. 
2. Download the python scripts from the ClientSide directory. 
3. Edit and save the following lines in each script:
```
port = 'COMx'
baud = 9600
remoteFilePath = "<path of network drive>"
localFilePath  = "<a local path on host computer>"
```
4. Press Windows+R to open run prompt and enter shell:startup. This will open the startup folder.
5. Copy the saved scripts in this location. 
6. Create links to the scripts on the desktop. 
7. Double click and run scripts. 


### Server Side Installation Steps for Windows

1. Log into lab server computer running Oracle. 
2. Download the python scripts from the ServerSide directory. 
3. Edit and save the following lines in each script:
```
connectString = u'test/test@127.0.0.1:1521/XE'
remoteFilePath = "Z:\\M18\\"
successFilePath = "F:\\lab_results\\M18_Success"
failureFilePath = "F:\\lab_results\\M18_Failed"

```
4. Press Windows+R to open run prompt and enter shell:startup. This will open the startup folder.
5. Copy the saved scripts in this location. 
6. Create links to the scripts on the desktop. 
7. Double click and run scripts. 