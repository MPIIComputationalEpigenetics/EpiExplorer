# the regions are stored in a local file DB and the search structure is inteval tree
import os
import os.path
import numpy
import sqlite3
import gc
import sys
import gzip
import os.path
import time

if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
else:    
    mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep    
    sys.path.insert(0,mainFolder)   

from utilities import *
import Dataset
import IntervalArray
import IntervalTree
import settings
import cPickle
import utilities

class BroadHistonesSingle(Dataset.Dataset):
    
    def init(self,initCompute=True):
        self.intervalArrays = {}
        Dataset.Dataset.init(self,initCompute)
        if isinstance(self.tissues,str):
            self.tissues = map(lambda x:x.strip(),self.tissues.split(","))        
        if isinstance(self.datasetFrom,str):
            self.datasetFrom = map(lambda x:x.strip(),self.datasetFrom.split(","))
        if len(self.datasetFrom) != 1 and len(self.datasetFrom) != len(self.tissues):
            raise GDMException, "Invalid length of self.datasetFrom "+str(len(self.datasetFrom)) 
        self.initialized = True
        
    
    def getDownloadInfo(self,tissueIndex):        
        tissue = self.tissues[tissueIndex]
        if len(self.datasetFrom) > 1:
             datasetFrom = self.datasetFrom[tissueIndex]
        else:
            datasetFrom = self.datasetFrom[0]
        if tissue == "HSMMtube":
            thURL = datasetFrom.replace("TISSUE","Hsmmt")   
        else:
            thURL = datasetFrom.replace("TISSUE",tissue.capitalize())
                            
        datasetURL = thURL.replace("HMOD",self.histoneMark.capitalize())
        downloadedLastPart = os.path.basename(datasetURL)
        datasetLocalFile = os.path.abspath(settings.downloadDataFolder[self.genome] + downloadedLastPart)
        return datasetURL,datasetLocalFile
    
    def downloadDataset(self):
        if self.hasAllDownloadedFiles():
            return        
        for tissueIndex in range(len(self.tissues)):
            tissue = self.tissues[tissueIndex]            
            datasetURL,datasetLocalFile = self.getDownloadInfo(tissueIndex)
            if not os.path.isfile(datasetLocalFile):        
                downloadFile(datasetURL, datasetLocalFile)
                log(self.datasetSimpleName + ": file " + str(os.path.basename(datasetLocalFile) + " was downloaded"))
            else:
                log(self.datasetSimpleName + ": file " + str(os.path.basename(datasetLocalFile) + " exists"))
                
            self.downloadUrls[tissue] = datasetURL
            self.downloadDate = fileTimeStr(datasetLocalFile)                         
    
    def hasAllDownloadedFiles(self):
        if isinstance(self.tissues,str):
            self.tissues = map(lambda x:x.strip(),self.tissues.split(","))
        if isinstance(self.datasetFrom,str):
            self.datasetFrom = map(lambda x:x.strip(),self.datasetFrom.split(","))
        if len(self.datasetFrom) != 1 and len(self.datasetFrom) != len(self.tissues):
            raise GDMException, "Invalid length of self.datasetFrom "+str(len(self.datasetFrom))
        for tissueIndex in range(len(self.tissues)):
            tissue = self.tissues[tissueIndex]           
            datasetURL,datasetLocalFile = self.getDownloadInfo(tissueIndex)
            if os.path.isfile(datasetLocalFile):
                self.downloadUrls[tissue] = datasetURL
                self.downloadDate = fileTimeStr(datasetLocalFile)
            else:
                return False
                
        return True
 
    def computeSingleRegionProperties(self, row, cgsAS):        
        # regionID, overlap_ratio, overlap_count, distance_upstream, distance_downstream, tissue, histoneMark
        results = []        
        isOfType = 0
        chrom = row[1]
        start = row[2]
        stop = row[3]
        strand = row[6]
        
        for tissue in self.intervalArrays.keys():
            overlapingRegions = self.intervalArrays[tissue].findTwoDimentionalWithAdditionalInfo(chrom, start, stop,cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue])
            #confData = {}
            #overlapingRegionsConfirm = self.intervalArrays[tissue].findTwoDimentional(chrom, start, stop,confData)
            overlap_count = len(overlapingRegions)
            #overlap_count_confirm = len(overlapingRegionsConfirm)
            
            #if abs(overlap_count - overlap_count_confirm) > 1:
            #    raise GDMException,"Different overlap counts "+str([str(row),self.histoneMark,tissue,overlap_count,overlap_count_confirm,str(cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue]),str(confData),str(map(list,list(overlapingRegions))),str(map(list,list(overlapingRegionsConfirm)))])
            if overlap_count == 0:
                distance_upstream_array = cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue]['distanceUpstream']
                distance_downstream_array = cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue]['distanceDownstream']
                #if distance_upstream_array != confData['distanceUpstream']:
                #    raise GDMException,"Different distance upstream "+str([str(row),self.histoneMark,tissue,distance_upstream_array,confData['distanceUpstream'],str(cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue]),str(confData)])
                #if distance_downstream_array != confData['distanceDownstream']:
                #    raise GDMException,"Different distance downstream "+str([str(row),self.histoneMark,tissue,distance_downstream_array,confData['distanceDownstream'],str(cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue]),str(confData)])
                # we do not provide the signal value and the p-value for the closest case
                if strand == 1:
                    #minus strand, reverse
                    result = [row[0], 0, 0, distance_downstream_array, distance_upstream_array, tissue, 0, 0]
                else:                    
                    result = [row[0], 0, 0, distance_upstream_array, distance_downstream_array, tissue, 0, 0]
            else:
                #maxSignalValue = max([ovr[2] for ovr in list(overlapingRegions)])
                #maxPValue = max([ovr[3] for ovr in list(overlapingRegions)])
                
                reducedGR = gr_reduceRegionSet(list(overlapingRegions))
                #reducedGR_conf = gr_reduceRegionSet(list(overlapingRegionsConfirm))
                
                overlap_ratio = gr_Coverage(reducedGR, start, stop) / float(stop - start)
                #overlap_ratio_confirm = gr_Coverage(reducedGR_conf, start, stop) / float(stop - start)
                #if overlap_ratio != overlap_ratio_confirm:
                #    raise GDMException,"Different overlap ratio "+str([str(row),self.histoneMark,tissue,overlap_ratio,overlap_ratio_confirm,str(cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue]),str(confData)])
                result = [row[0], overlap_ratio, overlap_count, 0, 0, tissue, 0, 0]
                if overlap_ratio < 0:
                    raise GDMException,"Negative overlap ratio "+str([str(row),self.histoneMark,tissue,overlap_count,overlap_ratio,str(cgsAS.featuresDatasets[self.datasetSimpleName]['data'][tissue]),str(list(overlapingRegions))])
                    
            # check for neighborhood
            if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"useNeighborhood"):
                                
                positions = map(lambda x:start-x,cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"neighborhoodBeforeStart"))
                positions +=  map(lambda x:stop+x,cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"neighborhoodAfterEnd"))
                if strand == 1:
                    #minus strand reverse
                    positions.reverse()
