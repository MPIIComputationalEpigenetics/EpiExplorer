from utilities import *
import os
import os.path
import time
import sqlite3
import random
import utilities

def exportAllData(datasets, cgsAS):
    log(cgsAS.datasetCollectionName+": Exporting all data")
    fnwd = getCompleteSearchDocumentsWordsFile(cgsAS.datasetCollectionName, cgsAS.genome)
    fndd = getCompleteSearchDocumentsDescrioptionsFile(cgsAS.datasetCollectionName, cgsAS.genome)
    fnpd = getCompleteSearchPrefixesFile(cgsAS.datasetCollectionName, cgsAS.genome)
    # Switch off the exit if the words and docs file already exist
    #if os.path.isfile(fnwd) and os.path.isfile(fndd):
    #     log(cgsAS.datasetCollectionName+": Export files already exist \n\t\t"+fnwd+"\n\t\t"+fndd)
    #     return

    csDir = getCompleteSearchDirectory(cgsAS.genome)
    if not os.path.isdir(csDir):
        os.makedirs(csDir)

    fwd = open(fnwd,"w",10000000)
    fdd = open(fndd,"w",1000000)
    try:
        currentDocumentIndex = exportRegionsData(fdd,fwd,datasets,cgsAS)
        exportExtraData(fdd,fwd,datasets,cgsAS,currentDocumentIndex)

    except:
        #delete the temporary files and exit
        os.unlink(fnwd)
        os.unlink(fndd)
        os.unlink(fnpd)
        raise

    fdd.close()
    fwd.close()
    #exporting word prefixes
    exportWordPrefixes(fnpd,fnwd,datasets,cgsAS)

def exportWordPrefixes(prefixesFileName,wordFileName,datasets,cgsAS):
    log(cgsAS.datasetCollectionName+": Exporting prefixes")
    prefixes = set(exportRegionPrefixes(cgsAS))
    prefixes.update(set(exportExtraPrefixes()))
    for datasetKey in datasets.keys():
        if cgsAS.getFeatureDatasetProperty(datasetKey,"hasFeatures") == False:
            continue
        datasetPrefixes = set(datasets[datasetKey].getWordPrefixes(cgsAS))
        #print datasetKey,list(datasetPrefixes)
        prefixes.update(datasetPrefixes)
    prefixesList = list(prefixes)
    prefixesList.sort()

    #check that each of those prefixes occurs in the words file

    prefixesListToRemove = [prefix for prefix in prefixesList]
    lenPrefixesListToRemove = len(prefixesListToRemove)
    fw = open(wordFileName)
    line = fw.readline()
    while line and lenPrefixesListToRemove > 0:
        for w in prefixesListToRemove:
            if line.startswith(w):
                prefixesListToRemove.remove(w)
                lenPrefixesListToRemove -= 1
                break
        line = fw.readline()
    fw.close()
    log([cgsAS.datasetCollectionName,"These prefixes do not occur in the words file: ", prefixesListToRemove])
    for w in prefixesListToRemove:
        prefixesList.remove(w)

    log([cgsAS.datasetCollectionName,"All prefixes sorted",prefixesList])
    fpd = open(prefixesFileName,"w")
    fpd.write("\n".join(prefixesList))
    fpd.close()
    log(cgsAS.datasetCollectionName+": Prefixes exported")


