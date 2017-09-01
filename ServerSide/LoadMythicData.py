#!/usr/bin/env python

import os
import cx_Oracle
import datetime
import time
import shutil

connectString = u'tvm/tvm@127.0.0.1:1521/XE'
remoteFilePath = "F:\\lab_results\\M18\\"
successFilePath = "F:\\lab_results\\M18_Success\\"
failureFilePath = "F:\\lab_results\\M18_Failed\\"
MACHINE_ID=1
con = None

def retNumber(s):
   try:
      float_val = float(s)
      return float_val
   except ValueError:
      return -1

class MythicData:
   def __init__(self, labId, testDate, labParams):
      self.lab_id = labId   
      self.test_date = testDate
      self.lab_params = labParams
   @staticmethod
   def parseMythicFile(filePathName):
      acrList = ['WBC','RBC','HGB','HCT','PLT','LYM','MON','GRA','LYM%','MON%','GRA%','MCV','MCH','MCHC','RDW','MPV',"MCY","BPH"]
      mResultList = []
      lab_id = 0
      lab_params = {}
      testDate = datetime.date.today()
      openRecord = 0
      f_file=open(filePathName,'r')
      line = f_file.readline()
      while line:
         line = line.strip()
         curToks=line.split(';')
         if curToks[0].strip() == 'MYTHIC 1':
            openRecord=1;
         elif openRecord==1 and curToks[0].strip()=='DATE':              #DATE LINE
            testDate = datetime.datetime.strptime(curToks[1], "%d/%m/%Y").date()
         elif openRecord==1 and curToks[0].strip()=='ID':                #LAB ID LINE
            lab_id=curToks[1].strip()
         elif openRecord==1 and curToks[0].strip()=='OPERATOR' and len(curToks)>2:          #WBC LINE
            param_key=curToks[1].strip()
            param_value=curToks[2].strip()
            lab_params[param_key] = retNumber(param_value)*1000
         elif openRecord==1 and curToks[0].strip()=='MON%':              #EOSINOPHILS LINE
            param_key=curToks[0].strip()
            param_value=curToks[1].strip()
            lab_params[param_key] = round(retNumber(param_value))
         elif openRecord==1 and curToks[0].strip()=='LYM%':              #LYMPHOCYTES LINE
            param_key=curToks[0].strip()
            param_value=curToks[1].strip()
            lab_params[param_key] = int(retNumber(param_value))
         elif openRecord==1 and curToks[0].strip()=='GRA%':              #NEUTROPHILS LINE
            param_key=curToks[0].strip()
            param_value=curToks[1].strip()
            lab_params[param_key] = int(retNumber(param_value))
         elif openRecord==1 and curToks[0].strip()=='PLT':               #PLT LINE
            param_key=curToks[0].strip()
            param_value=curToks[1].strip()
            pltCount = retNumber(param_value)/100
            #If very less dont enter in lakhs/cumm but in hundred/cumm  
            if pltCount < 1.0:
               lab_params[param_key] = pltCount*100*1000
            else:
               lab_params[param_key] = pltCount
         elif openRecord==1 and curToks[0].strip() in acrList:           #OTHER PARAMETER LINES
            param_key=curToks[0].strip()
            param_value=curToks[1].strip()
            if param_key=='WBC':
               lab_params[param_key] = retNumber(param_value)*1000
            else:
               lab_params[param_key] = retNumber(param_value)
         elif openRecord==1 and curToks[0].strip()=='END_RESULT':       #END LINES
            #Insert derived defaults Basophils(BPH) and Monocytes(MCY)
            lab_params['BPH']=0
            eosPhi_value = lab_params.get('MON%',0)
            lymCyt_value = lab_params.get('LYM%',0)
            neuPhi_value = lab_params.get('GRA%',0)
            lab_params['MCY']=(100-eosPhi_value-lymCyt_value-neuPhi_value)
            print(lab_params.get('MCY'))
            mResultList.append(MythicData(lab_id,testDate,lab_params))
            lab_id = 0
            lab_params = {}
            testDate = datetime.date.today()
            openRecord = 0
            if curToks[1].strip().find('MYTHIC 1') > -1:
               openRecord = 1
         line = f_file.readline()
      f_file.close()
      return mResultList	  
   
def StoreResults(mythicResult):
    dateStr = mythicResult.test_date.strftime('%m/%d/%Y')
    ret_val=0;
    try:
       con = cx_Oracle.connect(connectString)
       #Query DBMS for records based on lab_id and date
       curSelect = con.cursor()
       curInsert = con.cursor() 
       dcl = 'select psr.SERVICE_REGISTRATION_ID, mexp.METHOD_ACRONYM, psr.PARAMETER_ID from \
(SELECT MIN(pa.SERVICE_REGISTRATION_ID) as SERVICE_REGISTRATION_ID, m.PARAMETER_ID \
from patient_account pa,m_parameters m \
where m.SERVICE_SUBTYPE=pa.SERVICE_SUBTYPE \
and m.SERVICE_TYPE=\'HAEMATOLOGY\' and m.STATUS=\'Active\' \
and lab_id = :1 and trunc(pa.REPORT_DATE) = TO_DATE( :2 , \'MM/DD/YYYY\') \
and (pa.SERVICE_REGISTRATION_ID,m.PARAMETER_ID) NOT IN (select SERVICE_REGISTRATION_ID,PARAMETER_ID from t_results) \
group by m.PARAMETER_ID) psr, M_METHODS_EXP mexp \
where psr.PARAMETER_ID=mexp.PARAMETER_ID and mexp.MACHINE_ID= :3'
       curSelect.execute(dcl,(mythicResult.lab_id,dateStr,MACHINE_ID))
       isLoaded = 0;
       for row in curSelect:
         #process row
         acr_key = row[1]
         if acr_key in mythicResult.lab_params:
            param_value = mythicResult.lab_params.get(acr_key)
            dml = 'insert into t_results(service_registration_id,parameter_id,result,status) \
values( :1, :2, :3,\'Complete\')'
            curInsert.execute(dml,(row[0],row[2],param_value))
            con.commit()
            isLoaded=1;
       if isLoaded == 0:
          ret_val=1
    except Exception as error:
       print('Caught this error: ' + repr(error))   
       #if no lab_id found or no hematology records or format error
       #move file to failureFilePath
       ret_val=1
    finally:
       curSelect.close()
       curInsert.close()
       if con is not None:
          con.close()
    return ret_val;


while 1:
   #check if new file in remoteFilePath
   files = os.listdir(remoteFilePath)
   for f in files:     #Check if any files are present in the list
      #Process new file
      absolutefilename = remoteFilePath + f
      print('Processing file:' + absolutefilename)
      successFlag=0
      mythicResultsList = MythicData.parseMythicFile(absolutefilename)
      for mResult in mythicResultsList:
          successFlag += StoreResults(mResult)
      if successFlag==0:      # Move file to success folder if all tests were loaded
         successFileName = successFilePath + f
         shutil.move(absolutefilename, successFileName)
      else:                   # Move file to failure folder if some tests were not loaded
         failureFileName = failureFilePath + f
         shutil.move(absolutefilename, failureFileName)
   #Wait before next directory check
   time.sleep(30)    

