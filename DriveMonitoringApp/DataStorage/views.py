from django.shortcuts import render
from django.http import HttpResponse
import pymongo
from django.conf import settings
from django.http import JsonResponse
import json
from bson.json_util import dumps, loads
from mongo_utils import MongoDb
from django.views.decorators.csrf import csrf_exempt

database = MongoDb

def index(request):
    return database.getData(database)
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
            return JsonResponse({"Message": "There was no new data to store."})
        if correct:
            return JsonResponse({"Message": "The data has been stored successfully."})
        else:
            return JsonResponse({"Message": "The data was not totally inserted due to duplicity or an error."})
@csrf_exempt
def storeData(request):
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
        imagePattern = body[0]["img"][0].split("/")
        imageSpltiEnd = imagePattern[-1].split(".")
        imageFinal = imagePattern[-4]+"/"+imagePattern[-3]+"/"+imagePattern[-2]+"/"+imageSpltiEnd[0]
        generalData["img"] = imageFinal
        generalData["addText"] = body[0]["addText"][0]
        #TODO - Store the rest of the data
        print(body[0])
        """ position = json.loads(body[0]["position"][0])
        pinData = json.loads(body[0]["loadPin"][0])
        track = json.loads(body[0]["track"][0])
        torque = json.loads(body[0]["torque"][0])
        accuracy = json.loads(body[0]["accuracy"][0])
        bendModel = json.loads(body[0]["bendModel"][0]) """
        correct = True
        if database.checkDuplicatedValues(database, generalData["type"], generalData["Sdate"], generalData["Stime"]) == False:
            correct = database.storeGeneralData(database, generalData)
        else:
            return JsonResponse({"Message": "There was no new data to store."})
        if correct:
            return JsonResponse({"Message": "The data has been stored successfully."})
        else:
            return JsonResponse({"Message": "The data was not totally inserted due to duplicity or an error."})

def update(request):
    return database.updateData(database)
def delete(request):
    return database.deleteData(database)
def start(request):
    return database.__init__(database)
def home(request):
    if database.isData(database) == True:
        latestTime = database.getLatestDate(database)
        data = [latestTime, database.getData(database)]
        return render(request, "storage/index.html", {"data" : data})
    else:
        return JsonResponse({"Message": "There is no data to show"})
    
def getLogs(request):
    if request.method == "GET":
        if database.isData(database) == True:
            data = {"data": database.listLogs(database, database.getLatestDate(database)), "filters": database.getFilters(database)}
            return JsonResponse(data)
        else:
            return JsonResponse({"Message": "There is no data to show"})
def getData(request):
    #TODO - Needs optimitation it takes 2.10 secs
    if request.method == "GET":
        if database.isData(database) == True:
            data = {"data": database.listData(database, database.getLatestDate(database))}
            return JsonResponse(data)
        else:
            return JsonResponse({"Message": "There is no data to show"})