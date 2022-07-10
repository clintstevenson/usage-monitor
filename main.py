from typing import Optional
from ctypes import wintypes, windll, create_unicode_buffer
import win32api
import time
import codecs
from datetime import datetime
import boto3
import math as m
import pandas as pd
from os import listdir
from os.path import isfile, join
import glob
import yaml
import json
import io
import csv
import gzip
import re
import os
import socket

USER_DIR = os.path.expanduser('~')
COMPUTER_NAME = socket.gethostname()
###############################
# Install beyond base Python
#
# python pip -m install pywin32
# python pip -m install boto3
# python pip -m install pandas
# python pip -m install pyyaml
###############################

def credload(dir = None):    
    if dir is None:
        return False
        
    try:
        with open(dir, 'r') as yaml_in:
            yaml_object = yaml.load(yaml_in, Loader = yaml.SafeLoader) # yaml_object will be a list or a dict
            yaml_default = yaml_object['default']
    except Exception as e:
        return str(e)
    
    return yaml_default


def add_to_startup(file_path=""):
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(__file__))
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
        bat_file.write(r'start "" "%s"' % file_path)


def getForegroundWindowTitle() -> Optional[str]:
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    
    if buf.value:
        return buf.value
    else:
        return None
    
def s3_send(df, s3_bucket = None, s3_key = None, compresslevel = 9, credentials = None):
    msg = ''
    status = False
    
    try:
        if credentials is None:
            raise("Credentials are required")
        
        ACCESS_KEY = credentials['ACCESS_KEY']
        SECRET_KEY = credentials['SECRET_KEY']
      
        s3 = boto3.resource('s3', aws_access_key_id = ACCESS_KEY, aws_secret_access_key = SECRET_KEY)
      
        gz_buffer = io.BytesIO()  
        s_buf = io.StringIO()
        df.to_csv(s_buf, index = False, quoting=csv.QUOTE_NONNUMERIC, quotechar = '"', doublequote=False, sep ='\t')
        s_buf.seek(0)
      
        with gzip.open(gz_buffer, mode = 'wb', compresslevel = int(compresslevel)) as gz_file:            
            gz_file.write(s_buf.getvalue().encode())   
      
        s3_object = s3.Object(s3_bucket, s3_key)   
        s3_object.put(Body = gz_buffer.getvalue())
      
        status = True
      
    except Exception as e:
        msg = str(e)
      
    return {'status': status, 'Compression': compresslevel, 'Bucket': s3_bucket, 'ObjectLocation': s3_key, 'message': msg}    
    
def track_it(cred_file = None, s3_bucket = None, heart_beat_time = 60, send_2_s3_minute_interval = 10):
    
    yaml_default = credload(dir = cred_file)
    creds = {'ACCESS_KEY' : yaml_default['aws_access_key'], 'SECRET_KEY' : yaml_default['aws_secret_key'] }

    prev_pos = curr_pos = [0, 0]
    curr_window_title = ''
    start_time = int( time.time() )
    start_time_minute = m.floor(start_time / 60)

    while True:
        prev_pos = win32api.GetCursorPos()
        window_title = getForegroundWindowTitle()
        now = int( time.time() )
        pos_str = ','.join(str(j) for j in prev_pos)

        if prev_pos[0] != curr_pos[0] or prev_pos[1] != curr_pos[1] or curr_window_title != window_title:        
            out = str(pos_str) + '\t' + str(now) + '\t' + str(window_title) + '\n'
            
            path = USER_DIR + "/tmp-usage-out/"            
            isExist = os.path.exists(path)
            if not isExist:
                os.makedirs(path)
                
            out_filename = path + COMPUTER_NAME + "_" + str(datetime.now().strftime("%Y%m%d")) + ".txt"        
            f = codecs.open(str(out_filename), "a", "utf-8")
            f.write(out)
            f.close()

        curr_time_minute = m.floor(start_time / heart_beat_time)

        # if curr_time_minute - start_time_minute % send_2_s3_minute_interval == 0: 
        log_files = glob.glob(path + "/[a-zA-Z0-9\-]*.txt")

        for i in log_files:                
            d = pd.read_csv(i, sep="\t", names=['position','timestamp', 'window_name'])   
            
            p = re.compile("[a-zA-Z0-9\-]+\.txt")
            i_filename = p.search(i).group(0)            
            p2 = re.compile("^[a-zA-Z0-9\-]+")
            i_date = p2.search(i_filename).group(0)
            
            s3_filename = i_filename + '.gz'
            s3_complete = s3_send(df = d, s3_bucket = s3_bucket, s3_key = s3_filename, compresslevel = 9, credentials = creds)                  

            if datetime.now().strftime("%Y%m%d") != i_date:
                os.unlink(i)            

        curr_pos = prev_pos
        curr_window_title = window_title
        time.sleep(heart_beat_time)
    
    
if __name__ == '__main__':
    cred_file_name = USER_DIR + '/Documents/authentication/test_creds.yml'
    
    track_it(cred_file = cred_file_name, 
             s3_bucket = 'home-usage-logger', heart_beat_time = 2, 
             send_2_s3_minute_interval = 1)
