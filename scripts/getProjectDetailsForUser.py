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
import json, argparse
import boto3
from boto3.s3.transfer import S3Transfer

# import common parameters
CONFIG_FILE = 'config.json'
C = json.load(open(CONFIG_FILE))

class GetProjectDetailsForUser():
    def __init__(self, user:str, proj:str, dfile:str):
        print('inside init')
        self.user = user
        self.proj = proj
        self.dfile = dfile
        # initialize s3 client
        self.s3client = boto3.client('s3', aws_access_key_id=C['AWS_ACCESS_KEY'],
                                     aws_secret_access_key=C['AWS_ACCESS_SECRET_KEY'])

    # function to get folder names inside user
    def getAllProjectDetails(self):
        print(f'fetching project details for user: {self.user}')
        # append / end of user
        self.user = self.user if self.user.endswith('/') else self.user + '/'
        projects = []
        paginator = self.s3client.get_paginator('list_objects')
        page_iterator = paginator.paginate(Bucket=C['PROJECT_BUCKET'], Prefix=self.user, Delimiter='/',
                                           PaginationConfig={'PageSize': None})
        for page in page_iterator:
            prefixes = page.get('CommonPrefixes', [])
            # check if any sub-folders
            if len(prefixes) > 0:
                for prefix in prefixes:
                    pr = prefix['Prefix']
                    pr = pr.rstrip('/') if pr.endswith('/') else pr
                    projects.append(pr.split('/')[1])
        print(f'project details: {projects}')
        return projects

    # function to read user/project.json
    def getAllProjectDetails2(self):
        print(f'fetching {self.user}/projects.json')
        projects = []
        result = self.s3client.get_object(Bucket=C['PROJECT_BUCKET'], Key=f'{self.user}/projects.json')
        file = json.loads(result['Body'].read().decode())
        # remove index and convert to list
        projects = []
        [projects.append(file[k]) for k in file.keys()]
        print(f'project details: {projects}')
        return projects

    # function to get project datafile
    # will return file as a string
    def getProjectDataFile(self):
        print('inside getProjectDataFile')
        result = self.s3client.get_object(Bucket=C['PROJECT_BUCKET'], Key=f'{self.user}/{self.proj}/{self.dfile}')
        # result = self.s3client.get_object(Bucket=C['PROJECT_BUCKET'], Key="manish/heart/US_Heart_Patients.csv"){self.dfile}
        file = result['Body'].read().decode('utf-8')
        return file


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
    projectsDetails = GetProjectDetailsForUser(args_user, args_proj, args_dfile)
    projectsDetails.getAllProjectDetails()
    print("DONE")
