from datetime import datetime
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import gridspec
import pytz
import pandas as pd
import numpy as np
import math
from math import log
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, solar_system_ephemeris,ICRS
import plotly.graph_objects as go
import plotly.io as pio

def FigureTrack(dfpos,dfloadpin,dftrack,dftorque, path):
    fig = go.Figure()
    for i in range(0, len(dfpos)):
        if dfloadpin[i] is not None:
            mask107 = dfloadpin[i]['LoadPin']==107
            mask207 = dfloadpin[i]['LoadPin']==207
            loadPinSorted = dfloadpin[i].sort_values(by=["T"])
            if i == 0:
                fig.add_trace(go.Scatter(x=loadPinSorted[mask107]["T"], y=loadPinSorted[mask107]["Load"], line= dict(color="blue"), name="Cable 107", legendgroup="Cable 107"))
                fig.add_trace(go.Scatter(x=loadPinSorted[mask207]["T"], y=loadPinSorted[mask207]["Load"], line= dict(color="green"), name="Cable 207", legendgroup="Cable 207"))
            else:
                fig.add_trace(go.Scatter(x=loadPinSorted[mask107]["T"], y=loadPinSorted[mask107]["Load"], line= dict(color="blue"), name="Cable 107", legendgroup="Cable 107", showlegend=False))
                fig.add_trace(go.Scatter(x=loadPinSorted[mask207]["T"], y=loadPinSorted[mask207]["Load"], line= dict(color="green"), name="Cable 207", legendgroup="Cable 207", showlegend=False))



        dfposSorted = dfpos[i].sort_values(by=["T"])
        if i == 0:
            fig.add_trace(go.Scatter(x=dfposSorted["T"], y=dfposSorted["Az"], line= dict(color="red"), yaxis="y2", name="Azimuth", legendgroup="Azimuth"))
            fig.add_trace(go.Scatter(x=dfposSorted["T"], y=dfposSorted["ZA"], line= dict(color="black"), yaxis="y3", name="Zenith Angle", legendgroup="Zenith Angle"))
        else:
            fig.add_trace(go.Scatter(x=dfposSorted["T"], y=dfposSorted["Az"], line= dict(color="red"), yaxis="y2", name="Azimuth", legendgroup="Azimuth", showlegend=False))
            fig.add_trace(go.Scatter(x=dfposSorted["T"], y=dfposSorted["ZA"], line= dict(color="black"), yaxis="y3", name="Zenith Angle", legendgroup="Zenith Angle", showlegend=False))

        dftrackSorted = None
        if dftrack is not None:
            dftrackSorted = dftrack[i].sort_values(by=["T"])
            if i == 0:
                fig.add_trace(go.Scatter(x=dftrackSorted["Tth"], y=dftrackSorted["Azth"], line= dict(color="red", dash="dash"), yaxis="y2", name="Azimuth Th.", legendgroup="Azimuth Th."))
                fig.add_trace(go.Scatter(x=dftrackSorted["Tth"], y=dftrackSorted["ZAth"], line= dict(color="black", dash="dash"), yaxis="y3", name="Zenith Angle Th.", legendgroup="Zenith Angle Th."))
            else:
                fig.add_trace(go.Scatter(x=dftrackSorted["Tth"], y=dftrackSorted["Azth"], line= dict(color="red", dash="dash"), yaxis="y2", name="Azimuth Th.", legendgroup="Azimuth Th.", showlegend=False))
                fig.add_trace(go.Scatter(x=dftrackSorted["Tth"], y=dftrackSorted["ZAth"], line= dict(color="black", dash="dash"), yaxis="y3", name="Zenith Angle Th.", legendgroup="Zenith Angle Th.", showlegend=False))


            
    fig.update_layout(
        #title="My plot title",
        xaxis_tickformat = "%H:%M:%S",
        yaxis= dict(
            title="Load [KG]",
            titlefont=dict(
                color='blue'
            ),
            tickfont=dict(
                color='blue'
            ),
        ),
        yaxis2= dict(
            title="Azimuth [DEG]",
            titlefont=dict(
                color='red'
            ),
            tickfont=dict(
                color='red'
            ),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        yaxis3= dict(
            title="Zenith Angle [DEG]",
            titlefont=dict(
                color='black'
            ),
            tickfont=dict(
                color='black'
            ),
            anchor="free",
            overlaying="y",
            side="right",
            autoshift=True,
            #title_something to space the title from the ticks
            shift=30

        ),
        legend= dict( 
            orientation="h",
            yanchor="middle",
            y=1.2,
            xanchor="center",
            x=0.5,
        ),
    )
    figImg = go.Figure(fig)
    fig.write_html(path)
    #pio.write_image(figImg, path.replace(".html", ".png").replace("html", "img"), width=1080, height=720)

    fig2 = go.Figure()
    if dftorque is not None:
        for i in range(0, len(dftorque)):
            torqueSorted = dftorque[i].sort_values(by=["T"])
            if i == 0:
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['El1_mean'], line= dict(color="chocolate"), name="El S", legendgroup="El S"))
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['El2_mean'], line= dict(color="red"), name="El N", legendgroup="El N"))
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az1_mean'], line= dict(color="lime"), name="Az SE", legendgroup="Az SE"))
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az2_mean'], line= dict(color="forestgreen"), name="Az NE", legendgroup="Az NE"))
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az3_mean'], line= dict(color="cyan"), name="Az NW", legendgroup="Az NW"))
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az4_mean'], line= dict(color="dodgerblue"), name="Az SW", legendgroup="Az SW"))
            else:
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['El1_mean'], line= dict(color="chocolate"), name="El S", legendgroup="El S", showlegend=False))
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['El2_mean'], line= dict(color="red"), name="El N", legendgroup="El N", showlegend=False))
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az1_mean'], line= dict(color="lime"), name="Az SE", legendgroup="Az SE", showlegend=False))
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az2_mean'], line= dict(color="forestgreen"), name="Az NE", legendgroup="Az NE", showlegend=False))
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az3_mean'], line= dict(color="cyan"), name="Az NW", legendgroup="Az NW", showlegend=False))
                fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az4_mean'], line= dict(color="dodgerblue"), name="Az SW", legendgroup="Az SW", showlegend=False))



    fig2.update_layout(
        #title="My second interactive plot",
        xaxis_tickformat = "%H:%M:%S",
        xaxis= dict(
            title="Time"
        ),
        yaxis= dict(
            title="Torque [N.m]",
            titlefont=dict(
                color='black'
            ),
            tickfont=dict(
                color='black'
            ),
        ),
        legend= dict( 
            orientation="h",
            yanchor="middle",
            y=1.2,
            xanchor="center",
            x=0.5,
        ),
    )
    figImg2 = go.Figure(fig2)
    fig2.write_html(path.replace(".html", "-torque.html"))
    #pio.write_image(figImg2, path.replace(".html", "-torque.png").replace("html", "img"), width=1080, height=720)
    
