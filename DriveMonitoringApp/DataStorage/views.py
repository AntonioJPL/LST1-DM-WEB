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

@csrf_exempt
#Function that returns the Logs from the database in case there are.
def getLogs(request):
    if request.method == "GET":
        if database.isData(database) == True:
            data = {"data": database.listLogs(database, database.getLatestDate(database)), "filters": database.getFilters(database)}
            return JsonResponse(data)
        else:
            return JsonResponse({"Message": "There is no data to show"})
    else:
        if request.method == "POST":
            if database.isData(database) == True:
                userdict = json.loads(str(request.body,encoding='utf-8'))
                data = {"data": database.listLogs(database, userdict["date"]), "filters": database.getFilters(database, userdict["date"])}
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
        generalTrack = {}
        generalTrack["dfpos"], generalTrack["dfloadpin"], generalTrack["dftrack"], generalTrack["dftorque"], generalTrack["dfacc"], generalTrack["dfbm"], generalTrack["name"], generalTrack["addText"], generalTrack["RA"], generalTrack["DEC"] = ([] for i in range(10))
        generalParkin = {}
        generalParkin["dfpos"], generalParkin["dfloadpin"], generalParkin["dftrack"], generalParkin["dftorque"], generalParkin["dfacc"], generalParkin["dfbm"], generalParkin["name"], generalParkin["addText"], generalParkin["RA"], generalParkin["DEC"] = ([] for i in range(10))
        generalParkout = {}
        generalParkout["dfpos"], generalParkout["dfloadpin"], generalParkout["dftrack"], generalParkout["dftorque"], generalParkout["dfacc"], generalParkout["dfbm"], generalParkout["name"], generalParkout["addText"], generalParkout["RA"], generalParkout["DEC"] = ([] for i in range(10))
        generalGotopos = {}
        generalGotopos["dfpos"], generalGotopos["dfloadpin"], generalGotopos["dftrack"], generalGotopos["dftorque"], generalGotopos["dfacc"], generalGotopos["dfbm"], generalGotopos["name"], generalGotopos["addText"], generalGotopos["RA"], generalGotopos["DEC"] = ([] for i in range(10))
        types = database.getOperationTypes(database)
        foundType = None
        for element in data:
            for type in types:
                if str(type["_id"]) == element["type"]:
                    foundType =  type["name"]
            
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
            dfpos = pd.DataFrame.from_dict(position)
            dfloadpin = pd.DataFrame.from_dict(loadPin) 
            dftrack = pd.DataFrame.from_dict(track) 
            dftorque = pd.DataFrame.from_dict(torque) 
            dfbm = pd.DataFrame.from_dict(bendModel) 
            dfacc = pd.DataFrame.from_dict(accuracy)
            file = element["file"].split("/")
            file = finders.find(file[0]+"/"+file[1]+"/"+file[2])
            if foundType == "Track":
                generalTrack["dfpos"].append(dfpos)
                generalTrack["dfloadpin"].append(dfloadpin)
                generalTrack["dftrack"].append(dftrack)
                generalTrack["dftorque"].append(dftorque)
                if dfacc is not None and dfacc.empty != True:
                    generalTrack["dfacc"].append(dfacc)
                if dfbm is not None and dfacc.empty != True:
                    generalTrack["dfbm"].append(dfbm)
                filename = "Track-"+str(datetime.fromtimestamp(operation[0]["Tmin"]).strftime("%Y-%m-%d"))+"-"+str(datetime.fromtimestamp(operation[0]["Tmax"]).strftime("%Y-%m-%d"))
                generalTrack["name"] = file+"/"+filename+".html"
                generalTrack["addText"] = element["addText"]
                generalTrack["RA"].append(element["RA"])
                generalTrack["DEC"].append(element["DEC"])
            if foundType == "Park-in":
                generalParkin["dfpos"].append(dfpos)
                generalParkin["dfloadpin"].append(dfloadpin)
                generalParkin["dftrack"].append(dftrack)
                generalParkin["dftorque"].append(dftorque)
                if dfacc is not None and dfacc.empty != True:
                    generalParkin["dfacc"].append(dfacc)
                if dfbm is not None and dfacc.empty != True:
                    generalParkin["dfbm"].append(dfbm)
                filename ="Park-in-"+str(datetime.fromtimestamp(operation[0]["Tmin"]).strftime("%Y-%m-%d"))+"-"+str(datetime.fromtimestamp(operation[0]["Tmax"]).strftime("%Y-%m-%d"))
                generalParkin["name"] = file+"/"+filename+".html"
                generalParkin["addText"] = element["addText"]
                generalParkin["RA"].append(element["RA"])
                generalParkin["DEC"].append(element["DEC"])
            if foundType == "Park-out":
                generalParkout["dfpos"].append(dfpos)
                generalParkout["dfloadpin"].append(dfloadpin)
                generalParkout["dftrack"].append(dftrack)
                generalParkout["dftorque"].append(dftorque)
                if dfacc is not None and dfacc.empty != True:
                    generalParkout["dfacc"].append(dfacc)
                if dfbm is not None and dfbm.empty != True:
                    generalParkout["dfbm"].append(dfbm)
                filename = "Park-out-"+str(datetime.fromtimestamp(operation[0]["Tmin"]).strftime("%Y-%m-%d"))+"-"+str(datetime.fromtimestamp(operation[0]["Tmax"]).strftime("%Y-%m-%d"))
                generalParkout["name"] = file+"/"+filename+".html"
                generalParkout["addText"] = element["addText"]
                generalParkout["RA"].append(element["RA"])
                generalParkout["DEC"].append(element["DEC"])
            if foundType == "GoToPos":
                generalGotopos["dfpos"].append(dfpos)
                generalGotopos["dfloadpin"].append(dfloadpin)
                generalGotopos["dftrack"].append(dftrack)
                generalGotopos["dftorque"].append(dftorque)
                if dfacc is not None and dfacc.empty != True:
                    generalGotopos["dfacc"].append(dfacc)
                if dfbm is not None and dfacc.empty != True:
                    generalGotopos["dfbm"].append(dfbm)
                filename = "GoToPos-"+str(datetime.fromtimestamp(operation[0]["Tmin"]).strftime("%Y-%m-%d"))+"-"+str(datetime.fromtimestamp(operation[0]["Tmax"]).strftime("%Y-%m-%d"))
                generalGotopos["name"] = file+"/"+filename+".html"
                generalGotopos["addText"] = element["addText"]
                generalGotopos["RA"].append(element["RA"])
                generalGotopos["DEC"].append(element["DEC"])
        #figuresFunctions.FigureTrack(generalTrack["addText"], generalTrack["dfpos"], generalTrack["dfloadpin"], generalTrack["dftrack"], generalTrack["dftorque"], generalTrack["name"])
        #figuresFunctions.FigureTrack(generalParkin["addText"], generalParkin["dfpos"], generalParkin["dfloadpin"], generalParkin["dftrack"], generalParkin["dftorque"], generalParkin["name"])
        #figuresFunctions.FigureTrack(generalParkout["addText"], generalParkout["dfpos"], generalParkout["dfloadpin"], generalParkout["dftrack"], generalParkout["dftorque"], generalParkout["name"])
        #figuresFunctions.FigureTrack(generalGotopos["addText"], generalGotopos["dfpos"], generalGotopos["dfloadpin"], generalGotopos["dftrack"], generalGotopos["dftorque"], generalGotopos["name"])
        """  if len(generalTrack["dfacc"]) != 0:
            #figuresFunctions.FigAccuracyTime(generalTrack["dfacc"], generalTrack["name"])
        if len(generalParkin["dfacc"]) != 0:
            #figuresFunctions.FigAccuracyTime(generalParkin["dfacc"], generalParkin["name"])
        if len(generalParkout["dfacc"]) != 0:
            #figuresFunctions.FigAccuracyTime(generalParkout["dfacc"], generalParkout["name"])
        if len(generalGotopos["dfacc"]) != 0:
            #figuresFunctions.FigAccuracyTime(generalGotopos["dfacc"], generalGotopos["name"]) """
        if len(generalTrack["dfbm"]) != 0:
            figuresFunctions.FigureRADec(generalTrack["dfpos"], generalTrack["dfbm"], generalTrack["RA"], generalTrack["DEC"], generalTrack["dfacc"], generalTrack["dftrack"], generalTrack["name"])
        if len(generalParkin["dfbm"]) != 0:
            figuresFunctions.FigureRADec(generalParkin["dfpos"], generalParkin["dfbm"], generalParkin["RA"], generalParkin["DEC"], generalParkin["dfacc"], generalParkin["dftrack"], generalParkin["name"])
        if len(generalParkout["dfbm"]) != 0:
            figuresFunctions.FigureRADec(generalParkout["dfpos"], generalParkout["dfbm"], generalParkout["RA"], generalParkout["DEC"], generalParkout["dfacc"], generalParkout["dftrack"], generalParkout["name"])
        if len(generalGotopos["dfbm"]) != 0:
            figuresFunctions.FigureRADec(generalGotopos["dfpos"], generalGotopos["dfbm"], generalGotopos["RA"], generalGotopos["DEC"], generalGotopos["dfacc"], generalGotopos["dftrack"], generalGotopos["name"])
        

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