#!/usr/bin/env python

import cx_Oracle
import os
from datetime import datetime as dt
import datetime
import time
import shutil

dbUser='tvm'
connectString = u'tvm/tvm@127.0.0.1:1521/XE'
remoteFilePath = "Z:\\M18\\"
successFilePath = "F:\\lab_results\\M18_Success"
failureFilePath = "F:\\lab_results\\M18_Failed"
MACHINE_ID=1

#Get the Lab_ID from the file
def ReadLabID(filePathName)
   f_file=open(filePathName,'r')
   lab_id = 0
   lineNum = 0
   for line in f_file:
      line = line.strip()
      lineNum=lineNum+1
      if lineNum == 9:    #FIX LINE NUMBER
         curToks=line.split(';')
         lab_id=curToks[2].strip()
         f_file.close()
         return lab_id

#Return a dictionary with all the (parameter,value)
#FIX THIS FUNCTION 
def ReadFileParams(filePathName)
   lab_params = {}
   f_file=open(filePathName,'r')
   lineNum=0
   for line in f_file:
      curToks=line.split(';')
      lineNum=lineNum+1
      if lineNum >= 12 and lineNum <= 27:
         param_key=curToks[0].strip()
         param_value=curToks[0].strip()
         lab_params[param_key] = param_value
   f_file.close()
   return lab_params 

con = None

while 1:
   #check if new file in remoteFilePath
   files = os.listdir(remoteFilePath)
   for f in files:     #Check if any files are present in the list
      try:
         #Process new file
         lab_id = ReadLabID(f)
         lab_params = ReadFileParams(f)
         todayDate = datetime.date.today()
         todayDateStr = todayDate.strftime('%m/%d/%Y')
         #Query DBMS for records based on lab_id and date
         con = cx_Oracle.connect(connectString)
         cur = con.cursor()         
         dcl = 'SELECT pa.SERVICE_REGISTRATION_ID,mexp.METHOD_ACRONYM,m.PARAMETER_ID \
from patient_account pa,m_parameters m, M_METHODS_EXP mexp \
where m.SERVICE_SUBTYPE=pa.SERVICE_SUBTYPE \
and m.SERVICE_TYPE=\'HAEMATOLOGY\' and  m.PARAMETER_ID=mexp.PARAMETER_ID \
and m.STATUS=\'Active\' and mexp.MACHINE_INDEX = :1 \
and lab_id = :2 and DATE_FROM = TO_DATE( :3 , \'MM-DD-YYYY\')'
         cur.execute(dcl,(MACHINE_ID,lab_id,todayDateStr))
         for row in cur:
            #process row
            acr_key = row[1]
            if acr_key in lab_params:
               param_value = lab_params.get(acr_value)
               dml = 'insert into t_results(service_registration_id,parameter_id,result,status,updated_by) \
values( :1, :2, :3,\'Complete\', :4)'
               cur.execute(dml,(row[0],row[2],param_value, 'tvm'))
               con.commit()
         #move file to successFilePath
         shutil.move(f, successFilePath)
      except:       
         #if no lab_id found or no hematology records or format error
         #move file to failureFilePath
         shutil.move(f, failureFilePath)
      finally:
         cur.close()
         if con is not None:
            con.close()
   #Wait before next directory check
   time.sleep(30)    

