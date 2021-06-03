# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 15:59:02 2021

# file contains the definition of the application and its views


set below variable in command prompt before running this script
export/set FLASK_APP=app.py # main script for app
export/set FLASK_DEBUG=1    # debug mode
flask run                   # run with flask command

"""
# https://hackersandslackers.com/flask-jinja-templates/
# https://jinja.palletsprojects.com/en/2.11.x/templates/
# https://stackabuse.com/flask-form-validation-with-flask-wtf/


# imports
from IPython.core.display import JSON
import pandas as pd
import json
from io import StringIO
from flask import Flask, render_template, url_for, request,redirect,session

from templates import *
# from scripts import uploadFile
from scripts.uploadFile import UploadFile
from scripts.getProjectDetailsForUser import GetProjectDetailsForUser
from scripts.getModelDetailsForUser import GetModelDetailsForUser
from scripts.trainModel import trainModel_classification

# create flask instance taking __name__ of the script
app = Flask(__name__)
app.secret_key = 'secretkey'

# home page
# also to process initial project choice
@app.route('/')
@app.route('/home')
@app.route('/home', methods=['GET', 'POST'])
def home():
    """Home page"""
    print('inside home')
    # check if form submit request
    if request.method == 'POST':
        print('got POST request')
        fileParams = request.form.to_dict()
        userName = fileParams['userName']
        userChoice = fileParams['choice']
        # print(fileParams)
        # store userName in session
        session['userName'] = userName
        if userChoice == 'newProject':
            print('user want to create new project')
            # return 'user want to create new project'
            return redirect(url_for('projectCreate'))
        if userChoice == 'viewProject':
            print('user want to view existing project')
            # return 'user want to view existing project'
            return redirect(url_for('projectsAll'))
    # check if redirect to homepage
    fromPage = request.args.get('fromPage')
    sts = request.args.get('msg')
    if fromPage=='projectCreate':
        print('redirect from projectCreate page')
        # open homepage with status message
        return render_template('home.html', msg=sts, title='Home', description='Home')

    # default initial home page
    # remove all session variable
    session.pop('userName', None)
    session.pop('thisProject', None)
    return render_template('home.html', title='Home', description='Home')


# projectCreate page
@app.route('/projectCreate')
@app.route('/projectCreate', methods=['GET', 'POST'])
def projectCreate():
    print(f'inside project create')
    # get username from session
    if not session.get("userName"):
        print('userName not found in session. ')
        return redirect(url_for('home'))
    userName = session['userName']

    # check if form submit request
    if request.method == 'POST':
        fileParams = request.form.to_dict()
        print(fileParams)
        # print(fileParams['userName'])
        # print(fileParams['projectName'])
        # print(fileParams['fileName'])
        userName = fileParams['userName']
        projectName = fileParams['projectName']
        fileName = fileParams['fileName']

        # upload input file
        uploadStatus = 'ERROR'
        UploadFileObj = UploadFile(fileParams['userName'], fileParams['projectName'], fileParams['fileName'] )
        uploadStatus = UploadFileObj.run()
        # uploadStatus=0
        print(f'Return value from uploadfile: {uploadStatus}')
        if uploadStatus==0:
            sts = "Project created successfully"
        else:
            sts = f'Project creation failed with error {uploadStatus}. Click on New Project to try again'
        return redirect(url_for('home', fromPage='projectCreate', msg=sts))

    # default initial project page
    return render_template('projectCreate.html', user=userName,
                           title='New Project', description='Create new project')


@app.route('/projectsAll')
@app.route('/projectsAll', methods=['GET', 'POST'])
def projectsAll():
    print('inside projectsAll')
    # get username from session
    if not session.get("userName"):
        print('userName not found in session. ')
        return redirect(url_for('home'))
    userName = session['userName']

    # check if form submit request
    if request.method == 'POST':
        print('got POST request')
        fileParams = request.form.to_dict()
        thisProject = fileParams['thisProject']
        # thisProject is dict e.g.:
        # {'projectName': 'Program Choice', 'createdOn': 20210321180903, 'datafileName': 'Program_Choice.csv'}
        print(f'thisProject: {thisProject}')
        # store thisProject in session
        session['thisProject'] = thisProject
        # return redirect(url_for('projectView', thisproject=thisProject ))
        return redirect(url_for('projectView' ))

    print(f'user: {userName}')
    # fetch project details for user
    ProjectDetailsObj = GetProjectDetailsForUser(userName, 'NA', 'NA')
    userProjectAll = ProjectDetailsObj.getAllProjectDetails2()
    # userProjectAll = ['project1', 'project2']
    print(f'user project details: {userProjectAll}')
    # remove session variable
    session.pop('thisProject', None)

    return render_template('projectsAll.html', projects=userProjectAll, title='All Projects', description='All Projects View')


# @app.route('/projectView/<thisproject>')
@app.route('/projectsAll/project')
@app.route('/projectsAll/project', methods=['GET', 'POST'])
def projectView():
    print('inside projectView')
    # get username from session
    if not session.get("userName"):
        print('userName not found in session. ')
        return redirect(url_for('home'))
    userName = session['userName']
    if not session.get("thisProject"):
        print('thisProject not found in session. ')
        return redirect(url_for('projectsAll'))
    thisProject = eval(session['thisProject'])
    #{'projectName': 'Program Choice', 'createdOn': 20210321180903, 'datafileName': 'Program_Choice.csv'}
    print(f'fetch details for {userName}/{thisProject["projectName"]}')

    # check if form submit request
    if request.method == 'POST':
        print('got POST request')
        fileParams = request.form.to_dict()
        action = fileParams['action']
        if action=='viewDatafile':
            print('user want to view datafile')
            return redirect(url_for('projectDatafileView'))
        elif action=='EDA':
            print('user want to run EDA')
            return redirect(url_for('projectEDA'))
        elif action=='trainNewModel':
            print('user want to train new model')
            return redirect(url_for('projectTrainModel'))
        else:
            print(f'user want to view trained model {action}')
            return redirect(url_for('projectModelDetails', modeljson = action))
         
    ModelDetailsObj = GetModelDetailsForUser(userName,thisProject["projectName"],'NA')
    userModelAll = ModelDetailsObj.getModelDetails()
    print(f'user Model details: {userModelAll}')
    # remove session variable
    # session.pop('thisProject', None)
    return render_template('projectDetails.html', proj=thisProject, models = userModelAll
                           , title=thisProject["projectName"], description=thisProject["projectName"] )


# @app.route('/projectView/project/datafile')
@app.route('/projectsAll/project/datafile')
def projectDatafileView():
    print('inside projectDatafileView')
    # get username from session
    if not session.get("userName"):
        print('userName not found in session. ')
        return redirect(url_for('home'))
    userName = session['userName']
    if not session.get("thisProject"):
        print('thisProject not found in session. ')
        return redirect(url_for('projectsAll'))
    thisProject = eval(session['thisProject'])
    # fetch project datafile
    ProjectDetailsObj = GetProjectDetailsForUser(userName, thisProject["projectName"], thisProject["datafileName"])
    projectDatafile = pd.read_csv(StringIO(ProjectDetailsObj.getProjectDataFile()))
    # thisproject['datafile'] = projectDatafile.to_html(classes='data')
    # thisproject['datafileCol'] = projectDatafile.columns.values
    return render_template('projectDatafile.html', title=thisProject["projectName"], description=thisProject["projectName"],
                           tables=list(projectDatafile.values.tolist()), titles=projectDatafile.columns.values, link_column="id",zip=zip,
                           proj = thisProject)


@app.route('/projectsAll/project/EDA')
def projectEDA():
    print('inside projectEDA')
    # get thisProject from session
    if not session.get("thisProject"):
        print('thisProject not found in session. ')
        return redirect(url_for('projectsAll'))
    thisProject = eval(session['thisProject'])
    return render_template('projectEDA.html', proj=thisProject
                           , title=thisProject["projectName"], description=thisProject["projectName"] )


@app.route('/projectsAll/project/trainModel')
@app.route('/projectsAll/project/trainModel', methods=['POST'])
def projectTrainModel():
    print('inside projectTrainModel')
    # get thisProject from session
    # get username from session
    if not session.get("userName"):
        print('userName not found in session.')
        return redirect(url_for('home'))
    userName = session['userName']
    if not session.get("thisProject"):
        print('thisProject not found in session. ')
        return redirect(url_for('projectsAll'))
    thisProject = eval(session['thisProject'])
    # EDA script/page
    ProjectDetailsObj = GetProjectDetailsForUser(userName, thisProject["projectName"], thisProject["datafileName"])
    projectDatafile = pd.read_csv(StringIO(ProjectDetailsObj.getProjectDataFile()))
    data=projectDatafile.columns.tolist()
    print(data)
    # check if form submit request
    if request.method == 'POST':
        print('got POST request from project train model')
        fileParams = request.form.to_dict()
        print("file parameter",fileParams)
        jsonForModelTrain = json.dumps(fileParams, indent = 4)  
        # print(jsonForModelTrain)
        print(f'user want to train model with parameter {jsonForModelTrain}')
        return redirect(url_for('trainedModelDetails', modeljson = jsonForModelTrain, projectData = projectDatafile))
    return render_template('integrate.html', proj=thisProject, data=data, len = len(data)
                           , title=thisProject["projectName"], description=thisProject["projectName"] )


@app.route('/projectsAll/project/trainedModelDetail')
def trainedModelDetails():
    print('inside trainedModelDetails')
    global modeljson
    modeljson = request.args['modeljson']
    print(modeljson)
    projectData = request.args['projectData']
    print(projectData)
    # get username from session
    if not session.get("userName"):
        print('userName not found in session. ')
        return redirect(url_for('home'))
    userName = session['userName']
    if not session.get("thisProject"):
        print('thisProject not found in session. ')
        return redirect(url_for('projectsAll'))
    thisProject = eval(session['thisProject'])
    trainModelDetails = trainModel_classification(userName, thisProject["projectName"],modeljson,thisProject["datafileName"])
    userModelAll = trainModelDetails.modelTrain_Classification()
    print(f'user Model details: {userModelAll}')
    return render_template('trainedModelDetail.html', proj=thisProject, models = userModelAll,
                            tables=list(userModelAll.values.tolist()), titles=userModelAll.columns.values, link_column="id",zip=zip,
                            title=thisProject["projectName"], description=thisProject["projectName"] )


@app.route('/projectsAll/project/modelDetail')
def projectModelDetails():
    print('inside projectModelDetails')
    modeljson = request.args['modeljson']
    print(modeljson)
    # get username from session
    if not session.get("userName"):
        print('userName not found in session. ')
        return redirect(url_for('home'))
    userName = session['userName']
    if not session.get("thisProject"):
        print('thisProject not found in session. ')
        return redirect(url_for('projectsAll'))
    thisProject = eval(session['thisProject'])
    modeljson = modeljson.replace("\'", "\"")
    print("type of modeljson ",type(modeljson))
    modelDetails = json.loads(modeljson)
    # key = modelDetails['model_file']+"_"+modelDetails['model_type']+"_"+modelDetails['uploadedon']
    # print("key of the predictmodel",key)
    modelResult = trainModel_classification.downloadImage(userName,thisProject["projectName"])
    print("function complete save model",modelResult)
    return render_template('projectModelDetail.html', model = modelDetails)


@app.route('/projectsAll/project/trainedModelDetail/saveModel')
@app.route('/projectsAll/project/trainedModelDetail/saveModel', methods=['GET', 'POST'])
def saveTrainedModelDetails():
    print('inside saveTrainedModelDetails')
    # get username from session
    if not session.get("userName"):
        print('userName not found in session.')
        return redirect(url_for('home'))
    userName = session['userName']
    if not session.get("thisProject"):
        print('thisProject not found in session. ')
        return redirect(url_for('projectsAll'))
    thisProject = eval(session['thisProject'])
    saveModel = trainModel_classification.saveTrainedModel(modeljson,userName,thisProject["projectName"])
    print("function complete save model",saveModel)
    return render_template('saveModelDetail.html', model = saveModel )


@app.route('/projectsAll/project/trainModel/predictModel')
@app.route('/projectsAll/project/trainModel/predictModel', methods=['POST'])
def predictModel():
    if not session.get("userName"):
        print('userName not found in session.')
        return redirect(url_for('home'))
    userName = session['userName']
    if request.method == 'POST':
        print('got POST request from project train model')
        fileParams = request.form.to_dict()
        print("file parameter",fileParams)
        jsonForModelPredict = json.dumps(fileParams, indent = 4)  
        # print(jsonForModelTrain)
        print(f'user want to redict model with parameter {jsonForModelPredict}')
        predictedModel = trainModel_classification.predictOnTrainedModel(jsonForModelPredict)
        print("type od predicted Model",type(predictedModel))
        print("function complete predict model",predictedModel)
        return render_template('predictedDataDetail.html',model = predictedModel,tables=list(predictedModel.values.tolist()), 
                                titles=predictedModel.columns.values, link_column="id",zip=zip)
        # redirect(url_for('predictedModelDetails', model = predictedModel))
    return render_template('predictModelDetail.html')


# about page
@app.route('/about')
def about():
    return render_template('about.html', title='About', description='About')

# -----------------------
# run script from python directly
if __name__ == '__main__':
    app.run(debug=True)