#!/usr/bin/env python -O
# -*- coding: utf-8 -*-
"""
******************************************************************************
* Simple Threading XMLRPC-Server
******************************************************************************
"""


# from threading import *
from utilities import *
# from random import randint
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler  # ,SimpleXMLRPCServer

import ThreadedXMLRPCServer
import xmlrpclib
# import time
import sys
# import logging
import socket
import os
import os.path
# import subprocess
import settings
# import shutil

# Make sure STDOUT is unbuffered so the init output gets printed else all other output should be logged (with buffering)
# This should really be done ins CGSBaseServer.py class which absorb some other common things from the other CGS servers
# Do we need to manage file locks for threads as per logs? This assumes all prints are done before threading is launched
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)


class CGSServer:
    def __init__(self):
        start_msg = "__init__: Starting CGS Forwarder XMLRPC-Server at:\t" + str(socket.gethostname()) + ":" + str(settings.forwardServerPort)
        log_CFS(start_msg)
        print start_msg + "\nLogfile:\t" + settings.logFile

        #self.query_server() = xmlrpclib.Server("http://"+settings.query_server()Host+":"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
        #self.dataset_server = xmlrpclib.Server("http://"+settings.datasetServerHost+":"+str(settings.datasetServerPort),encoding='ISO-8859-1',allow_none=True)
        self.blockedServers = {}
        print "__init__: end"
        log_CFS("__init__: end")

    def query_server(self):
        return xmlrpclib.Server("http://"+settings.queryServerHost+":"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)

    def dataset_server(self):
        return xmlrpclib.Server("http://"+settings.datasetServerHost+":"+str(settings.datasetServerPort),encoding='ISO-8859-1',allow_none=True)

    def blockServer(self, serverName, serverRequestType="all"):
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
                queryServerStatus = self.query_server().getStatus()
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
                datasetServerStatus = self.dataset_server().getStatus()
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
        return self.query_server.activateUserDataset(datasetName)

    def getActiveServers(self, genome, onlyDefault=False, datasetType="Default"):
        print("getActiveServers genome="+str(genome)+" onlyDefault="+str(onlyDefault)+" datasetType="+str(datasetType))
        return self.query_server().getActiveServers(genome, onlyDefault, datasetType)

    def answerQueryRaw(self, queryUrl):
        return self.query_server().answerQueryRaw(queryUrl)

    def answerQuery(self, query, completions,hits, selectedRegionsSet,extraSettings="",detailedLog=False):
        #log_CFS(["answerQuery: called ",query, completions,hits, selectedRegionsSet,extraSettings,detailedLog])
        queryAnswer = self.query_server().answerQuery(query, completions,hits, selectedRegionsSet,extraSettings,detailedLog)

        return queryAnswer

    def exportQueryRegions(self, regionSet, query, mail):
        #log_CFS(["exportQueryRegions called",regionSet, query, mail])
        return self.query_server().exportQueryRegions(regionSet, query, mail)

    def exportQueryRegionAndSendBack(self, regionSet, query, exportType):
        #log_CFS(["exportQueryRegionAndSendBack called",regionSet, query, exportType])
        return self.query_server().exportQueryRegionAndSendBack(regionSet, query, exportType)

    def exportGenesAndSendBack(self, regionSet, query, exportType):
        #log_CFS(["exportQueryRegionAndSendBack called",regionSet, query])
        return self.query_server().exportGenesAndSendBack(regionSet, query, exportType)

    def exportGOsAndSendBack(self, regionSet, query):
        #log_CFS(["exportQueryRegionAndSendBack called",regionSet, query])
        return self.query_server().exportGOsAndSendBack(regionSet, query)

    def exportGOTermsAndSendBack(self, regionSet, query):
        #log_CFS(["exportQueryRegionAndSendBack called",regionSet, query])
        return self.query_server().exportGOTermsAndSendBack(regionSet, query)

    def exportOMIMTermsAndSendBack(self, regionSet, query):
        #log_CFS(["exportQueryRegionAndSendBack called",regionSet, query])
        return self.query_server().exportOMIMTermsAndSendBack(regionSet, query)

    def sendFeedbackEmail(self,ftype,name,email,feedback):
        #log_CFS(["sendFeedbackEmail: called with ",ftype,name,email,feedback])
        return self.query_server().sendFeedbackEmail(ftype,name,email,feedback)

    def getCoverages(self, genome, datasetName):
        return self.query_server().getCoverages(genome, datasetName)

    def exportQueryData(self, regionSet, query, mail, datasetKeys):
        #log_CFS(["exportQueryData called",regionSet, query, mail,datasetKeys])
        return self.dataset_server().exportQueryData(regionSet, query, mail, datasetKeys)

    def getDatasetInfo(self,datasetSimpleName,properties=[]):
        print "entrou getDatasetInfo", datasetSimpleName, properties
        #log_CFS("getDatasetInfo: dataset name "+datasetSimpleName)
        return self.dataset_server().getDatasetInfo(datasetSimpleName,properties)

    def getGeneExtraInfo(self,genome,infoType,elements):
        return self.dataset_server().getGeneExtraInfo(genome,infoType,elements)

    def processUserDatasetFromBuffer(self,datasetName, datasetBuffer, genome, additionalSettings, notificationEmail = "", syncCall = False,datasetLink="",datasetDesc="",computeSettings={}):
        #log_CFS(["processUserDatasetFromBuffer: called with ",str(datasetName),str(len(datasetBuffer)), str(genome), notificationEmail, syncCall,datasetLink,datasetDesc,computeSettings])
        return self.dataset_server().processUserDatasetFromBuffer(datasetName, datasetBuffer, str(genome), additionalSettings, notificationEmail, syncCall,datasetLink,datasetDesc,computeSettings)

    def getGenomicRegionProperties(self, genome, region, datasetsKeys=[]):
        #log_CFS(["getGenomicRegionProperties: called with ", genome, region, datasetsKeys])
        return self.dataset_server().getGenomicRegionProperties(self, genome, region, datasetsKeys)

    def getDatasetAnnotationSettings(self,genome,datasetName,onlyProperties):
        return self.dataset_server().getDatasetAnnotationSettings(genome,datasetName,onlyProperties)

    def getVisualizationFeatures(self,genome,regionSetName):
        return self.query_server().getVisualizationFeatures(genome,regionSetName)

    def getSelectionLink(self,selectionList):
        return self.dataset_server().getSelectionLink(selectionList)

    def getLinkSelection(self,queryHash):
        return self.dataset_server().getLinkSelection(queryHash)

    def getDatasetStatus(self,datasetID):
        return self.dataset_server().getDatasetStatus(datasetID)

    def getDatasetDescriptions(self, datasetSimpleName):
        return self.dataset_server().getDatasetDescriptions(datasetSimpleName);

    def recordUserLicence(self,userData):
        return self.dataset_server().recordUserLicense(userData)

    def storeData(self, name, software, data_format, data):
        return self.dataset_server().store_data(name, software, data_format, data)

    def processInfiniumDataset(self, file_internal_id, software, referenceDataset, datasetName, scoresIndex, hypoIndex, hyperIndex, rankIndex, notificationEmail, moreInfoLink, description):
        return self.dataset_server().processInfiniumDataset(file_internal_id, software, referenceDataset, datasetName, scoresIndex, hypoIndex, hyperIndex, rankIndex, notificationEmail, moreInfoLink, description)

    def getDatasetQueueStatus(self):
        return self.dataset_server().getDatasetQueueStatus()

    def stopComputation(self, datasetID):
        return self.dataset_server().stopDatasetComputation(datasetID)

