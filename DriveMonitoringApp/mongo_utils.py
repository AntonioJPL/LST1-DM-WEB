import pymongo
from bson.json_util import dumps, loads
from bson import ObjectId
import os
import glob
from datetime import datetime
import datetime as DT
import pytz
from django.contrib.staticfiles import finders

#Class containing all the Database information and functions
class MongoDb:

    my_client = pymongo.MongoClient('localhost', 27005)
    dbname = my_client['Drive-Monitoring']
    collection_logs = dbname["Logs"]
    collection_data = dbname["Data"]
   
    #Function that initialize the general data into MongoDB
    def __init__(self):
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
    #Function that returns all the logs data in between an operation Tmin and Tmax value, if there is no operation or there are more than one operation for the same date it returns a Message
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
    #Function that returns all the general data including the plots urls, it returns an object containing a "data" attribute. This attribut is an array of an object for each type of operation. Each object has data, file and type attributes. Data attribute contains all the data documents values of that type of operation in the given date. File attribute is an array of strings being this ones the urls to the interactive plots and the type attribute is a string identifier to this data group
    def listData(self, date):
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
                        files[i] = "static/"+files[i][-4]+"/"+files[i][-3]+"/"+files[i][-2]+"/"+files[i][-1]+"/"
                        plot["file"].append(files[i])
                    plot["data"]=foundElement
                    elements.append(plot)
            return elements
        if len(operation) == 0: 
            return {"Message": "There is no data to show"}
        if len(operation) > 1:
            return {"Message": "There is more than one operation in this date"}
    #INFO: All the store functions check if there is an index created and if not creates it. This is meant to happen just the first time. This is done right before trying to insert the data
    #Function that stores an operation entry
    def storeOperation(self, data):
        if len(self.dbname["Operations"].index_information()) == 1:
            self.dbname["Operations"].create_index([('Date', pymongo.ASCENDING), ("Tmin", pymongo.ASCENDING), ("Tmax", pymongo.ASCENDING)], unique=True)
        try:
            self.dbname["Operations"].insert_one(data)
        except Exception:
            print("Duplicated Operation entry on Date: "+data["Date"])
    #Function that stores a log entry
    def storeLogs(self, data):
        if data["LogStatus"] != None:
            statusId = self.dbname["LogStatus"].find_one({"name":data["LogStatus"]}, {"name": 0})
            data["LogStatus"] = str(statusId["_id"]) #Id value of the status

        commandId = self.dbname["Commands"].find_one({"name":data["Command"]}, {"name": 0})
        data["Command"] = str(commandId["_id"]) #Id value of the command
        
        if data["Status"] != None:
            commandStatusId = self.dbname["CommandStatus"].find_one({"name":data["Status"]}, {"name": 0})
            data["Status"] = str(commandStatusId["_id"]) #Id value of the commandstatus
        stringTime = data["Date"].replace("-", "/")+" "+data["Time"]
        timeStamp = datetime.strptime(stringTime, '%Y/%m/%d %H:%M:%S')
        timeStamp = timeStamp.timestamp()

        if len(self.dbname["Logs"].index_information()) == 1:
            self.dbname["Logs"].create_index([('Command', pymongo.ASCENDING), ("Date", pymongo.ASCENDING), ("LogStatus", pymongo.ASCENDING), ("Status", pymongo.ASCENDING), ("Time", pymongo.ASCENDING)], unique=True)

        try:
            self.dbname["Logs"].insert_one(data)
        except Exception:
            pass
    #Function that stores a data entry
    def storeGeneralData(self, data):
        typeId = self.dbname["Types"].find_one({"name": data["type"]}, {"name": 0})
        data["type"] = str(typeId["_id"])
        if len(self.dbname["Data"].index_information()) == 1:
            self.dbname["Data"].create_index([('addText', pymongo.ASCENDING), ("DEC", pymongo.ASCENDING), ("Edate", pymongo.ASCENDING), ("Etime", pymongo.ASCENDING), ("file", pymongo.ASCENDING), ("RA", pymongo.ASCENDING), ("Sdate", pymongo.ASCENDING), ("Stime", pymongo.ASCENDING), ("type", pymongo.ASCENDING)], unique=True)
        try:
            self.dbname["Data"].insert_one(data)
            return True
        except Exception:
            pass
    #Function that stores a position entry
    def storePosition(self, data):
        if len(self.dbname["Position"].index_information()) == 1:
            self.dbname["Position"].create_index([('T', pymongo.ASCENDING), ("Az", pymongo.ASCENDING), ("ZA", pymongo.ASCENDING)], unique=True)
        try:
            self.dbname["Position"].insert_one(data)
        except Exception:
            pass
    #Function that stores a loadpin entry        
    def storeLoadPin(self, data):
        if len(self.dbname["Load_Pin"].index_information()) == 1:
            self.dbname["Load_Pin"].create_index([('T', pymongo.ASCENDING), ("LoadPin", pymongo.ASCENDING), ("Load", pymongo.ASCENDING)], unique=True)
        try: 
            self.dbname["Load_Pin"].insert_one(data)
        except Exception:
            pass
    #Function that stores a track entry
    def storeTrack(self, data):
        if len(self.dbname["Track"].index_information()) == 1:
            self.dbname["Track"].create_index([('T', pymongo.ASCENDING), ("Azth", pymongo.ASCENDING), ("ZAth", pymongo.ASCENDING), ("vsT0", pymongo.ASCENDING), ("Tth", pymongo.ASCENDING)], unique=True)
        try:
            self.dbname["Track"].insert_one(data)
        except Exception:
            pass
    #Function that stores a torque entry               
    def storeTorque(self, data):
        if len(self.dbname["Torque"].index_information()) == 1:
            self.dbname["Torque"].create_index([('T', pymongo.ASCENDING), ("Az1_mean", pymongo.ASCENDING), ("Az1_min", pymongo.ASCENDING), ("Az1_max", pymongo.ASCENDING), ("Az2_mean", pymongo.ASCENDING), ("Az2_min", pymongo.ASCENDING), ("Az2_max", pymongo.ASCENDING), ("Az3_mean", pymongo.ASCENDING), ("Az3_min", pymongo.ASCENDING), ("Az3_max", pymongo.ASCENDING), ("Az4_mean", pymongo.ASCENDING), ("Az4_min", pymongo.ASCENDING), ("Az4_max", pymongo.ASCENDING), ("El1_mean", pymongo.ASCENDING), ("El1_min", pymongo.ASCENDING), ("El1_max", pymongo.ASCENDING), ("El2_mean", pymongo.ASCENDING), ("El2_min", pymongo.ASCENDING), ("El2_max", pymongo.ASCENDING)], unique=True)
        try:
            self.dbname["Torque"].insert_one(data)
        except Exception:
            pass
    #Function that stores a accuracy entry    
    def storeAccuracy(self, data):
        if len(self.dbname["Accuracy"].index_information()) == 1:
            self.dbname["Accuracy"].create_index([('T', pymongo.ASCENDING), ("Azmean", pymongo.ASCENDING), ("Azmin", pymongo.ASCENDING), ("Azmax", pymongo.ASCENDING), ("Zdmean", pymongo.ASCENDING), ("Zdmin", pymongo.ASCENDING), ("Zdmax", pymongo.ASCENDING)], unique=True)
        try:
            self.dbname["Accuracy"].insert_one(data)
        except Exception:
            pass
    #Function that stores a bend_model entry        
    def storeBendModel(self, data):
        if len(self.dbname["Bend_Model"].index_information()) == 1:
            self.dbname["Bend_Model"].create_index([('T', pymongo.ASCENDING), ("AzC", pymongo.ASCENDING), ("ZAC", pymongo.ASCENDING)], unique=True)
        try:
            self.dbname["Bend_Model"].insert_one(data)
        except Exception:
            pass
    #Function that returns true if there is data on the Data collection or false if there is not           
    def isData(self):
        return True if len(self.dbname["Data"].distinct("_id")) > 0 else False
    #Function that returns the latest date stored. It takes it from the logs      
    def getLatestDate(self):
        result =  list(self.dbname["Logs"].find({}, {"_id": 0 ,"Date": 1}).sort({"Date": -1}).limit(1))
        dateParts = result[0]["Date"].split("-")
        newDay = int(dateParts[2])-1
        newDay = str(newDay)
        result = dateParts[0]+"-"+dateParts[1]+"-"+newDay.zfill(2)
        return result
    #Function that returns the types, dates and times for the given date as an object
    def getFilters(self, date):
        if(date == None):
            date == self.getLatestDate(self)
        response = {}
        response["types"] = self.dbname["Types"].distinct("name")
        operation = list(self.dbname["Operations"].find({"Date": date}))
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
    #Function that returns the position document values between a minimum and maximum timestamps values
    def getPosition(self, tmin, tmax):
        result = {}
        result["T"] = {}
        result["Az"] = {}
        result["ZA"] = {}
        index = 0
        tmin = str(tmin).replace(".0", "")+"000"
        tmax = str(tmax).replace(".0", "")+"000"
        for data in self.dbname["Position"].find({'T': {'$gte': int(tmin), '$lte': int(tmax)}}):
            result["T"][index] = datetime.fromtimestamp(int(str(data["T"])[:-3]), tz=pytz.utc)
            result["Az"][index] = data["Az"]
            result["ZA"][index] = data["ZA"]
            index += 1
        return result
    #Function that returns the loadpins document values between a minimum and maximum timestamps values
    def getLoadPin(self, tmin, tmax):
        result = {}
        result["T"] = {}
        result["LoadPin"] = {}
        result["Load"] = {}
        index = 0
        tmin = str(tmin)
        tmax = str(tmax)
        for data in self.dbname["Load_Pin"].find({'T': {'$gte': tmin, '$lte': tmax}, "LoadPin": {"$in": [207,107]}}):
            dataF = float(data["T"])
            result["T"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            result["LoadPin"][index] = data["LoadPin"]
            result["Load"][index] = data["Load"]
            index += 1
        return result
    #Function that returns all the loadpin values inside an operation date
    def getAllLoadPin(self, date):
        result = {}
        result["T"] = {}
        result["LoadPin"] = {}
        result["Load"] = {}
        index = 0
        tmin = datetime.strptime(date+" 00:00:00.000000", '%Y-%m-%d %H:%M:%S.%f').timestamp()
        tmax = datetime.strptime(date+" 23:59:59.900000", '%Y-%m-%d %H:%M:%S.%f').timestamp()
        tmin = str(tmin)
        tmax = str(tmax)
        for data in self.dbname["Load_Pin"].find({'T': {'$gte': tmin, '$lte': tmax}}):
            dataF = float(data["T"])
            dataF = dataF
            result["T"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            result["LoadPin"][index] = data["LoadPin"]
            result["Load"][index] = data["Load"]
            index += 1
        return result
    #Function that returns the track document values between a minimum and maximum timestamps values
    def getTrack(self, tmin, tmax):
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
    #Function that returns the torque document values between a minimum and maximum timestamps values
    def getTorque(self, tmin, tmax):
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
    #Function that returns the accuracy document values between a minimum and maximum timestamps values
    def getAccuracy(self, tmin, tmax):
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
    #Function that returns the bending_model document values between a minimum and maximum timestamps values
    def getBM(self, tmin, tmax):
        result = {}
        result["T"] = {}
        result["AzC"] = {}
        result["ZAC"] = {}
        index = 0
        for data in self.dbname["Bend_Model"].find({'T': {'$gt': int(tmin), '$lt': int(tmax)}}):
            result["T"][index] = data["T"]
            result["AzC"][index] = data["AzC"]
            result["ZAC"][index] = data["ZAC"]
            index += 1
        return result
    #Function that returns the operation document of the given date value
    def getOperation(self, date):
        return list(self.dbname["Operations"].find({"Date": date}))
    #Function that returns the data docuemtn values between a minimum and maximum timestamps values, this timestamp values are parsed into date and time values to compare the Stime, Etime and Sdate and Edate values
    def getDatedData(self, tmin, tmax):
        start = datetime.fromtimestamp(tmin)
        start = str(start).split(" ")
        end = datetime.fromtimestamp(tmax)
        end = str(end).split(" ")
        return list(self.dbname["Data"].aggregate([{"$match":{"$or": [{"$and": [{"Sdate": start[0]}, {"Stime": {"$gte": start[1]}}]}, {"$and": [{"Edate": end[0]},{"Etime": {"$lte": end[1]}}]}]}}]))
    #Function that returns all the operation types as a list
    def getOperationTypes(self):
        return list(self.dbname["Types"].find())
    #Function that generates the Load Pin plot url and returns them. It generates the url based on the data "file" parameter and replaces the end of it with the found plot path.
    def getLPPlots(self, date):
        operation = list(self.dbname["Operations"].find({"Date": date}))
        if len(operation) > 0:
            start = datetime.fromtimestamp(operation[0]["Tmin"])
            start = str(start).split(" ")
            data = self.dbname["Data"].find_one({"Sdate": date, "Stime": {"$gte": start[1]}})
            path = data["file"]
            pathParts = path.split("/")
            path = path.replace(pathParts[-2]+"/"+pathParts[-1], "LoadPin")
            file = finders.find(path)
            if file is not None:
                files = glob.glob(file+"/"+"LoadPin_"+date+"*")
                plots = []
                for i in range(0, len(files)):
                    files[i] = files[i].split("/")
                    files[i] = "static/"+files[i][-4]+"/"+files[i][-3]+"/"+files[i][-2]+"/"+files[i][-1]+"/"
                    plots.append(files[i])
                if len(plots) > 0:
                    return {"plots": plots}
                else:
                    return {"Message": "There is no data to show"}
            else:
                return {"Message": "There is no data to show"}
        else:
            return {"Message": "There is no data to show"}
    #Function that returns the las 7 operation stored in the DB, this is used to check if the plots are generated on the LibDisplayTrackStore.py file
    def getLast7Operations(self):
        return list(self.dbname["Operations"].aggregate([{"$sort": {"Date": -1}}, {"$limit": 7}]))
    #Function that checks if the date passed is equal to the last date stored, in case it is it returns true, in case the database has no operations it returns Empty and in case the date is not equal it returns the last date stored, if there is an error it returns False. All of this is returned in an object with a "lastDate" attribute
    def checkDates(self, date):
        try:
            lastElementFound = list(self.dbname["Operations"].aggregate([{"$sort": {"Date": -1}}, {"$limit": 1}]))
        except Exception:
            return {"lastDate": False}
        if len(lastElementFound) > 0:
            lastElementFound = lastElementFound[0]
        else:
            return {"lastDate": "Empty"}
        if lastElementFound["Date"] == date:
            return {"lastDate": True}
        else:
            return {"lastDate": lastElementFound["Date"]}