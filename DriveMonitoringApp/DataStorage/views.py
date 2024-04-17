from django.shortcuts import render
from django.http import HttpResponse
import pymongo
from django.conf import settings
from django.http import JsonResponse
import json
from bson.json_util import dumps, loads
from mongo_utils import MongoDb
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import gridspec
import pytz
import pandas as pd

from . import figuresFunctions

import plotly.graph_objects as go
from django.contrib.staticfiles import finders

database = MongoDb

def index(request):
    return database.getData(database)
#Function thata stores the Logs into MongoDB
@csrf_exempt
def storeLogs(request):
    if(request.method == 'POST'):
        userdict = json.loads(str(request.body,encoding='utf-8'))
        dictNewValues = []
        #print(userdict)
        correct = True
        for item in userdict:
            if database.checkDuplicatedLogs(database, item["Time"], item["Command"], item["Date"]) == False:
                dictNewValues.append(item)
        #print(dictNewValues)
        if len(dictNewValues) > 0:
            correct = database.storeLogs(database, dictNewValues)
        else:
            return JsonResponse({"Message": "There was no new Logs data to store."})
        if correct:
            return JsonResponse({"Message": "The data has been stored successfully."})
        else:
            return JsonResponse({"Message": "The data was not totally inserted due to duplicity or an error."})
#Function that stores the general data into MongoDB
@csrf_exempt
def storeData(request):
    #TODO - Needs optimization as it takes a LOT of time to store all the data
    if(request.method == 'POST'):
        body = json.loads(str(request.body,encoding='utf-8'))
        generalData = {}
        generalData["type"] = body[0]["type"][0]
        generalData["Sdate"] = body[0]["Sdate"][0]
        generalData["Stime"] = body[0]["Stime"][0]
        generalData["Edate"] = body[0]["Edate"][0]
        generalData["Etime"] = body[0]["Etime"][0]
        generalData["RA"] = body[0]["RA"][0]
        generalData["DEC"] = body[0]["DEC"][0]
        imagePattern = body[0]["file"][0].split("/")
        imageSpltiEnd = imagePattern[-1].split(".")
        finalImage = imagePattern[-4]+"/"+imagePattern[-3]+"/"+imagePattern[-2]+"/"+imageSpltiEnd[0]
        generalData["file"] = finalImage
        generalData["addText"] = body[0]["addText"][0]
        #TODO - Store the rest of the data
        if len(body[0]["position"]) != 0:
            position = json.loads(body[0]["position"][0])
            database.storePosition(database, position)
        if len(body[0]["loadPin"]) != 0:
            pinData = json.loads(body[0]["loadPin"][0])
            database.storeLoadPin(database, pinData)
        if len(body[0]["track"]) != 0:
            track = json.loads(body[0]["track"][0])
            database.storeTrack(database, track)
        if len(body[0]["torque"]) != 0:
            torque = json.loads(body[0]["torque"][0])
            database.storeTorque(database, torque)
        if len(body[0]["accuracy"]) != 0:
            accuracy = json.loads(body[0]["accuracy"][0])
            database.storeAccuracy(database, accuracy)
        if len(body[0]["bendModel"]) != 0:
            bendModel = json.loads(body[0]["bendModel"][0])
            database.storeBendModel(database, bendModel)
        correct = True
        if database.checkDuplicatedValues(database, generalData["type"], generalData["Sdate"], generalData["Stime"]) == False:
            correct = database.storeGeneralData(database, generalData)
        else:
            return JsonResponse({"Message": "There was no new General data to store."})
        if correct:
            return JsonResponse({"Message": "The data has been stored successfully."})
        else:
            return JsonResponse({"Message": "The data was not totally inserted due to duplicity or an error."})
#TEST
def update(request):
    return database.updateData(database)
#TEST
def delete(request):
    return database.deleteData(database)
#TEST
def start(request):
    return database.__init__(database)
#Function that returns the data and render the home view or throws an Json response with an error message
def home(request):
    if database.isData(database) == True:
        latestTime = database.getLatestDate(database)
        data = [latestTime, database.getData(database)]
        return render(request, "storage/index.html", {"data" : data})
    else:
        return JsonResponse({"Message": "There is no data to show"})

#Function that returns the Logs from the database in case there are.
def getLogs(request):
    if request.method == "GET":
        if database.isData(database) == True:
            data = {"data": database.listLogs(database, database.getLatestDate(database)), "filters": database.getFilters(database)}
            return JsonResponse(data)
        else:
            return JsonResponse({"Message": "There is no data to show"})
#Function that returns the data from the database in case there is.
def getData(request):
    if request.method == "GET":
        if database.isData(database) == True:
            data = {"data": database.listData(database, database.getLatestDate(database))}
            return JsonResponse(data)
        else:
            return JsonResponse({"Message": "There is no data to show"})
        
#Function that generates all the plots. TESTING FUNCTION
def generatePlots(date):
        operation = database.getOperation(database,date)
        data = database.getDatedData(database, operation[0]["Tmin"], operation[0]["Tmax"])
        for element in data:
            stringTime = element["Sdate"]+" "+element["Stime"]
            tmin = datetime.strptime(stringTime, '%Y-%m-%d %H:%M:%S').timestamp()
            stringTime = element["Edate"]+" "+element["Etime"]
            tmax = datetime.strptime(stringTime, '%Y-%m-%d %H:%M:%S').timestamp()
            #operation = database.getOperationTime(database)
            #print("Esta es la operacion")
            #print(operation)
            #tmin = operation[0]["Tmin"]
            #tmax = operation[0]["Tmax"] 
            #cmd_status = 0
            position = database.getPosition(database, tmin, tmax)
            loadPin = database.getLoadPin(database, tmin, tmax)
            track = database.getTrack(database, tmin, tmax)
            torque = database.getTorque(database, tmin, tmax)
            accuracy = database.getAccuracy(database, tmin, tmax)
            bendModel = database.getBM(database, tmin, tmax)
            dfpos = pd.DataFrame.from_dict(position) #Time format is slightly different. Check if that is important 00:00:00+00:00 Original format
            dfloadpin = pd.DataFrame.from_dict(loadPin) 
            dftrack = pd.DataFrame.from_dict(track) 
            dftorque = pd.DataFrame.from_dict(torque) 
            dfbm = pd.DataFrame.from_dict(bendModel) 
            dfacc = pd.DataFrame.from_dict(accuracy)
            file = element["file"].split("/")
            filename = file[3]
            file = finders.find(file[0]+"/"+file[1]+"/"+file[2])
            figuresFunctions.FigureTrack(dfpos, dfloadpin, dftrack, dftorque, file+"/"+filename+".html")
        

        #figuresFunctions.FigureTrack(tmin, tmax, cmd_status, firstElement["addText"], dfpos, dfloadpin, dftrack, dftorque)
        if dfbm is not None:
            print("There is DFBM")
            #figuresFunctions.FigureRADec(dfpos, dfbm, firstElement["RA"], firstElement["DEC"], dfacc, dftrack)
        if dfacc is not None:
            print("There is DFACC")
            #figuresFunctions.FigAccuracyTime(firstElement["addText"], dfacc)
        
        #FigureTrack()

def showTestView(request):
    if request.method == "GET":
        generatePlots("2024-02-01")
        return render(request, "storage/testPLot.html")