#Used in GenerateFig
def FigAccuracyTime(addtext,dfacc, path):
    #TODO - https://community.plotly.com/t/fill-area-between-2-lines-solved/42865/3 Try if you can specify the Y axis number to have a "Zone" to fill.
    figname2 = "/Users/antoniojose/Desktop/data/example/data/R0/LST1/lst-drive/log/DisplayTrack/DriveMonitoringApp/DataStorage/static/img/generatedFig.png".replace(".png","_Diff.png")
    #addhtmlfile(fichierhtml,figname2)
    fig,hostd = plt.subplots(figsize = (25, 12))
    plt.gcf().subplots_adjust(left = 0.1, bottom = 0.1,right = 0.9, top = 0.9, wspace = 0.1, hspace = 0.1)

    #spec = gridspec.GridSpec(ncols=1, nrows=1,width_ratios=[4,1])
    #hostd = fig.add_subplot(0)

    formatter = mdates.DateFormatter("%H:%M:%S") ; 
    formatter.set_tzinfo(pytz.utc); 
    plt.gca().xaxis.set_major_formatter(formatter)

    pfill = plt.fill_between(dfacc['T'],-60.,60., color='palegreen',label="1' req.")
    pfill2 = plt.fill_between(dfacc['T'],-14.,14., color='limegreen',label="14'' req.")

    p1d = hostd.fill_between(dfacc['T'],dfacc['Azmax'],dfacc['Azmin'],facecolor='blue',alpha=0.5,label='Azimuth')
    p1bd = hostd.fill_between(dfacc['T'],dfacc['Zdmax'],dfacc['Zdmin'],facecolor='red',alpha=0.5,label='Zenith angle')

    hostd.set_ylabel("Pointing Error [arcsec]", fontsize=15)

    lines = [p1d,p1bd]

    hostd.axhline(y=0,xmin=0.05,xmax=0.95,linestyle='dotted')
    lines = [p1d,p1bd,pfill,pfill2]
    hostd.legend(lines, [l.get_label() for l in lines],fontsize=13,title=addtext)
    hostd.set_title(figname2, fontsize=15)    
    plt.legend()
    plt.savefig(figname2, bbox_inches='tight')
    plt.close()

