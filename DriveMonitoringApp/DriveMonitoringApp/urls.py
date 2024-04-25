"""
URL configuration for DriveMonitoringApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from DataStorage import views as Sv
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('driveMonitoring', Sv.driveMonitoring, name="driveMonitoring"),
    path('loadPins', Sv.loadPins, name="loadPins"),
    path('storage/index', Sv.index),
    path('storage/storeLogs', Sv.storeLogs),
    path('storage/storeData', Sv.storeData),
    path('storage/getLogs', Sv.getLogs),
    path('storage/getData', Sv.getData),
    path('storage/test', Sv.showTestView),
    path('storage/update', Sv.update),
    path('storage/delete', Sv.delete),
    path('storage/start', Sv.start),
    path('storage/plotGeneration', Sv.generateDatePlots),
    path('storage/checkUpToDate', Sv.checkUpToDate),



] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
