# import library
import pandas as pd
from pycaret.classification import *
import os, json, argparse
from scripts.getProjectDetailsForUser import GetProjectDetailsForUser
# from io import StringIO
# from datetime import datetime
# import imblearn
import boto3
from boto3.s3.transfer import S3Transfer
from boto3 import client
CONFIG_FILE = 'config.json'
C = json.load(open(CONFIG_FILE))


class predictModelData():

    def __init__(self, user: str, projName:str, key:str, dfile:str):
        print('inside predictModel init')
        self.user = user
        self.proj = projName
        self.key = key
        self.data = dfile
        # initialize s3 client
        self.s3client = boto3.client('s3', aws_access_key_id=C['AWS_ACCESS_KEY'], aws_secret_access_key=C['AWS_ACCESS_SECRET_KEY'])
        self.s3transfer = S3Transfer(self.s3client)
    
    def predictOnTrainedModel(self):
        print("Inside PredictonTrainedModel")
        newData = json.loads(self.data)
        data_unseen = pd.read_csv(newData['unseenDataFile'])
        self.s3transfer.download_file(C['PROJECT_BUCKET'],self.user + "/" + self.proj + "/" + "model" + "/" + self.key +"/"+ self.key +".pkl","modelResult.pkl") 
        savedModel = load_model('modelResult')
        # generate predictions on unseen data
        predictions = predict_model(savedModel, data = data_unseen)
        return predictions

    
    def downloadImage(self):
        print("Inside DownloadImage")
        self.s3transfer.download_file(C['PROJECT_BUCKET'],self.user + "/" + self.proj + "/" + "model" + "/" + self.key +"/"+ self.key +".png","static\AUC.png")




if __name__ == "__main__":
    
    # contruct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', type=str, required=True, help='username')
    ap.add_argument('-p', '--projName', type=str, required=True, help='project')
    ap.add_argument('-k', '--key', type=str, help='Key of the file on S3')
    ap.add_argument('-d', '--dfile', type=str, help='unseen data filename')
    args = vars(ap.parse_args())
    print(f'input arguments: {args}')
    args_user = args['user']
    args_projName = args['projName']
    args_key = args['key']
    args_dfile = args['dfile']
    print(f'input user: {args_user}')
    print(f'input proj: {args_projName}')
    print(f'input key for S3: {args_key}')
    print(f'input unseen data: {args_dfile}')

    # invoke class
    projectsDetails = predictModelData(args_user, args_projName, args_key, args_dfile)
    projectsDetails.predictOnTrainedModel()
    print("DONE")
