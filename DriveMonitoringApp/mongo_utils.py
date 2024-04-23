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
import datetime as DT
import pytz
from django.contrib.staticfiles import finders

class MongoDb:

    my_client = pymongo.MongoClient('localhost', 27017)
    dbname = my_client['Drive-Monitoring']
    collection_logs = dbname["Logs"]
    collection_data = dbname["Data"]
   
    #Function that initialize the general data
    def __init__(self):
        data = {}
        self.dbname["CommandStatus"].insert_many([
            {"name": "command sent"},
            {"name": "in progress"},
            {"name": "Done received"},
            {"name": "action error"}
        ])
        self.dbname["LogStatus"].insert_many([
            {"name": "Finished"},
            {"name": "Stopped"},
            {"name": "Error"},
            {"name": "Unknown"}
        ])
        self.dbname["Types"].insert_many([
            {"name": "Track"},
            {"name": "Park-in"},
            {"name": "Park-out"},
            {"name": "GoToPos"}
        ])
        self.dbname["Commands"].insert_many([
            {"name": "StopDrive"},
            {"name": "Drive Regulation Parameters Azimuth"},
            {"name": "Drive Regulation Parameters Elevation"},
            {"name": "[Drive] Track start"},
            {"name": "Start Tracking"},
            {"name": "Park_Out"},
            {"name": "Park_In"},
            {"name": "GoToTelescopePosition"},
            {"name": "Start_Tracking"},
            {"name": "GoToPosition"}
        ])
    
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
        operation = list(self.dbname["Operations"].find({"Date": date}))
        if len(operation) == 1:
            start = datetime.fromtimestamp(operation[0]["Tmin"])
            start = str(start).split(" ")
            end = datetime.fromtimestamp(operation[0]["Tmax"])
            end = str(end).split(" ")
            data = list(self.dbname["Logs"].aggregate([{"$match":{"$or": [{"$and": [{"Date": start[0]}, {"Time": {"$gte": start[1]}}]}, {"$and": [{"Date": end[0]},{"Time": {"$lte": end[1]}}]}]}}]))
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
        if len(operation) == 0: 
            return {"Message": "There is no data to show"}
        if len(operation) > 1:
            return {"Message": "There is more than one operation in this date"}

    def listData(self, date):
        #TODO Find a way to get the start and end date and time to filter the data. IMPORTANT !! Have to get it from the LOGS !
        operation = list(self.dbname["Operations"].find({"Date": date}))
        if len(operation) == 1:
            start = datetime.fromtimestamp(operation[0]["Tmin"])
            start = str(start).split(" ")
            end = datetime.fromtimestamp(operation[0]["Tmax"])
            end = str(end).split(" ")
            types = list(self.dbname["Types"].find())
            elements = []
            endDate = datetime.strptime(date.replace("-", ""), '%Y%m%d')
            endDate += DT.timedelta(days=1)
            for element in types:
                plot = {}
                plot["type"] = element["name"]
                foundElement = list(self.dbname["Data"].aggregate([{"$match":{"$or": [{"$and": [{"Sdate": start[0]}, {"Stime": {"$gte": start[1]}}]}, {"$and": [{"Edate": end[0]},{"Etime": {"$lte": end[1]}}]}]}}, {"$match": {"type": str(element["_id"])}}, {"$addFields": {"_id": {"$toString": "$_id"}, "type": plot["type"]}}]))
                if len(foundElement) > 0:
                    file = foundElement[0]["file"].split("/")
                    filename = element["name"]+"-"+date+"-"+str(endDate.strftime("%Y-%m-%d"))
                    file = finders.find(file[0]+"/"+file[1]+"/"+file[2])
                    files = glob.glob(file+"/"+filename+"*")
                    plot["file"] = []
                    for i in range(0, len(files)):
                        files[i] = files[i].split("/")
                        #print(files[i])
                        files[i] = "static/"+files[i][-4]+"/"+files[i][-3]+"/"+files[i][-2]+"/"+files[i][-1]+"/"
                        plot["file"].append(files[i])
                    plot["data"]=foundElement
                    elements.append(plot)
            #print(elements)
            return elements
        if len(operation) == 0: 
            return {"Message": "There is no data to show"}
        if len(operation) > 1:
            return {"Message": "There is more than one operation in this date"}
    
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
            #print("Find result")
            #print(len(list(self.dbname["Operations"].find(operation))) == 0)
            if len(list(self.dbname["Operations"].find(operation))) == 0:
                self.dbname["Operations"].insert_one(operation)
        except Exception:
            print(Exception.with_traceback())
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
    def getFilters(self, date):
        if(date == None):
            date == self.getLatestDate(self)
        response = {}
        response["types"] = self.dbname["Types"].distinct("name")
        operation = list(self.dbname["Operations"].find({"Date": date}))
        print(date)
        if len(operation) == 1:
            start = datetime.fromtimestamp(operation[0]["Tmin"])
            start = str(start).split(" ")
            end = datetime.fromtimestamp(operation[0]["Tmax"])
            end = str(end).split(" ")
            response["dates"] = [start[0], end[0]]
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
        result["T"] = {}
        result["Az"] = {}
        result["ZA"] = {}
        index = 0
        tmin = str(tmin).replace(".0", "")+"000"
        tmax = str(tmax).replace(".0", "")+"000"
        for data in self.dbname["Position"].find({'T': {'$gt': int(tmin), '$lt': int(tmax)}}):
            result["T"][index] = datetime.fromtimestamp(int(str(data["T"])[:-3]), tz=pytz.utc)
            result["Az"][index] = data["Az"]
            result["ZA"][index] = data["ZA"]
            index += 1
        return result
    def getLoadPin(self, tmin, tmax):
        #TODO - Find how to query in MongoDB to get the items
        result = {}
        result["T"] = {}
        result["LoadPin"] = {}
        result["Load"] = {}
        index = 0
        tmin = str(tmin).replace(".0", "")+"000"
        tmax = str(tmax).replace(".0", "")+"000"
        for data in self.dbname["Load_Pin"].find({'T': {'$gt': int(tmin), '$lt': int(tmax)}}):
            dataF = float(data["T"])
            dataF = dataF/1000
            result["T"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            result["LoadPin"][index] = data["LoadPin"]
            result["Load"][index] = data["Load"]
            index += 1
        return result
    def getTrack(self, tmin, tmax):
        #TODO - Find how to query in MongoDB to get the items
        result = {}
        result["T"] = {}
        result["Azth"] = {}
        result["ZAth"] = {}
        result["vsT0"] = {}
        result["Tth"] = {}
        index = 0
        tmin = str(tmin).replace(".0", "")+"000"
        tmax = str(tmax).replace(".0", "")+"000"
        for data in self.dbname["Track"].find({'Tth': {'$gt': int(tmin), '$lt': int(tmax)}}):
            result["T"][index] = data["T"]
            result["Azth"][index] = data["Azth"]
            result["ZAth"][index] = data["ZAth"]
            result["vsT0"][index] = data["vsT0"]
            dataF = float(data["Tth"])
            dataF = dataF/1000
            result["Tth"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            index += 1
        return result
    def getTorque(self, tmin, tmax):
        #TODO - Find how to query in MongoDB to get the items
        result = {}
        result["T"] = {}
        result["Az1_mean"] = {}
        result["Az1_min"] = {}
        result["Az1_max"] = {}
        result["Az2_mean"] = {}
        result["Az2_min"] = {}
        result["Az2_max"] = {}
        result["Az3_mean"] = {}
        result["Az3_min"] = {}
        result["Az3_max"] = {}
        result["Az4_mean"] = {}
        result["Az4_min"] = {}
        result["Az4_max"] = {}
        result["El1_mean"] = {}
        result["El1_min"] = {}
        result["El1_max"] = {}
        result["El2_mean"] = {}
        result["El2_min"] = {}
        result["El2_max"] = {}
        index = 0
        tmin = str(tmin).replace(".0", "")+"000"
        tmax = str(tmax).replace(".0", "")+"000"
        for data in self.dbname["Torque"].find({'T': {'$gt': int(tmin), '$lt': int(tmax)}}):
            dataF = float(data["T"])
            dataF = dataF/1000
            result["T"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            result["Az1_mean"][index] = data["Az1_mean"]
            result["Az1_min"][index] = data["Az1_min"]
            result["Az1_max"][index] = data["Az1_max"]
            result["Az2_mean"][index] = data["Az2_mean"]
            result["Az2_min"][index] = data["Az2_min"]
            result["Az2_max"][index] = data["Az2_max"]
            result["Az3_mean"][index] = data["Az3_mean"]
            result["Az3_min"][index] = data["Az3_min"]
            result["Az3_max"][index] = data["Az3_max"]
            result["Az4_mean"][index] = data["Az4_mean"]
            result["Az4_min"][index] = data["Az4_min"]
            result["Az4_max"][index] = data["Az4_max"]
            result["El1_mean"][index] = data["El1_mean"]
            result["El1_min"][index] = data["El1_min"]
            result["El1_max"][index] = data["El1_max"]
            result["El2_mean"][index] = data["El2_mean"]
            result["El2_min"][index] = data["El2_min"]
            result["El2_max"][index] = data["El2_max"]
            index += 1
        return result
    def getAccuracy(self, tmin, tmax):
        #TODO - Find how to query in MongoDB to get the items
        result = {}
        result["T"] = {}
        result["Azmean"] = {}
        result["Azmin"] = {}
        result["Azmax"] = {}
        result["Zdmean"] = {}
        result["Zdmin"] = {}
        result["Zdmax"] = {}
        index = 0
        tmin = str(tmin).replace(".0", "")+"000"
        tmax = str(tmax).replace(".0", "")+"000"
        for data in self.dbname["Accuracy"].find({'T': {'$gt': int(tmin), '$lt': int(tmax)}}):
            dataF = float(data["T"])
            dataF = dataF/1000
            result["T"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            result["Azmean"][index] = data["Azmean"]
            result["Azmin"][index] = data["Azmin"]
            result["Azmax"][index] = data["Azmax"]
            result["Zdmean"][index] = data["Zdmean"]
            result["Zdmin"][index] = data["Zdmin"]
            result["Zdmax"][index] = data["Zdmax"]
            index += 1
        return result
    def getBM(self, tmin, tmax):
        result = {}
        result["T"] = {}
        result["AzC"] = {}
        result["ZAC"] = {}
        index = 0
        #tmin = str(tmin).replace(".0", "")+"000"
        #tmax = str(tmax).replace(".0", "")+"000"
        #print(tmin)
        #print(list(self.dbname["Bend_Model"].find({'T': {'$gt': tmin, '$lt': tmax}})))
        for data in self.dbname["Bend_Model"].find({'T': {'$gt': int(tmin), '$lt': int(tmax)}}):
            #dataF = float(data["T"])
            #dataF = dataF/1000
            result["T"][index] = data["T"]
            result["AzC"][index] = data["AzC"]
            result["ZAC"][index] = data["ZAC"]
            index += 1
        return result
    def getOperation(self, date):
        return list(self.dbname["Operations"].find({"Date": date}))
    def getDatedData(self, tmin, tmax):
        start = datetime.fromtimestamp(tmin)
        start = str(start).split(" ")
        end = datetime.fromtimestamp(tmax)
        end = str(end).split(" ")
        return list(self.dbname["Data"].aggregate([{"$match":{"$or": [{"$and": [{"Sdate": start[0]}, {"Stime": {"$gte": start[1]}}]}, {"$and": [{"Edate": end[0]},{"Etime": {"$lte": end[1]}}]}]}}]))
    def getOperationTypes(self):
        return list(self.dbname["Types"].find())
    