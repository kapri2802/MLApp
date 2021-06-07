
# import library
from warnings import catch_warnings
from numpy.lib.npyio import save
import pandas as pd
from pycaret.classification import *
import os, json, argparse
from scripts.getProjectDetailsForUser import GetProjectDetailsForUser
from io import StringIO
from datetime import datetime
import imblearn
import boto3
from boto3.s3.transfer import S3Transfer
from boto3 import client

class trainModel_classification():

    def __init__(self, user: str, projName:str, fileParameter:str, dataFileName:str):
        print('inside trainModel_classification init')
        self.user = user
        self.proj = projName
        self.fileParameter = fileParameter
        self.dataFileName = dataFileName

        C = json.loads(fileParameter)
        print("type after json",type(C))
        print(C)
        #Reading csv file in dataframe
        ProjectDetailsObj = GetProjectDetailsForUser(self.user, self.proj, self.dataFileName)
        self.df = pd.read_csv(StringIO(ProjectDetailsObj.getProjectDataFile()))
        print("After reading from another function")        
        print(self.df.columns.tolist())

        #Reading values from dictionary
        self.target_column =  C['target']
        print("target_column: ", self.target_column)
        self.training_size = C['train_size']
        self.model_type = C['model']
        self.category_imputation = C['categorical_imputation']
        self.numerical_imputation = C['numeric_imputation']
        self.normalization_method = C['normalize_method']
        self.outliers_value = C['outliers_threshold']
        self.multicollinearity_value = C['multicollinearity_threshold']
        #setting up default values for parameters
        #for categorical values
        # if(self.category_imputation == "None"):
        #     self.category_features = "None"
        #     self.category_imputation = "constant"
        # else :
        #     self.category_features = C['categorical_features']

        # #for numerical values
        # if(self.numerical_imputation == "None"):
        #     self.numerical_features = "None"
        #     self.numerical_imputation = "mean"
        # else :
        #     self.numerical_features = C['numeric_features']

        #for normalization
        if(self.normalization_method == "None"):
            self.normalization_type = "False"
            self.normalization_method = "zscore"
        else :
            self.normalization_type = "True"
            self.normalization_method = C['normalize_method']

        #for Outliers
        if(self.outliers_value == "None"):
            self.outliers_type = "False"
            self.outliers_value = "0.05"
        else :
            self.outliers_type = "True"
            self.outliers_value = C['outliers_threshold']

        #for multicollinearity
        if(self.multicollinearity_value == "None"):
            self.multicollinearity_type = "False"
            self.multicollinearity_value = 0.9
        else :
            self.multicollinearity_type = "True"
            self.multicollinearity_value = C['multicollinearity_threshold']
        
        self.sort_model = C['sort_model']
        print("target_column: ", self.target_column)
        print("training_size:" , self.training_size )

    # function to set values for model training
    def modelTrain_Classification(self):
        #setting up data for the model
        # if self.category_imputation == 'None':
        #     print("1st if Categorical is none")
        #     clf=setup(data=self.df,target=self.target_column,train_size = float(self.training_size),silent=True, 
        #     numeric_features= [self.numerical_features], numeric_imputation= self.numerical_imputation, normalize= bool(self.normalization_type),
        #     normalize_method = self.normalization_method, remove_outliers= bool(self.outliers_type), 
        #     outliers_threshold = float(self.outliers_value), remove_multicollinearity = bool(self.multicollinearity_type), multicollinearity_threshold = float(self.multicollinearity_value))
        # elif self.numerical_imputation == 'None':
        #     print("2nd if numerical is none")
        #     clf=setup(data=self.df,target=self.target_column,train_size = float(self.training_size),silent=True,
        #     categorical_features= [self.category_features],categorical_imputation= self.category_imputation,
        #     normalize= bool(self.normalization_type), normalize_method = self.normalization_method, remove_outliers= bool(self.outliers_type), outliers_threshold = float(self.outliers_value), 
        #     remove_multicollinearity = bool(self.multicollinearity_type), multicollinearity_threshold = float(self.multicollinearity_value))
        # elif self.category_imputation == 'None' and self.numerical_imputation == 'None':
        #     print("3rd if Both are none")
        #     clf=setup(data=self.df,target=self.target_column,train_size = float(self.training_size),silent=True,
        #     normalize= bool(self.normalization_type), normalize_method = self.normalization_method,
        #     remove_outliers= bool(self.outliers_type), outliers_threshold = float(self.outliers_value), 
        #     remove_multicollinearity = bool(self.multicollinearity_type), multicollinearity_threshold = float(self.multicollinearity_value))
        # else:
        print("Automatically choosing")
        clf=setup(data=self.df,target=self.target_column,train_size = float(self.training_size),silent=True,
        categorical_imputation= self.category_imputation,numeric_imputation= self.numerical_imputation,
        normalize= bool(self.normalization_type), normalize_method = self.normalization_method,
        remove_outliers= bool(self.outliers_type), outliers_threshold = float(self.outliers_value), 
        remove_multicollinearity = bool(self.multicollinearity_type), multicollinearity_threshold = float(self.multicollinearity_value)
        ,fix_imbalance=True,fix_imbalance_method=imblearn.over_sampling.BorderlineSMOTE())
        
        if self.model_type == 'None':
            modelTrained = compare_models(sort = self.sort_model)
        else:
            modelTrained = create_model(self.model_type)

        global modelFinal
        modelFinal = finalize_model(modelTrained)
        print(type(modelFinal))
        global best_model_results
        best_model_results = pull(modelFinal)
        print(type(best_model_results))
        # save_model(modelFinal, 'lr_26052021')
        # best = tune_model(modelTrained, n_iter=200, choose_better=True)
        # report the best model
        # print(best)
        try:
            plot_model(modelFinal, save= True)
            plot_model(modelFinal, save= True,plot = 'confusion_matrix')
            os.replace("AUC.png", "static\AUC.png")
            os.replace("Confusion Matrix.png", "static\Confusion Matrix.png")
        except:
            print("There is no AUC")
            return "There is no AUC Plot in this Model"
        return best_model_results[:1]

    # function to save model
    def saveTrainedModel(fileParameter, userName, projectName):
        C = json.loads(fileParameter)
        print("Inside getProjectDeatilsForUser -- saveTrainedModel")
        print("best fit models",best_model_results[:1])
        bestFitModel = pd.DataFrame(best_model_results[:1])
        model_type = bestFitModel['Model']
        # print("Automatic selected model name",model_type.str.split(" ")[0])
        # print("type of model",type(model_type))
        now = datetime.now()
        currentDateTime = now.strftime("%m%d%Y%H%M%S")
        print("date and time ", currentDateTime)
        userModelName = C['modelName']
        print("Model type ",model_type.str.replace(" ", "_")[0])
        modelType = model_type.str.replace(" ", "_")[0]
        global saveModelName
        saveModelName = userModelName +"_"+ modelType +"_"+ currentDateTime
        print("Model Name in S3",saveModelName)
        save_model(modelFinal, saveModelName)
        #file property
        # dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        propertydictionary ={
                            "uploadedon": currentDateTime ,
                            "model_file": userModelName,
                            "model_type": model_type.str.replace(" ", "_")[0],
                            "target_column": C['target'],
                            "training_size": C['train_size'],
                            "sort_model": C['sort_model'],
                            "category_imputation": C['categorical_imputation'],
                            "numerical_imputation": C['numeric_imputation'],
                            "normalization_method": C['normalize_method'],
                            "outliers_value": C['outliers_threshold'],
                            "multicollinearity_value": C['multicollinearity_threshold']
                            }
                        
        # Serializing json  
        with open(saveModelName+".json", 'w') as fp:
            json.dump(propertydictionary, fp)
        S3Conf = json.load(open('config.json'))
        print(S3Conf)

        # initialize s3 client
        client = boto3.client('s3', aws_access_key_id=S3Conf['AWS_ACCESS_KEY'], aws_secret_access_key=S3Conf['AWS_ACCESS_SECRET_KEY'])
        transfer = S3Transfer(client)
        transfer.upload_file(saveModelName+".pkl", S3Conf['PROJECT_BUCKET'],
                                 userName + "/" + projectName + "/" + "model" + "/" + saveModelName +"/"+ saveModelName +".pkl" )
        transfer.upload_file(saveModelName+".json", S3Conf['PROJECT_BUCKET'],
                                 userName + "/" + projectName + "/" + "model" + "/" + saveModelName +"/"+ saveModelName +".json" )
        transfer.upload_file("static/AUC"+".png", S3Conf['PROJECT_BUCKET'],
                                 userName + "/" + projectName + "/" + "model" + "/" + saveModelName +"/"+ saveModelName +".png" )
        
        return saveModelName
        

if __name__ == "__main__":
    
    # contruct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', type=str, required=True, help='username')
    ap.add_argument('-p', '--projName', type=str, required=True, help='project')
    ap.add_argument('-f', '--fileParameter', type=str, help='parameter of the file to train')
    ap.add_argument('-d', '--dataFileName', help='name of CSV file of data')
    args = vars(ap.parse_args())
    print(f'input arguments: {args}')
    args_user = args['user']
    args_projName = args['projName']
    args_fileParameter = args['fileParameter']
    args_dataFileName = args['dataFileName']
    print(f'input user: {args_user}')
    print(f'input proj: {args_projName}')
    print(f'input fileparameter: {args_fileParameter}')
    print(f'input datafile: {args_dataFileName}')

    # invoke class
    projectsDetails = trainModel_classification(args_user, args_projName, args_dataFileName , args_fileParameter)
    projectsDetails.modelTrain_Classification()
    print("DONE")
