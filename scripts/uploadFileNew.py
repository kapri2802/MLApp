# -*- coding: utf-8 -*-
# ------------------------------------------
#
# script to upload file to user S3 bucket
# INPUT: dict
# username: User              : Name of user uploaded
# datasetname: Dataset Name   : name for dataset
# foldername: Dataset folder  : folder to read file from
# filename: Dataset file      : name for file to read
#
# ------------------------------------------

import numpy as np
import pandas as pd
import os, argparse
import boto3
from boto3.s3.transfer import S3Transfer
from boto3 import client
import json
from datetime import datetime

# # setup input arguments. These will be used when calling as a script.
# # Disabled in notebook.

# contruct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument('-u', '--user', type=str, help='username')
ap.add_argument('-d', '--datasetName', type=str, help='name of the dataset')
ap.add_argument('-f', '--fileName', type=str, help='name of the file to upload')
args = vars(ap.parse_args())
args_user = args['user']
args_datasetName = args['datasetName']
args_fileName = args["fileName"]
with open('C:/Users/abhishek.kapri/Downloads/app/app/resources/config.json') as config_file:
    data = json.load(config_file)

print(f'input user: {args_user}')
print(f'input dataset name: {args_datasetName}')
print(f'input file path: {args_fileName}')
filename = args_fileName.split("/")
print("This is filename",filename[-1])
client = boto3.client('s3', aws_access_key_id=data['AWS_ACCESS_KEY'],aws_secret_access_key=data['AWS_ACCESS_SECRET_KEY'])
transfer = S3Transfer(client)

# check if the file exists
Flag = False
for key in client.list_objects(Bucket=data['bucket'])['Contents']:
    if key['Key'] == args_user+"/"+args_datasetName+"/"+"data"+"/"+filename[-1] :
        Flag = True

Flagfiletype = False
# check that file is csv only
if args_fileName.endswith('.csv') :
    Flagfiletype = True

#file property
dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
propertydictionary ={
                    "uploadedon": dt_string ,
                    "filename": filename[-1]
                    }
                
# Serializing json  
with open("data_properties.json", 'w') as fp:
    json.dump(propertydictionary, fp)

# upload to s3 bucket
if Flag == False :
    if Flagfiletype == True :
        transfer.upload_file("data_properties.json", data['bucket'], args_user+"/"+args_datasetName+"/"+"data_properties.json")
        transfer.upload_file(args_fileName, data['bucket'], args_user+"/"+args_datasetName+"/"+"data"+"/"+filename[-1])
        print('Sucess!! Data and properties Uploaded to S3 ')
    else :
        print("File type is not CSV")
else :
    print("Flie Already exist ")







# return "SUCCESS"



