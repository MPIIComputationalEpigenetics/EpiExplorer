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
import urllib
import logging
import socket
import traceback
import xmlrpclib
import os.path

import subprocess
import readDatasetDescriptions
from utilities import *
import settings
import CSQuery
import CGSServerEngine
import ReportManager
       
# Make sure STDOUT is unbuffered so the init output gets printed else all other output should be logged (with buffering)
# This should really be done ins CGSBaseServer.py class which absorb some other common things from the other CGS servers
# Do we need to manage file locks for threads as per logs? This assumes all prints are done before threading is launched
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)


class CGSQueryServer():
    def __init__(self):
        start_msg = "__init__: Starting CGS Query XMLRPC-Server at:\t" + str(socket.gethostname()) + ":" + str(settings.queryServerPort)
        log_CQS(start_msg)
        print start_msg + "\nLog file:\t" + settings.logFile
        self.servers = {} 
        self.serverPorts = {}
        #This holds the information for all currently started servers
        self.activeDatasetInfo = {}
        #connect to the dataset server
        self.datasetServer = xmlrpclib.Server("http://"+settings.datasetServerHost+":"+str(settings.datasetServerPort),encoding='ISO-8859-1',allow_none=True)
        
        self.__waitForDatasetServer__()
                    
#       # A variable for the preprocessed visualization settings
        self.visualizationSettings = {}
        
        self.coverageData = {}
        
        self.runningUserServers = {}
        
        self.csManager = Timer(settings.CS_TIME_CHECK_TIME, self.cleanOldCS) # run each hour
        self.csManager.start()
        
        self.reportManager = ReportManager.ReportManager(self.datasetServer)
        self.reportTimer = Timer(self.reportManager.getRemainingTimeUntilNextEvent(6,0), self.collectAndSendReport) # run each hour
        self.reportTimer.start()
        
        # kill all started CS servers
        log_CQS("__init__: killing any CS servers left from previous sessions")
        if os.path.isfile(settings.startedServersFile):
            f = open(settings.startedServersFile)
            lines = f.readlines()
            for line in lines:
                lineParts =  line.strip().split("\t")
                if len(lineParts) == 2:
                    self.__stopServerByPort__(lineParts[1])
                elif len(lineParts) < 2:
                    pass
                else:
                    raise GDMException, "Error: "+"Invalid line in the started CS servers file "+ line
            os.unlink(settings.startedServersFile)
            
        #refresh the processed servers
        log_CQS("__init__: Loading information about the available datasets")
        self.fullyProcessedDefaultDatasets = {}
        self.fullyProcessedUserDatasets = {}
        self.refreshFullyProcessedServers()
        
        log_CQS("__init__: Starting a server for every available default dataset")        
        for processedDataset in self.fullyProcessedDefaultDatasets.keys():        
            #retcode = subprocess.call(["cd", settings.indexDataFolder[self.fullyProcessedDefaultDatasets[processedDataset].genome]], shell=True)    
            self.startServer(processedDataset,True,True)
            time.sleep(2)
        # 02.02.2011 KH Switching of the II27 datasets fr now
        #log_CQS("__init__: Starting a server for every available II27 dataset")
        #userDatasetsInfo = self.datasetServer.getDatasetInfo("all")
        #for processedDataset in self.fullyProcessedUserDatasets.keys():
        #    if userDatasetsInfo[processedDataset]["datasetType"] == "II27":             
        #        self.startServer(processedDataset,False)
        #        time.sleep(2)
        log_CQS("__init__: end")
        
    def __waitForDatasetServer__(self):
        def isDatasetEchoDifferent():
            echoMsg = "abc"
            try:
                res = self.datasetServer.echo(echoMsg)
            except:
                res = "fail"
            return res != echoMsg  
        
        sleepTime = 60        
        while isDatasetEchoDifferent():
            print "Appears that the dataset server is not loaded yet, waiting",sleepTime,"seconds"
            time.sleep(sleepTime)
    
    def refreshFullyProcessedServers(self):
        log_CQS("refreshFullyProcessedServers called")
        self.fullyProcessedDefaultDatasets = {}
        for genomeID in settings.fullyProcessedDefaultDatasetsFile.keys():
            genomeDefaultDatasets = readSettingsFile(settings.fullyProcessedDefaultDatasetsFile[genomeID])
            self.fullyProcessedDefaultDatasets.update(genomeDefaultDatasets)        
        log_CQS("refreshFullyProcessedServers: Current available processed datasets are "+",".join(self.fullyProcessedDefaultDatasets.keys()))
        self.fullyProcessedUserDatasets = {}
        for genomeID in settings.fullyProcessedUserDatasetsFile.keys():
            genomeUserDatasets = readSettingsFile(settings.fullyProcessedUserDatasetsFile[genomeID])
            self.fullyProcessedUserDatasets.update(genomeUserDatasets)        
        log_CQS("refreshFullyProcessedServers end\n\tdefaultDatasets= "+str(self.fullyProcessedDefaultDatasets.keys())+"\n\tuserDatasets= "+str(self.fullyProcessedUserDatasets.keys()))
        return True
        
    def echo(self, msg):
        log_CQS("echo called"+msg)
        #print "echo: Request received "+str(msg)
        #time.sleep(10)
        return str(msg)
    
    def log_me(self,msg):
        log_CQS("log_me: "+msg)    
    
    def exportQueryRegionAndSendBack(self, regionSet, query, exportType):        
        log_CQS(["exportQueryRegionAndSendBack called",regionSet, query, exportType])
        if not self.activeDatasetInfo.has_key(regionSet):
            activateRegion = self.activateUserDataset(regionSet)
            if activateRegion[0] == 1:
                return activateRegion
        if query:
            queryParts = query.strip().split("::qq::")
        else:
            queryParts = []
        totalIds = CGSServerEngine.getIDsfromQuery(regionSet,queryParts)
        log_CQS("exportQueryRegionAndSendBack total IDs processed "+str(len(totalIds)))
        regionsContent = CGSServerEngine.convertIDsToSingleExportStr("exportRegions",totalIds)
        log_CQS("exportQueryRegionAndSendBack regionsContent processed "+str(len(regionsContent)))
        if exportType == "UCSC":
            header = "## Export of custom EpiExplorer track to UCSC genome browser\n"
            firstLine = regionsContent[:regionsContent.find("\n")].strip().split("\t")
            header += "browser position "+firstLine[0]+":"+firstLine[1]+"-"+firstLine[2]+"\n"
            header += 'track name=EpiExplorer description="'+regionSet+'" visibility=2 url="http://epiexplorer.mpi-inf.mpg.de/index.php?userdatasets='+regionSet+'"\n'
            regionsContent = header+ regionsContent
        return regionsContent
    def exportGenesAndSendBack(self, regionSet, query, exportType):
        log_CQS(["exportGenesAndSendBack called",regionSet, query,exportType]) 
        if not self.activeDatasetInfo.has_key(regionSet):
           activateRegion = self.activateUserDataset(regionSet)
           if activateRegion[0] == 1:
                return activateRegion    
        if query:
            queryParts = query.strip().split("::qq::")
        else:
            queryParts = []
        allGenes = CGSServerEngine.getGenesFromQuery(regionSet, queryParts, exportType)
        log_CQS("exportGenesAndSendBack total genes processed "+str(len(allGenes)))
        if len(allGenes):
            regionsContent = "\n".join(map(lambda gene:"\t".join(gene),allGenes))
        else:
            regionsContent = "<this query resulted in no genes. If you believe this to be a mistake, please contact epiexplorer@mpi-inf.mpg.de>"
        log_CQS("exportGenesAndSendBack regionsContent processed "+str(len(regionsContent)))
        return regionsContent
    def exportGOsAndSendBack(self,regionSet,query):
        log_CQS(["exportGOsAndSendBack called",regionSet, query])
        if not self.activeDatasetInfo.has_key(regionSet):
           activateRegion = self.activateUserDataset(regionSet)
           if activateRegion[0] == 1:
                return activateRegion        
        if query:
            queryParts = query.strip().split("::qq::")
        else:
            queryParts = []
        try:
            allGOCategories = CGSServerEngine.getGOCategoriesFromQuery(regionSet,queryParts)
        except GDMException, ex:
            print "Exception:"+ex
            allGOCategories = {}
        log_CQS("exportGenesAndSendBack total GO categories processed "+str(len(allGOCategories)))
        if len(allGOCategories):
            allGOCategoriesList = map(lambda goTerm:allGOCategories[goTerm]+[goTerm],allGOCategories.keys())
            allGOCategoriesList.sort()
            allGOCategoriesList.reverse()
            goExport = "\n".join(map(lambda go:"\t".join(map(str,[go[-1][4:]]+go[1:4]+[go[0]])),allGOCategoriesList))
        else:
            goExport = "<this query resulted in no GO categories. If you believe this to be a mistake, please contact epiexplorer@mpi-inf.mpg.de>"
        log_CQS("exportGOsAndSendBack regionsContent processed "+str(len(goExport)))
        return goExport
        
    def exportGOTermsAndSendBack(self,regionSet,query):
        log_CQS(["exportGOTermsAndSendBack called",regionSet, query])  
        if not self.activeDatasetInfo.has_key(regionSet):
            activateRegion = self.activateUserDataset(regionSet)
            if activateRegion[0] == 1:
                return activateRegion     
        if query:
            queryParts = query.strip().split("::qq::")
        else:
            queryParts = []
        allGOterms = CGSServerEngine.getGOtermsFromQuery(regionSet,queryParts)
        log_CQS("exportGOTermsAndSendBack total GO terms processed "+str(len(allGOterms)))
        if len(allGOterms):
            allGOtermsList = map(lambda k:[allGOterms[k],k],allGOterms.keys())
            allGOtermsList.sort()
            allGOtermsList.reverse()
            termContent = "\n".join(map(lambda term:str(term[1])+"\t"+str(term[0]),allGOtermsList))
        else:
            termContent = "<this query resulted in no terms. If you believe this to be a mistake, please contact epiexplorer@mpi-inf.mpg.de>"
        log_CQS("exportGOTermsAndSendBack regionsContent processed "+str(len(termContent)))
        return termContent    
    
    def exportOMIMTermsAndSendBack(self,regionSet,query):
        log_CQS(["exportOMIMTermsAndSendBack called",regionSet, query])
        if not self.activeDatasetInfo.has_key(regionSet):
           activateRegion = self.activateUserDataset(regionSet)
           if activateRegion[0] == 1:
                return activateRegion        
        if query:
            queryParts = query.strip().split("::qq::")
        else:
            queryParts = []
        allGOterms = CGSServerEngine.getOMIMtermsFromQuery(regionSet,queryParts)
        log_CQS("exportOMIMTermsAndSendBack total OMIM terms processed "+str(len(allGOterms)))
        if len(allGOterms):
            allGOtermsList = map(lambda k:[allGOterms[k],k],allGOterms.keys())
            allGOtermsList.sort()
            allGOtermsList.reverse()
            termContent = "\n".join(map(lambda term:str(term[1])+"\t"+str(term[0]),allGOtermsList))
        else:
            termContent = "<this query resulted in no terms. If you believe this to be a mistake, please contact epiexplorer@mpi-inf.mpg.de>"
        log_CQS("exportOMIMTermsAndSendBack regionsContent processed "+str(len(termContent)))
        return termContent     
                    
    def exportQueryRegions(self, regionSet, query, mail):
        log_CQS(["exportQueryRegions called",regionSet, query, mail])
        if not self.activeDatasetInfo.has_key(regionSet):
            activateRegion = self.activateUserDataset(regionSet)
            if activateRegion[0] == 1:
                return activateRegion
        if query:                
            subprocess.Popen(["python",getCurrentFolder()+"CGSServerEngine.py","exportRegions",str(regionSet),str(query),str(mail)])
        else:
            subprocess.Popen(["python",getCurrentFolder()+"CGSServerEngine.py","exportRegions",str(regionSet),"None",str(mail)])
        log_CQS(["exportQueryRegions end"])        
            
    def __startServerTestServer__(self,query,datasetName):
        log_CQS("__startServerTestServer__: ...testing the server by sending an '"+str(query)+"' query")
        try:
            queryAnswer = self.answerQuery(query,0,0,datasetName)
        except IOError:
            log_CQS("startServer: did not start in 5 seconds, waiting another 15")
            time.sleep(15)
            try:                    
                queryAnswer = self.answerQuery(query,0,0,datasetName)
            except IOError:
                log_CQS("startServer: did not start in 20 seconds, waiting another 60")
                time.sleep(60)
                try:
                    queryAnswer = self.answerQuery(query,0,0,datasetName)
                except IOError:
                    log_CQS("startServer: did not start in 60 seconds, waiting another 180")
                    time.sleep(180)
                    queryAnswer = self.answerQuery(query,0,0,datasetName)
        return queryAnswer
        
    def startServer(self, datasetName, isDefault = False, runRefreshQueries = False):
        log_CQS(["startServer called",datasetName, isDefault, runRefreshQueries])
        try:
            self.activeDatasetInfo[datasetName] = self.datasetServer.getDatasetInfo(datasetName)
        except Exception, ex:
            log_CQS("startServer:Error "+str(ex)+" this is either due to the DATASET SERVER NOT STARTED or some problem with the datasetName ("+datasetName+")")
