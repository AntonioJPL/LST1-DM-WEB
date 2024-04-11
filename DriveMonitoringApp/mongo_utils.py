from django.http import HttpResponse
import pymongo
from django.conf import settings
from django.http import JsonResponse
import json
from bson.json_util import dumps, loads
from bson import ObjectId
import os
import glob
from datetime import datetime

class MongoDb:

    my_client = pymongo.MongoClient('localhost', 27017)
    dbname = my_client['Drive-Monitoring']
    collection_logs = dbname["Logs"]
    collection_data = dbname["Data"]
    img_rute = "/Users/antoniojose/Desktop/data/example/data/R0/LST1/lst-drive/log/DisplayTrack/DriveMonitoringApp/DataStorage/static/"
   

    def __init__(self):
        data = {}
        

    def getData(self):
        #source ~/.bash_profile needed
        PORT = os.getenv("DB_HOST")
        print(PORT)
        datalist = {}
        for element in self.collection_logs.find():
            id = str(element["_id"])
            datalist[id] = element
            datalist[id]["_id"] = id
        return datalist
        #HttpResponse("Buenas tardes")
        return JsonResponse({"status": "true", "data": datalist})

    def updateData(self):    
        update_data = self.collection_name.update_one({'medicine_id':'RR000123456'}, {'$set':{'common_name':'Paracetamol 500'}})

    #count = collection_name.count()
        print(self.collection_name)

    def deleteData(self):
        delete_data = self.collection_name.delete_one({'medicine_id':'RR000123456'})
        print(delete_data)
        return HttpResponse("Deleting an objecth with the indicated id")

    def listLogs(self, date):
        #TODO Find a way to get the start and end date and time to filter the data. IMPORTANT !!
        data = list(self.collection_logs.find().sort({"Stime": -1}).sort({"Sdate": +1}))
        logs = list(self.dbname["LogStatus"].find())
        commands = list(self.dbname["Commands"].find())
        comStatus = list(self.dbname["CommandStatus"].find())
        for element in data:
            element["_id"] = str(element["_id"])
            if element["LogStatus"] is not None:
                element["LogStatus"] = [searchedElement["name"] for searchedElement in logs if searchedElement["_id"] == ObjectId(element["LogStatus"])]
                element["LogStatus"] = element["LogStatus"][0]
            element["Command"] = [searchedElement["name"] for searchedElement in commands if searchedElement["_id"] == ObjectId(element["Command"])]
            element["Command"] = element["Command"][0]
            if element["Status"] is not None:
                element["Status"] = [searchedElement["name"] for searchedElement in comStatus if searchedElement["_id"] == ObjectId(element["Status"])]
                element["Status"] = element["Status"][0]
        return data
    def listData(self, date):
        #TODO Find a way to get the start and end date and time to filter the data. IMPORTANT !! Have to get it from the LOGS !
        data = list(self.collection_data.find().sort({"Stime": -1}).sort({"Sdate": +1}))
        types = list(self.dbname["Types"].find())
        for element in data:
            element["_id"] = str(element["_id"])
            if element["type"] is not None:
                element["type"] = [searchedElement["name"] for searchedElement in types if searchedElement["_id"] == ObjectId(element["type"])]
                element["type"] = element["type"][0]
            images = glob.glob(self.img_rute+element["img"]+"*")
            for i in range(0, len(images)):
                images[i] = images[i].replace(self.img_rute, "static/")
            element["img"] = images
        return data
    
    def storeLogs(self, data):
        operation = {}
        for i in range(0, len(data)):
            if data[i]["LogStatus"] != None:
                statusId = self.dbname["LogStatus"].find_one({"name":data[i]["LogStatus"]}, {"name": 0})
                data[i]["LogStatus"] = str(statusId["_id"]) #Id value of the status

            commandId = self.dbname["Commands"].find_one({"name":data[i]["Command"]}, {"name": 0})
            data[i]["Command"] = str(commandId["_id"]) #Id value of the command
            
            if data[i]["Status"] != None:
                commandStatusId = self.dbname["CommandStatus"].find_one({"name":data[i]["Status"]}, {"name": 0})
                data[i]["Status"] = str(commandStatusId["_id"]) #Id value of the commandstatus
            stringTime = data[i]["Date"].replace("-", "/")+" "+data[i]["Time"]
            timeStamp = datetime.strptime(stringTime, '%Y/%m/%d %H:%M:%S')
            timeStamp = timeStamp.timestamp()
            if operation.get("Date") is None:
                operation["Date"] = data[i]["Date"]
            else:
                if operation["Date"] > data[i]["Date"]:
                    operation["Date"] = data[i]["Date"]
            if operation.get("Tmin") is None:
                operation["Tmin"] = timeStamp
            else:
                if operation["Tmin"] > timeStamp:
                    operation["Tmin"] = timeStamp
            if operation.get("Tmax") is None:
                operation["Tmax"] = timeStamp
            else:
                if operation["Tmax"] < timeStamp:
                    operation["Tmax"] = timeStamp
                     
        try:
            self.dbname["Logs"].insert_many(data)
            if self.dbname["Operations"].find(operation) == None:
                self.dbname["Operations"].insert_one(operation)
            return True
        except Exception:
            return False
    def storeGeneralData(self, data):
        typeId = self.dbname["Types"].find_one({"name": data["type"]}, {"name": 0})
        data["type"] = str(typeId["_id"])
        if self.dbname["Data"].find_one({"type": data["type"], "Stime": data["Stime"], "Sdate": data["Sdate"], "Edate": data["Edate"], "Etime": data["Etime"]}) == None:
            try:
                self.dbname["Data"].insert_one(data)
                return True
            except Exception:
                return False
    def storePosition(self, data):
        newData = []
        keys = list(data["T"].keys())
        if len(keys) > 0:
            for i in keys:
                rowData = {}
                rowData["T"] = data["T"][i]
                rowData["Az"] = data["Az"][i]
                rowData["ZA"] = data["ZA"][i]
                if self.dbname["Position"].find_one(rowData) == None:
                    newData.append(rowData)
            if len(newData)>1:
                self.dbname["Position"].insert_many(newData)
                return True
            else:
                if len(newData) == 1:
                    self.dbname["Position"].insert_one(newData[0])
                    return True
                else:
                    return False
            
    def storeLoadPin(self, data):
        newData = []
        keys = list(data["T"].keys())
        if len(keys) > 0:
            for i in keys:
                rowData = {}
                rowData["T"] = data["T"][i]
                rowData["LoadPin"] = data["LoadPin"][i]
                rowData["Load"] = data["Load"][i]
                if self.dbname["Load_Pin"].find_one(rowData) == None:
                    newData.append(rowData)
            if len(newData)>1:
                self.dbname["Load_Pin"].insert_many(newData)
                return True
            else:
                if len(newData) == 1:
                    self.dbname["Load_Pin"].insert_one(newData[0])
                    return True
                else:
                    return False
    
    def storeTrack(self, data):
        newData = []
        keys = list(data["T"].keys())
        if len(keys) > 0:
            for i in keys:
                rowData = {}
                rowData["T"] = data["T"][i]
                rowData["Azth"] = data["Azth"][i]
                rowData["ZAth"] = data["ZAth"][i]
                rowData["vsT0"] = data["vsT0"][i]
                rowData["Tth"] = data["Tth"][i]
                if self.dbname["Track"].find_one({"T": rowData["T"], "Azth": rowData["Azth"], "ZAth": rowData["ZAth"], "vsT0": rowData["vsT0"]}) == None:
                    newData.append(rowData)
            if len(newData)>1:
                self.dbname["Track"].insert_many(newData)
                return True
            else:
                if len(newData) == 1:
                    self.dbname["Track"].insert_one(newData[0])
                    return True
                else:
                    return False

    def storeTorque(self, data):
        newData = []
        keys = list(data["T"].keys())
        if len(keys) > 0:
            for i in keys:
                rowData = {}
                rowData["T"] = data["T"][i]
                rowData["Az1_mean"] = data["Az1_mean"][i]
                rowData["Az1_min"] = data["Az1_min"][i]
                rowData["Az1_max"] = data["Az1_max"][i]
                rowData["Az2_mean"] = data["Az2_mean"][i]
                rowData["Az2_min"] = data["Az2_min"][i]
                rowData["Az2_max"] = data["Az2_max"][i]
                rowData["Az3_mean"] = data["Az3_mean"][i]
                rowData["Az3_min"] = data["Az3_min"][i]
                rowData["Az3_max"] = data["Az3_max"][i]
                rowData["Az4_mean"] = data["Az4_mean"][i]
                rowData["Az4_min"] = data["Az4_min"][i]
                rowData["Az4_max"] = data["Az4_max"][i]
                rowData["El1_mean"] = data["El1_mean"][i]
                rowData["El1_min"] = data["El1_min"][i]
                rowData["El1_max"] = data["El1_max"][i]
                rowData["El2_mean"] = data["El2_mean"][i]
                rowData["El2_min"] = data["El2_min"][i]
                rowData["El2_max"] = data["El2_max"][i]

                if self.dbname["Torque"].find_one(rowData) == None:
                    newData.append(rowData)
            if len(newData)>1:
                self.dbname["Torque"].insert_many(newData)
                return True
            else:
                if len(newData) == 1:
                    self.dbname["Torque"].insert_one(newData[0])
                    return True
                else:
                    return False

    def storeAccuracy(self, data):
        newData = []
        keys = list(data["T"].keys())
        if len(keys) > 0:
            for i in keys:
                rowData = {}
                rowData["T"] = data["T"][i]
                rowData["Azmean"] = data["Azmean"][i]
                rowData["Azmin"] = data["Azmin"][i]
                rowData["Azmax"] = data["Azmax"][i]
                rowData["Zdmean"] = data["Zdmean"][i]
                rowData["Zdmin"] = data["Zdmin"][i]
                rowData["Zdmax"] = data["Zdmax"][i]

                if self.dbname["Accuracy"].find_one(rowData) == None:
                    newData.append(rowData)

            if len(newData)>1:
                self.dbname["Accuracy"].insert_many(newData)
                return True
            else:
                if len(newData) == 1:
                    self.dbname["Accuracy"].insert_one(newData[0])
                    return True
                else:
                    return False
            
    def storeBendModel(self, data):
        newData = []
        keys = list(data["T"].keys())
        if len(keys) > 0:
            for i in keys:
                rowData = {}
                rowData["T"] = data["T"][i]
                rowData["AzC"] = data["AzC"][i]
                rowData["ZAC"] = data["ZAC"][i]

                if self.dbname["Bend_Model"].find_one(rowData) == None:
                    newData.append(rowData)
            if len(newData)>1:
                self.dbname["Bend_Model"].insert_many(newData)
                return True
            else:
                if len(newData) == 1:
                    self.dbname["Bend_Model"].insert_one(newData[0])
                    return True
                else:
                    return False
            
    def checkDuplicatedLogs(self, Time, Command, Date):
        commandId = self.dbname["Commands"].find_one({"name": Command}, {"name": 0})
        commandId = str(commandId["_id"])
        if self.dbname["Logs"].find_one({"Time": Time, "Command": commandId, "Date": Date}) != None:
            return True
        else:
            return False
    def checkDuplicatedValues(self, type, date, time):
        typeId = self.dbname["Types"].find_one({"name": type}, {"name": 0})
        typeId = str(typeId["_id"])
        if self.dbname["Data"].find_one({"type": type, "Sdate": date, "Stime": time}) != None:
            return True
        else:
            return False
    def getLatestDate(self):
        result =  list(self.dbname["Logs"].find({}, {"_id": 0 ,"Date": 1}).sort({"Date": -1}).limit(1))
        dateParts = result[0]["Date"].split("-")
        newDay = int(dateParts[2])-1
        newDay = str(newDay)
        result = dateParts[0]+"-"+dateParts[1]+"-"+newDay.zfill(2)
        return result
    def getFilters(self):
        response = {}
        response["types"] = self.dbname["Types"].distinct("name")
        response["dates"] = self.dbname["Logs"].distinct("Date")
        times = {}
        for date in response["dates"]:
            times[date] = self.dbname["Logs"].distinct("Time", {"Date": date})
        response["times"] = times
        return response
    def isData(self):
        return True if len(self.dbname["Data"].distinct("_id")) > 0 or len(self.dbname["Data"].distinct("_id")) > 0 else False
    def getFirstData(self):
        return self.dbname["Data"].find_one()
    def getPosition(self, tmin, tmax):
        #TODO - Find how to query in MongoDB to get the items
        result = {}
        for data in self.dbname["Position"].find():
            print(data)


    