if __name__ == '__main__':
    start_msg = "Starting CGSServer ThreadedXMLRPCServer:\t" + str(settings.forwardServerHost) + ":" + str(settings.forwardServerPort)
    log_CFS(start_msg)
    print(start_msg)
    server = ThreadedXMLRPCServer.ThreadedXMLRPCServer((settings.forwardServerHost, settings.forwardServerPort),
                                                       SimpleXMLRPCRequestHandler)
                                                       # , encoding='ISO-8859-1') #', allow_none=False)
    # server.request_queue_size = 2000
    server.register_instance(CGSServer())
    # server.socket_type = socket.SOCK_STREAM

    start_msg = "Running CGSServer ThreadedXMLRPCServer at:\t" + str(socket.gethostname()) + ":" + str(settings.forwardServerPort)
    log_CFS(start_msg)
    print(start_msg)

    # Write shared front/back end config
    fserver_file = settings.configFolder + "forwardServer.conf"

    try:
        conf_file = open(fserver_file, 'w')
        conf_file.write("SetEnv forwardServerHost " + str(socket.gethostname()) +
                        "\nSetEnv forwardServerPort " + str(settings.forwardServerPort) +
                        "\nSetEnv contact_email " + settings.contact_email)
        conf_file.close()
        print "Wrote forwardServer config. Keep this outside the web document root and add this to httpd.conf:\n" + \
              "\tInclude " + fserver_file
    except IOError, e:
        #warning("Failed to write forwardServer config to:\t" + fserver_file)
        raise IOError(e.args[0], e.args[1] + "\n\t" + fserver_file )

    write_pid_to_file("CGSServer.py", settings.configFolder + "CGSServers.pid.txt")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "CFS Server is stopping..."
