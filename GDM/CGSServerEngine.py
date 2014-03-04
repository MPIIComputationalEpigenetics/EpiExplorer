import sys
import socket
import xmlrpclib
#import urllib
#import xml.parsers.expat
#from xml.etree import ElementTree as ET
import gzip
import zipfile
import os.path
from utilities import *
import settings
import readDatasetDescriptions
import CGSAnnotationsSettings


def convertIDsToSingleExportStr(exportType,totalIds):
    newIds = {}
    idsParts = map(lambda x: x.split(":"), totalIds.keys())
    for idParts in idsParts:
        if exportType == "exportRegions":
            newIds[int(idParts[-1])] = "\t".join(idParts[1:4])
        elif exportType == "exportQueryData":
            newIds[int(idParts[-1])] = "\t".join(idParts[1:5])
    
    sortedDataIds = newIds.keys()
    sortedDataIds.sort()
    content = ""
    for sid in sortedDataIds:
        content += newIds[sid] + "\n"
    
    return content

def getQueryUniqueIDAndFile(regionSet,queryParts,type,datasets=[]):
    log_CSEngine(["Engine getQueryUniqueIDAndFile",regionSet,queryParts,type,datasets])    
    queryParts.sort()    
    datasets.sort()
    import hashlib
    m = hashlib.md5()
    m.update(type)
    m.update(regionSet)
    m.update("::qq::".join(queryParts))
    m.update(",".join(datasets))
    queryHash = m.hexdigest()
    queryExportFileName = settings.exportBaseFolder+type+'_'+queryHash+'.zip'
    log_CSEngine(["Engine getQueryUniqueIDAndFile result",queryHash, queryExportFileName])
    return queryHash, queryExportFileName

def exportDataInitializeStructures(datasets,regionSet,exportGenome):
    raise GDMException, "openDBDataConnection was changed"
    initializadDatasets = {}    
    cgsAS = CGSAnnotationsSettings.CGSAnnotationsSettings(regionSet,exportGenome,{},{})
    datasetsIndexFile = getMainDatasetIndexFileName(exportGenome)
    defaultDatasets = readDatasetDescriptions.readDatasets(datasetsIndexFile)
    #fullyProcessedDefaultDatasets = readSettingsFile(settings.fullyProcessedDefaultDatasetsFile)
    for datasetKey in defaultDatasets.keys():
        if not datasetKey in datasets or cgsAS.getFeatureDatasetProperty(datasetKey,"hasFeatures") == False:
            log_CSEngine("exportDataInitializeStructures: Skipping "+datasetKey)
            continue                            
        log_CSEngine("exportDataInitializeStructures: Loading "+datasetKey)                
        defaultDatasets[datasetKey].init(False)
        defaultDatasets[datasetKey].openDBDataConnection(cgsAS)
        initializadDatasets[datasetKey] = defaultDatasets[datasetKey]
        if datasetKey == regionSet:
            cgsAS.addRegionDataset({datasetKey:{}})
        cgsAS.addFeatureDataset({datasetKey:{}})
    return initializadDatasets        
        
def exportDataForDataset(queryExportFileName,ids,regionSet,queryParts,exportType,dataset):
    log_CSEngine([ "Extracting data for dataset",dataset.datasetSimpleName])
    readme = ""
    # extract its data table name
    dataset.cD.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")                
    try:
        datasetName = str(dataset.cD.fetchone()[0])
    except Exception,ex:
        log_CSEngine([  "Error: No data for dataset ",ex])
        return ""        
    content = ""   
    log_CSEngine([ "Start keys",len(ids)])
    METHOD = "download all"
    if METHOD == "one_by_one":
        i = 0     
        for key in ids:
            i += 1
            if i % 100 == 0:
                log_CSEngine([ key,i])
            #print "Key",key         
            dataset.cD.execute("SELECT * FROM "+datasetName+" WHERE regionID="+str(key))
            for row in dataset.cD:             
                content += "\t".join(map(str,row))+"\n"
    elif METHOD == "download all":
        index = 0
        l = len(ids)
        dataset.cD.execute("SELECT * FROM "+datasetName+" ORDER BY regionID")
        try:
            for row in dataset.cD:
                indexAdjusted = False
                while not indexAdjusted:
                    if row[0] == ids[index]:
                         content += "\t".join(map(str,row))+"\n"
                         indexAdjusted = True
                    elif row[0] < ids[index]:
                        indexAdjusted = True
                    elif row[0] > ids[index]:
                        index += 1
                        if index == l:
                            raise GDMException, "Error: Index out"    
                        if index % 5000 == 0:
                            log_CSEngine([ index])                    
                        
        except GDMException:
            pass
            
                    
    log_CSEngine("Header")
    header = map(lambda x:str(x[0]),dataset.cD.description)
    #log_CSEngine("Content")    
    content = "\t".join(header)+"\n"+content 
    baseFileName = datasetName+".txt"
    #log_CSEngine("Content")
    exportToZip(queryExportFileName,baseFileName,content)
    readme = "#\n"
    readme += "###\t"+baseFileName+"\n"            
    readme += "###\tFormat:\t"+"\t".join(header)+"\n"    
    readme += "#\n"
    return readme
         