#                print positions,start,stop
                neighborhood = self.intervalArrays[tissue].findTwoDimentionalNeighborhood(chrom,positions)
                result.append(neighborhood)
            results.append(result)
        return results

        
    def preprocessDownloadedDataset(self):
        if not self.hasAllDownloadedFiles():
           exText = self.datasetSimpleName + ": the dataset files are not downloadeded "
           log(exText)
           raise GDMException, exText
        if self.hasPreprocessedFile():
            #what to do if the data was already preprocessed
            extext = self.datasetSimpleName + ": the dataset was already preprocessed in "+self.binaryFile
            log(extext)
            return
        log(self.datasetSimpleName + ": preprocessing the dataset into local database")
        self.binaryFile = self.getDatasetBinaryName()
        try:
            conn = sqlite3.connect(self.binaryFile)
            c = conn.cursor()
            c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER, tissue TEXT, signalValue FLOAT, pValue FLOAT)')
            
            self.chromIndex = int(self.chromIndex)
            self.chromStartIndex = int(self.chromStartIndex)
            self.chromEndIndex = int(self.chromEndIndex)
             
            self.signalValueIndex = int(self.signalValueIndex)
            self.pValueIndex = int(self.pValueIndex)
            
            for tissueIndex in range(len(self.tissues)):
                tissue = self.tissues[tissueIndex]
                datasetURL,datasetLocalFile = self.getDownloadInfo(tissueIndex)
                #print tissue,datasetLocalFile
                f = gzip.GzipFile(datasetLocalFile,"rb")
                lines = map(lambda x:x.strip().split("\t"),f.readlines())
                f.close()                
                for line in lines:
                    try:
                        chrom = convertChromToInt(self.genome,line[self.chromIndex])
                    except:
                        if "_random" in line[self.chromIndex]:
                            continue
                        elif "chrM" in line[self.chromIndex]:
                            continue
                        elif "hap" in line[self.chromIndex]:
                            continue
                        elif line[self.chromIndex].startswith("chrUn"):
                            continue                        
                        else:
                            raise                                                              
                    c.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?,?,?,?,?,?)',
                                   tuple([chrom,
                                          int(line[self.chromStartIndex]),
                                          int(line[self.chromEndIndex]),
                                          tissue,
                                          float(line[self.signalValueIndex]),
                                          float(line[self.pValueIndex]),                                                
                                          ]))
                conn.commit()
                
        except:            
            # if there was exception, delete the database file
            c.close()
            conn.close()
            os.unlink(self.binaryFile)
            raise
            
        c.close()
        conn.close()
        log(self.datasetSimpleName + ": the dataset was preprocessed into local DB "+self.binaryFile)
        
    def cleanup(self,cgsAS):        
        sqlite3Data = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(sqlite3Data):
            os.unlink(sqlite3Data)
