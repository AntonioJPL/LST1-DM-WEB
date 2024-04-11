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
            return JsonResponse({"Message": "There was no new Logs data to store."})
        if correct:
            return JsonResponse({"Message": "The data has been stored successfully."})
        else:
            return JsonResponse({"Message": "The data was not totally inserted due to duplicity or an error."})
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
        imagePattern = body[0]["img"][0].split("/")
        imageSpltiEnd = imagePattern[-1].split(".")
        finalImage = imagePattern[-4]+"/"+imagePattern[-3]+"/"+imagePattern[-2]+"/"+imageSpltiEnd[0]
        generalData["img"] = finalImage
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
    if request.method == "GET":
        if database.isData(database) == True:
            data = {"data": database.listData(database, database.getLatestDate(database))}
            return JsonResponse(data)
        else:
            return JsonResponse({"Message": "There is no data to show"})
def getFirstPlot(request):
    print(request.method)
    if request.method == "GET":
        firstElement = database.getFirstData(database)
        print(firstElement)
        stringTime = firstElement["Sdate"]+" "+firstElement["Stime"]
        tmin = datetime.strptime(stringTime, '%Y-%m-%d %H:%M:%S').timestamp()
        stringTime = firstElement["Edate"]+" "+firstElement["Etime"]
        tmax = datetime.strptime(stringTime, '%Y-%m-%d %H:%M:%S').timestamp()
        print(tmin, tmax)
        cmd_status = 0
        position = database.getPosition(database, tmin, tmax)
        """ fig = plt.figure(figsize = (20, 12))
        plt.gcf().subplots_adjust(left = 0.1, bottom = 0.1,right = 0.9, top = 0.9, wspace = 0, hspace = 0.1)
        
        spec = gridspec.GridSpec(ncols=1, nrows=2,height_ratios=[2, 1])
        host1 = fig.add_subplot(spec[0])
        
        formatter = mdates.DateFormatter("%H:%M:%S")
        formatter.set_tzinfo(pytz.utc); 
        plt.gca().xaxis.set_major_formatter(formatter)
        
        par1 = host1.twinx()
        par2 = host1.twinx()
        par2.spines["right"].set_position(("axes", 1.08))
        
        par2.set_frame_on(True)
        par2.patch.set_visible(False)
        for sp in par2.spines.values():
            sp.set_visible(False)

        par2.spines["right"].set_visible(True)

        lines = []
        
        if dfloadpin is not None:
            mask107 = dfloadpin['LoadPin']==107
            mask207 = dfloadpin['LoadPin']==207

            p1, = host1.plot(dfloadpin[mask107]['T'],dfloadpin[mask107]['Load'], color='blue', label="Cable 107")
            p1b, = host1.plot(dfloadpin[mask207]['T'],dfloadpin[mask207]['Load'], color='green', label="Cable 207")
            lines.append(p1)
            lines.append(p1b)
            
        p2, = par1.plot(dfpos['T'],dfpos['Az'], color='red', label="Azimuth")
        lines.append(p2)
        if dftrack is not None:
            p2b, = par1.plot(dftrack['Tth'],dftrack['Azth'], color='red',ls='dashed', label="Azimuth Th.")
            lines.append(p2b)
        p3, = par2.plot(dfpos['T'],dfpos['ZA'], color='black', label="Zenith Angle")
        lines.append(p3)
        if dftrack is not None:
            p3b, = par2.plot(dftrack['Tth'],dftrack['ZAth'], color='black',ls='dashed', label="Zenith Angle Th.")
            lines.append(p3b)
        
        host1.set_xlabel("", fontsize=15)
        host1.set_ylabel("Load [kg]", fontsize=15)
        host1.set_title(figname, fontsize=15)
        par1.set_ylabel("Azimuth [deg]", fontsize=15)
        par2.set_ylabel("Zenith Angle [deg]", fontsize=15)

        host1.yaxis.label.set_color(p1.get_color())
        par1.yaxis.label.set_color(p2.get_color())
        par2.yaxis.label.set_color(p3.get_color())

        tkw = dict(size=4, width=1.5)
        host1.tick_params(axis='y', colors=p1.get_color(), **tkw)
        par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
        par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
        host1.tick_params(axis='x', **tkw)
            
        host1.set_xlim(datetime.fromtimestamp(tmin, tz=pytz.utc),datetime.fromtimestamp(tmax, tz=pytz.utc))
        host1.legend(lines, [l.get_label() for l in lines],fontsize=13)
        
        if cmd_status ==0:
            host1.text(0., 1., 'ACTION FINISHED',verticalalignment='bottom', horizontalalignment='left',transform=host1.transAxes,color='green', fontsize=15)
        if cmd_status ==2:
            host1.text(0., 1., 'ACTION STOPPED BY USER',verticalalignment='bottom', horizontalalignment='left',transform=host1.transAxes,color='orange', fontsize=15)
        if cmd_status ==1:
            host1.text(0., 1., 'ACTION STOPPED BY ERROR',verticalalignment='bottom', horizontalalignment='left',transform=host1.transAxes,color='red', fontsize=15)
        if cmd_status ==3:
            host1.text(0., 1., 'CUSTOM PERIOD',verticalalignment='bottom', horizontalalignment='left',transform=host1.transAxes,color='blue', fontsize=15)
        
        host2 = fig.add_subplot(spec[1])
        plt.gca().xaxis.set_major_formatter(formatter)
        
        if dftorque is not None:        
            p13b, =host2.plot(dftorque['T'],dftorque['El1_mean'], color='chocolate',label="El S")
            p23b, =host2.plot(dftorque['T'],dftorque['El2_mean'], color='red',label="El N")
            p12b, =host2.plot(dftorque['T'],dftorque['Az1_mean'], color='lime',label="Az SE")
            p22b, =host2.plot(dftorque['T'],dftorque['Az2_mean'], color='forestgreen',label="Az NE")
            p32b, =host2.plot(dftorque['T'],dftorque['Az3_mean'], color='cyan',label="Az NW")
            p42b, =host2.plot(dftorque['T'],dftorque['Az4_mean'], color='dodgerblue',label="Az SW")
            host2.set_xlabel('Time', fontsize=15)
            host2.set_ylabel('Torque [N.m]', fontsize=15)
            host2.set_xlim(datetime.fromtimestamp(tmin, tz=pytz.utc),datetime.fromtimestamp(tmax, tz=pytz.utc))

            lines = [p13b,p23b,p12b,p22b,p32b,p42b]
            host2.legend(lines, [l.get_label() for l in lines],fontsize=13,title=addtext)
        
        #addhtmlfile(fichierhtml,figname)

        #plt.savefig(figname, bbox_inches='tight')
        plt.show()
        #plt.close() """
        return HttpResponse("Hello")
        #FigureTrack()