#                self.activeDatasetInfo[datasetName] = {
#                            "simpleName":datasetName,
#                            "officialName":datasetName,
#                            "genome":,
#                            "categories":[datasetName],
#                            "description":"Not available",
#                            "moreInfoLink":"Not available",
#                            "datasetType":"Default",
#                            "numberOfRegions":None,
#                            "isDefault":isDefault
#                            }
            raise 
        genome = self.activeDatasetInfo[datasetName]["genome"]
        #basic check
        if not os.path.isfile(settings.indexDataFolder[genome]+datasetName+".hybrid"):
            extext = "Error: "+"The main hybrid file "+settings.indexDataFolder[genome]+datasetName+".hybrid for the server "+datasetName+" does not exist!"
            log_CQS("startServer:Error "+extext)            
            raise GDMException,extext 
            
        port = settings.csPortsStart + (hash(datasetName+str(time.time())) % settings.csPortsMaxNumber)
        while self.serverPorts.has_key(port):
            port += 1
        try:            
            hibridSize = int(os.path.getsize(settings.indexDataFolder[genome]+datasetName+".hybrid")) 
            historySize = str(min(2*hibridSize,2*1024*1024*1024))
            cashSize = str(min(2*hibridSize,1024*1024*1024))
        except:
            historySize = str(2*1024*1024*1024)
            cashSize = str(1024*1024*1024)

        #retcode = subprocess.call(["cd", settings.indexDataFolder[genome]], shell=True)
        serverArguments = [
                           settings.startCompletionServer,# standard start                           
                           "--locale=en_US.utf8",
                           # the locale of the server and the text. This is not related to the POSIX based sorting
                           #Move this to settings.defaults.py?
#                           "--normalize-words", # not sure
                           "--log-file="+datasetName+".log",# the log file, this is the standard name
                           "--port="+str(port),#the port on which the server is going to be running
                           "-c "+cashSize,# cash size for the excerpt generator
                           "-h "+historySize,# history size
                           "-q 10000",#number of queroes storedin the history(impl is quadratic)
#                            "-r",# automatically restart the server on crash
#                            "-m",#multithreading
#                            "-d 1",#documents should be ranked by document ID, hopefully this will save some
#                            "-w 1",#words should be sorted by documents count
                            "-T",#do not return document titles as links
#                            "-P .completesearch_"+socket.gethostname()+"_"+str(port)+".pid",# name of file containing the process id,first %s will be replaced by host name, second %s will be replaced by port.
                            datasetName+".hybrid" # the file name of the main hybrid file
                           ]

        log_CQS("startServer: Starting " + datasetName + " CS instance:\t" + " ".join(serverArguments))     

        p = subprocess.call(serverArguments,cwd=settings.indexDataFolder[genome])

        #Is this error caught? We don't really want to die here, but early exit with error log would
        #be good. How are these errors displayed in the interface?
        #Can we return False early to signify failure. 

        if not isDefault:
            self.__updateRunningUserCSServer__(datasetName)           
        self.servers[datasetName] = port
        self.serverPorts[port] = datasetName
                
        try:
            time.sleep(5)
            queryAnswer = retryCall(lambda:self.__startServerTestServer__(settings.wordPrefixes["region"],datasetName),3,5)            
            # load all the info for this dataset
            # This assumes two things
            # 1. the dataset server is currently started
            # 2. the dataset server has info for this region
                        
            numberOfRegions = int(queryAnswer[2])
            self.activeDatasetInfo[datasetName]["numberOfRegions"] = numberOfRegions
            self.datasetServer.updateDatasetInfo(datasetName, "numberOfRegions", numberOfRegions)
            self.activeDatasetInfo[datasetName]["isDefault"] = isDefault
            log_CQS("startServer: Success "+str(queryAnswer))
        except Exception, ex:
            log_CQS("startServer:Error: "+ str(ex))            
            self.__stopServerByPort__(str(port))
            raise
		#preprocess the overlap query which is very standard for the server
        if runRefreshQueries:
            self.__startServerTestServer__(settings.wordPrefixes["region"]+" "+settings.wordPrefixes["overlap"]+":*",datasetName)                        
            self.__startServerTestServer__(settings.wordPrefixes["region"]+" "+settings.wordPrefixes["overlap10p"]+":*",datasetName)
            self.__startServerTestServer__(settings.wordPrefixes["region"]+" "+settings.wordPrefixes["overlap50p"]+":*",datasetName)
        self.getVisualizationFeatures(genome,datasetName)
              
        f = open(settings.startedServersFile,"a")
        f.write(datasetName+"\t"+str(port)+"\n") 
        f.close() 
        log_CQS("startServer: end")
        return True
                
        
    def stopServer(self, datasetName):
        log_CQS("stopServer: Trying to kill the server for "+datasetName)
        if not self.servers.has_key(datasetName):
            extext = "The CS server for "+datasetName+" is not started, or at least we don't have information for it"
            log_CQS("stopServer:Error: "+extext)
            raise GDMException,extext      
        self.__stopServerByPort__(self.servers[datasetName])
        if self.runningUserServers.has_key(datasetName):
            del self.runningUserServers[datasetName]
        log_CQS("stopServer: end")
        return True
        
    def __stopServerByPort__(self,port):
        log_CQS("__stopServerByPort__: Trying to kill the server at port "+str(port))
        #retcode = subprocess.call(["cd", settings.indexDataFolder[genome]], shell=True)
        serverArguments = [
                           settings.startCompletionServer,# standard start
                           "-k "+str(port)#the port on which the server is going to be running,
#                           "-P .completesearch_"+socket.gethostname()+"_"+str(port)+".pid"                        
                           ]
        p = subprocess.call(serverArguments)
        #remove the server from the local structures        
        if self.serverPorts.has_key(int(port)):
            try:
                datasetName = self.serverPorts[port]
                del self.servers[datasetName]            
                del self.activeDatasetInfo[datasetName]
            except Exception,ex:
                log_CQS("__stopServerByPort__:Error "+str(ex))                
            del self.serverPorts[port]
        #delete the server from the files
        f = open(settings.startedServersFile)
        newlines = filter(lambda x:not ("\t"+str(port)+"\n" in x), f.readlines())
        f.close()
        fw = open(settings.startedServersFile,"w")
        fw.write("".join(newlines)) 
        fw.close()
            
    
    def answerQueryRaw(self, queryUrl):
        try:        
            queryAnswerXML = urllib.urlopen(queryUrl).read()
        except Exception, ex:
            queryAnswerXML = str(ex)
        return queryAnswerXML
        
    def answerQuery(self, query, completions,hits, selectedRegionsSet,extraSettings="",detailedLog=False):
        log_CQS(["answerQuery: called ",query, completions,hits, selectedRegionsSet,extraSettings])
        # return (self.query,self.totalCompletions,self.totalHits,self.completions,self.hits)
        if selectedRegionsSet:
            try:
                if not self.servers.has_key(selectedRegionsSet):
                    asr = self.activateUserDataset(selectedRegionsSet)
                    if asr[0] == 1:
                        #error
                        extext = "No proper region set is specified "+selectedRegionsSet+str(self.servers.keys())
                        log_CQS("answerQuery:Error: "+extext)
                        raise Exception,extext
                query = query.replace("#","%23")
                query = query.replace("&","%26")
                query = "http://"+socket.gethostname()+":"+str(self.servers[selectedRegionsSet])+"/?q="+query+"&c="+str(completions)+"&h="+str(hits)
                if extraSettings:
                    query = query + "&"+extraSettings            
                # maybe
    #            query += "&er=0&rd=1&rw=1"
                log_CQS("answerQuery: Query: "+query)
                queryResult = retryCall(lambda:CSQuery.getQueryResult(query,detailedLog),3,5)
                if detailedLog:
                    log_CQS("answerQuery: Query result: "+str(queryResult))
                else:
                    log_CQS("answerQuery: Query result: "+str(queryResult[:3]))
            except Exception,ex:
                log_CQS(["Error: problem with the query ",query, completions,hits, selectedRegionsSet,extraSettings,detailedLog,str(ex)])
                queryResult = ["There was a problem with your query",0,0,{},{}]
            return queryResult
        else:
            extext = "No proper region set is specified "+selectedRegionsSet+str(self.servers.keys())
            log_CQS("answerQuery:Error: "+extext)
            raise Exception,extext
         
    
    def getActiveServers(self, genome, onlyDefault=False, datasetType="Default"):
        log_CQS("getActiveServers:called with genome="+str(genome)+" onlyDefault="+str(onlyDefault)+" datasetType="+str(datasetType))
        returnedServers = {}
        
        for serverKey in self.activeDatasetInfo.keys():
            if onlyDefault:
                 if not self.activeDatasetInfo[serverKey].has_key('isDefault'):
                     self.activeDatasetInfo[serverKey] = False
                     log_CQS("getActiveServers:Error: no 'isDefault' attribute for region "+serverKey)
                     continue
                 elif not self.activeDatasetInfo[serverKey]['isDefault']:                                
                    continue
            if not self.activeDatasetInfo[serverKey].has_key('datasetType') and datasetType != "Default":
                log_CQS("getActiveServers:Error: "+str(serverKey)+" does not have datasetType")
                continue            
            if self.activeDatasetInfo[serverKey]['datasetType'] != datasetType:
                continue
            if self.activeDatasetInfo[serverKey]['genome'] != genome:
                continue 
            returnedServers[serverKey] = self.activeDatasetInfo[serverKey]
         
        log_CQS("getActiveServers:end "+str(returnedServers.keys()))
        return returnedServers
        
    
    def getAvailableUserDatasets(self):
        log_CQS("getAvailableUserDatasets called")
        log_CQS("getAvailableUserDatasets end "+str(self.fullyProcessedUserDatasets.keys()))
        return self.fullyProcessedUserDatasets.keys()
    
    def getDatasetNumberOfCases(self,datasetName):
        log_CQS("getDatasetNumberOfCases called "+datasetName)
        if not self.activeDatasetInfo.has_key(datasetName):
            log_CQS("getDatasetNumberOfCases end -1")
            return -1
        else:
            log_CQS("getDatasetNumberOfCases end "+str(self.activeDatasetInfo[datasetName]["numberOfRegions"]))
            return self.activeDatasetInfo[datasetName]["numberOfRegions"]
            
    
    def activateUserDataset(self,datasetName):
        log_CQS("activateUserDataset called "+datasetName)
        if not self.fullyProcessedUserDatasets.has_key(datasetName):
            log_CQS("activateUserDataset end "+"No user dataset with the name: '"+datasetName+"'")
            return [1,"No user dataset named: '"+datasetName+"'"]
        if not self.activeDatasetInfo.has_key(datasetName):
            # Server is not active
            log_CQS("activateUserDataset server is not active, so starting it")
            try:
                self.startServer(datasetName, False, False)
            except Exception,ex:                
		log_CQS("error activateUserDataset: " + str(ex))
                return [1,"Error:" +str(ex)+" '"+datasetName+"'"]
        else:
        	#update the running time with the last requested time
            self.__updateRunningUserCSServer__(datasetName)
        log_CQS("activateUserDataset end")
        return [0,"Your dataset is now active",self.activeDatasetInfo[datasetName]]
    
    def sendFeedbackEmail(self,ftype,name,email,feedback):
        log_CQS(["sendFeedbackEmail: called with ",ftype,name,email,feedback])
        sendMail = "/usr/sbin/sendmail"
        messageText = "Mime-Version: 1.0\n"
        messageText += "Content-type: text/html; charset=\"iso-8859-1\"\n"
        messageText += "To:epiexplorer@mpi-inf.mpg.de\n"        
        messageText += "From:epiexplorer@mpi-inf.mpg.de\n"
        #if email:
        #    messageText += "Reply-to: "+str(email)+"\n";        
        messageText += "Subject: EpiExplorer "+str(ftype)+" feedback \n"        
        messageText += "\n"
        messageText += "<html><body>\n"
        messageText += "Dear EpiExplorer admin,\n<br>"
        messageText += "\n<br>"
        messageText += "The user with name '"+str(name)+"' and email '"+str(email)+"' left the following "+str(ftype)+" feedback <br>\n"
        messageText += "<br>\n"
        messageText += "'"+feedback+"'<br\>\n"
        messageText += "<br>\n"        
        messageText += "\n<br>"
        messageText += "Kind regards,\n<br>"
        messageText += "EpiExplorer support\n<br>"
        messageText += "</body></html>\n"
        if "win32" in sys.platform:
            log_CQS("sendFeedbackEmail: Email notification is not supported under Windows OS")        
        try:
            p = os.popen("%s -t" % sendMail, 'w')
            p.write(messageText)
            p.close()
        except Exception,ex:
            log_CQS("sendFeedbackEmail: Error: Problem with sending the user email "+str(ex))
        log_CQS("sendFeedbackEmail: end ")
        return True 
    
    def getStatus(self):
        return "OK"
    
    def hasActiveServer(self,dataserName):
        """ Checks if a server for this region sets is active        
        """
        if self.servers.has_key(dataserName):
            if self.activeDatasetInfo.has_key(dataserName):
                return True
            else:
                extext = "Error: hasActiveServer "+str(dataserName)+" in servers but not in activeDatasetInfo"
                log(extext)
                raise GDMException,extext
        else:
            if self.activeDatasetInfo.has_key(dataserName):
                extext = "Error: hasActiveServer "+str(dataserName)+" not in servers but in activeDatasetInfo"
                log(extext)
                raise GDMException,extext
            else:
                return False
            
    def getCoverages(self, genome, datasetName):
        log_CQS(["getCoverage: called with genome=",str(genome),"and datasetName=",str(datasetName)])
        # check if this dataset is started
        if not self.activeDatasetInfo.has_key(datasetName):
            log_CQS("getCoverage: no dataset "+str(datasetName)) 
            return {}        
        datasetInfo = self.activeDatasetInfo[datasetName]
        # check if the genome is right        
        if datasetInfo["genome"] != genome:
            log_CQS("getCoverageInfo: wrong genome '"+str(genome)+"' for dataset "+str(datasetName))
            return {}
        # check if there is a started server
        if not self.servers.has_key(datasetName):
            log_CQS("getCoverageInfo: Error: dataset "+str(datasetName)+" appears started but no port info in the self.servers")
            return {}
        # now it seems everything is in order, so we should proceed with the query answer
        if self.coverageData.has_key(datasetName):
            return self.coverageData[datasetName]        
        
        try:
            answer = {}            
            queryAnswer = self.answerQuery("coverage:::*", 1000,0, datasetName)
        
            for feature in queryAnswer[3].keys():
                featureParts = feature.split(":::")                                
                
                datasetSimpleName = featureParts[1]
                tissue = featureParts[2]
                coverage = int(featureParts[3])
                
                if not answer.has_key(datasetSimpleName):
                    answer[datasetSimpleName] = {}
                
                answer[datasetSimpleName][tissue] = coverage 
                
            self.coverageData[datasetName] = answer 
        
        except Exception,ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()            
            log_CDS("getVisualizationFeatures: Error: traceback:"+repr(traceback.format_tb(exc_traceback)))
            errorMessage = str(ex)
            log_CDS("getVisualizationFeatures: Error: in short "+errorMessage)
            answer = {}  
        return answer
            
        
    def getVisualizationFeatures(self,genome,datasetName):
        log_CQS(["getVisualizationFeatures: called with genome=",str(genome),"and datasetName=",str(datasetName)])
        # check if this dataset is started
        if not self.activeDatasetInfo.has_key(datasetName):
            log_CQS("getVisualizationFeatures: no dataset "+str(datasetName)) 
            return {}        
        datasetInfo = self.activeDatasetInfo[datasetName]
        # check if the genome is right        
        if datasetInfo["genome"] != genome:
            log_CQS("getVisualizationFeatures: wrong genome '"+str(genome)+"' for dataset "+str(datasetName))
            return {}
        # check if there is a started server
        if not self.servers.has_key(datasetName):
            log_CQS("getVisualizationFeatures: Error: dataset "+str(datasetName)+" appears started but no port info in the self.servers")
            return {}
        # now it seems everything is in order, so we should proceed with the query answer
        if self.visualizationSettings.has_key(datasetName):
            return self.visualizationSettings[datasetName]
        try:
            processedAnswer = {}
            queryAnswer = self.answerQuery(settings.wordPrefixes["features"]+"*", 1000,0, datasetName)
            for feature in queryAnswer[3].keys():
                featureParts = feature.split(":::")
                if len(featureParts) < 2:
                    log_CQS("getVisualizationFeatures: skipping "+feature)
                    continue
                data = processedAnswer
                for i in range(1,len(featureParts)-1):
                    # if the group is actually a processed dataset store it                    
                    try:
                        featureParts[i] = self.fullyProcessedUserDatasets[featureParts[i]]
                    except:
                        pass                     
                    if not data.has_key(featureParts[i]):
                        data[featureParts[i]] = {}
                    data = data[featureParts[i]]               
                if len(featureParts[-1]) > 0:
                    if not data.has_key("featureBox"):
                        data["featureBox"] = []
                    visParts = featureParts[-1].split("::")
                    if len(visParts):
                        if len(visParts[0]):
                            if visParts[0][0] == "_":
                                visParts[0] = "-"+visParts[0][1:]
                            if  not (visParts[0].startswith("OVERLAP") or  visParts[0].startswith("-OVERLAP")):                                 
                                if visParts[0][-1] != ":":
                                    visParts[0] = visParts[0]+":"   
                            if len(visParts) > 1 and visParts[1].startswith("Eor:"):
                                if visParts[1][-1] != ":":
                                    visParts[1] = visParts[1]+":"                                                             
                    data["featureBox"].append(visParts)
            self.visualizationSettings[datasetName] = processedAnswer       
        except Exception,ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()            
            log_CDS("getVisualizationFeatures: Error: traceback:"+repr(traceback.format_tb(exc_traceback)))
            errorMessage = str(ex)
            log_CDS("getVisualizationFeatures: Error: in short "+errorMessage)
            processedAnswer = {}  
        return processedAnswer
    
    def __updateRunningUserCSServer__(self,datasetName):
        self.runningUserServers[datasetName] = time.time()
    
    def getRunningServers(self):
        return self.runningUserServers   
         
    def cleanOldCS(self):
        log_CQS("__init__: Start cleanOldCS")
        actualTime = time.time()
                
        total = 0
        for datasetName in self.runningUserServers.keys():
            startedTime = self.runningUserServers[datasetName]
            if actualTime - startedTime > settings.CS_TIME_LIFE:
                self.stopServer(datasetName)
                total = total + 1
        
        log_CQS("__init__: Leave cleanOldCS. Killed " + str(total) + " CS instances.")        
        self.csManager = Timer(settings.CS_TIME_CHECK_TIME, self.cleanOldCS)
        self.csManager.start()  
   
    def collectAndSendReport(self):
        log_CQS("__init__: Start collectAndSendReport")
        try:        
            report = self.reportManager.generateReport()
            self.datasetServer.sendNotificationEmail("halachev@mpi-inf.mpg.de,felipe.albrecht@mpi-inf.mpg.de","","epiexplorer@mpi-inf.mpg.de","","EpiExplorer daily report",report)
            self.reportManager.initStats()        
                
            self.reportTimer = Timer(settings.CS_TIME_REPORT_TIME, self.collectAndSendReport) 
            self.reportTimer.start()
        except Exception,ex:
            log_CQS("__init__: collectAndSendReport Error: " + str(ex))

        log_CQS("__init__: Leave collectAndSendReport.")
    
    def finish(self):
        for datasetName in self.servers.keys():
            self.stopServer(datasetName)
        print "The CGS Query killed all processes"
        self.reportTimer.cancel()
        self.csManager.cancel()

if __name__ == '__main__':
    start_msg = "Starting CGS Query ThreadedXMLRPCServer:\t" + str(settings.queryServerHost) + ":" + str(settings.queryServerPort)
    log_CQS(start_msg)
    print(start_msg)
    server = ThreadedXMLRPCServer.ThreadedXMLRPCServer((settings.queryServerHost, settings.queryServerPort), 
                                                       SimpleXMLRPCRequestHandler,
                                                       encoding='ISO-8859-1',
                                                       allow_none=True)
    server.request_queue_size = 20
    sys.setcheckinterval(30)#default is 100
    queryServer = CGSQueryServer()
    server.register_instance(queryServer)
    start_msg = "Running CGS Query ThreadedXMLRPCServer at:\t" + str(socket.gethostname()) + ":" + str(settings.queryServerPort)
    log_CQS(start_msg)
    print(start_msg)
    write_pid_to_file("CGSQueryServer.py", settings.configFolder + "CGSServers.pid.txt")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        queryServer.finish()
        
            
            
        
        