def exportRegionsData(fdd,fwd,datasets,cgsAS):
    log(cgsAS.datasetCollectionName+": Exporting the regions data")
    try:
        #load the regions file
        regionsFile = getRegionsCollectionName(cgsAS.datasetCollectionName,cgsAS.genome)
        connRegions = sqlite3.connect(regionsFile)
        cR = connRegions.cursor()
        datasetDataConnections = {}
        for datasetKey in datasets.keys():
            dataset = datasets[datasetKey]
            if cgsAS.getFeatureDatasetProperty(datasetKey,"hasFeatures") == False:
                log(cgsAS.datasetCollectionName+": Dataset "+datasetKey+" does not provide features to be exported")
                continue
            datasetDataConnections[datasetKey] = dataset.openDBConnections(cgsAS)
            datasetDataConnections[datasetKey][0][1].execute("SELECT * FROM " + dataset.datasetSimpleName + "_data ORDER BY regionID")

        log(cgsAS.datasetCollectionName+": All database connections opened with data aligned and waiting for fetching")
        #wdbuffer = ""
        #ddbuffer = ""
        bufferedDatasetLines = {}
        # format: id, chrom, start, stop, datasetID,datasetName
        cR.execute("SELECT * FROM regions JOIN datasets ON regions.datasetID = datasets.datasetID ORDER BY regionID")
        log(cgsAS.datasetCollectionName+": ExportRegionsData - regions are sorted")
        i = 0
        for regionData in cR:
            i += 1
            regionWords = []
            regionWordsWithScores = []

            regionID = regionData[0]
            regionWordsD = exportRegionWords(cgsAS,regionID,regionData[1],regionData[2],regionData[3],regionData[5],regionData[6],regionData[7])
            regionWords.extend(regionWordsD)
            allData = {}
            dataCompleted = {}
            for datasetKey in datasets:
                dataCompleted[datasetKey] = False
            try:
                #for every region extract the columns from every database
                for datasetKey in datasets:
                    dataset = datasets[datasetKey]
                    if cgsAS.getFeatureDatasetProperty(datasetKey,"hasFeatures") == False:
                        continue
                    if dataCompleted[datasetKey]:
                        continue

                    # if there is a buffered data load it,otherwise read a new line from the DB
                    if bufferedDatasetLines.has_key(datasetKey):
                        datasetData = bufferedDatasetLines[datasetKey]
                    else:
                        try:
                            datasetData = list(datasetDataConnections[datasetKey][0][1].fetchone())
                        except TypeError:
                            dataCompleted[datasetKey] = True
                            continue
                    if datasetData[0] > regionID:
                        bufferedDatasetLines[datasetKey] = datasetData
                    elif datasetData[0] == regionID:
                        try:
                            while datasetData[0] == regionID:
                                regionWordsD,regionWordsWithScoresD = dataset.getRegionComputedDataFromExtractedLine(datasetData, cgsAS)
                    #            regionWordsD = dataset.getRegionComputedData(regionWords["region:ID"])
                                regionWords.extend(regionWordsD)
                                regionWordsWithScores.extend(regionWordsWithScoresD)
                                datasetData = list(datasetDataConnections[datasetKey][0][1].fetchone())
                        except TypeError,ex:
                            #log("MARK:"+str(ex)+str([regionID,datasetKey,datasetData]))
                            #log("Error:"+str(ex)+str([datasetData[0],regionID,regionWordsD]))
                            dataCompleted[datasetKey] = True
                            if bufferedDatasetLines.has_key(datasetKey):
                                del bufferedDatasetLines[datasetKey]
                            continue
                        if datasetData:
                            bufferedDatasetLines[datasetKey] = datasetData
                    else:
                        if dataCompleted[datasetKey]:
                            pass
                        else:
                            log(["Error:",datasetKey,datasetData,regionID,regionWords])
                            raise Exception, str(regionID)+ " != "+str(datasetData[0])
            except Exception,ex:
                log(["Error:",str(ex),regionData,datasetKey,datasetData])
                #remove the current words and docs files
                raise


            #print regionWords
            #import time
            #time.sleep(10)
            # add word document data
            wdbuffer = appendRegionWordDocumentDataBuffer(str(regionID),regionWords,regionData,cgsAS,False)
            fwd.write(wdbuffer)
            wdbuffer = appendRegionWordDocumentDataBuffer(str(regionID),regionWordsWithScores,regionData,cgsAS,True)
            fwd.write(wdbuffer)

            #if len(wdbuffer) > 1000000:
            #    fwd.write(wdbuffer)
            #    wdbuffer = ""
            # add document description
            ddbuffer = appendRegionDocumentDescriptionBuffer(regionID,regionWords,regionData,cgsAS)
            fdd.write(ddbuffer)
            #if len(ddbuffer) > 100000:            
                #fdd.write(ddbuffer)
                #ddbuffer = ""
            if i % 50000 == 0:
                log([i,"exported"])                
    finally:
        try:
            for datasetKey in datasets.keys():
                try:
                    if datasetDataConnections.has_key(datasetKey):
                        datasets[datasetKey].closeDBConnections(datasetDataConnections[datasetKey])
                except:
                    pass
            cR.close()
            connRegions.close()
        except:
            pass
    #fdd.write(ddbuffer)
    #fwd.write(wdbuffer)
    log(cgsAS.datasetCollectionName+": All regions data was exported")
    return i

