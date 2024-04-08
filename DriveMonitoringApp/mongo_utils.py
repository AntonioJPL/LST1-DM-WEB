from django.http import HttpResponse
import pymongo
from django.conf import settings
from django.http import JsonResponse
import json
from bson.json_util import dumps, loads
from bson import ObjectId
import os

class MongoDb:

    my_client = pymongo.MongoClient('localhost', 27017)
    dbname = my_client['Drive-Monitoring']
    collection_logs = dbname["Logs"]
    collection_data = dbname["Data"]
   

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

    def listData(self, date):
        #TODO Find a way to get the start and end date and time to filter the data. IMPORTANT !!
        data = list(self.collection_logs.find().sort({"Time": -1}).sort({"Date": +1}))
        for element in data:
            element["_id"] = str(element["_id"])
            if element["LogStatus"] is not None:
                element["LogStatus"] = self.dbname["LogStatus"].find_one({"_id": ObjectId(element["LogStatus"])}, {"_id":0, "name":1})
                element["LogStatus"] = element["LogStatus"]["name"]
            element["Command"] = self.dbname["Commands"].find_one({"_id": ObjectId(element["Command"])}, {"_id":0, "name":1})
            element["Command"] = element["Command"]["name"]
            if element["Status"] is not None:
                element["Status"] = self.dbname["CommandStatus"].find_one({"_id": ObjectId(element["Status"])}, {"_id":0, "name":1})
                element["Status"] = element["Status"]["name"]
        return data
    
    def storeData(self, data):
        for i in range(0, len(data)):
            if data[i]["LogStatus"] != None:
                statusId = self.dbname["LogStatus"].find_one({"name":data[i]["LogStatus"]}, {"name": 0})
                data[i]["LogStatus"] = str(statusId["_id"]) #Id value of the status

            commandId = self.dbname["Commands"].find_one({"name":data[i]["Command"]}, {"name": 0})
            data[i]["Command"] = str(commandId["_id"]) #Id value of the command
            
            if data[i]["Status"] != None:
                commandStatusId = self.dbname["CommandStatus"].find_one({"name":data[i]["Status"]}, {"name": 0})
                data[i]["Status"] = str(commandStatusId["_id"]) #Id value of the commandstatus

        try:
            self.dbname["Logs"].insert_many(data)
            return True
        except Exception:
            return False
    
    def checkDuplicatedValues(self, Time, Command, Date):
        commandId = self.dbname["Commands"].find_one({"name": Command}, {"name": 0})
        commandId = str(commandId["_id"])
        if self.dbname["Logs"].find_one({"Time": Time, "Command": commandId, "Date": Date}) != None:
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
        return True if len(self.dbname["Logs"].distinct("_id")) > 0 or len(self.dbname["Data"].distinct("_id")) > 0 else False