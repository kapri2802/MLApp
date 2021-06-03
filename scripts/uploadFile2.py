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

# config file
# import config as CONFIG
# with open('../config.json') as f:
#     CONFIG = json.load(f)

C = json.load(open('../config.json'))
print(C)

# initialize s3 client
client = boto3.client('s3', aws_access_key_id=C.['AWS_ACCESS_KEY'], aws_secret_access_key=C.AWS_ACCESS_SECRET_KEY)
transfer = S3Transfer(client)

# # setup input arguments. These will be used when calling as a script.
# # Disabled in notebook.



# check if the file exists


# check that file is csv only


# upload to s3 bucket


# function to check if file exits
def fileCheck():
    print('inside fileCheck')
    # check that file is csv only
    if not args_fileName.endswith('.csv'):
        print("Not a csv file")
        return 'FILE_NOT_CSV'

    exists = False
    for key in client.list_objects(Bucket=C.PROJECT_BUCKET)['Contents']:
        if key['Key'] == args_user + "/" + args_datasetName + "/" + "data" + "/" + args_fileName[-1]:
            exists = True
            print("Dataset/File already exists")
            return "DATASET_FILE_ALREADY_EXISTS"


# function to upload file to s3
def fileUpload():
    print("inside upload file")
    # create dataset property file
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    propertydictionary = {
        "uploadedon": dt_string,
        "filename": args_fileName[-1]
    }
    # Serializing json
    with open("data_properties.json", 'w') as fp:
        json.dump(propertydictionary, fp)

    # upload dataset and property file

    # upload to s3 bucket
    transfer.upload_file(args_fileName, C.PROJECT_BUCKET,
                                 args_user + "/" + args_datasetName + "/" + "data" + "/" + args_fileName[-1])
    transfer.upload_file("data_properties.json", C.PROJECT_BUCKET,
                                 args_user + "/" + args_datasetName + "/" + "data_properties.json")
    print('SUCCESS!! Data and properties File Uploaded to S3 ')
    return "DATAFILE_UPLOADED"


if __name__ == "__main__":
    # contruct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', type=str, required=True, help='username')
    ap.add_argument('-d', '--datasetName', type=str, required=True, help='name of the dataset')
    ap.add_argument('-f', '--fileName', type=str, required=True, help='name of the file to upload')
    args = vars(ap.parse_args())
    print(f'input arguments: {args}')
    args_user = args['user']
    args_datasetName = args['datasetName']
    args_fileName = args["fileName"]

    print(f'input user: {args_user}')
    print(f'input dataset name: {args_datasetName}')
    print(f'input file name: {args_fileName}')

    # check if file already exists
    fileCheck()

    # upload the file
    fileUpload()
    print("DONE")