def exportExtraDataSettings(fdd,fwd,datasets,cgsAS,documentID):
    #write the settigns documents
    sep = "\t"
    sdID = str(documentID)
    base = settings.wordPrefixes["settings"]
    settingsSep = "::"
    settingsWords = [[],
                     ["date",str(time.strftime("%y:%m:%d:%H:%M:%S"))],
                     ["genome",cgsAS.genome],
                     ["dataset_name",cgsAS.datasetCollectionName]]

    restrictedFeatures = ["localRegionCursor","datasetId","insertSQL","data","currentLoadedChromosome","currentLoadedChromosomeSeq"]
    #add the region settings
    for region in cgsAS.regionDatasets.keys():
        settingsWords.append(["r","dataset",region])
        for regionSetting in cgsAS.regionDatasets[region].keys():
            if regionSetting not in restrictedFeatures:
                if isinstance(cgsAS.regionDatasets[region][regionSetting],list):
                    settingsWords.append(["r",str(region),str(regionSetting),":".join(map(str,cgsAS.regionDatasets[region][regionSetting]))])
                else:
                    settingsWords.append(["r",str(region),str(regionSetting),getSafeWord(str(cgsAS.regionDatasets[region][regionSetting]))])
    #add all feature settings
    for feature in cgsAS.featuresDatasets.keys():
        settingsWords.append(["f","dataset",feature])
        for featureSetting in cgsAS.featuresDatasets[feature].keys():
            if featureSetting not in restrictedFeatures:
                if isinstance(cgsAS.featuresDatasets[feature][featureSetting],list):
                    settingsWords.append(["f",str(feature),str(featureSetting),":".join(map(str,cgsAS.featuresDatasets[feature][featureSetting]))])
                else:
                    settingsWords.append(["f",str(feature),str(featureSetting),getSafeWord(str(cgsAS.featuresDatasets[feature][featureSetting]))])
    settingsDocument = sep.join([sdID,"u:","t:Settings","H:"])
    #print "Settings document content "+str(settingsDocument)
    fdd.write(settingsDocument+"\n")
    documentID = documentID + 1
    settingsWordsUpdated = map(lambda x:[settingsSep.join([base]+x),sdID,0,0],settingsWords)
    fwd.write("\n".join(map(lambda x:sep.join(map(str,x)),settingsWordsUpdated))+"\n")
    return documentID