#        for tissue in self.intervalArrays.keys():                         
#            self.intervalArrays[tissue].cleanup()
             
    def initializePropertiesComputeStructures(self):
        log("computing interval array for "+self.histoneMark)
        chromData = {}
        chromSizes = {}
       
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()
        try:
            # initializing the IntervalArrays
            for tissueName in self.tissues:            
                c.execute("SELECT COUNT(*) FROM "+self.datasetSimpleName+" WHERE tissue=? ORDER BY start",(tissueName,))
                nc = c.fetchone()[0]            
                if nc == 0:
                    continue
                self.intervalArrays[tissueName] = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName([tissueName]),numpy.float64,4)
            self.intervalArrays["any"] = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName(["any"]),numpy.float64,4)
            exist = True
            for tissue in self.intervalArrays.keys():            
                if self.intervalArrays[tissue].exist(1) and self.intervalArrays[tissue].exist(5) and self.intervalArrays[tissue].exist(11) and self.intervalArrays[tissue].exist(15):
                    continue
                else:
                    log(self.datasetSimpleName+" "+tissue+" has no stored computed array for some chromosomes")
                    exist = False
                    break
                
                
                            
            if exist:
                log(self.datasetSimpleName+" have stored precomputed arrays")
                c.close()
                conn.close()
                return        
            
            c.execute("SELECT chrom, start, stop,  signalValue, pValue, tissue FROM "+self.datasetSimpleName+" ORDER BY chrom,start")                                    
            data = c.fetchall()
        except:
            c.close()
            conn.close()
            raise 
        
        c.close()
        conn.close()
        #log("MARK: all data was fetched")
        if len(data):
            for tissue in self.tissues:                        
                tissueData = map(lambda x:x[:5],filter(lambda x:x[5]==tissue,data))
                self.intervalArrays[tissue].loadFullDataSortedbyChrom(tissueData,True)
                log("\ttissue "+tissue+" is ready")
            #log(["Adding an array for histone mark",hmark,"and tissue all with total of",len(data),"rows"])
            self.intervalArrays["any"].loadFullDataSortedbyChrom(map(lambda x:x[:5],data),True)
            log("\ttissue any is ready")
                        
        log("Interval array computed for "+self.histoneMark)
        for tissue in self.intervalArrays.keys():            
            self.intervalArrays[tissue].store()
            
            self.intervalArrays[tissue].cleanup()
        log("Interval array stored for "+self.histoneMark)
        
    def calculateCoverages(self):
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()
                
        try:
            for tissueName in self.tissues:
                c.execute("SELECT chrom, start, stop FROM "+self.datasetSimpleName+" WHERE tissue=? ORDER BY chrom,start", (tissueName,))                                                
                data = c.fetchall()
                # TODO workaround because the calculateCoverage uses numpy array. 
                coverage = self.calculateCoverage(numpy.asarray(data))
                self.coverages[tissueName] = coverage

            c.execute("SELECT chrom, start, stop FROM "+self.datasetSimpleName+" ORDER BY chrom,start")                                                
            data = c.fetchall()        
            # TODO workaround because the calculateCoverage uses numpy array. 
            coverage = self.calculateCoverage(numpy.asarray(data))
            self.coverages["any"] = coverage
            
        except:
            c.close()
            raise
                           
                                    
    def initializePropertiesStoreStructures(self,cgsAS, dataConnections):        
        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"useNeighborhood"):
            dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, maxSignalValue FLOAT, maxpValue FLOAT, neighborhood TEXT)")
        else:
            # no neighborhood
            dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, maxSignalValue FLOAT, maxpValue FLOAT)")

    def getRegions(self):
        return self.getRegionsFromLocalDB()
    
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
#        regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT, maxSignalValue FLOAT, maxpValue FLOAT, neighborhood TEXT (depending on useNeighborhood)
        regionData = []
        regionDataWithScores = []
              
        if result[2] > 0:
            # indicates that the regions overlaps with DNaseI hypersensitive site
            regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName,self.histoneMark,str(result[5])])
            if result[1] >= 0.1:
                regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName,self.histoneMark,str(result[5])])
            if result[1] >= 0.5:
                regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName,self.histoneMark,str(result[5])])
                
            regionData.append([settings.wordPrefixes["overlapRatio"],self.datasetWordName,self.histoneMark,str(result[5]),wordFloat(result[1],2)])
            #regionData.append([settings.wordPrefixes["significanceValue"],self.datasetWordName,self.histoneMark,str(result[5]),wordFixed(int(round(result[6])),6)])
            #regionData.append([settings.wordPrefixes["pValue"],self.datasetWordName,self.histoneMark,str(result[5]),wordFixed(int(round(result[7])),4)])
            
        else:
            #the region does not overlap with a site, report distance to the nearest (not tissue specific)
            if str(result[5]) == "any":
                if result[4] < settings.MAX_DISTANCE:
                    dd  = wordMagnitude(result[4])
