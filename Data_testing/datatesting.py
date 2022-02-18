import csv
from datetime import datetime
import subprocess  
import os  
    
print(os.getcwd())    
    
#To be used with file indexing
now = datetime.now()
current= now.strftime("%m/%d/%Y_%H:%M:%S")
pfilename = "./data/" +"Pressure_sensor_data_" + current +".csv"

args = ['echo',"' test'",">>",pfilename]
subprocess.run(["echo", "helloworld"])

subprocess.Popen(args)