def FigureRADec(dfpos,dfbm,ra,dec,dfacc,dftrack, path):  
    figname3 = f"/Users/antoniojose/Desktop/data/example/data/R0/LST1/lst-drive/log/DisplayTrack/DriveMonitoringApp/DataStorage/static/img/generatedFig.png".replace(".png","_SkyCoord.png")

    dfpos['AzSky'] = dfpos['Az']+dfbm['AzC']
    dfpos['ZASky'] = dfpos['ZA']+dfbm['ZAC']
    dfpos['AltSky'] = 90.- dfpos['ZASky']

    #print(dftrack)
    #print(dfbm)
    
    tracksky = None
    if dftrack is not None:
        tracksky = pd.merge(dftrack, dfbm, on="T",how='inner')
        tracksky['AzSky'] = tracksky['Azth']+tracksky['AzC']
        tracksky['ZASky'] = tracksky['ZAth']+tracksky['ZAC']
        tracksky['AltSky'] = 90.- tracksky['ZASky']
    #print(tracksky)

    lst=EarthLocation.from_geodetic(-17.8915 * u.deg, 28.7615 * u.deg, 2202* u.m)
    #print(dfpos)
    direc_lst = AltAz(location=lst, obstime=dfpos['T'],az=dfpos['AzSky'] * u.deg, alt=dfpos['AltSky'] * u.deg,obswl=0.35*u.micron,relative_humidity=0.5,temperature=10*u.deg_C,pressure=790*u.hPa)
    sky_lst = SkyCoord(direc_lst.transform_to(ICRS()))
    target = SkyCoord(ra=ra*u.deg,dec=dec*u.deg, frame='icrs')
    distsky = target.separation(sky_lst)

    if tracksky is not None:
        direc_lst_track = AltAz(location=lst, obstime=tracksky['Tth'],az=tracksky['AzSky'] * u.deg, alt=tracksky['AltSky'] * u.deg,obswl=0.35*u.micron,relative_humidity=0.5,temperature=10*u.deg_C,pressure=790*u.hPa)
        sky_lst_track = SkyCoord(direc_lst_track.transform_to(ICRS()))
        target_track = SkyCoord(ra=ra*u.deg,dec=dec*u.deg, frame='icrs')
        distsky_track = target.separation(sky_lst_track)

    #addhtmlfile(fichierhtml,figname3)

    #Here it starts to generate the Plot
    fig = plt.figure(figsize = (20, 12))
    plt.gcf().subplots_adjust(left = 0.1, bottom = 0.15,right = 0.9, top = 0.85, wspace = 0.1, hspace = 0.1)

    spec = gridspec.GridSpec(ncols=2, nrows=2)

    hostd = fig.add_subplot(spec[0])
    if tracksky is not None:
        plt.hist(sky_lst_track.ra.deg,bins=30,histtype='step',density=False,label='Drive target', alpha=0.7,linewidth=3)
    plt.hist(sky_lst.ra.deg,bins=30,histtype='step',density=False,label='Telescope pointing', alpha=0.7,linewidth=3)
    plt.axvline(x=ra, color='k', linestyle='--',label="Target")
    hostd.set_xlabel("RA[deg]", fontsize=15)
    #hostd.set_title(figname3, fontsize=15)    
    hostd.legend()

    hostd = fig.add_subplot(spec[1])
    if tracksky is not None:
        plt.hist(sky_lst_track.dec.deg,bins=30,histtype='step',density=False,label='Drive target', alpha=0.7,linewidth=3)
    plt.hist(sky_lst.dec.deg,bins=30,histtype='step',density=False,label='Telescope pointing', alpha=0.7,linewidth=3)
    plt.axvline(x=dec, color='k', linestyle='--',label="Target")
    hostd.set_xlabel("Declination[deg]", fontsize=15)
    #hostd.set_title(figname3, fontsize=15)    
    hostd.legend()

    hostd = fig.add_subplot(spec[2])
    if tracksky is not None:
        log10distsky_track = np.log10(distsky_track.deg*3600.)
        plt.hist(log10distsky_track,histtype='step',density=False,label='Drive target', alpha=0.7,linewidth=3)
    log10distsky = np.log10(distsky.deg*3600.)
    plt.hist(log10distsky,histtype='step',density=False,label='Telescope pointing', alpha=0.7,linewidth=3)
    for i in range(1,10):
        plt.axvline(x=math.log10(i), color='red', linestyle='--')
        plt.axvline(x=math.log10(i*10), color='blue', linestyle='--')
        plt.axvline(x=math.log10(i*100), color='k', linestyle='--')

    hostd.set_xlabel("Log10 Angular Distance to Target[arcsec]", fontsize=15)
    #hostd.set_title(figname3, fontsize=15)    
    hostd.legend()

    hostd = fig.add_subplot(spec[3])
    azmaxacc = np.log10(np.maximum(np.abs(dfacc.Azmax),np.abs(dfacc.Azmin)))
    zdmaxacc = np.log10(np.maximum(np.abs(dfacc.Zdmax),np.abs(dfacc.Zdmin)))

    plt.hist(np.log10(np.abs(dfacc.Azmean)),bins=30,histtype='step',density=True,label='Azimuth 2s average', alpha=0.7,linewidth=3)
    plt.hist(azmaxacc,bins=30,histtype='step', density=True,label='Azimuth 2s max', alpha=0.7,linewidth=3)
    plt.hist(np.log10(np.abs(dfacc.Zdmean)),bins=30,histtype='step',density=True,label='Elevation 2s average', alpha=0.7,linewidth=3)
    plt.hist(zdmaxacc,bins=30,histtype='step', density=True,label='Elevation 2s max', alpha=0.7,linewidth=3)
    plt.axvline(x=math.log10(30.), color='k', linestyle='--',label="30\"")
    plt.axvline(x=math.log10(4.e-02), color='red', linestyle='--',label="Encoder resolution")
    hostd.set_xlabel('log$_{10}$(Accuracy [arcsec])',fontsize=15)
    hostd.legend()

    plt.savefig(figname3, bbox_inches='tight')
    #plt.show()
    plt.close()