#                    regionData.append(["mdd","bhistone",str(result[6]),str(result[5]),dd])
                    regionData.append([settings.wordPrefixes["minimumDistanceDownstream"],self.datasetWordName,str(self.histoneMark),dd])
                if result[3] < settings.MAX_DISTANCE:
                    du  = wordMagnitude(result[3])
#                    regionData.append(["mud","bhistone",str(result[6]),str(result[5]),du])
                    regionData.append([settings.wordPrefixes["minimumDistanceUpstream"],self.datasetWordName,str(self.histoneMark),du])
                if result[4] < result[3]:
#                    regionData.append(["mmd","bhistone",str(result[6]),str(result[5]),dd])
                    regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(self.histoneMark),dd])
                elif result[3] < result[4]:
#                    regionData.append(["mmd","bhistone",str(result[6]),str(result[5]),du])
                    regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(self.histoneMark),du])
                elif result[3] < settings.MAX_DISTANCE:
#                    regionData.append(["mmd","bhistone",str(result[6]),str(result[5]),du])
                    regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(self.histoneMark),du])
        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"useNeighborhood"):
            index = 0
            # Neighborhood is demanded and computed for this dataset
            beforeStart =  cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"neighborhoodBeforeStart")
            for i in xrange(len(beforeStart)):
                if result[8][i] == "1":
                    regionData.append([settings.wordPrefixes["neighborhood"],
                                       self.datasetWordName,
                                       self.histoneMark,
                                       str(result[5]),
                                       "bs"+str(beforeStart[i])])
            bsl = len(beforeStart)
            afterEnd =  cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"neighborhoodAfterEnd")
            for j in xrange(len(afterEnd)):
                if result[8][j+bsl] == "1":
                    regionData.append([settings.wordPrefixes["neighborhood"],
                                   self.datasetWordName,
                                   self.histoneMark,
                                   str(result[5]),
                                   "ae"+str(afterEnd[j])])
            
            
        return regionData,regionDataWithScores
    
    def getWordPrefixes(self,cgsAS):
        wordPrefixes =  [settings.wordPrefixes["overlap"],
                settings.wordPrefixes["overlap10p"],
                settings.wordPrefixes["overlap50p"],
                #":".join([settings.wordPrefixes["overlap"],self.datasetWordName,self.histoneMark]),
                #":".join([settings.wordPrefixes["overlap10p"],self.datasetWordName,self.histoneMark]),
                #":".join([settings.wordPrefixes["overlap50p"],self.datasetWordName,self.histoneMark]),
                ":".join([settings.wordPrefixes["overlapRatio"],self.datasetWordName,self.histoneMark]),
                #":".join([settings.wordPrefixes["significanceValue"],self.datasetWordName,self.histoneMark]),
                #":".join([settings.wordPrefixes["pValue"],self.datasetWordName,self.histoneMark]),                
                ":".join([settings.wordPrefixes["minimumDistanceDownstream"],self.datasetWordName,self.histoneMark]),
                ":".join([settings.wordPrefixes["minimumDistanceUpstream"],self.datasetWordName,self.histoneMark]),
                ":".join([settings.wordPrefixes["minimumDistance"],self.datasetWordName,self.histoneMark])]
        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"useNeighborhood"):
            wordPrefixes.append(":".join([settings.wordPrefixes["neighborhood"],self.datasetWordName,self.histoneMark]))
        return wordPrefixes
    
    def getWordsDescription(self):
        doc = []
        for tissue in self.tissues: 
            pass            
        #doc.append(["overlaps:bhistone:H3k4me3:Hepg2","Overlaps with H3K4me3 in the tissue Hepg2",["overlaps:bhistone:"]+["overlaps:bhistone:"+hm+":" for hm in self.histoneMarks]+["overlaps:bhistone:"+hm+":all" for hm in self.histoneMarks]+["overlaps:bhistone:"+hmt+":" for hmt in hmTissues]])
        #doc.append(["or:bhistone:H3k4me3:Hepg2:77","Overlaps 77% with H3K4me3 in the tissue Hepg2",["or:bhistone:"]+["or:bhistone:"+hm+":" for hm in self.histoneMarks]+["or:bhistone:"+hm+":all" for hm in self.histoneMarks]+["or:bhistone:"+hmt+":" for hmt in hmTissues]])
