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
import traceback
import hashlib
import re

from utilities import *
import collectRegions
import readDatasetDescriptions
import exportRegionData
import CGSAnnotationsSettings
import csDataBuilder
import UserHandling

from DatasetClasses import *
from Vocabulary import *
#from settings import datasetClasses
from DataStorageServer import DataStorageServer
from DatasetProcessorManager import DatasetProcessorManager

# import multiprocessing #Needs python2.6

# Make sure STDOUT is unbuffered so the init output gets printed else all other output should be logged (with buffering)
# This should really be done in a CGS_base_server.py class which absorbs some other common things from the other
# CGS servers e.g. log wrapper (instead of having them in utilities)
# Do we need to manage file locks for threads as per logs? This assumes all prints are done before threading is launched
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)


class CGSDatasetServer:
    def __init__(self):   
        start_msg = "__init__: Starting CGS Dataset XMLRPC-Server at:\t" + str(socket.gethostname())+ ":" + str(settings.datasetServerPort)
        log_CDS(start_msg)
        print start_msg + "\nLog file:\t" + settings.logFile
        self.queryServer = xmlrpclib.Server("http://"+settings.queryServerHost+":"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)     
        self.dataStorage = DataStorageServer()   
        # load default datasets and their structures
        self.defaultDatasets = {}
        self.defaultAnnotationNames = {}
        self.antibodyVocabulary = AntibodyVocabulary()
        self.cellLineVocabulary = CellLineVocabulary()
        for genomeID in settings.genomeData.keys():
            datasetsIndexFile = getMainDatasetIndexFileName(genomeID)                
            genomeDefaultDatasets = readDatasetDescriptions.readDatasets(datasetsIndexFile)
            self.defaultDatasets.update(genomeDefaultDatasets)
        self.datasetInfo = {}
        log_CDS("__init__: Default datasets read "+str(self.defaultDatasets.keys()))
        for datasetKey in self.defaultDatasets.keys():
            log_CDS("__init__: Loading "+datasetKey)

            dataset = self.defaultDatasets[datasetKey]             
            dataset.init()
            datasetRegionsCount = 0
            try:
                if self.queryServer.hasActiveServer(dataset.datasetSimpleName):
                    datasetRegionsCount = int(self.queryServer.answerQuery(settings.wordPrefixes["region"],0,0,dataset.datasetSimpleName)[2])
            except Exception,ex:
                log_CDS("__init__: Failed to retrieve regions count for dataset "+str(datasetKey))
                
            self.datasetInfo[dataset.datasetSimpleName] = {
                                "simpleName":dataset.datasetSimpleName,
                                "officialName":dataset.datasetOfficialName,
                                "genome":dataset.genome,
                                "categories":map(lambda x:x.strip(),dataset.dataCategories.split("/")),
                                "description":dataset.datasetDescription.replace("###","\n"),
                                "moreInfoLink":dataset.datasetMoreInfo,
                                "numberOfRegions":datasetRegionsCount,
                                "datasetType":dataset.datasetType,
                                "hasBinning":dataset.hasBinning,
                                "overlappingText": dataset.overlappingText,
                                "urls": dataset.downloadUrls, 
                                "date": dataset.downloadDate,
                                "isDefault":True
                                
                                }            
            log_CDS("__init__: Dataset "+str(datasetKey)+" was started")
        # Load the llst of all datasets that are processed
        self.fullyProcessedDatasets = {}
            # load the default datasets 
        self.fullyProcessedDefaultDatasets = {}
        for genomeID in settings.fullyProcessedDefaultDatasetsFile.keys():
            genomeDefaultDatasets = readSettingsFile(settings.fullyProcessedDefaultDatasetsFile[genomeID])
            self.fullyProcessedDefaultDatasets.update(genomeDefaultDatasets)
        self.fullyProcessedDatasets.update(self.fullyProcessedDefaultDatasets)
        # load the user datasets
        self.reloadProcessedUserDatasets()
        # load the hashed queries
        self.hashedQueries = {}
        self.loadHashedQueries()
        # initialize the semaphore for blocking more than 2 dataset computations at the same time
        self.queuedDatasetComputations = DatasetProcessorManager()
        
        #Needs python2.6
        #self.multiprocessingWorkers = multiprocessing.Pool(processes=5)
        log_CDS(["__init__: Fully processed datasets are",str(self.fullyProcessedDatasets.keys())])
        log_CDS(["__init__: Dataset info keys are",str(self.datasetInfo.keys())])
        log_CDS("__init__: end")
    
    def reloadProcessedUserDatasets(self):
        # load the user datasets
        userDatasetsIds = {}
        for genomeID in settings.fullyProcessedUserDatasetsFile.keys():
            genomeUserDatasets = readSettingsFile(settings.fullyProcessedUserDatasetsFile[genomeID])
            userDatasetsIds.update(genomeUserDatasets)
        
        self.fullyProcessedDatasets.update(userDatasetsIds)
        #load the user dataset info
        for userDatasetID in userDatasetsIds.keys():
            try:
                dataset = readDatasetDescriptions.readDataset([userDatasetID,settings.folderForTemporaryDatasets+userDatasetID+".ini",""])
                dataset.hasBinning = hasattr(dataset, "hasBinning") and dataset.hasBinning == "True"            
                self.datasetInfo[dataset.datasetSimpleName] = {
                            "simpleName":dataset.datasetSimpleName,
                            "officialName":dataset.datasetOfficialName,
                            "genome":dataset.genome,
                            "categories":map(lambda x:x.strip(),dataset.dataCategories.split("/")),
                            "description":dataset.datasetDescription.replace("###","\n"),
                            "moreInfoLink":dataset.datasetMoreInfo,
                            "numberOfRegions":0,
                            "datasetType":dataset.datasetType,
                            "hasBinning":dataset.hasBinning,
                            "isDefault":False,
                            "overlappingText": dataset.datasetSimpleName
                            }                
            except Exception,ex:
                log_CDS(["__init__: Error for user dataset",str(userDatasetID),str(ex)])
    
    def getCustomDatasetIniFileName(self,datasetName):
        return settings.folderForTemporaryDatasets + datasetName + ".ini"

    def __createUserDatasetSettingsFile__(self, datasetName, regionsFile, 
										  genome, additionalSettingsFileName,  
										  officialName="", description="", 
										  moreInfoLink="", computeSettings={}):
        filename = self.getCustomDatasetIniFileName(datasetName)

        dset_info = {"simpleName":datasetName,
                     "officialName":(officialName or datasetName),
                     "hasBinning":True,
                     "genome":genome,
                     "categories":["User"],
                     "description":description.replace("###","\n"),
                     "moreInfoLink":moreInfoLink,
                     "numberOfRegions":0,
                     "datasetType":"Default",
                     "isDefault":False,
                     "overlappingText": datasetName
        }
        self.datasetInfo[datasetName] = dset_info

        write_dataset_ini_file(filename, os.path.abspath(settings.downloadDataFolder[genome] + datasetName + ".user"),
                               dset_info, regionsFile, additionalSettingsFileName, computeSettings)
        log_CDS(["__createUserDatasetSettingsFile__: Added datasetinfo for ",
                 str(datasetName),self.datasetInfo[datasetName]["officialName"],
                 str(genome)])
        return filename

    
    def __processDatasetGivenRegions__(self, datasetName, cgsAS, regionsDict, isDefault, additionalSettings, size = 0, delete_intermediary=True):
        returnMessage = ""
        try:
            self.queuedDatasetComputations.indicateComputationWaiting(datasetName)# waiting                
            # the dataset name is valid
            log_CDS("__processDatasetGivenRegions__: "+str(datasetName)+" is about to be allowed to be computed")
            self.queuedDatasetComputations.acquire(datasetName,size)            
            log_CDS("__processDatasetGivenRegions__: "+str(datasetName)+" is now computing")
            if self.getDatasetStatus(datasetName)[0] != -1:
                self.queuedDatasetComputations.indicateComputationProgress(datasetName,getDatasetStatusAsText(0))# computing
            else:
                raise GDMException, "The dataset was stopped forcefully by the admins"
                        
            #collect the regions from this dataset into a single structure
            collectRegions.collectFullRegions(regionsDict, cgsAS)
            log_CDS("__processDatasetGivenRegions__: regions collected"+str(datasetName))
            self.queuedDatasetComputations.indicateComputationProgress(datasetName,getDatasetStatusAsText(1))# computing
            # Select the dataset for which we shoudl compute features
            featureDatasets = {}
            totalAnnotationFeatures = 0
            if (not isDefault) and cgsAS.getFeatureDatasetProperty(datasetName,"hasFeatures"):
                # If it is a user dataset and it has features, compute them
                regionsDict[datasetName].init(True)
                featureDatasets[datasetName] = regionsDict[datasetName]
                cgsAS.addFeatureDataset({datasetName:regionsDict[datasetName].getDefaultAnnotationSettings()})
                for ds in self.defaultDatasets.keys():
                    if self.defaultDatasets[ds].genome == cgsAS.genome:
                        featureDatasets[ds] = self.defaultDatasets[ds]
                        cgsAS.addFeatureDataset({ds:self.defaultDatasets[ds].getDefaultAnnotationSettings()})
                        totalAnnotationFeatures += len(self.defaultDatasets[ds].getSubAnnotations())
            else:
                # otherwise go with the defaults
                for ds in self.defaultDatasets.keys():
                    if self.defaultDatasets[ds].genome == cgsAS.genome:                    
                        featureDatasets[ds] = self.defaultDatasets[ds]   
                        cgsAS.addFeatureDataset({ds:self.defaultDatasets[ds].getDefaultAnnotationSettings()})
                        totalAnnotationFeatures += len(self.defaultDatasets[ds].getSubAnnotations())
            # apply additional settings
            for additionalDatasetName in additionalSettings.keys():
                if featureDatasets.has_key(additionalDatasetName):            
                    cgsAS.addFeatureDataset({additionalDatasetName:additionalSettings[additionalDatasetName]})
                    totalAnnotationFeatures += 1
                elif self.defaultDatasets.has_key(additionalDatasetName):
                    #hmmm strange not a default set but in  the default sets
                    log_CDS(["__processDatasetGivenRegions__:1: Omitting additional settings for ",additionalDatasetName,datasetName])
                else:
                    if additionalSettings[additionalDatasetName]["hasFeatures"]:
                        if self.fullyProcessedDatasets.has_key(additionalDatasetName):
                            log_CDS(["__processDatasetGivenRegions__: Activating a user dataset ",additionalDatasetName,datasetName])
                            dataset = readDatasetDescriptions.readDataset([additionalDatasetName,settings.folderForTemporaryDatasets+additionalDatasetName+".ini",""])
                            dataset.init()
                            log_CDS(["__processDatasetGivenRegions__: User dataset activated",additionalDatasetName,datasetName])
                            featureDatasets[additionalDatasetName] = dataset
                            userDatasetAnnotationSettings = dataset.getDefaultAnnotationSettings()
                            userDatasetAnnotationSettings.update(additionalSettings[additionalDatasetName])
                            cgsAS.addFeatureDataset({additionalDatasetName:userDatasetAnnotationSettings})
                            totalAnnotationFeatures += len(dataset.getSubAnnotations())
                        else:
                            log_CDS(["__processDatasetGivenRegions__:2: Omitting additional settings for ",additionalDatasetName,datasetName])
                    else:
                        log_CDS(["__processDatasetGivenRegions__:3: Omitting additional settings for ",additionalDatasetName,datasetName])    
                    #probably user dataset, activate it and add it to the features 
            currentNumber = 1
            for featureDatasetName in featureDatasets.keys():
                log_CDS(["__processDatasetGivenRegions__: Computing scores for",datasetName, featureDatasetName])
                if self.queuedDatasetComputations.getComputationStatus(datasetName)[0] == -1:
                    returnMessage = "Dataset computation was stopped by the EpiExplorer staff. Contact " + settings.contact_email + " for more info."
                    self.queuedDatasetComputations.indicateComputationError(datasetName,returnMessage)
                    raise GDMException, returnMessage  
                self.queuedDatasetComputations.indicateComputationProgress(datasetName,getDatasetStatusAsText(2,"Step 3/6: Computing annotation "+featureDatasets[featureDatasetName].datasetOfficialName+" ("+str(currentNumber)+" out of total "+str(totalAnnotationFeatures)+" annotations are completed)"))# computing
                #featureDatasets[featureDatasetName].datasetCollectionName = localDatasetCollectionName
                featureDatasets[featureDatasetName].computeRegionsProperties(cgsAS)
                currentNumber += len(featureDatasets[featureDatasetName].getSubAnnotations())
                log_CDS(["__processDatasetGivenRegions__: Scores computed for",datasetName, featureDatasetName])    
                
            self.queuedDatasetComputations.indicateComputationProgress(datasetName,getDatasetStatusAsText(3))# computing
            exportRegionData.exportAllData(featureDatasets, cgsAS)
            log_CDS(["__processDatasetGivenRegions__: Data exported", datasetName])
            #exportRegionData.exportWordDescription(self.defaultDatasets, cgsAS)
            #log_CDS(["__processDatasetGivenRegions__: Word description also exported", datasetName])
            #        raise Exception, "Now I need to recompute the "
            self.queuedDatasetComputations.indicateComputationProgress(datasetName,getDatasetStatusAsText(4))# computing
            retcode = subprocess.call(["cd", settings.indexDataFolder[cgsAS.genome]], shell=True)
            log_CDS("__processDatasetGivenRegions__: Creating the CompleteSearch index files for the dataset "+datasetName)
            

            csDataBuilder.buildCSData(getFastTmpCollectionFolder(cgsAS.datasetCollectionName), cgsAS.datasetCollectionName, delete_intermediary)
            
            #clean up the word description files            
            self.queuedDatasetComputations.indicateComputationProgress(datasetName,getDatasetStatusAsText(5))# computing
            if not isDefault and not settings.keepWordsFiles:
                #only for the custom datasets and not for the default datasets
                unsortedWordsFile = getCompleteSearchDocumentsWordsFile(cgsAS.datasetCollectionName,cgsAS.genome)
                if os.path.isfile(unsortedWordsFile):
                    os.unlink(unsortedWordsFile)
                for uselessFileExtention in [".words-sorted.ascii",".docs",".docs-sorted",".hybrid.prefixes",".hybrid.build-index-log",".hybrid.build-index-errors",".hybrid.from-ascii.withprefixes"]:
        #        for uselessFileExtention in [".hybrid.prefixes",".hybrid.build-index-log",".hybrid.build-index-errors"]:
                    uselessFile = unsortedWordsFile.replace(".words-unsorted.ascii",uselessFileExtention)
                    if os.path.isfile(uselessFile):                        
                        os.unlink(uselessFile)
                        
            # Move the data
            moveTmpIndexFilesToIndexFolder(cgsAS.datasetCollectionName,cgsAS.genome)
            for featureDatasetName in featureDatasets.keys():
               featureDatasets[featureDatasetName].cleanup(cgsAS)
     
            #update the list of fully processed datasets
            if isDefault:            
                f = open(settings.fullyProcessedDefaultDatasetsFile[cgsAS.genome], "a")
            else:
                f = open(settings.fullyProcessedUserDatasetsFile[cgsAS.genome], "a")
            f.write(cgsAS.datasetCollectionName+"="+regionsDict[datasetName].datasetOfficialName+"\n")
            f.close()
            self.fullyProcessedDatasets[datasetName] = regionsDict[datasetName].datasetOfficialName
        except Exception,ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()            
            log_CDS("processUserDataset:Error: preprocessing problem traceback:"+repr(traceback.format_tb(exc_traceback)))
            returnMessage = str(ex)
            log_CDS("processUserDataset:Error: preprocessing problem "+returnMessage)            
            self.queuedDatasetComputations.indicateComputationError(datasetName,returnMessage)
            raise GDMException, returnMessage            
        finally:
            self.queuedDatasetComputations.release(datasetName,size)
            del cgsAS
        
        self.queuedDatasetComputations.removeComputation(datasetName)
        try:
            self.queryServer.refreshFullyProcessedServers()
        except:
            log_CDS("__processDatasetGivenRegions__: Query server is not available")
            
        return returnMessage
        
    def echo(self, msg):
        log_CDS("echo called with param "+msg)                
        return str(msg)
    
    def log_me(self,msg):
        log_CDS("log_me: "+msg)
    
    def exportQueryData(self, regionSet, query, mail, datasetKeys):
        log_CDS(["exportQueryData called",regionSet, query, mail,datasetKeys])
        if not query:
            query = "None"
        if not datasetKeys:
            datasetKeys = "None"
        subprocess.Popen(["python",getCurrentFolder()+"CGSServerEngine.py","exportQueryData",str(regionSet),str(query),str(mail),datasetKeys])        
        log_CDS(["exportQueryData end"])  
        
    def getGenomicRegionProperties(self, genome, region, datasetsKeys=[]):
        log_CDS(["getGenomicRegionProperties called with param ",genome, region, datasetsKeys])        
        regionProperties = {}        
        regionWords = {}
        try:
            region[0] = convertChromToInt(genome,region[0])
            region[1] = int(region[1])   
            region[2] = int(region[2])
            # Now that we are sure that the coordinates are more or less ok
            cgsAS = CGSAnnotationsSettings.CGSAnnotationsSettings("_".join(map(str,[genome]+region[:3])),genome,{},{})
            # if no datasets are provided, return data for the default datasets     
            if not datasetsKeys:
                datasetsKeys = self.defaultDatasets.keys()            
            for datasetKey in datasetsKeys:                
                dataset = self.defaultDatasets[datasetKey]
                # Now the dataset is known, os add it as feature property
                cgsAS.addFeatureDataset({datasetKey:dataset.getDefaultAnnotationSettings()})
                if dataset.initialized and cgsAS.getFeatureDatasetProperty(datasetKey,"hasFeatures") and dataset.genome == genome:
                    regionWords[datasetKey] = []
                    try:                
                        dProperties = dataset.computeSingleRegionProperties([-1,region[0],region[1],region[2],-1], cgsAS)
                        for dProperty in dProperties:
                            spWords,spWordsWithScores = dataset.getRegionComputedDataFromExtractedLine(dProperty, cgsAS)
                            #log_CDS(["getGenomicRegionProperties: for dataset ",datasetKey," extracted raw data ",str(dProperty)," which resulted in words ",str(spWords)])                            
                            regionWords[datasetKey].extend(spWords)
                            regionWords[datasetKey].extend(map(lambda x:x[0],spWordsWithScores))
                        regionProperties[datasetKey] = map(lambda x:map(str,list(x)),dProperties)
                    except Exception, ex:
                        extext = "Error: Could not retrieve the properties of "+str(region) +" for dataset "+datasetKey+" with ex "+str(ex)
                        log_CDS(["getGenomicRegionProperties:Error",extext])
        except Exception, ex:
            extext = "Error: Could not retrieve the properties of "+str(region) +" with ex "+str(ex)
            log_CDS(["getGenomicRegionProperties:Error",extext])
        log_CDS(["getGenomicRegionProperties:return",str(regionProperties),str(regionWords)])
        return [regionProperties,regionWords]     
    
    def getGenomicRegionPropertiesForDataset(self,genome, region,datasetKey,dProperties=[]):
        log_CDS(["getGenomicRegionPropertiesForDataset",genome,region,datasetKey,dProperties])
        
        regionWords = []
        properties = []
        try:
            region[0] = convertChromToInt(genome,region[0])
            region[1] = int(region[1])   
            region[2] = int(region[2])
            cgsAS = CGSAnnotationsSettings.CGSAnnotationsSettings("_".join(map(str,[genome]+region[:3])),genome,{},{})            
            dataset = self.defaultDatasets[datasetKey]
            cgsAS.addFeatureDataset({datasetKey:dataset.getDefaultAnnotationSettings()})
            if not dProperties:           
                dProperties = dataset.computeSingleRegionProperties([-1,region[0],region[1],region[2],-1], cgsAS)
                log_CDS(["getGenomicRegionPropertiesForDataset raw properties",str(dProperties)])
            properties = dProperties 
            for dProperty in dProperties:                
                log_CDS(["getGenomicRegionPropertiesForDataset raw properties to words",str(dProperty)])
                spWords,spWordsWithScores = dataset.getRegionComputedDataFromExtractedLine(dProperty, cgsAS)
                log_CDS(["getGenomicRegionPropertiesForDataset: extracted raw data ",str(dProperty)," which resulted in words ",str(spWords)])
                regionWords.extend(spWords)
                regionWords.extend(map(lambda x:x[0],spWordsWithScores))            
        except Exception, ex:
            extext = "Error: Could not retrieve the properties of "+str(region) +" with ex "+str(ex)
            log_CDS(["getGenomicRegionPropertiesForDataset",extext])
        return [properties,regionWords] 
            
        
    def processStoredDataset(self, internal_id, software, datasetName, genome, additionalSettings,
                                        notificationEmail, syncCall, datasetLink, datasetDesc, computeSettings):
        bed_file = self.retrieve_file_as_bed(software, internal_id)
        return self.processUserDatasetFromBuffer(datasetName, bed_file, genome, additionalSettings,
                                    notificationEmail, syncCall, datasetLink, datasetDesc, computeSettings)

    def processInfinumReference(self, datasetName, forceProcess = False, additionalSettings={}):
        self.processDefaultDataset(datasetName, forceProcess,additionalSettings, False)            
    
    def processDataset(self, datasetName, propertiesDatasets=[], regionsFile = "", forceProcess = False):
        raise GDMException,"Not supposed to be called directly maybe?"
        log_CDS(["processDataset: called with param ",datasetName, propertiesDatasets, regionsFile, forceProcess])
        if self.fullyProcessedDatasets.has_key(datasetName):
            genome  = self.fullyProcessedDatasets[datasetName].genome    
            fnwd = getCompleteSearchDocumentsWordsFile(datasetName,genome)
            fndd = getCompleteSearchDocumentsDescrioptionsFile(datasetName,genome)        
            log_CDS(["processDataset: Dataset",datasetName,"was fully processed in",fnwd,"and",fndd])
            return 
        if not propertiesDatasets:
            propertiesDatasets = self.defaultDatasets.keys()
        if self.defaultDatasets.has_key(datasetName):
            self.processDefaultDataset(self, datasetName,forceProcess)
        else:
            raise GDMException,"Not supposed to be called directly maybe?"
            #self.processUserDataset(self, datasetName)
        log_CDS(["processDataset: end"])
        return 1
            
    def processDefaultDataset(self, datasetName, forceProcess = False, additionalSettings={}, delete_intermediary=True):
        cgsAS = CGSAnnotationsSettings.CGSAnnotationsSettings(datasetName,self.defaultDatasets[datasetName].genome,{},{})
        log_CDS(["processDefaultDataset called with param ",datasetName, forceProcess])
        if not self.defaultDatasets.has_key(datasetName):
            raise Exception, "Error:"+datasetName+" is not a default dataset name "+str(self.defaultDatasets.keys())
        regionsDict = {datasetName: self.defaultDatasets[datasetName]}
        cgsAS.addRegionDataset({datasetName:self.defaultDatasets[datasetName].getDefaultAnnotationSettings()})
        #multiprocessing needs python2.6
        #result = self.multiprocessingWorkers.apply_async(self.__processDatasetGivenRegions__, (datasetName,cgsAS,regionsDict,True,additionalSettings))
        #resultText = result.get(None)
        #if resultText:
        #    #there was an error
        #    raise GDMException,resultText
        # multiprocessing needs python2.6 
        self.__processDatasetGivenRegions__(datasetName,cgsAS,regionsDict,True,additionalSettings, 0, delete_intermediary)
        log_CDS(["processDefaultDataset: end"])
        return 1     
   
    def checkUserDatasetFormat(self,regionsFile,genome,computeSettings):
        log_CDS(["checkUserDatasetFormat called with param",regionsFile,genome,computeSettings])
        fUpdatedContent = ""
        f = open(regionsFile)
        line = f.readline()
        lineIndex = 0
        invalidLines = 0 
        ignoreChromosomeError = computeSettings.has_key("ignoreNonStandardChromosomes") and computeSettings["ignoreNonStandardChromosomes"]
        useScore = computeSettings.has_key("useScore") and computeSettings["useScore"]
        useStrand = computeSettings.has_key("useStrand") and computeSettings["useStrand"]
        noLineLimit = computeSettings.has_key("noLineLimit") and computeSettings["noLineLimit"]
        
        while line:            
            lineParts = line.strip().split("\t")
            keepLine = True
            if len(lineParts) < 3:
                invalidLines += 1 
                keepLine = False
            else:            
                try:
                    chr = convertChromToInt(genome,lineParts[0])
                except:
                    
                    try:
                        chr = convertChromToInt(genome,lineParts[0].replace("_random",""))
                    except:    
                        if lineParts[0][0] == "#" or lineIndex ==0 or ignoreChromosomeError:
                            pass
                        else: 
                            ertext = "Error: "+"Invalid format at line "+str(lineIndex)+". Invalid chromosome symbol "+lineParts[0]
                            log_CDS(["checkUserDatasetFormat Error:",ertext])                                    
                            raise CGSInvalidFormatException, ertext
                    
                    invalidLines += 1   
                    keepLine = False
            if keepLine:         
                try:
	                start = int(lineParts[1])
                except:                
	                ertext = "Error: "+"Invalid format at line "+str(lineIndex)+". Invalid chromosome start "+lineParts[1]
	                log_CDS(["checkUserDatasetFormat Error:",ertext])                
	                raise CGSInvalidFormatException, ertext 
                try:
	                end = int(lineParts[2])
                except:      
	                ertext = "Error: "+"Invalid format at line "+str(lineIndex)+". Invalid chromosome end "+lineParts[2]          
	                log_CDS(["checkUserDatasetFormat Error:",ertext])                
	                raise CGSInvalidFormatException, ertext 
                if end <= start:                      
	                ertext = "Error: "+"Invalid format at line "+str(lineIndex)+". chromosome end("+lineParts[2]+") should be larger than chromosome start ("+lineParts[1]+")"          
	                log_CDS(["checkUserDatasetFormat Error:",ertext])                
	                raise CGSInvalidFormatException, ertext
                if end > start + 10000000:                      
                    ertext = "Error: "+"Invalid format at line "+str(lineIndex)+". The length of a region cannot be more than 10,000,000 basepairs. Note, EpiExplorer is mostly efficient on datasets in the order of up to hundred thousand basepairs."           
                    log_CDS(["checkUserDatasetFormat Error:",ertext])                
                    raise CGSInvalidFormatException, ertext
                if start < 0 or end > settings.genomeDataNumbers[genome][chr]:
                    ertext = "Error: "+"Invalid region coordinates at line "+str(lineIndex)+". The region ("+str(start)+", "+str(end)+") is out of the chromosome ( 0, "+str(settings.genomeDataNumbers[genome][chr])+"). Please check if you are using the correct genome assembly."          
                    log_CDS(["checkUserDatasetFormat Error:",ertext])                
                    raise CGSInvalidFormatException, ertext
                if useScore:
                    if len(lineParts) < 5:
                        ertext = "Error: "+"Invalid format at line "+str(lineIndex)+". There must be a score at the 5th position, but there are less than 5 positions"
                        log_CDS(["checkUserDatasetFormat Error:",ertext])
                        raise CGSInvalidFormatException, ertext
                    try:                        
	            		# score is expected to be the 5th column and to be number between 0 and 1000
	            		# see http://genome.ucsc.edu/FAQ/FAQformat.html#format1
	                    score = int(lineParts[4])
	                    if score < 0 or score> 1000:
	                    	raise Exception
                    except:
	                	ertext = "Error: "+"Invalid format at line "+str(lineIndex)+". score is ("+lineParts[4]+") but it must be an integer between 0 and 1000"
	                	log_CDS(["checkUserDatasetFormat Error:",ertext])
	                	raise CGSInvalidFormatException, ertext
                if useStrand:
                    if len(lineParts) < 6:
                        ertext = "Error: "+"Invalid format at line "+str(lineIndex)+". There must be a strand at the 6th position, but there are less than 6 positions"
                        log_CDS(["checkUserDatasetFormat Error:",ertext])
                        raise CGSInvalidFormatException, ertext
            		# strand is expected to be the 6th column and should be either a '+' or a '-'
            		# see http://genome.ucsc.edu/FAQ/FAQformat.html#format1
            		if lineParts[5] == "+" or lineParts[5] == "-":
            			pass
                   	else:
	                	ertext = "Error: "+"Invalid format at line "+str(lineIndex)+". strand is ("+lineParts[5]+") but it must be either '+' or '-'"
	                	log_CDS(["checkUserDatasetFormat Error:",ertext])
	                	raise CGSInvalidFormatException, ertext
            if keepLine:
                fUpdatedContent += "\t".join(lineParts)+"\n"
            line = f.readline()
            lineIndex += 1
            if lineIndex > 500000 and not noLineLimit:
                ertext = "Error: Your dataset exceeds the maximum number of regions (500,000) that can be processed via the web interface. If you really need to process a bigger dataset, please contact the EpiExplorer support with more details"          
                log_CDS(["checkUserDatasetFormat Error:",ertext])                
                raise CGSInvalidFormatException, ertext
        f.close()
        if invalidLines > 0:
            fw = open(regionsFile,"w")
            fw.write(fUpdatedContent)
            fw.close()
        if invalidLines >= lineIndex:
            ertext = "Error: the dataset has no valid lines. Make sure you privided a well formated BED file. This error is often caused by a BED file using spaces as separators between the values instead of tabs. If so, you may try using the 'Convert spaces to tabs' option."
            log_CDS(["checkUserDatasetFormat Error:","The dataset has no valid lines"])                
            raise CGSInvalidFormatException, ertext
        del fUpdatedContent
        
        log_CDS(["checkUserDatasetFormat: Completed with "+str(invalidLines)+" lines removed"])
        return invalidLines
        
    def getUniqueDatasetName(self, datasetName):
        log_CDS("getUniqueDatasetName: "+datasetName)
        # make new name for every dataset. For the moment we are not considering if the dataset already exists or not
        datasetNewName = getSafeWord(datasetName)+ "_" +str(randint(100000,999999))
        while self.defaultDatasets.has_key(datasetNewName) or self.fullyProcessedDatasets.has_key(datasetNewName):            
            datasetNewName = getSafeWord(datasetName)+ "_" +str(randint(100000,999999))        
        