def exportExtraDataFeatures(fdd,fwd,datasets,cgsAS,documentID):
    sdID = str(documentID)
    base = settings.wordPrefixes["features"]
    hierarchySep = ":::"
    sep = "\t"
    featuresParts = [[],
                     [cgsAS.genome+"summary"+hierarchySep],
                     ["regionList"+"::"+settings.wordPrefixes["region"]+"::10"],
                     [settings.wordPrefixes["regionLength"]+"::3::0"],
                     ["location",settings.wordPrefixes["chrom"]],
                     ]
    # add the list for scores and strands
    dsn = cgsAS.regionDatasets.keys()[0]
    if cgsAS.regionDatasets[dsn]["useScore"]:
        featuresParts.append([settings.wordPrefixes["regionScore"]+"::0::4"])
    if cgsAS.regionDatasets[dsn]["useStrand"]:
        featuresParts.append(["location",settings.wordPrefixes["regionStrand"]])
    for datasetName in cgsAS.featuresDatasets.keys():
        datasetAnnotationSettings = cgsAS.featuresDatasets[datasetName]
        if datasetAnnotationSettings["hasFeatures"] and datasets.has_key(datasetName):
            featuresParts += datasets[datasetName].getVisualizationFeatures(cgsAS.featuresDatasets[datasetName])
        else:
            log("Omitting features from "+str(datasetName))
    featuresPartsUpdated = map(lambda x:[hierarchySep.join([base]+x),sdID,0,0],featuresParts)
    fwd.write("\n".join(map(lambda x:sep.join(map(str,x)),featuresPartsUpdated))+"\n")
    fdd.write(sep.join([sdID,"u:","t:Features","H:"])+"\n")
    documentID = documentID + 1
    return documentID

def exportExtraDataCoverage(fdd,fwd,datasets,cgsAS,documentID):
    sdID = str(documentID)
    base = settings.wordPrefixes["coverage"]
    hierarchySep = ":::"
    sep = "\t"
    featuresParts = [[]]

    for datasetName in cgsAS.featuresDatasets.keys():
        #The user dataset being computed is present as featureDataset, but is not part of datasets
        if datasets.has_key(datasetName):
            for coverageTissue in datasets[datasetName].coverages.keys():
                featuresParts.append([datasetName,coverageTissue,wordFloat(datasets[datasetName].coverages[coverageTissue],4)])
        elif cgsAS.datasetCollectionName == datasetName:
            mainDatasetCoverages = utilities.getCovarageValues(cgsAS.genome,datasetName)
            if mainDatasetCoverages is not None:
                for tissue in mainDatasetCoverages:
                    featuresParts.append([datasetName, tissue, wordFloat(mainDatasetCoverages[tissue],4)])
                #else:
                #    log("Error: Unable to get coverage value for " + datasetName)

  #do with them as in the if part
    featuresPartsUpdated = map(lambda x:[hierarchySep.join([base]+x),sdID,0,0],featuresParts)
    fwd.write("\n".join(map(lambda x:sep.join(map(str,x)),featuresPartsUpdated))+"\n")
    fdd.write(sep.join([sdID,"u:","t:Coverage","H:"])+"\n")
    documentID = documentID + 1

    return documentID

def exportExtraDataRangeNRatioWords(fdd,fwd,datasets,cgsAS,documentID):
    sdID = str(documentID)
    sep = "\t"
    junkWords = [settings.wordPrefixes["junkWords"]]
    for datasetName in cgsAS.featuresDatasets.keys():
        datasetAnnotationSettings = cgsAS.featuresDatasets[datasetName]
        if datasetAnnotationSettings["hasFeatures"] and datasets.has_key(datasetName):
            junkWords += datasets[datasetName].getRangeNRatioWords(cgsAS.featuresDatasets[datasetName])
        else:
           pass
            #log("Omitting features from "+str(datasetName))
    junkWordsUpdated = map(lambda x:sep.join([x,sdID,"0","0"]),junkWords)
    fwd.write("\n".join(junkWordsUpdated)+"\n")
    fdd.write(sep.join([sdID,"u:","t:Junk Words","H:"])+"\n")
    documentID = documentID + 1
    return documentID

