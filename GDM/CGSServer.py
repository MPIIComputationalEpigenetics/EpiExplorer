#!/usr/bin/env python -O 
# -*- coding: utf-8 -*- 
""" 
****************************************************************************** 
* Simple Threading XMLRPC-Server 
****************************************************************************** 
""" 


import ThreadedXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCServer,SimpleXMLRPCRequestHandler
import xmlrpclib
from random import randint 
import time
from threading import * 
import sys
import logging
import socket
import os
import os.path
import subprocess
import settings
import shutil

from utilities import *



class CGSServer:
    def __init__(self):   
        log_CFS("__init__: The CGS Forwarder XMLRPC-Server starts at host: "+str(socket.gethostname())+".")
        self.queryServer = xmlrpclib.Server("http://"+settings.queryServerHost+":"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
        self.datasetServer = xmlrpclib.Server("http://"+settings.datasetServerHost+":"+str(settings.datasetServerPort),encoding='ISO-8859-1',allow_none=True)
        self.blockedServers = {}     
        log_CFS("__init__: end")
    
    def blockServer(self,serverName,serverRequestType="all"):
        log_CFS("blockServer: '"+serverName+"' type '"+serverRequestType+"'")
        if serverName:
            if not self.blockedServers.has_key(serverName):        
                self.blockedServers[serverName] = {}
            self.blockedServers[serverName][serverRequestType] = True
        log_CFS("blockServer: blockedServers '"+str(self.blockedServers)+"' ")
        return self.blockedServers
    
    def unblockServer(self,serverName,serverRequestType="all"):
        log_CFS("unblockServer: '"+serverName+"' type '"+serverRequestType+"'")
        if self.blockedServers.has_key(serverName):
            if serverRequestType == "all":
                del self.blockedServers[serverName]
            if self.blockedServers[serverName].has_key(serverRequestType):
                del self.blockedServers[serverName][serverRequestType]
                if len(self.blockedServers[serverName].keys()) == 0:
                    del self.blockedServers[serverName]
        log_CFS("unblockServer: blockedServers '"+str(self.blockedServers)+"' ")
        return self.blockedServers
        
    def getStatus(self,serverName = "",serverRequestType="all"):
        #log_CFS("getStatus")
        status = ""
        if serverName and self.blockedServers.has_key(serverName):
            if serverRequestType == "all" or \
               self.blockedServers[serverName].has_key(serverRequestType) or \
               self.blockedServers[serverName].has_key("all"):
                status = "The server '"+serverName+"' type '"+serverRequestType+"' is blocked!"
        else:
            socket.setdefaulttimeout(5)            #set the timeout to 10 seconds
            try:
                queryServerStatus = self.queryServer.getStatus()
                if queryServerStatus != "OK":
                    status = "Query server: "+queryServerStatus+". "        
            except socket.error,ex:
                log_CFS("getStatus:Error query server "+str(ex))            
                status = "The query server is not started. "
            except Exception,ex:
                log_CFS("getStatus:Error query server "+str(ex))            
                status = "There is a problem with the query server. "
            
            socket.setdefaulttimeout(15)    
            try:
                datasetServerStatus = self.datasetServer.getStatus()
                if datasetServerStatus != "OK":
                    status += "Dataset server: "+datasetServerStatus+". "
            except socket.error,ex:
                log_CFS("getStatus:Error dataset server "+str(ex))
                status += "The dataset server is not started."
            except Exception,ex:
                log_CFS("getStatus:Error dataset server "+str(ex))            
                status = "There is a problem with the query server. "
            if status == "":
                status = "OK"
            socket.setdefaulttimeout(None)        
        #log_CFS("getStatus:status is "+str(status))
        return status
    
    def log_me(self,msg):
        log_CFS("log_me: "+msg)
        return 1 
            
    def echo(self,st):
        return "Echoed: "+st
    
    def activateUserDataset(self,datasetName):
        #log_CFS("activateUserDataset with "+str(datasetName))
        return self.queryServer.activateUserDataset(datasetName)
    
    def getActiveServers(self, genome, onlyDefault=False, datasetType="Default"):
        #log_CFS("getActiveServers genome="+str(genome)+" onlyDefault="+str(onlyDefault)+" datasetType="+str(datasetType))
        return self.queryServer.getActiveServers(genome, onlyDefault, datasetType)
    
    def answerQueryRaw(self, queryUrl):        
        return self.queryServer.answerQueryRaw(queryUrl)
    
    def answerQuery(self, query, completions,hits, selectedRegionsSet,extraSettings="",detailedLog=False):
        #log_CFS(["answerQuery: called ",query, completions,hits, selectedRegionsSet,extraSettings,detailedLog])
        queryAnswer = self.queryServer.answerQuery(query, completions,hits, selectedRegionsSet,extraSettings,detailedLog)
        
        return queryAnswer
    
    def exportQueryRegions(self, regionSet, query, mail):
        #log_CFS(["exportQueryRegions called",regionSet, query, mail])
        return self.queryServer.exportQueryRegions(regionSet, query, mail)
    
    def exportQueryRegionAndSendBack(self, regionSet, query, exportType):
        #log_CFS(["exportQueryRegionAndSendBack called",regionSet, query, exportType])
        return self.queryServer.exportQueryRegionAndSendBack(regionSet, query, exportType)    
    
    def exportGenesAndSendBack(self, regionSet, query, exportType):
        #log_CFS(["exportQueryRegionAndSendBack called",regionSet, query])
        return self.queryServer.exportGenesAndSendBack(regionSet, query, exportType)
    
    def exportGOsAndSendBack(self, regionSet, query):
        #log_CFS(["exportQueryRegionAndSendBack called",regionSet, query])
        return self.queryServer.exportGOsAndSendBack(regionSet, query)
    
    def exportGOTermsAndSendBack(self, regionSet, query):
        #log_CFS(["exportQueryRegionAndSendBack called",regionSet, query])
        return self.queryServer.exportGOTermsAndSendBack(regionSet, query)
    
    def exportOMIMTermsAndSendBack(self, regionSet, query):
        #log_CFS(["exportQueryRegionAndSendBack called",regionSet, query])
        return self.queryServer.exportOMIMTermsAndSendBack(regionSet, query)
    
    def sendFeedbackEmail(self,ftype,name,email,feedback):
        #log_CFS(["sendFeedbackEmail: called with ",ftype,name,email,feedback])
        return self.queryServer.sendFeedbackEmail(ftype,name,email,feedback)
    
    def getCoverages(self, genome, datasetName):
        return self.queryServer.getCoverages(genome, datasetName)
                        
    def exportQueryData(self, regionSet, query, mail, datasetKeys):
        #log_CFS(["exportQueryData called",regionSet, query, mail,datasetKeys])
        return self.datasetServer.exportQueryData(regionSet, query, mail, datasetKeys)
    
    def getDatasetInfo(self,datasetSimpleName,properties=[]):
        #log_CFS("getDatasetInfo: dataset name "+datasetSimpleName)
        return self.datasetServer.getDatasetInfo(datasetSimpleName,properties)
    
    def getGeneExtraInfo(self,genome,infoType,elements):                
        return self.datasetServer.getGeneExtraInfo(genome,infoType,elements)

#    def processUserDataset(self,datasetName, regionsFile, genome, additionalSettings, notificationEmail="", syncCall = False,datasetLink="",datasetDesc="",computeReference=False):
#        #log_CFS(["processUserDataset: called with ",str(datasetName),regionsFile, str(genome), notificationEmail, syncCall,datasetLink,datasetDesc])
#        return self.datasetServer.processUserDataset(datasetName, regionsFile, str(genome),additionalSettings, notificationEmail, syncCall,datasetLink,datasetDesc,computeReference)
    
    def processUserDatasetFromBuffer(self,datasetName, datasetBuffer, genome, additionalSettings, notificationEmail = "", syncCall = False,datasetLink="",datasetDesc="",computeSettings={}):
        #log_CFS(["processUserDatasetFromBuffer: called with ",str(datasetName),str(len(datasetBuffer)), str(genome), notificationEmail, syncCall,datasetLink,datasetDesc,computeSettings])
        return self.datasetServer.processUserDatasetFromBuffer(datasetName, datasetBuffer, str(genome), additionalSettings, notificationEmail, syncCall,datasetLink,datasetDesc,computeSettings)        
    
    def getGenomicRegionProperties(self, genome, region, datasetsKeys=[]):
        #log_CFS(["getGenomicRegionProperties: called with ", genome, region, datasetsKeys])
        return self.datasetServer.getGenomicRegionProperties(self, genome, region, datasetsKeys)
    
    def getDatasetAnnotationSettings(self,genome,datasetName,onlyProperties):
        return self.datasetServer.getDatasetAnnotationSettings(genome,datasetName,onlyProperties)
    
    def getVisualizationFeatures(self,genome,regionSetName):
        return self.queryServer.getVisualizationFeatures(genome,regionSetName)
    
    def getSelectionLink(self,selectionList):
        return self.datasetServer.getSelectionLink(selectionList)
    
    def getLinkSelection(self,queryHash):
        return self.datasetServer.getLinkSelection(queryHash)
    
    def getDatasetStatus(self,datasetID):
        return self.datasetServer.getDatasetStatus(datasetID)
    
    def getDatasetDescriptions(self, datasetSimpleName):
        return self.datasetServer.getDatasetDescriptions(datasetSimpleName);
    
    def recordUserLicence(self,userData):
        return self.datasetServer.recordUserLicense(userData)
    
    def storeData(self, name, software, data_format, data):
        return self.datasetServer.store_data(name, software, data_format, data)
    
    def processInfiniumDataset(self, file_internal_id, software, referenceDataset, datasetName, scoresIndex, hypoIndex, hyperIndex, rankIndex, notificationEmail, moreInfoLink, description):
        return self.datasetServer.processInfiniumDataset(file_internal_id, software, referenceDataset, datasetName, scoresIndex, hypoIndex, hyperIndex, rankIndex, notificationEmail, moreInfoLink, description)
    
    def getDatasetQueueStatus(self):
        return self.datasetServer.getDatasetQueueStatus()   
    
    def stopComputation(self, datasetID):
        return self.datasetServer.stopDatasetComputation(datasetID) 

if __name__ == '__main__':   
    cfsServer = CGSServer()     
    s = getForwardServer(settings.instanceServer)
    print s
    server = ThreadedXMLRPCServer.ThreadedXMLRPCServer(s, SimpleXMLRPCRequestHandler)#, encoding='ISO-8859-1') #', allow_none=False)
    #server.request_queue_size = 2000
    server.register_instance(cfsServer)
    #server.socket_type = socket.SOCK_STREAM
    log_CFS("The CGS Forwarder XMLRPC-Server runs at host: "+str(s[0])+", port: "+str(s[1])+".")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "CFS Server is stopping..."