def exportData(queryExportFileName,totalIds,regionSet,queryParts,exportType,datasets,exportGenome):
    raise GDMException, "openDBDataConnection was changed"
    log_CSEngine(["Engine exportData",queryExportFileName,len(totalIds),regionSet,queryParts,exportType,datasets])
    initializadDatasets = exportDataInitializeStructures(datasets,regionSet,exportGenome)
    if len(initializadDatasets.keys())  == 0:
        exText = "Engine exportData no recognizable datasets in "+", ".join(datasets)
        log_CSEngine(exText)
        raise exText
    ids = map(lambda x:int(x.split(":")[-1]),totalIds.keys())
    ids.sort()
    readme = ""
    # for every dataset
    for datasetKey in initializadDatasets.keys():
        dataset = initializadDatasets[datasetKey]
        readme += exportDataForDataset(queryExportFileName,ids,regionSet,queryParts,exportType,dataset)
        #print dataset,readme
        #raise Exception
    #raise Exception             
    return readme
                                                 
    
def exportRegions(exportFileName,totalIds,exportType):
    log_CSEngine(["Engine exportRegions",exportFileName,len(totalIds),exportType])
    baseFileName = "regions.txt"

    content = convertIDsToSingleExportStr()
    
    exportToZip(exportFileName,baseFileName,content)
    
    log_CSEngine(["Engine exportRegions result ",exportFileName])
    readmeDesc = "#\n"
    readmeDesc += "###\t"+baseFileName+"\n"
    if exportType == "exportRegions":        
        readmeDesc += "###\tFormat: chromosome\tchromosome start\tchromosome end\n"
    elif exportType == "exportQueryData":
        readmeDesc += "###\tFormat: chromosome\tchromosome start\tchromosome end\tregionID\n"
    readmeDesc += "#\n"
    return readmeDesc

def exportToZip(zipFileName,baseFileName,content):
    log_CSEngine(["Engine exportToZip start ",zipFileName,baseFileName,len(content)])
    #os.chdir(os.path.dirname(zipFileName))
    #f = zipfile.ZipFile(os.path.basename(zipFileName),"a",zipfile.ZIP_DEFLATED)
    if os.path.isfile(zipFileName):
        mode = "a"
    else:
        mode = "w"    
    f = zipfile.ZipFile(zipFileName,mode,zipfile.ZIP_DEFLATED)
    #f = zipfile.ZipFile(zipFileName,mode)
    f.writestr(baseFileName, content)
    f.close()    
    log_CSEngine(["Engine exportToZip end "])
    #f = gzip.open(os.path.basename(exportFileName), 'wb')
    #f.write(content)
    #f.close()
    
def exportToGz(zipFileName):
    log_CSEngine(["Engine exportToGz start ",zipFileName])
    os.chdir(os.path.dirname(zipFileName))
    f = zipfile.ZipFile(os.path.basename(zipFileName),"a",zipfile.ZIP_DEFLATED)
    #f = gzip.open(os.path.basename(zipFileName)+".gz", 'wb')
    f.write(open(zipFileName).read())
    f.close()   
    log_CSEngine(["Engine exportToGz end "])