def exportExtraData(fdd,fwd,datasets,cgsAS,documentID):
    log(cgsAS.datasetCollectionName+": Exporting extra data")
    # Add any extra data
    for datasetKey in datasets.keys():
        dataset = datasets[datasetKey]
        if cgsAS.getFeatureDatasetProperty(datasetKey,"hasFeatures") == False:
            continue
        documentID = dataset.exportExtraData(documentID,fdd,fwd,cgsAS)
    documentID += 1
    # add the ratio and range full list of words to avoid the problem with quering ranges and missing words
    documentID = exportExtraDataRangeNRatioWords(fdd,fwd,datasets,cgsAS,documentID)
    #add the settings document
    documentID = exportExtraDataSettings(fdd,fwd,datasets,cgsAS,documentID)
    # add the region features to be listed
    documentID = exportExtraDataFeatures(fdd,fwd,datasets,cgsAS,documentID)
    # add the data
    documentID = exportExtraDataCoverage(fdd,fwd,datasets,cgsAS,documentID)

    return documentID




def appendRegionWordDocumentDataBuffer(srID,regionWords,regionData,cgsAS,withScores):
    doc = ""
    sep="\t"
    if len(regionWords):
        if withScores:
            doc = "\n".join(map(lambda word:sep.join([getWord(word[0]),srID,word[1],word[2]]),regionWords))+"\n"
        else:
            doc = "\n".join(map(lambda word:sep.join([getWord(word),srID,"0","0"]),regionWords))+"\n"
    return doc

def appendRegionDocumentDescriptionBuffer(regionID,regionWords,regionData,cgsAS):
    sep = "\t"
    docText = str(regionID)+sep
#    docText += "u:http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg18&position="+str(convertIntToChrom(genome,regionData[1]))+"%3A"+str(regionData[2])+"-"+str(regionData[3])
    docText += "u:"
    docText += sep+"t:"+"_".join([cgsAS.genome,str(regionData[7]),str(convertIntToChrom(cgsAS.genome,regionData[1])),str(regionData[2]),str(regionData[3])])
#    docText += sep+"H:"+getDocument(regionWords)
    docText += sep+"H:"
    docText += "\n"
    return docText


def getWord(word):
    return ":".join(map(str,word))
def getDocument(words):
    return ",".join(map(getWord,words))

def exportRegionWords(cgsAS,regionID, chrom,start,stop,score,strand,source):
    #print chrom,start,stop,source
    start,stop = getCorrectedCoordinates(cgsAS.genome,chrom,start,stop)
    length = stop-start+1
    regionWordsD = []
    # the chromosome on which is the region
    regionWordsD.append([settings.wordPrefixes["chrom"],convertIntToChrom(cgsAS.genome,chrom)])
    # the start of the chromosome
#    regionWordsD.append(["srchromstart",start])
    # the end of the regions
#    regionWordsD.append(["srchromend",stop])
    #the type of the region as a category
#    regionWordsD.append(["ct","region",str(source).lower(),str(source).lower()])
#    regionWordsD.append([settings.wordPrefixes["regionType"],str(source).lower()])
    # the magnitute of the start
#    regionWordsD.append([settings.wordPrefixes["chromStart"],convertIntToChrom(cgsAS.genome,chrom),wordMagnitude(int(start/1000),3)])
    # the magnitude of the end
#    regionWordsD.append([settings.wordPrefixes["chromEnd"],convertIntToChrom(cgsAS.genome,chrom),wordMagnitude(int(stop/1000),3)])
    #the length of the region
#    regionWordsD.append(["length",length])
    if score != -1:
        scoreF = wordFixed(score,4)
        regionWordsD.append([settings.wordPrefixes["regionScore"],scoreF])
    if strand != 0:
        if strand == 1:
            regionWordsD.append([settings.wordPrefixes["regionStrand"],"Minus"])
        else:
            regionWordsD.append([settings.wordPrefixes["regionStrand"],"Plus"])
    #magnitute of the length as a category
    ml = wordMagnitude(length,3)
#    regionWordsD.append(["ct","length_magnitude",ml,"Length_is_between_"+str(int(pow(10,ml)))+"_and_"+str(int(pow(10,ml+1)))])
    regionWordsD.append([settings.wordPrefixes["regionLength"],ml])
    regionWordsD.append([settings.wordPrefixes["id"],convertIntToChrom(cgsAS.genome,chrom),start,stop,regionID])
    regionWordsD.append([settings.wordPrefixes["region"]])
    regionWordsD.append([settings.wordPrefixes["regionBin"],random.randint(1,10)])
    return regionWordsD

