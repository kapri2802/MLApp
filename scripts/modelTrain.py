# -*- coding: utf-8 -*-
# ------------------------------------------
#
# script to train model
# INPUT: dict
# fileName = s3bucket name, filename
# targetCol
# testSize = 0.3
# modelType
# modelParam
# perfMetric


import numpy as np
import pandas as pd
import os, argparse
import sklearn
from sklearn import metrics
from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,roc_curve,classification_report,confusion_matrix,plot_confusion_matrix


# contruct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument('--folderName', type=str, help='S3 bucket Name')
ap.add_argument('--fileName', type=str, help='name of the file to read')
ap.add_argument('--targetCol', type=str, help='name of the target column')
ap.add_argument('--testSize', type=str, default=0.3, help='test size in pct')
ap.add_argument('--modelType', type=str, default='logistic', help='type of ML model to train')
ap.add_argument('--perfMetric', type=str, default='accuracy', help='performance metric measure')
args = vars(ap.parse_args())

args_folderName = args['folderName']
args_fileName = args["fileName"]
args_targetCol = args['targetCol']
args_testSize = args['testSize']
args_modelType = args['modelType']
args_perfMetric = args['perfMetric']

# echo ipput values
print(f'input folderName: {args_folderName}')
print(f'input file name: {args_fileName}')
print(f'input targetCol: {args_targetCol}')
print(f'input test size: {args_testSize}')
print(f'input model type: {args_modelType}')
print(f'input perf metric: {args_perfMetric}')

# initialize random-state
rs = np.random.randint(100)



# STEP1: read file file from s3 bucket
# read from s3 bucket
# read in df

# STEP2: get indept and dept col names
Ycol = args_targetCol
Xcol = all cols from df except args_targetCol

X = df.drop(args_targetCol, axis=1)
Y = df[args_targetCol]

# STEP3: train/test split dataset
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=args_testSize, random_state=rs)


# STEP4: model training
if args_modelType == 'logistic':
    model = LogisticRegression()
    model.fit(X_train, Y_train)


# STEP5: model eval
# check perf of train dataset
Y_train_pred = model.predict(X_train)
print(confusion_matrix(Y_train,Y_train_pred))
print(model.score(X_train, Y_train))
print(classification_report(Y_train, Y_train_pred))

# check perf of test dataset
Y_test_pred = model.predict(X_test)
print(confusion_matrix(Y_test,Y_test_pred))
print(model.score(X_test, Y_test))
print(classification_report(Y_test, Y_test_pred))

