#!/usr/bin/env python

import cx_Oracle
import os
connectString = u'test/test@127.0.0.1:1521/XE'
remoteFilePath = "Z:\\M18\\"
successFilePath = "F:\\lab_results\\M18_Success"
failureFilePath = "F:\\lab_results\\M18_Failed"

#Get the Lab_ID from the file
def ReadLabID(filePathName)
   f_file=open(filePathName,'r')
   lab_id = 0
   for line in f_file:
      lineNum=lineNum+1
      if lineNum == ??:    #FIX LINE NUMBER
         curToks=line.strip().split(';')
         lab_id=curToks[2].strip()
   return lab_id

#Return a dictionary with all the (parameter,value)
#FIX THIS FUNCTION 
def ReadFileParams(filePathName)
   lab_params = {}
   f_file=open(filePathName,'r')
   lineNum=0
   lineStr=''
   for line in f_file:
      curLine=line.split(';')
      lineNum=lineNum+1
      if lineNum == 1:
         p_id=curLine[2].strip()
      if lineNum == 3:
         testDate=curLine[1].strip()
      if lineNum == 4:
         testTime=curLine[1].strip()
      if lineNum >= 14 and lineNum <=29:
         lineStr=p_id+','+testDate+' '+testTime+','+curLine[0]+','+curLine[1]
         out_file.write(lineStr+'\n')
   f_file.close()
   return lineStr 


con = cx_Oracle.connect(connectString)

while 1:
   #check if new file in remoteFilePath
   filePathName = ''
   if ??:

   else:
      continue;

   #Process new file

   lab_id = ReadLabID(filePathName)
   lab_params = ReadFileParams(filePathName)

   #Query DBMS for records based on lab_id
   cur = con.cursor()
   dcl = 'select ... where lab_id=' + lab_id
   cur.execute(dcl)
   for row in cur:
      #process row
      #if heamatology insert data
      dml = 'update ... '
      cur.execute(...)
      con.commit()
   cur.close()

   #if no lab_id found or no hematology records or format error
      #move file to failureFilePath
   #else:
      #move file to successFilePath

