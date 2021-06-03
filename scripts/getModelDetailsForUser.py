# -*- coding: utf-8 -*-
# ------------------------------------------
#
# script to list file to user S3 bucket
# INPUT: string
# username: User    : Name of user to fetch project details for
# OUTPUT: list
# project name
# ------------------------------------------

# import library
import os, json, sys, argparse
import pprint
import boto3
from boto3.s3.transfer import S3Transfer

CONFIG_FILE = 'config.json'
C = json.load(open(CONFIG_FILE))

class GetModelDetailsForUser():
    def __init__(self, user: str, proj:str, dfile:str):
        print('inside init')
        self.user = user
        self.proj = proj
        self.dfile = dfile
        # initialize s3 client
        self.s3client = boto3.client('s3', aws_access_key_id=C['AWS_ACCESS_KEY'],
                                     aws_secret_access_key=C['AWS_ACCESS_SECRET_KEY'])
        # self.s3transfer = S3Transfer(self.s3client)

    # function to get folder names inside user
    def getModelDetails(self):
        print(f'fetching project details for user: {self.user}/{self.proj}')
        # append / end of user
        self.user = self.user if self.user.endswith('/') else self.user + '/'
        models = []
        directories = []
        for obj in self.s3client.list_objects_v2(Bucket=C['PROJECT_BUCKET'], Prefix=f'{self.user}')['Contents']:
            [directories.append(obj['Key'])]
        print("directories",directories)
        
        for i in directories:
            if f'{self.proj}/model' in i:
                if i.endswith('.json'):
                    print(i)
                    result = self.s3client.get_object(Bucket=C['PROJECT_BUCKET'], Key=i)
                    file = json.loads(result['Body'].read())
                    [models.append(file)]
        return models


if __name__ == "__main__":
    # Disabled in notebook.
    # contruct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', type=str, required=True, help='username')
    ap.add_argument('-p', '--proj', type=str, required=True, help='project')
    ap.add_argument('-d', '--dfile', type=str, required=True, help='datafile')
    args = vars(ap.parse_args())
    print(f'input arguments: {args}')
    args_user = args['user']
    args_proj = args['proj']
    args_dfile = args['dfile']
    print(f'input user: {args_user}')
    print(f'input proj: {args_proj}')
    print(f'input datafile: {args_dfile}')

    # invoke class
    projectsDetails = GetModelDetailsForUser(args_user, args_proj, args_dfile )
    projectsDetails.getModelDetails()
    print("DONE")