def exportRegionPrefixes(cgsAS):
    prefixes =  [settings.wordPrefixes["regionLength"],
            settings.wordPrefixes["id"],
#            settings.wordPrefixes["chromEnd"],
#            settings.wordPrefixes["chromStart"],
#            settings.wordPrefixes["regionType"],
            settings.wordPrefixes["chrom"],
            settings.wordPrefixes["region"]]
    dsn = cgsAS.regionDatasets.keys()[0]
    if cgsAS.regionDatasets[dsn]["useScore"]:
        prefixes.append(settings.wordPrefixes["regionScore"])
    if cgsAS.regionDatasets[dsn]["useStrand"]:
        prefixes.append(settings.wordPrefixes["regionStrand"])
    return prefixes

def exportExtraPrefixes():
    return [settings.wordPrefixes["settings"],
            settings.wordPrefixes["features"],
            settings.wordPrefixes["junkWords"]]


def getWordsDescription():
    doc = []
    doc.append(["chr1","This region is on chromosome 1",["chr"]])
    doc.append(["region:cpgislands","Indicates that this region is a CpG island",["region:"]])
    doc.append(["srmchromstart:623","Indicates that the magnitude of the chromosome start is 10^6 and the start is between 23*10^6 and 24*10^6",["srmchromstart:"]])
    doc.append(["srmchromend:627","Indicates that the magnitude of the chromosome end is 10^6 and the end is between 27*10^6 and 28*10^6",["srmchromend:"]])
    doc.append(["ID:chr13:11111111:12000000:2578","The region is located on chromosome 13, starting at 11111111 and ending at 12000000 with local ID of 2578",["ID:"]])
    doc.append(["length_magnitude:42","The length is between 2*10^4 and 3*10^4",["length_magnitude:"]])
    return doc

def exportWordDescription(datasets,cgsAS):
    sep = "\t"
    docs = getWordsDescription()
    #processedTypes = {}
    for datasetName in datasets.keys():
        if not cgsAS.getFeatureDatasetProperty(datasetName,"hasFeatures") == False:
            print "Processing",datasetName
            #if not processedTypes.has_key(datasets[datasetName].datasetPythonClass):
            docs.extend(datasets[datasetName].getWordsDescription())
#            processedTypes[datasets[datasetName].datasetPythonClass] = True
    #stores the word description
    fn = os.path.join(settings.indexDataFolder[cgsAS.genome],cgsAS.datasetCollectionName+"_features_desc.txt")
    log(["Outputing words description to",fn])
    f = open(fn,"w")
    docHelpDesc = map(lambda x:x[0]+sep+x[1],docs)
    docHelpDescUnique = []
    for dhd in docHelpDesc:
        if dhd in docHelpDescUnique:
            pass
        else:
            docHelpDescUnique.append(dhd)
    f.write("\n".join(docHelpDescUnique))
    f.close()
    # exports the words description index
    wordsDescriptionFile = getCompleteSearchDocumentsWordsFile(cgsAS.datasetCollectionName+"_description",cgsAS.genome)
    docsDescriptionFile = getCompleteSearchDocumentsDescrioptionsFile(cgsAS.datasetCollectionName+"_description",cgsAS.genome)
    fd = open(docsDescriptionFile,"w")
    fw = open(wordsDescriptionFile,"w")
    includedWords = {}
    for i in range(len(docs)):
        if len(docs[i][2]) > 0:
            fd.write(str(i+1)+sep+"u:"+sep+"t:"+sep+"H:"+"\n")
            for dw in docs[i][2]:
                if includedWords.has_key(dw):
                    continue
                else:
                    includedWords[dw] = i
                    fw.write(dw+sep+str(i+1)+sep+str(100-len(dw))+sep+"0\n")
    fw.close()
    fd.close()