#        if self.defaultDatasets.has_key(datasetName) or self.defaultDatasets.has_key(datasetNewName):
#            raise Exception, "A default dataset with the same name already exists!"
#        if self.fullyProcessedDatasets.has_key(datasetName) or self.fullyProcessedDatasets.has_key(datasetNewName):
#            fnwd = getCompleteSearchDocumentsWordsFile(datasetName)
#            fndd = getCompleteSearchDocumentsDescrioptionsFile(datasetName)        
#            log(["Dataset",datasetName,"was fully processed in",fnwd,"and",fndd])
#            raise Exception, "This dataset was already processed!"
        log_CDS("getUniqueDatasetName: end "+datasetNewName)
        return datasetNewName
    
    def sendUserDatasetNotificationEmail(self, originalDatasetName, datasetName,email,errorMessage):
        if not settings.doSendMails:
            return

        log_CDS(["sendUserDatasetNotificationEmail: called with ",originalDatasetName, datasetName,email,errorMessage])
        sendMail = "/usr/sbin/sendmail"
        messageText = "Mime-Version: 1.0\n"
        messageText += "Content-type: text/html; charset=\"iso-8859-1\"\n"

        if str(email):
            messageText += "To:"+str(email)+"\n"

        if settings.bcc_emails:
            messageText += "Bcc:" + settings.bcc_emails + "\n"

        messageText += "From:" + settings.contact_email + "\n"
        messageText += "Reply-to:" + settings.contact_email + "\n"

        if errorMessage:
            messageText += "Subject: There was a problem with your EpiExplorer dataset ("+originalDatasetName+")\n"
        else:
            messageText += "Subject: Your EpiExplorer dataset ("+originalDatasetName+") is available\n"

        messageText += "\n"
        messageText += "<html><body>\n"
        messageText += "Dear EpiExplorer user,\n<br>"
        messageText += "\n<br>"

        if errorMessage:
            messageText += "There was a problem with computing your dataset.\n<br><br>" 
            messageText += "The error message is '"+errorMessage+"'.\n<br><br>"
            messageText += "In case you don't know how to resolve the problem, please contact us by replying to this email.\n<br>"
        else:
            messageText += "Your EpiExplorer dataset is available under the DID <b>"+datasetName+"</b>\n<br>"
            messageText += 'You can use it directly by going to <a href="http://epiexplorer.mpi-inf.mpg.de/index.php?userdatasets='+datasetName+'">EpiExplorer from here</a>\n<br>'
        messageText += "\n<br>"
        messageText += "Regards,\n<br>"
        messageText += "EpiExplorer support\n<br>"
        messageText += "</body></html>\n"
        if "win32" in sys.platform:
            log_CDS("Email notification is not supported under Windows OS")   
            return     
        try:
            p = os.popen("%s -t" % sendMail, 'w')
            p.write(messageText)
            p.close()
        except Exception,ex:
            log_CDS("Error: "+"Problem with sending the user email "+str(ex))
        log_CDS("sendUserDatasetNotificationEmail: end ")   
    
    def sendNotificationEmail(self,toEmail,bccEmail,fromEmail,replyToEmail,subject,body):
        sendMail = "/usr/sbin/sendmail"
        messageText = "Mime-Version: 1.0\n"
        messageText += "Content-type: text/html; charset=\"iso-8859-1\"\n"
        if str(toEmail):
            messageText += "To:"+str(toEmail)+"\n"
        if str(bccEmail):
            messageText += "Bcc:"+str(bccEmail)+"\n"
        if str(fromEmail):
            messageText += "From:"+str(fromEmail)+"\n"
        if str(replyToEmail):
            messageText += "Reply-to:"+str(replyToEmail)+"\n"        
        
        messageText += "Subject: "+subject+"\n"
        messageText += "\n"
        messageText += body        
        if "win32" in sys.platform:
            log_CDS("Email notification is not supported under Windows OS")   
            return     
        try:
            p = os.popen("%s -t" % sendMail, 'w')
            p.write(messageText)
            p.close()
        except Exception,ex:
            log_CDS("Error: "+"Problem with sending the user email "+str(ex))
                
    
    def sendExportNotificationEmail(self, 
                                    exportType, 
                                    regionSet, 
                                    queryParts, 
                                    exportFileName, 
                                    email, 
                                    datasets, 
                                    errorMessage):
        if not settings.doSendMails:
            return
        log_CDS(["sendExportNotificationEmail: called with ",exportType, regionSet, queryParts,exportFileName, email,datasets,errorMessage])
        sendMail = "/usr/sbin/sendmail"
        messageText = "Mime-Version: 1.0\n"
        messageText += "Content-type: text/html; charset=\"iso-8859-1\"\n"
        messageText += "To:"+str(email)+"\n"

        if settings.bcc_emails:
            messageText += "Bcc:" + settings.bcc_emails + "\n"

        messageText += "From:" + settings.contact_email + "\n"
        messageText += "Reply-to:" + settings.contact_email + "\n"

        if errorMessage:
            messageText += "Subject: There was a problem with the export of your EpiExplorer dataset\n"
        else:
            messageText += "Subject: The export from EpiExplorer is available\n"
        messageText += "\n"
        messageText += "<html><body>\n"
        messageText += "Dear EpiExplorer user,\n<br>"
        messageText += "\n<br>"
        if errorMessage:
            messageText += "There was a problem with exporting your dataset.\n<br>" 
            messageText += "The error message is '"+errorMessage+"'.\n<br>"
            messageText += "In case you don't know how to resolve the problem, please contact us by replying to this email.\n<br>"
        else:
            messageText += "The export for the following query is complete<br>\n"
            messageText += 'You can download it from <a href="http://http://epiexplorer.mpi-inf.mpg.de/getExport.php?id='+os.path.basename(exportFileName).split(".")[0]+'">here</a>\n<br>'
        messageText += "<br>\n"
        messageText += "Export type: "+str(exportType)+"<br>\n"
        messageText += "Regions: "+str(regionSet)+"<br>\n"
        if len(queryParts) == 0:
            messageText += "Query: Empty<br>\n"
        else:    
            messageText += "Query: "+" ,".join(queryParts)+"<br>\n"
        if datasets:
            messageText += "Datasets: "+" ,".join(datasets)+" <br>\n"
        messageText += "\n<br>"
        messageText += "Kind regards,\n<br>"
        messageText += "EpiExplorer support\n<br>"
        messageText += "</body></html>\n"
        if "win32" in sys.platform:
            log_CDS("Email notification is not supported under Windows OS")
            return        
        try:
            p = os.popen("%s -t" % sendMail, 'w')
            p.write(messageText)
            p.close()
        except Exception,ex:
            log_CDS("Error: "+"Problem with sending the user email "+str(ex))
        log_CDS("sendExportNotificationEmail: end ")              

    
    def processUserDatasetCore(self,datasetName,filename, notificationEmail,originalSafeDatasetName,additionalSettingsFileName, size, delete_intermediary=True):         
        try:
            # run the bulk of the analysis
            tempDataset = readDatasetDescriptions.readDataset([datasetName,filename,""])
            tempDataset.init(False)
            
            tempDataset.hasBinning = hasattr(tempDataset, "hasBinning") and tempDataset.hasBinning == "True"            
            self.datasetInfo[tempDataset.datasetSimpleName] = {
                        "simpleName":tempDataset.datasetSimpleName,
                        "officialName":tempDataset.datasetOfficialName,
                        "genome":tempDataset.genome,
                        "categories":map(lambda x:x.strip(),tempDataset.dataCategories.split("/")),
                        "description":tempDataset.datasetDescription.replace("###","\n"),
                        "moreInfoLink":tempDataset.datasetMoreInfo,
                        "numberOfRegions":0,
                        "datasetType":tempDataset.datasetType,
                        "hasBinning":tempDataset.hasBinning,
                        "isDefault":False,
                        "overlappingText": tempDataset.datasetSimpleName
                        }
            cgsAS = CGSAnnotationsSettings.CGSAnnotationsSettings(datasetName,tempDataset.genome,{},{})
            cgsAS.addRegionDataset({datasetName:tempDataset.getDefaultAnnotationSettings()})
            cgsAS.addFeatureDataset({datasetName:tempDataset.getDefaultAnnotationSettings()})
            additionalSettings = {}
            if additionalSettingsFileName != "None":
                if os.path.isfile(additionalSettingsFileName):
                    cgsASAdditional = CGSAnnotationsSettings.CGSAnnotationsSettings(datasetName,tempDataset.genome,{},{})
                    cgsASAdditional.fromFile(additionalSettingsFileName)
                    additionalSettings = cgsASAdditional.featuresDatasets
                else:
                    exText = "Error: The file for additional settings "+str(additionalSettingsFileName)+" does not exist"
                    log_CDS(exText)
                    raise GDMException,exText
            #multiprocessing needs python2.6
            #result = self.multiprocessingWorkers.apply_async(self.__processDatasetGivenRegions__, (datasetName,cgsAS, {datasetName:tempDataset},False,additionalSettings))
            #resultText = result.get(None)
            #if resultText:
            #    #there was an error
            #    raise GDMException,resultText  
            #multiprocessing needs python2.6
            self.__processDatasetGivenRegions__(datasetName,cgsAS, {datasetName:tempDataset},False,additionalSettings, size, delete_intermediary)
            del cgsAS
        except Exception,ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()            
            log_CDS("processUserDataset:Error: preprocessing problem traceback:"+repr(traceback.format_tb(exc_traceback)))
            errorMessage = str(ex)
            log_CDS("processUserDataset:Error: preprocessing problem "+errorMessage)     
            #send a notification email
            #if notificationEmail:
            try:
                self.sendUserDatasetNotificationEmail(originalSafeDatasetName,datasetName,notificationEmail,errorMessage)
            except Exception,ex1:
                log_CDS("Error: "+"processUserDataset: Problem while sending the mail "+str(ex1))                        
            return [1,errorMessage]
        #send a notification email
        #if notificationEmail:
        try:
            self.sendUserDatasetNotificationEmail(originalSafeDatasetName,datasetName,notificationEmail,"")
            if notificationEmail:
                UserHandling.recordUserDataset(notificationEmail,datasetName)
        except Exception,ex:
            log_CDS("Error: "+"processUserDataset: Problem while sending the mail "+str(ex))
        return [0,datasetName] 
    
    def processUserDatasetFromBuffer(self,datasetName, datasetBuffer, genome, additionalSettings, 
                                     notificationEmail, syncCall,
                                     datasetLink,datasetDesc,computeSettings):
        log_CDS(["processUserDatasetFromBuffer: called with ",datasetName,str(len(datasetBuffer)), genome, notificationEmail, syncCall,datasetLink,datasetDesc,str(additionalSettings),str(computeSettings)])
        originalSafeDatasetName  = getSafeWord(datasetName,"")
        if originalSafeDatasetName[0].isdigit():
            originalSafeDatasetName = "d_"+originalSafeDatasetName
            
        exist = True
        while exist:
            fn = settings.folderForTemporaryUserData + originalSafeDatasetName + ".region." + str(randint(100000,999999))
            exist = os.path.isfile(fn)
        if datasetBuffer.find("\r\n") > -1:
            datasetBuffer = datasetBuffer.translate(None,"\r")
        elif datasetBuffer.find("\n") == -1 and datasetBuffer.find("\r") > -1:
            datasetBuffer = datasetBuffer.replace("\r","\n")
        log_CDS("processUserDatasetFromBuffer: writing the user dataset buffer in "+str(fn))
        fd = open(fn,"w")
        fd.write(datasetBuffer)
        fd.close()
        size = len(datasetBuffer.split("\n"))
        return self.processUserDataset(datasetName, fn, genome, additionalSettings, notificationEmail, syncCall,datasetLink,datasetDesc,computeSettings, size)
        
    def processUserDataset(self,datasetName, regionsFile, genome, additionalSettings, 
                           notificationEmail, syncCall,
                           datasetLink,datasetDesc,computeSettings={}, size=0):        
        log_CDS(["processUserDataset: called with ",datasetName,regionsFile, genome, notificationEmail, syncCall,datasetLink,datasetDesc,str(additionalSettings),computeSettings])        
        originalSafeDatasetName  = getSafeWord(datasetName," ")        
        errorMessage = "" 
        try:
            # get a new unique name
            datasetNewName = self.getUniqueDatasetName(originalSafeDatasetName)
            # chcek the dataset format
            invalidLines = self.checkUserDatasetFormat(regionsFile,genome,computeSettings)            
            datasetName = datasetNewName
            if datasetName[0].isdigit():
                datasetName = "d_"+datasetName            
            # completely new dataset is about to be processed             
            absName = os.path.abspath(settings.downloadDataFolder[genome] + datasetName+".user")
            shutil.copy2(regionsFile,absName)
            additionalSettingsFileName = self.__checkAdditionalSettings__(datasetName, genome, additionalSettings)
            # create an index file for this dataset
            filename = self.__createUserDatasetSettingsFile__(datasetName, regionsFile, genome, 
															  additionalSettingsFileName, 
															  originalSafeDatasetName,
															  datasetDesc,datasetLink,
															  computeSettings)            
            
            log_CDS(["processUserDataset: "+datasetName+" preprocessing is complete"])
            if syncCall:
                self.processUserDatasetCore(datasetName,filename,notificationEmail,originalSafeDatasetName,additionalSettingsFileName, size)
            else:
                subprocess.Popen(["python",getCurrentFolder()+"CGSServerEngine.py","processUserDataset",datasetName,filename,notificationEmail,originalSafeDatasetName,additionalSettingsFileName,str(size)])            
        except Exception,ex:
            #Exception, while preprocessing
            errorMessage = str(ex)
            log_CDS("processUserDataset:Error:"+datasetName+" pre-processing problem "+errorMessage)                
            return [1,errorMessage]
        if computeSettings.has_key("computeReference") and computeSettings["computeReference"]:
            #compute a reference dataset
            log_CDS(["processUserDataset: preprocessing reference start"])            
            referenceSeed = datasetName[datasetNewName.rfind("_")+1:]
            log_CDS(["Seed",datasetName,referenceSeed])
            referenceDatasetName = datasetName[:datasetName.rfind("_")]+"_ref"+datasetName[datasetName.rfind("_"):]
            log_CDS(["refName",referenceDatasetName,datasetName])
            referenceOriginalName = "Control set for "+originalSafeDatasetName
            log_CDS(["refOrigName",referenceOriginalName,originalSafeDatasetName])
            referenceDescription = ""
            if datasetDesc:
                referenceDescription = "A shuffled dataset illustates the properties that the original dataset("+originalSafeDatasetName+") would have if similar regions were chosen at random. The randomized dataset is constructed as for every region from the original dataset a genome region with the same length is selected by random and added to the set"
            unsortedShuffledFile = regionsFile+".shuffled"
            sortedShuffledFile = regionsFile+".shuffled.sorted"
            if computeSettings["mergeOverlaps"]:
                # Because the regions file might be further processed(merged etc), that is why we wait until there
                # is a final bed file and then we shuffle
                finalRegionsBed = settings.rawDataFolder[genome]+datasetName+".bed"
                maxWaitingTime = 15*60
                while not os.path.isfile(finalRegionsBed) and maxWaitingTime >= 0 :
                    time.sleep(10)
                    maxWaitingTime -= 10
                time.sleep(10)
            else:
                finalRegionsBed = regionsFile
             
            shuffleCommand = settings.bedToolsFolder+"shuffleBed -excl "+settings.bedToolsFolder+"../genomes/"+genome+".unassembled.bed -seed "+referenceSeed+" -i "+finalRegionsBed+" -g "+settings.bedToolsFolder+"../genomes/"+genome+".genome >  "+unsortedShuffledFile
            log_CDS(shuffleCommand)
            stdout, stderr = subprocess.Popen(shuffleCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
            if stderr:
                log_CDS("Error: "+str(stderr))
            sortShuffledCommand = settings.bedToolsFolder+"sortBed -i "+unsortedShuffledFile+" > "+sortedShuffledFile
            log(sortShuffledCommand)
            stdout, stderr = subprocess.Popen(sortShuffledCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
            if stderr:
                log_CDS("Error: "+str(stderr))
            refabsName = os.path.abspath(settings.downloadDataFolder[genome] + referenceDatasetName+".user")
            log_CDS("copying reference file to "+refabsName)
            shutil.copy2(sortedShuffledFile,refabsName)
            # create an index file for this dataset
            reffilename = self.__createUserDatasetSettingsFile__(referenceDatasetName, 
																 sortedShuffledFile, 
																 genome, 
																 additionalSettingsFileName, 
																 referenceOriginalName,
																 referenceDescription,
																 "",
																 {})
            log_CDS(["processUserDataset: preprocessing reference is complete in "+reffilename])
            if syncCall:
                self.processUserDatasetCore(referenceDatasetName,reffilename,notificationEmail,referenceOriginalName,additionalSettingsFileName, size)
            else:
                subprocess.Popen(["python",getCurrentFolder()+"CGSServerEngine.py","processUserDataset",referenceDatasetName,reffilename,notificationEmail,referenceOriginalName,additionalSettingsFileName,str(size)])
            log_CDS(["processUserDataset: preprocessing reference is complete"])
        # all is good
        log_CDS("processUserDataset: good end") 
        return [0,datasetName,invalidLines]
    
    def __getAdditionalSettingsFileName__(self,datasetName):
        return settings.folderForTemporaryUserData+datasetName+".additional.settings"
        
    def __checkAdditionalSettings__(self, datasetName, genome, additionalSettings):
        exText = ""
        if len(additionalSettings) == 0:
            return "None"
        additionalSettingsFileName = self.__getAdditionalSettingsFileName__(datasetName)
        try:
            if not isinstance(additionalSettings,dict):
                exText = "Error: __checkAdditionalSettings__ "+str(additionalSettings)+" is not a valid dictionary"            
                raise GDMException
            for datasetName in additionalSettings:
                if not self.defaultDatasets.has_key(datasetName) and not self.datasetInfo.has_key(datasetName):
                    exText = "Error: __checkAdditionalSettings__ '"+str(datasetName)+"' is not a valid dataset"
                    raise GDMException
                if self.datasetInfo[datasetName]["genome"] != genome:
                    exText = "Error: __checkAdditionalSettings__ '"+str(datasetName)+"' is not defined for the genome '"+str(genome)+"'"
                    raise GDMException
                validProperties = {
                                   "useNeighborhood":bool,#defines whether to compute neighborhood for the histone mods
                                   "useNeighborhood":bool,#defines whether to compute neighborhood for the histone mods
                                   }
                for property in additionalSettings[datasetName].keys():
                    if property == "hasFeatures" or \
                       property == "includeGeneDescriptions" or \
                       property == "includeGO" or \
                       property == "includeOMIM" or \
                       property == "useNeighborhood":
                        #defines whether to compute features for this dataset at all
                        if not isinstance(additionalSettings[datasetName][property], bool):
                            exText = "Error: __checkAdditionalSettings__ '"+str(additionalSettings[datasetName][property])+"' is not of the valid type for the property "+str(property)
                            raise GDMException                    
                    elif property == "neighborhoodBeforeStart" or \
                         property == "neighborhoodAfterEnd":
                        if not isinstance(additionalSettings[datasetName][property], list):
                            exText = "Error: __checkAdditionalSettings__ '"+str(additionalSettings[datasetName][property])+"' is not of the valid type for the property "+str(property)
                            raise GDMException
                        if len(additionalSettings[datasetName][property]) > 10:
                            exText = "Error: __checkAdditionalSettings__ '"+str(additionalSettings[datasetName][property])+"' cannot have more thna 10 elements for the property "+str(property)
                            raise GDMException
                        for el in additionalSettings[datasetName][property]:
                            try:
                                x = int(el)
                                if x< 0 or x > 100000:
                                    raise Exception
                            except:
                                exText = "Error: __checkAdditionalSettings__ '"+str(additionalSettings[datasetName][property])+"' invalid element '"+str(el)+"' for property "+str(property)
                                raise GDMException
                    elif property == "includeGenesUpTo":
                        #This is a gne eproprty defining for which genes , we shoudl store overlap information
                        # it must be an interget of minimum 0 and of up to 50,000
                        if not isinstance(additionalSettings[datasetName][property], int):
                            exText = "Error: __checkAdditionalSettings__ '"+str(additionalSettings[datasetName][property])+"' is not of the valid type for the property "+str(property)
                            raise GDMException
                        if additionalSettings[datasetName][property] < 0 or additionalSettings[datasetName][property] > 50000:
                            exText = "Error: __checkAdditionalSettings__ '"+str(additionalSettings[datasetName][property])+"' is invalid value for the property "+str(property)
                            raise GDMException
                        
                    elif property == "patterns":
                        if not isinstance(additionalSettings[datasetName][property], list):
                            exText = "Error: __checkAdditionalSettings__ '"+str(additionalSettings[datasetName][property])+"' is not of the valid type for the property "+str(property)
                            raise GDMException
                        if len(additionalSettings[datasetName][property]) > 20:
                            exText = "Error: __checkAdditionalSettings__ '"+str(additionalSettings[datasetName][property])+"' has too many values for the property "+str(property)
                            raise GDMException
                        if len(additionalSettings[datasetName][property]) != len(set(additionalSettings[datasetName][property])):
                            exText = "Error: __checkAdditionalSettings__ '"+str(additionalSettings[datasetName][property])+"' has duplicates for the property "+str(property)
                            raise GDMException
                       
                        for el in additionalSettings[datasetName][property]:
                            if el != el.upper():
                                exText = "Error: __checkAdditionalSettings__ '"+str(el)+"' is not upper case for the property "+str(property)
                                raise GDMException
                            if el != filter(lambda x:x in "ACGT",el):
                                exText = "Error: __checkAdditionalSettings__ '"+str(el)+"' has invalid cases for the property "+str(property)
                                raise GDMException
                    else:
                        exText = "Error: __checkAdditionalSettings__  invalid property "+str(property)
                        raise GDMException
            cgsAdditional = CGSAnnotationsSettings.CGSAnnotationsSettings(datasetName,genome,{},additionalSettings)
            cgsAdditional.toFile(additionalSettingsFileName)
                 
        except GDMException:
            if exText != "":
                log_CDS(exText)
            raise GDMException, exText
            
        return additionalSettingsFileName# or None

    def processInfiniumDataset(self, file_internal_id, software, referenceDataset, datasetName, scoresIndex, hypoIndex, hyperIndex, rankIndex,
                               notificationEmail, moreInfoLink, description):
        originalSafeDatasetName = getSafeWord(datasetName, " ")             
        datasetNewName = self.getUniqueDatasetName(originalSafeDatasetName)                    
        datasetName = datasetNewName                
        if datasetName[0].isdigit():
            datasetName = "d_" + datasetName
            
        if __debug__:
            self.processInfiniumDatasetInternal(file_internal_id, software, referenceDataset, datasetName, scoresIndex, hypoIndex, hyperIndex, rankIndex, notificationEmail, moreInfoLink, description)
        else:
            t = Thread(target=self.processInfiniumDatasetInternal, args=(file_internal_id, software, referenceDataset,datasetName, scoresIndex, hypoIndex, hyperIndex, rankIndex,notificationEmail, moreInfoLink, description,))
            t.start()
            
        return datasetName

    def processInfiniumDatasetInternal(self, file_internal_id, software, referenceDataset, datasetName, scoresIndex, hypoIndex, hyperIndex, rankIndex,
                               notificationEmail, moreInfoLink, description):

        #TODO(albrecht): check if the referenceDataset exists.
                    
        log_CDS(["processInfiniumDatasetInternal: called with ", datasetName, notificationEmail, moreInfoLink, description])                         
        #absName = os.path.abspath(settings.downloadDataFolder[genome] + datasetName + ".user")
        #shutil.copy2(scoresFile, absName)                      
        data = self.dataStorage.retrieve_file_as_bed(software, file_internal_id)
        self.checkIlluminaDifferentialData(data)
        scoresIndex = int(scoresIndex)
        hypoIndex = int(hypoIndex)
        hyperIndex = int(hyperIndex)
        rankIndex = int(rankIndex)
                
        genome = self.defaultDatasets[referenceDataset].genome                
                
        filename = settings.folderForTemporaryDatasets + datasetName + ".ini"
        f = open(filename, "w")
        f.write("datasetSimpleName = " + datasetName + "\n")
        f.write("datasetWordName = " + datasetName + "\n")
        f.write("genome = " + genome + "\n")
                
        f.write("hasGenomicRegions = True\n")
        f.write("regionsFiltering = \n")
        f.write("hasFeatures = False\n")
        f.write("datasetFrom = " + os.path.abspath(settings.downloadDataFolder[genome] + datasetName + ".user") + "\n")
        #f.write("scoresFile = " + scoresFile + "\n")
        f.write("differentiation = True\n")
        f.write("reference = " + referenceDataset + "\n")
        f.write("datasetPythonClass = ../../GDM/DatasetClasses/Infinium.py\n")
        f.write("datasetOfficialName = " + datasetName + "\n")
        f.write("dataCategories = User\n")
        f.write("datasetDescription = " + description.replace("\n", " ### ") + "\n")
        f.write("datasetMoreInfo = " + moreInfoLink + "\n")
        f.write("datasetType = Default\n")
        f.write("hasBinning = True\n")        
        f.write("hasScores = " + str(scoresIndex >= 0) + "\n")
        f.write("scoresIndex = " + str(scoresIndex) + "\n")        
        f.write("hasHypo = " + str(hypoIndex >= 0) + "\n")
        f.write("hypoIndex = " + str(hypoIndex) + "\n")                
        f.write("hasHyper = " + str(hyperIndex >= 0) + "\n") 
        f.write("hyperIndex = " + str(hyperIndex) + "\n")  
        f.write("hasRank = " + str(rankIndex >= 0) + "\n")
        f.write("rankIndex = " + str(rankIndex) + "\n")
        f.close()
            
        referenceWordName = self.defaultDatasets[referenceDataset].datasetWordName
        datasetWordName = datasetName        
        
        reference_fnwd = getCompleteSearchFinalDocumentsWordsFile(referenceDataset, genome)
        reference_fndd = getCompleteSearchFinalDocumentsDescrioptionsFile(referenceDataset, genome)
        reference_fnpd = getCompleteSearchFinalPrefixesFile(referenceDataset, genome)
        
        dataset_fnwd = getCompleteSearchFinalDocumentsWordsFile(datasetName, genome)
        dataset_fndd = getCompleteSearchFinalDocumentsDescrioptionsFile(datasetName, genome)
        dataset_fnpd = getCompleteSearchFinalPrefixesFile(datasetName, genome)
        
        posInfoMap = {}
        posWordSizeMap = {}
        if scoresIndex >= 0:
            posInfoMap[scoresIndex] = "regionScore"
            posWordSizeMap[scoresIndex] = 4
        if hypoIndex >= 0:
            posInfoMap[hypoIndex] = "hypomethylation"
            posWordSizeMap[hypoIndex] = 4
        if hyperIndex >= 0:
            posInfoMap[hyperIndex] = "hypermethylation"
            posWordSizeMap[hyperIndex] = 4
        if rankIndex >= 0:
            posInfoMap[rankIndex] = "regionRank"                                    
            posWordSizeMap[rankIndex] = 7 # rank from 0 to 9.999.999 million
            
                    
        f_reference = open(reference_fnwd, "r")
        f_dataset = open(dataset_fnwd, "w")
        for l in f_reference.readlines():
            new_line = l.replace(referenceWordName, datasetWordName)
            f_dataset.write(new_line)
        f_reference.close()
        f_dataset.close()
            
        f_reference = open(reference_fndd, "r")
        f_dataset = open(dataset_fndd, "w")
        features_re = re.compile('(\d*)\s+u:\s+t:Features\s+H:')
        for l in f_reference.readlines():
            new_line = l.replace(referenceWordName, datasetWordName)
            f_dataset.write(new_line)
            m = features_re.match(new_line)
            if m is not None:
                featuresDocId = m.group(1)                                 
        f_reference.close()
        f_dataset.close()
                
        f_reference = open(reference_fnpd, "r")
        f_dataset = open(dataset_fnpd, "w")
        for l in f_reference.readlines():
            new_line = l.replace(referenceWordName, datasetWordName)
            f_dataset.write(new_line)                
        for (_, q) in posInfoMap.items():                           
            f_dataset.write("\n" + settings.wordPrefixes[q])                                                            
        f_reference.close()
        f_dataset.close()
                                        
        lines = data.split("\n")        
        fnwd = open(dataset_fnwd, "a")
        docId = 0
        for line in lines:
            docId = docId + 1                        
            values = line.strip().split("\t")
            # For some unknow reason, inside the pydev, the enumerate function is overwrited by another function.
            for idx, val in __builtins__.enumerate(values):
                if val.isdigit():
                    score_line = settings.wordPrefixes[posInfoMap[idx]] + ":" + wordFixed(val, posWordSizeMap[idx]) + "\t" + str(docId) + "\t0\t0\n"
                    fnwd.write(score_line)                                                                
        for (scoresIndex, q) in posInfoMap.items():                           
            line = "features:::" + settings.wordPrefixes[q] + "::0::"+ str(posWordSizeMap[scoresIndex]) + "\t" +featuresDocId + "\t0\t0\n"
            fnwd.write(line)                                        
        fnwd.close()
                     
        retcode = subprocess.call(["cd", settings.indexDataFolder[genome]], shell=True)        
        csDataBuilder.buildCSData(settings.indexDataFolder[genome], datasetName, True)

        # TODO(abrecht): sync file writting.
        f = open(settings.fullyProcessedUserDatasetsFile[genome], "a")
        f.write(datasetName + "=" + datasetName + "\n")
        f.close()
        
        userNewDataset = {"simpleName":datasetName,
                          "officialName":datasetName,
                          "hasBinning":True,
                          "genome":genome,
                          "categories":["User", "Illumina"],
                          "description":description.replace("###", "\n"),
                          "moreInfoLink":moreInfoLink,
                          "numberOfRegions":0,
                          "datasetType":"Default",
                          "isDefault":False,
                          "overlappingText": datasetName
                            }        
    
        self.datasetInfo[datasetName] = userNewDataset
        log_CDS(["processInfiniumDatasetInternal: Added datasetinfo for ", str(datasetName), userNewDataset["officialName"], str(genome)])
                    
        self.fullyProcessedDatasets[datasetName] = datasetName
        try:
            self.queryServer.refreshFullyProcessedServers()
        except:
            log_CDS("__processDatasetGivenRegions__: Query server is not available")
      
        log_CDS(["processInfiniumDatasetInternal: completed for ", str(datasetName), userNewDataset["officialName"], str(genome)])

    # TODO(albrecht): check the number of lines with the model file.       
    def checkIlluminaDifferentialData(self, data):
        lines = data.split("\n")            
        for l in lines:
            l = l.strip()
            if len(l) == 0:
                continue 
            pieces = l.split("\t")
            for p in pieces:
                if not p.isdigit() and p != "NA":
                    raise Exception("Invalid line:"  + l)            
       
    
    def getDatasetInfo(self,datasetSimpleName,properties=[]):
        log_CDS("getDatasetInfo: dataset name "+datasetSimpleName+"properties: "+str(properties))
        if self.datasetInfo.has_key(datasetSimpleName): 
            if not properties:           
                return self.datasetInfo[datasetSimpleName]
            else:
                newDatasetInfo = {}
                for p in properties:
                    try:
                        newDatasetInfo[p] = self.datasetInfo[datasetSimpleName][p]
                    except:
                        pass
                return newDatasetInfo
                    
        else:
            if datasetSimpleName == "all":  
                #return data for all default datasets
                if not properties:
                    # if on properties are giver retrieve only the official names
                    properties = ["officialName"]
                    
                if len(properties) == 1 and properties[0] == "officialName":
                    # if only the official names are to be trieved check if they are not already computed
                    # if they are return them directly
                    if self.defaultAnnotationNames:
                        # already exists
                        return self.defaultAnnotationNames
                # compute all annotations and store them if they include only officialName    
                datasetsInfo = {}
                for dn in self.datasetInfo.keys():                        
                    for p in properties:
                        try:
                            if self.datasetInfo[dn]["isDefault"]:
                                if not datasetsInfo.has_key(dn):
                                    datasetsInfo[dn] = {}
                                datasetsInfo[dn][p] = self.datasetInfo[dn][p]
                        except:
                            pass
                if len(properties) == 1 and properties[0] == "officialName":
                    self.defaultAnnotationNames = datasetsInfo                    
                return datasetsInfo
            else:                
                return {}
        
    def updateDatasetInfo(self,datasetSimpleName,datasetProperty,propertyValue):        
        if self.datasetInfo.has_key(datasetSimpleName):
            self.datasetInfo[datasetSimpleName][datasetProperty] = propertyValue
        return True
    
    def getGeneExtraInfo(self,genome,infoType,elements):
        log(["getGeneExtraInfo called with",genome,infoType,len(elements)])
        # check if genes are a default dataset for this genoem
        genesDatasetKey  = genome+"_ensembl_gene_genes"
        if not self.datasetInfo.has_key(genesDatasetKey):
            log("Error there was no genes dataset("+genesDatasetKey+") for this genome("+genome+"). Not in "+str(self.datasetInfo.keys()))
            return []
        
        # check if the infotype is supported, currently only genes and GO
        if infoType == "genes":
            if not hasattr(self.defaultDatasets[genesDatasetKey],"geneDescriptions"):
                log("Error: gene descriptions are not loaded by the server")
                return []
            hasInfo = {}
            noInfo = []
            for term in elements:
                try:
                    hasInfo[term] = self.defaultDatasets[genesDatasetKey].geneDescriptions[term]
                except KeyError:
                    noInfo.append(term)
            return [hasInfo,noInfo]                    
        elif infoType == "GO":
            if not hasattr(self.defaultDatasets[genesDatasetKey],"fullGO"):
                log("Error: gene GOs are not loaded by the server")
                return [{},elements]
            hasInfo = {}
            noInfo = []
            for term in elements:
                try:
                    hasInfo[term] = self.defaultDatasets[genesDatasetKey].fullGO[term]
                except KeyError:
                    noInfo.append(term)
            return [hasInfo,noInfo] 
        elif infoType == "OMIM":
            if not hasattr(self.defaultDatasets[genesDatasetKey],"fullGO"):
                log("Error: gene OMIMs are not loaded by the server")
                return [{},elements]
            hasInfo = {}
            noInfo = []
            for term in elements:
                try:
                    hasInfo[term] = self.defaultDatasets[genesDatasetKey].fullOMIM[term]
                except KeyError:
                    noInfo.append(term)
            return [hasInfo,noInfo] 
        else:
            log("Error this info type "+infoType+" is not supported")
            return []
        
    def getDatasetAnnotationSettings(self,genome,datasetName,onlyProperties):
        log_CDS(["getDatasetAnnotationSettings called with",str(genome),str(datasetName),str(onlyProperties)])
        defaultAnnotationSettings = {}
        for ds in self.defaultDatasets.keys():
            if self.defaultDatasets[ds].genome == genome:
                if not datasetName or datasetName == ds:
                    fullDefaultSettings = self.defaultDatasets[ds].getDefaultAnnotationSettings()
                    if not fullDefaultSettings["canHaveFeatures"]:
                        # this dataset cannot have features
                        continue                    
                    for property in fullDefaultSettings.keys():
                        if property in onlyProperties:
                            if not defaultAnnotationSettings.has_key(ds):
                                defaultAnnotationSettings[ds] = {}
                            defaultAnnotationSettings[ds][property] = fullDefaultSettings[property]                             
                             
        log_CDS(["getDatasetAnnotationSettings returns",str(defaultAnnotationSettings)])
        return defaultAnnotationSettings
    
    
    def loadHashedQueries(self):
        self.hfn = settings.baseFolder+"Datasets/exportedLinks.txt"
        
        if not os.path.isfile(self.hfn):
            return
        f = open(self.hfn)
        lines = f.readlines()
        f.close() 
        for line in lines:            
            lineParts = line.strip().split(",")
            if len(lineParts) > 1:
                self.hashedQueries[lineParts[0]] = lineParts[1:]
                    
    def getSelectionLink(self,selectionList):
        selectionList = map(str,selectionList)
        log_CDS(["getSelectionLink called with"]+selectionList)
        newSelectionList = filter(lambda x:getSafeWord(x,"[-]%*|") == x,selectionList)
        if len(newSelectionList) != len(selectionList):
            return ["1","Invalid characters in the parameters"]
        
        m = hashlib.md5()
        for el in selectionList:
            m.update(el)        
        queryHash = m.hexdigest()
        if not self.hashedQueries.has_key(queryHash):
            # this has to be made synchronized at some point
            f = open(self.hfn,"a")
            f.write(",".join([queryHash]+selectionList)+"\n")
            f.close()
            self.hashedQueries[queryHash] = selectionList
        return ["0",queryHash]
    
    def getLinkSelection(self,queryHash):
        log_CDS(["getLinkSelection called with "+str(queryHash)])        
        if self.hashedQueries.has_key(queryHash):            
            return self.hashedQueries[queryHash]
        else:
            return []
    def getDatasetStatus(self, datasetID):
        dID = str(datasetID)
        log_CDS(["getDatasetStatus called with '"+datasetID+"'"])
        if self.fullyProcessedDatasets.has_key(datasetID):
            # The dataset as successfully processed        
            return [0]
        else: 
            #waiting, computing or not available
            return self.queuedDatasetComputations.getComputationStatus(datasetID)
    
    def stopWaitingDatasetComputation(self, datasetID):
        dID = str(datasetID)
        log_CDS(["stopWaitingDatasetComputation called with '"+dID+"'"])   
        return self.queuedDatasetComputations.stopWaitingComputation(dID)
    
    def stopDatasetComputation(self, datasetID):
        dID = str(datasetID)
        log_CDS(["stopDatasetComputation called with '"+dID+"'"])   
        return self.queuedDatasetComputations.removeComputation(dID)        
        
    def getStatus(self):
        return "OK"

    def getAntibodyInfo(self, antibody):
        return self.antibodyVocabulary.full(antibody)
    
    def getAntibodyDescription(self, antibody):
        return self.antibodyVocabulary.description(antibody)
    
    def getCellLineInfo(self, cellline):
        return self.cellLineVocabulary.full(cellline)
    
    def getCellLineDescription(self, cellline):
        return self.cellLineVocabulary.description(cellline)
    
    def store_data(self, name, software, data_format, data):
        return self.dataStorage.store_data(name, software, data_format, data)
    
    def retrieve_file(self, software, internal_id):
        return self.dataStorage.retrieve_file(software, internal_id)
        
    
# URL to EpiExplorer processed BED data (We don't have this yet, but we'll add them to the frontend) (example, epiexplorer.mpi-inf.mpg.de/RawAnnotation/20120212/H3K4me3_GM12878.bed.gz)
# How was it processed from EpiExplorer (Example, template, you can fill for all histones and TFBS: the regions from the current selection were intersected with the annotation bed files from UCSC. Every region that overlaps was marked and the percent of the region overlapping with peaks was computed. If a region did not overlap, the distance to the nearest peak was computed. The overlap and distance scores were computed using BEDtools.)

    def getDatasetDescriptions(self, datasetSimpleName):
        log_CDS(["getDatasetDescriptions called with '"+datasetSimpleName+"'"])
        dataset = self.defaultDatasets.get(datasetSimpleName, None)
        if dataset is None:
            log_CDS(["datasetSimpleName '"+datasetSimpleName+"' not found."])
            return {}

        result = {}
        celllines = []
        if hasattr(dataset, 'tissues'):
            celllines = dataset.tissues
            result["tissues_descriptions"] = {}
            result["tissues_details"] = {}

        elif hasattr(dataset, 'tissue'):
            celllines = [dataset.tissue]
            result["tissues_descriptions"] = {}
            result["tissues_details"] = {}

        for cellline in celllines:
            result["tissues_descriptions"][cellline] = self.getCellLineInfo(cellline)[2]
            result["tissues_details"][cellline] = self.getCellLineInfo(cellline)[7]

        if hasattr(dataset, 'histoneMark'):
            result["histonemark"] = dataset.histoneMark
            result["histonemark_info"] = self.getAntibodyDescription(dataset.histoneMark)
            result["histonemark_description"] = self.getAntibodyInfo(dataset.histoneMark)[3]

        if (hasattr(dataset, "datasetWordName")):
            if dataset.datasetWordName == "bhist" or dataset.datasetWordName == "tfbs":
                result["processed"] = "The regions from the current selection were intersected with the annotation bed files from UCSC. Every region that overlaps was marked and the percent of the region overlapping with peaks was computed. If a region did not overlap, the distance to the nearest peak was computed. The overlap and distance scores were computed using BEDtools."

        result["description"] = dataset.datasetDescription
        result["dataURL"] = dataset.downloadUrls
        result["data_date"] = dataset.downloadDate

        return result

    def recordUserLicense(self,userData):
        return UserHandling.recordUserLicense(userData)
    
    def restartUserDatasetComputation(self,datasetID,notificationEmail, syncCall=False):
        filename = self.getCustomDatasetIniFileName(datasetID)
        settingsDict = readSettingsFile(filename)
        size = line_count(settingsDict["datasetOriginal"])
        originalSafeDatasetName = settingsDict["datasetOfficialName"]
        additionalSettingsFileName = self.__getAdditionalSettingsFileName__(datasetID)
        if not os.path.isfile(additionalSettingsFileName):
            additionalSettingsFileName = "None"
        
        
        if syncCall:
            self.processUserDatasetCore(datasetID,filename,notificationEmail,originalSafeDatasetName,additionalSettingsFileName, size)
        else:
            subprocess.Popen(["python",getCurrentFolder()+"CGSServerEngine.py","processUserDataset",datasetID,filename,notificationEmail,originalSafeDatasetName,additionalSettingsFileName,str(size)])
    
    def saveQueuedDatasets(self):
        self.queuedDatasetComputations.saveQueuedDatasets()
    
    def loadQueuedDatasets(self):
        self.queuedDatasetComputations.loadQueuedDatasets()
    
    def setSendingMails(self,doSendMails):
        settings.doSendMails = doSendMails 
        
    def setKeepWordsFiles(self,keepWordsFiles):
        settings.keepWordsFiles = keepWordsFiles
    
    def setFastQueueThreshold(self,newThreshold):
        self.queuedDatasetComputations.setFastQueueThreshold(int(newThreshold))
    
    def getDatasetQueueStatus(self):
        return self.queuedDatasetComputations.status()      
        
if __name__ == '__main__':
    start_msg     = "Starting CGSDatasetServer ThreadedXMLRPCServer:\t" + str(settings.datasetServerHost) + ":" + str(settings.datasetServerPort)
    log_CDS(start_msg)
    print(start_msg)
    server = ThreadedXMLRPCServer.ThreadedXMLRPCServer((settings.datasetServerHost, settings.datasetServerPort), 
                                                       SimpleXMLRPCRequestHandler, 
                                                       encoding='ISO-8859-1', 
                                                       allow_none=True)
    server.request_queue_size = 20
    sys.setcheckinterval(30)#default is 100
    server.register_instance(CGSDatasetServer())
    start_msg = "Running CGSDatasetServer ThreadedXMLRPCServer at:\t" + str(socket.gethostname()) + ":" + str(settings.datasetServerPort)
    log_CDS(start_msg)
    print(start_msg)
    write_pid_to_file("CGSDatasetServer.py", settings.configFolder + "CGSServers.pid.txt")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "CDS Server is stopping..."
            

