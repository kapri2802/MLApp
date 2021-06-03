# -*- coding: utf-8 -*-
"""
Created on 17-Mar-2021

@author: yadav

set below variable in command prompt before running this script
export/set FLASK_APP=app.py # main script for app
export/set FLASK_DEBUG=1    # debug mode
flask run                   # run with flask command

https://hackersandslackers.com/flask-jinja-templates/

"""

# imports
import numpy as np
import pandas as pd
import os
from flask import Flask, render_template, url_for, request
# from scripts/uploadFile.py import *
# from resources import confi
from templates import *


# create flask instance taking __name__ of the script
app = Flask(__name__)

# env variable
#APP_HOME = './app' # from jupiter
APP_HOME = './'  # for script


# home page
@app.route('/')
@app.route('/home')
def home():
    #return "<h1>Hello World from HomePage!</h1>"
    return render_template('home.html', title='Home Page')

# fileUpload page
@app.route('/fileUpload', methods=['POST'])
def fileUpload():
    #return "<h1>Thanks for uploading file</h1>"
    fileParams = request.form.to_dict()
    print(fileParams)
    print(fileParams['userName'])
    print(fileParams['datasetName'])
    print(fileParams['fileName'])
    # call script
    # input datasetname, datafolder, datafile
    # uploadStatus = uploadFile.py fileParams

    uploadStatus = 'UPLOADED'
    if uploadStatus=='UPLOADED':
        return "<h1>Thanks for uploading file. Click on Model Training</h1>"
    else:
        return "<h1>Some error. Please try again</h1>"

# about page
@app.route('/about')
def about():
    return "<h1>About Page!</h1>"
    # return render_template('about.html', title='About')


# -----------------------
# run script from python directly

if __name__ == '__main__':
    app.run(debug=True)


#
# # setup input arguments. These will be used when calling as a script.
# # Disabled in notebook.
#
# # contruct the argument parser and parse the arguments
# import argparse
# ap = argparse.ArgumentParser()
# ap.add_argument('-u', '--user', type=str, help='username')
# ap.add_argument('-d', '--datasetName', type=str, help='name of the dataset')
# ap.add_argument('-f', '--fileName', type=str, help='name of the file to upload')
# args = vars(ap.parse_args())
# args_user = args['user']
# args_datasetName = args['datasetName']
# args_fileName = args["fileName"]
#
