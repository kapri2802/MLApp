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
import json
from datetime import datetime

# config file
# import config as CONFIG
# CONFIG_FILE = '../config.json'
CONFIG_FILE = 'config.json'
C = json.load(open(CONFIG_FILE))
# print(C)


class UploadFile():
    def __init__(self, user:str, datasetName:str, fileName:str):
        print('inside init')
        self.user = user
        self.datasetName = datasetName
        self.fileName = fileName
        # initialize s3 client
        self.s3client = boto3.client('s3', aws_access_key_id=C['AWS_ACCESS_KEY'], aws_secret_access_key=C['AWS_ACCESS_SECRET_KEY'])
        self.s3transfer = S3Transfer(self.s3client)

    # function to check if file exits
    def fileCheck(self):
        print('inside fileCheck')
        VAL = 0
        # check that file is csv only
        if not self.fileName.endswith('.csv'):
            print("Not a csv file")
            VAL = 'FILE_NOT_CSV'
            return VAL

        exists = False
        for key in self.s3client.list_objects(Bucket= C['PROJECT_BUCKET'])['Contents']:
            if key['Key'] == self.user + "/" + self.datasetName + "/" + "data" + "/" + self.fileName[-1]:
                exists = True
                print("Dataset/File already exists")
                VAL = 'DATASET_FILE_ALREADY_EXISTS'
        return VAL

    # function to upload file to s3
    def fileUpload(self):
        print("inside upload file")
        VAL = 0
        # create dataset property file
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        propertydictionary = {
            "uploadedon": dt_string,
            "filename": self.fileName
        }
        # Serializing json
        with open("data_properties.json", 'w') as fp:
            json.dump(propertydictionary, fp)

        # upload dataset and property file
        # upload to s3 bucket
        print('Uploading to S3...')
        # PENDING
        # check if user already exists in S3 else create it.
        # create folder inside user's s3 bucket
        # upload datafile and prop
        # self.s3transfer.upload_file(self.fileName, C['PROJECT_BUCKET'],
        #                              self.user + "/" + self.datasetName + "/" + "data" + "/" + self.fileName[-1])
        # self.s3transfer.upload_file("data_properties.json", C['PROJECT_BUCKET'],
        #                              self.user + "/" + self.datasetName + "/" + "data_properties.json")
        print('SUCCESS!! Data and properties File Uploaded to S3 ')
        # VAL = "DATAFILE_UPLOADED"
        VAL = 0
        return VAL

    # main function for flow
    def run(self):
        print('inside run')
        # duplicate check
        fileCheckStatus = self.fileCheck()
        if fileCheckStatus != 0:
            return fileCheckStatus
        # upload file
        fileUploadStatus = self.fileUpload()
        if fileUploadStatus != 0:
            return fileUploadStatus
        return 0



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

    # invoke class
    uploadfile = UploadFile(args_user, args_datasetName, args_fileName)
    uploadfile.run()
    print("DONE")