def getBaseReadme(totalIds,regionSet,queryParts,datasets,exportType):
    readmeBase = "# "
    readmeBase += "# This is an export from Complete Genome Search \n"
    readmeBase +=  "# \n"
    readmeBase += "# The export summarizes the data for\n"
    readmeBase += "# Region set: "+regionSet+"\n"
    if queryParts:
        readmeBase += "# Query: '"+" ,".join(queryParts)+"'\n"
    else:
        readmeBase += "# Query: None\n"
    if datasets:
        readmeBase += "# Datasets: '"+" ,".join(datasets)+"'\n"
    readmeBase +=  "# \n"
    readmeBase +=  "# This query resulted in "+str(len(totalIds))+" genomic regions\n"
    readmeBase +=  "# The related data for them is listed in the following files\n"
    readmeBase +=  "# \n"
    return readmeBase
         
def getGenesFromQuery(regionSet, queryParts, exportType):
    log_CSEngine(["Engine getIDsfromQuery",regionSet,str(queryParts)])
    currentDocIndex = 0
    maxNumber = 1000
    queryBase =" ".join(queryParts)    
    extraSettings = "rd=1a"
    allResults = []
    queryServer = xmlrpclib.Server("http://"+socket.gethostname()+":"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    #queryServer = xmlrpclib.Server("http://infao3806:"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    queryResult = queryServer.answerQuery(queryBase, 0,maxNumber, regionSet,extraSettings+"&f="+str(currentDocIndex),False)
    for geneTitle in queryResult[4].keys():        
        geneTitleParts = geneTitle.split(" ")
        if exportType == "TABLE":
            allResults.append([geneTitleParts[1],geneTitleParts[2]," ".join(geneTitleParts[3:])])
        elif exportType == "ENSEMBL":         
            if geneTitleParts[1]:
                allResults.append([geneTitleParts[1]])
        elif exportType == "SYMBOL":
            if geneTitleParts[2]:
                allResults.append([geneTitleParts[2]])
    while currentDocIndex + maxNumber < int(queryResult[2]):
        currentDocIndex += maxNumber
        queryResult = queryServer.answerQuery(queryBase, 0,maxNumber, regionSet,extraSettings+"&f="+str(currentDocIndex),False)
        for geneTitle in queryResult[4].keys():        
            geneTitleParts = geneTitle.split(" ")
            if exportType == "TABLE":
                allResults.append([geneTitleParts[1],geneTitleParts[2]," ".join(geneTitleParts[3:])])
            elif exportType == "ENSEMBL":         
                if geneTitleParts[1]:
                    allResults.append([geneTitleParts[1]])
            elif exportType == "SYMBOL":
                if geneTitleParts[2]:
                    allResults.append([geneTitleParts[2]])
    return allResults

def getGOtermsFromQuery(regionSet,queryParts):
    log_CSEngine(["Engine getGOtermsFromQuery",regionSet,str(queryParts)])
    maxNumber = 1000    
    sortingKey = "d"
    maxProcessedID = "gGOd:AAA"
    maxWord = "gGOd:zzz"    
    queryBase =" ".join(queryParts)    
    extraSettings = "rw=3"+sortingKey
    #queryServer = xmlrpclib.Server("http://infao3806:"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    queryServer = xmlrpclib.Server("http://"+socket.gethostname()+":"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    queryResult = queryServer.answerQuery(queryBase+" gGOd:*", 1,0, regionSet,extraSettings,False)
    totalIds = {}
    origCompletions = int(queryResult[1])
    currentIdsCount = 0  
    for id in queryResult[3].keys():        
        totalIds[id] = int(queryResult[3][id])
        if sortingKey == "d":
             maxWord = id
        currentIdsCount += 1 
    log_CSEngine(["Engine getGOtermsFromQuery", origCompletions,origCompletions,len(totalIds),maxWord])
    while currentIdsCount < origCompletions:
        newQuery = queryBase+" "+str(maxProcessedID)+"--"+str(maxWord)+" gGOd:*"
        queryResult = queryServer.answerQuery(newQuery, maxNumber,0, regionSet,extraSettings,False)
        maxWordOld = maxWord
        for id in queryResult[3].keys():
            if totalIds.has_key(id):
                if id != maxWordOld:
                    raise Exception, "Error: GO term "+ id +" is already processed"
            else:
                totalIds[id] = int(queryResult[3][id])
                if sortingKey == "d" and id < maxWord:
                     maxWord = id
                currentIdsCount += 1
        log_CSEngine(["Engine getGOtermsFromQuery", origCompletions,origCompletions,len(totalIds),maxWord])    
    return totalIds 

def getOMIMtermsFromQuery(regionSet,queryParts):
    log_CSEngine(["Engine getOMIMtermsFromQuery",regionSet,str(queryParts)])
    maxNumber = 1000    
    sortingKey = "d"
    maxProcessedID = "omimD:AAA"
    maxWord = "omimD:zzz"    
    queryBase =" ".join(queryParts)    
    extraSettings = "rw=3"+sortingKey
    #queryServer = xmlrpclib.Server("http://infao3806:"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    queryServer = xmlrpclib.Server("http://"+socket.gethostname()+":"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    queryResult = queryServer.answerQuery(queryBase+" omimD:*", 1,0, regionSet,extraSettings,False)
    totalIds = {}
    origCompletions = int(queryResult[1])
    currentIdsCount = 0  
    for id in queryResult[3].keys():        
        totalIds[id] = int(queryResult[3][id])
        if sortingKey == "d":
             maxWord = id
        currentIdsCount += 1 
    log_CSEngine(["Engine getOMIMtermsFromQuery", origCompletions,origCompletions,len(totalIds),maxWord])
    while currentIdsCount < origCompletions:
        newQuery = queryBase+" "+str(maxProcessedID)+"--"+str(maxWord)+" omimD:*"
        queryResult = queryServer.answerQuery(newQuery, maxNumber,0, regionSet,extraSettings,False)
        maxWordOld = maxWord
        for id in queryResult[3].keys():
            if totalIds.has_key(id):
                if id != maxWordOld:
                    raise Exception, "Error: OMIM term "+ id +" is already processed"
            else:
                totalIds[id] = int(queryResult[3][id])
                if sortingKey == "d" and id < maxWord:
                     maxWord = id
                currentIdsCount += 1
        log_CSEngine(["Engine getOMIMtermsFromQuery", origCompletions,origCompletions,len(totalIds),maxWord])    
    return totalIds 

def getGOCategoriesFromQuery(regionSet,queryParts):
    log_CSEngine(["Engine getGOCategoriesFromQuery",regionSet,str(queryParts)])    
    currentDocIndex = 0
    maxNumber = 1000
    #completionsLastPart = queryParts[-1]
    #queryParts[-1] = "GOterm"
    queryParts.append("GOterm")
    queryBase =" ".join(queryParts)    
    extraSettings = "rd=1a"
    allResults = {}
    queryServer = xmlrpclib.Server("http://"+socket.gethostname()+":"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    #queryServer = xmlrpclib.Server("http://infao3806:"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    queryResult = queryServer.answerQuery(queryBase, 0,maxNumber, regionSet,extraSettings+"&f="+str(currentDocIndex),False)
    for goTitle in queryResult[4].keys():        
        geneTitleParts = goTitle.split(" ")
        allResults[geneTitleParts[1]] = [int(geneTitleParts[2])," ".join(geneTitleParts[3:])]                 
    while currentDocIndex + maxNumber < int(queryResult[2]):
        currentDocIndex += maxNumber
        queryResult = queryServer.answerQuery(queryBase, 0,maxNumber, regionSet,extraSettings+"&f="+str(currentDocIndex),False)
        for goTitle in queryResult[4].keys():        
            geneTitleParts = goTitle.split(" ")
            allResults[geneTitleParts[1]] = [int(geneTitleParts[2])," ".join(geneTitleParts[3:])]    
    
    ## process the completions and stuff now
    queryParts.pop(-1)
    #queryParts[-1] = completionsLastPart    
    sortingKey = "d"
    maxNumber = 20000
    maxProcessedID = "gGO:G"
    maxWord = "gGO:Z"    
    queryBase =" ".join(queryParts)    
    extraSettings = "rw=3"+sortingKey
    #queryServer = xmlrpclib.Server("http://infao3806:"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    #queryServer = xmlrpclib.Server("http://"+socket.gethostname()+":"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    queryResult = queryServer.answerQuery(queryBase+" gGO:*", 1,0, regionSet,extraSettings,False)
    totalResults = {}
    origCompletions = int(queryResult[1])
    currentIdsCount = 0  
    for id in queryResult[3].keys():
        nr = int(queryResult[3][id])
        shortID = id[4:]
        totalResults[id] = [nr/float(allResults[shortID][0]),nr]+ allResults[shortID]        
        if sortingKey == "d":
             maxWord = id
        currentIdsCount += 1
    
    log_CSEngine(["Engine getGOtermsFromQuery", origCompletions,origCompletions,len(totalResults),maxWord])
    while currentIdsCount < origCompletions:
        newQuery = queryBase+" "+str(maxProcessedID)+"--"+str(maxWord)+" gGO:*"
        queryResult = queryServer.answerQuery(newQuery, maxNumber,0, regionSet,extraSettings,False)
        maxWordOld = maxWord
        for id in queryResult[3].keys():
            if totalResults.has_key(id):
                if id != maxWordOld:
                    raise Exception, "Error: GO term "+ id +" is already processed"
            else:
                nr = int(queryResult[3][id])
                shortID = id[4:]        
                totalResults[id] = [nr/float(allResults[shortID][0]),nr]+ allResults[shortID] 
                if sortingKey == "d" and id < maxWord:
                     maxWord = id
                currentIdsCount += 1
        log_CSEngine(["Engine getGOtermsFromQuery", origCompletions,origCompletions,len(totalResults),maxWord])
    print len(totalResults.keys()) ,len(allResults.keys())
    return totalResults 
    
def getIDsfromQuery(regionSet,queryParts):
    log_CSEngine(["Engine getIDsfromQuery",regionSet,str(queryParts)])
    maxNumber = 1000    
    sortingKey = "d"
    maxProcessedID = "ID:b"
    maxWord = "ID:d"    
    queryBase =" ".join(queryParts)    
    extraSettings = "rw=3"+sortingKey
    queryServer = xmlrpclib.Server("http://"+socket.gethostname()+":"+str(settings.queryServerPort),encoding='ISO-8859-1',allow_none=True)
    queryResult = queryServer.answerQuery(queryBase+" ID:*", 1,0, regionSet,extraSettings,False)
    totalIds = {}
    origCompletions = int(queryResult[1])
    currentIdsCount = 0  
    for id in queryResult[3].keys():        
        totalIds[id] = 1
        if sortingKey == "d":
             maxWord = id
        currentIdsCount += 1 
    log_CSEngine(["Engine getIDsfromQuery", origCompletions,origCompletions,len(totalIds),maxWord])
    while currentIdsCount < origCompletions:
        newQuery = queryBase+" "+str(maxProcessedID)+"--"+str(maxWord)+" ID:*"
        queryResult = queryServer.answerQuery(newQuery, maxNumber,0, regionSet,extraSettings,False)
        maxWordOld = maxWord
        for id in queryResult[3].keys():
            if totalIds.has_key(id):
                if id != maxWordOld:
                    raise Exception, "Error: Id "+ id +" is already processed"
            else:
                totalIds[id] = 1
                if sortingKey == "d" and id < maxWord:
                     maxWord = id
                currentIdsCount += 1
        log_CSEngine(["Engine getIDsfromQuery", origCompletions,origCompletions,len(totalIds),maxWord])    
    return totalIds      
#  Deprecated, not used currently 
def retriveDataForIds(ids,datasetCollectionName):    
    raise Exception, " Error: Not completed"    
    datasetsIndexFile = getMainDatasetIndexFileName(datasetCollectionName)
    datasets = readDatasetDescriptions.readDatasets(datasetsIndexFile,datasetCollectionName)
    for datasetKey in datasets.keys():
        dataset = datasets[datasetKey]
        if cgsAS.getFeatureDatasetProperty(datasetKey,"hasFeatures") == False:
            continue            
        dataset.openDBDataConnection(cgsAS)
    regionData = {}
    for id in ids:
        regionData[id] = {}
    for datasetKey in datasets.keys():
        dataset = datasets[datasetKey]
        for id in ids:
            raise Exception, "Error: Not completed"
       

#sys.argv = [getCurrentFolder()+"CGSServerEngine.py',"exportRegions", 'cgihunter_CpG_Islands','overlaps:exons;overlaps:introns', 'korako@gmail.com']
#sys.argv = [getCurrentFolder()+"CGSServerEngine.py',"exportQueryData", 'cgihunter_CpG_Islands','overlaps:exons::qq::overlaps:introns', 'korako@gmail.com','uw_DNaseI,ensembl_gene_TSS,ucsc_cpg_islands,broad_histones,tiling_around_genes,repeat_masker,cgihunter_CpG_Islands,ensembl_gene_exons,ensembl_gene_genes,ensembl_gene_promoters_region,conservation,ensembl_gene_promoters_centered,tiling_genome_wide,ensembl_gene_promoters']
if __name__ == '__main__':
    expectedNumberOfParams = {"exportRegions":5,
                              "exportQueryData":6,
                              "processUserDataset":6
                              }
    log_CSEngine("CSEngine was called with params "+str(sys.argv))
    if sys.argv[1] == "exportRegions" or sys.argv[1] == "exportQueryData":
        if len(sys.argv) < expectedNumberOfParams[sys.argv[1]]:
            log_CSEngine("Error: the parameters should be at least "+str(expectedNumberOfParams[sys.argv[1]])+" "+str(sys.argv))
        else:
            exportType = sys.argv[1]
            regionSet = sys.argv[2]
            if sys.argv[3] == "None":
                queryParts = []
            else:
                queryParts = sys.argv[3].strip().split("::qq::")
            mail = sys.argv[4]
            if exportType == "exportQueryData":
                if sys.argv[5] == "None":
                    datasets = []
                else:
                    datasets = sys.argv[5].split(",") 
            elif exportType == "exportRegions":
                datasets = []
            queryHash,queryExportFileName = getQueryUniqueIDAndFile(regionSet,queryParts,exportType,datasets)
            datasetServer = xmlrpclib.Server("http://"+socket.gethostname()+":"+str(settings.datasetServerPort),encoding='ISO-8859-1',allow_none=True)
            datasetInfo = datasetServer.getDatasetInfo(regionSet)
            exportGenome = datasetInfo["genome"]
            datasetReadableNames = []
            for dataset in datasets:
                datasetTempInfo = datasetServer.getDatasetInfo(dataset)
                datasetReadableNames.append(datasetTempInfo["officialName"])
                
            if os.path.isfile(queryExportFileName):
                #the file already exists
                log_CSEngine(" The export file for this export query already exists at "+queryExportFileName)
            else:
                try:
                    totalIds = getIDsfromQuery(regionSet,queryParts)
                    if len(totalIds) == 0:
                        # if there are no regions fitting this query
                        datasetServer.sendExportNotificationEmail(exportType, regionSet, queryParts,"", mail,datasetReadableNames,"No regions fitting the query")
                    else:
                        readmeText = getBaseReadme(totalIds,datasetInfo["officialName"],queryParts,datasets,exportType)                                             
                        readmeTextRegions = exportRegions(queryExportFileName,totalIds,exportType)
                        readmeText += readmeTextRegions
                        if exportType == "exportQueryData":
                            raise GDMException, "openDBDataConnection was changed"                        
                            readmeText += exportData(queryExportFileName,totalIds,regionSet,queryParts,exportType,datasets,exportGenome)
                        elif exportType == "exportRegions":
                            #nothing extra to do for exporting regions   
                            pass
                            
                        exportToZip(queryExportFileName,"README",readmeText)                        
                        #exportToGz(queryExportFileName)
                            
                except Exception,ex:
                    exText = str(ex)
                    log_CSEngine("Error: " + exText)
                    datasetServer.sendExportNotificationEmail(exportType, datasetInfo["officialName"], queryParts,"", mail,datasetReadableNames,exText)
                    raise
            # if things finished properly send the user an email
            datasetServer.sendExportNotificationEmail(exportType, regionSet, queryParts,queryExportFileName, mail,datasets,"")
    
    elif sys.argv[1] == "processUserDataset":    
        if len(sys.argv) < expectedNumberOfParams[sys.argv[1]]:
            log_CSEngine("Error: the parameters should be at least "+str(expectedNumberOfParams[sys.argv[1]])+" "+str(sys.argv))
        else:        
            datasetName = sys.argv[2]
            filename = sys.argv[3]
            notificationEmail = sys.argv[4]
            originalSafeDatasetName = sys.argv[5]
            additionalSettingsFileName = sys.argv[6]
            size = int(sys.argv[7])
            datasetServer = xmlrpclib.Server("http://"+socket.gethostname()+":"+str(settings.datasetServerPort),encoding='ISO-8859-1',allow_none=True)
            datasetServer.processUserDatasetCore(datasetName,filename,notificationEmail,originalSafeDatasetName,additionalSettingsFileName,size)
    
    
    

    