#        doc += "bhistoneoc:H3k4me3:Hepg2:2 overlaps with 2 H3K4me3 sites in the tissue Hepg2\n"        
        #doc.append(["mdd:bhistone:H3k4me3:34","Measures the magnitude of the distance (between 10^3*4 and 10^3 *5) to the nearest H3K4me3 site downstream",["mdd:bhistone:"]+["mdd:bhistone:"+hm+":" for hm in self.histoneMarks]])#+["mdd:bhistone:"+hm+":all" for hm in self.histoneMarks]])
        #doc.append(["mud:bhistone:H3k4me3:34","Measures the magnitude of the distance (between 10^3*4 and 10^3 *5) to the nearest H3K4me3 site upstream",["mmd:bhistone:"]+["mud:bhistone:"+hm+":" for hm in self.histoneMarks]])#+["mud:bhistone:"+hm+":all" for hm in self.histoneMarks]])
        #doc.append(["mmd:bhistone:H3k4me3:34","Measures the magnitude of the distance (between 10^3*4 and 10^3 *5) to the nearest H3K4me3 site",["mmd:bhistone:"]+["mmd:bhistone:"+hm+":" for hm in self.histoneMarks]])#+["mmd:bhistone:"+hm+":all" for hm in self.histoneMarks]])                
        return doc
    
    def getDefaultAnnotationSettings(self):        
        # obtain the default settings
        settingsLocal = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settingsLocal["hasGenomicRegions"] = self.hasGenomicRegions
        settingsLocal["hasFeatures"] = self.hasFeatures
        if isinstance(self.useNeighborhood,str):
            self.useNeighborhood = self.useNeighborhood == "True"
        settingsLocal["useNeighborhood"] = self.useNeighborhood
        
        #neighborhood is to be used, so chekc the defined distances            
        # initializing distances before the start
        settingsLocal["neighborhoodBeforeStart"] = self.neighborhoodBeforeStart.strip().split(",")
        #if none make sure there is no '' artifact from the split()
        if len(settingsLocal["neighborhoodBeforeStart"]) == 1 and not settingsLocal["neighborhoodBeforeStart"][0]:
              settingsLocal["neighborhoodBeforeStart"] = []
        # convert them all to ints
        settingsLocal["neighborhoodBeforeStart"] = map(int,settingsLocal["neighborhoodBeforeStart"])
        
        # initializing distances after the end
        settingsLocal["neighborhoodAfterEnd"] = self.neighborhoodAfterEnd.strip().split(",")
        #if none make sure there is no '' artifact from the split()
        if len(settingsLocal["neighborhoodAfterEnd"]) == 1 and not settingsLocal["neighborhoodAfterEnd"][0]:
              settingsLocal["neighborhoodAfterEnd"] = []
        # convert them all to ints
        settingsLocal["neighborhoodAfterEnd"] = map(int,settingsLocal["neighborhoodAfterEnd"])
        
        settingsLocal["data"] = {}
        for tissue in self.tissues+['any']:
            settingsLocal["data"][tissue] = {'distanceDownstream':settings.MAX_DISTANCE,
                            'distanceUpstream':settings.MAX_DISTANCE,
                            'currentChrom':None,
                            'currentChromStart': 0,
                            'currentStartIndex':None,
                            'currentEndIndex':None}
        
        #retrun them
        return settingsLocal

    # This method returns a list of feature words for the feature listing in the user interface 
    def getVisualizationFeatures(self,annotationFeatures):
        categories = self.dataCategories.strip()
        if len(categories) == 0:
            categoriesPath = [self.datasetSimpleName]
        else:
            categoriesPath = map(lambda x:x.strip(),categories.split("/"))+[self.datasetSimpleName]
        featureWords = []
        featureWords.append(categoriesPath+["OVERLAP:"+self.datasetWordName+":"+self.histoneMark+"::"+"Eor:"+self.datasetWordName+":"+self.histoneMark+":POS3SOP::2::0"])  
        featureWords.append(categoriesPath+["_OVERLAP:"+self.datasetWordName+":"+self.histoneMark])
        featureWords.append(categoriesPath+["distanceTo"]+["Emdd:"+self.datasetWordName+":"+self.histoneMark+"::2::0"])
        featureWords.append(categoriesPath+["distanceTo"]+["Emud:"+self.datasetWordName+":"+self.histoneMark+"::2::0"])
        featureWords.append(categoriesPath+["distanceTo"]+["Emmd:"+self.datasetWordName+":"+self.histoneMark+"::2::0"])
        if annotationFeatures["useNeighborhood"]:
            bsN = ":".join(map(str,annotationFeatures["neighborhoodBeforeStart"]))
            aeN = ":".join(map(str,annotationFeatures["neighborhoodAfterEnd"]))
            featureWords.append(categoriesPath+["Enbh:"+self.datasetWordName+":"+self.histoneMark+"::"+bsN+"::"+aeN])
        return featureWords 
    
    def getOverlappingText(self):
        return self.datasetWordName + ":" + self.histoneMark
    
    def getSubAnnotations(self):
        return self.tissues+["any"]
