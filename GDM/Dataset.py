## class Dataset
# this is the interface class that every new dataset should extend
from utilities import *
import settings
import sqlite3
import os.path
import numpy

class Dataset:
    def __init__(self):
        ## debug feature
        self.regionsCountMod = 100000
        
        ## Name of the dataset
        self.datasetSimpleName = "default" 
        ## id for the dataset
        ## self.datasetId = None       
        ## logical value indicating if the dataset defines genomic regions
        self.hasGenomicRegions = False
        
        self.initialized = False
        
        #self.insertSQL = ""
        
        self.datasetType = "Default"
        
        self.coverages = {}
        self.downloadUrls = {}
        # The current configuration of the forward server does not support None values
        self.downloadDate = ""
                
    ## init
    #
    # this methods initiates all structures required by this module, and possibly some preprocessing of the dataset
    def init(self,initCompute=True):
        # Check if the dataset has or uses scores or strands, Currently only the genes and custom datasets do
        if not hasattr(self, "useScore"):
            self.useScore = False
        if not hasattr(self, "useStrand"):
            self.useStrand = False
                    
        self.hasBinning = hasattr(self, "hasBinning") and (self.hasBinning == "True" or self.hasBinning == True)        

        if not self.hasAllDownloadedFiles():
            self.downloadDataset()

        if not self.hasPreprocessedFile():
            # if the file was downloaded but not preprocessed, preprocess the data
            self.preprocessDownloadedDataset()
        # make hasGenomicRegions boolean
        if isinstance(self.hasGenomicRegions,str):
            self.hasGenomicRegions = self.hasGenomicRegions == "True"
        # make hasFeatures boolean
        if isinstance(self.hasFeatures,str):
            self.hasFeatures = self.hasFeatures == "True"
        if initCompute:        
            # initialize the properties compute structures
            self.initializePropertiesComputeStructures()
            
        #try to load the stored coverage value
        coverages = getCovarageValues(self.genome, self.datasetSimpleName)
        if coverages is not None:  
            self.coverages = coverages
        else:                      
            self.calculateCoverages()
            storeCoverageValues(self.genome, self.datasetSimpleName, self.coverages)
        
        self.overlappingText = self.getOverlappingText()
        if self.overlappingText == None:
            self.overlappingText = ""
    ## getRegions
    #
    # retrieves all genomic regions from this dataset
    # this function is relevant only for datasets with hasGenomicRegion = True
    def getRegions(self):
        raise Exception, "getRegions not implemented for "+self.datasetSimpleName
    ## getRegionComputedData
    #
# DEPRECATED -> Replaced with getRegionComputedDataFromExtractedLine
#    def getRegionComputedData(self, regionID):
#        raise Exception, "getRegionComputedData not implemented for "+self.datasetSimpleName
#    ## getRegionComputedDataFromExtractedLine
    # 
    # given a row extracted from the dataset properties database, extract the properties of the region in a dictionary
    def getRegionComputedDataFromExtractedLine(self, row, cgsAS):
        """Returns regionWordsD,regionWordsWithScoresD
        regionWordsD  is a list of list where each list is a word component
                      for example the list [["overlap","CGI"],["overlap","promoter"]]
                      will encode the words overlap:CGI and overlap:promoter
        regionWordsWithScoresD is a list for the special cases when we want to code also the word score or position
                      It is a list of lists and each sub list encodes a word.
                      The first component of the list is a list of word components, 
                      the second is a string of the score (between 0 and 255) and
                      and the third is a string to encode the position(currently not used anywhere)
                      For example for example the list [[["overlap","CGI"],"1","0"],[["overlap","promoter"],"2","0"]]
                      will encode the same words as above but with scores 1 and 2    
        """
        raise Exception, "getRegionComputedDataFromExtractedLine not implemented for "+self.datasetSimpleName
    ## initializePropertiesStoreStructures
    # 
    # This method created the data structure in which the properties will be stored  
    def initializePropertiesStoreStructures(self,cgsAS,dataConnections):
        raise Exception, "initializePropertiesStoreStructures not implemented for "+self.datasetSimpleName
    ##
    #
    # This method initiates any support structures
    def initializePropertiesComputeStructures(self):
        raise Exception, "initializePropertiesComputeStructures not implemented for "+self.datasetSimpleName
    
    ## computeSingleRegionProperties
    #
    # computed the properties for this daset for the given region and stores them in the properties structure
    # @return: this method should not return the properties but store them
    def computeSingleRegionProperties(self, row, cgsAS):
        raise Exception, "computeSingleRegionProperties not implemented for "+self.datasetSimpleName
    ## cleanup
    #
    # this method is called after all the properties re computed and stored. The purpose is to clean up all the 
    # unnecessary structures
    def cleanup(self,cgsAS):
       raise Exception, "cleanup not implemented for "+self.datasetSimpleName
    
    ## testValues
    # 
    # every dataset should test a few of the values it computed for user selected regions
    # 
    def testValues(self):
        pass
#        raise Exception, "testValues not implemented for "+self.datasetSimpleName
    ## downloadDataset
    # 
    # defines how the dataset should be download
    def downloadDataset(self):
        raise Exception, "downloadDataset not implemented for "+self.datasetSimpleName       
    ## preprocessDownloadedDataset
    # 
    # defines how basic preprocessing of the downloaded dataset
    def preprocessDownloadedDataset(self):
        raise Exception, "preprocessDownloadedDataset not implemented for "+self.datasetSimpleName        
        
    def hasAllDownloadedFiles(self):
        raise Exception, "hasAllDownloadedFiles not implemented for "+self.datasetSimpleName
    
    def getDatasetLocalFile(self):
        raise Exception, "getDatasetLocalFile not implemented for "+self.datasetSimpleName
    
    # This returns the default settings structure which should be th e base for every CGSAnnotationsSettings
    def getDefaultAnnotationSettings(self):
        raise Exception, "getDefaultAnnotationSettings not implemented for "+self.datasetSimpleName
    
    # This method returns a list of feature words for the feature listing in the user interface 
    def getVisualizationFeatures(self,annotationFeatures):
        raise Exception, "getVisualizationFeatures not implemented for "+self.datasetSimpleName
    # Returns full list of Ratio and range words that could be produced by this dataset.
    # This is useful since the CompleteSearch range query xxx--yyy  has a problem if 
    # one of the words is missing from the words dictionary
    def getRangeNRatioWords(self,annotationFeatures):
        return []    
    # Returns the main prefixes of the words defined for this class. 
    # All of those are combined and used to optimally compile an index 
    def getWordPrefixes(self,cgsAS):
        raise Exception, "getWordPrefixes not implemented for "+self.datasetSimpleName

    def __getDefaultAnnotationSettingsBasic__(self):
        basicSettings = {}
        basicSettings["datasetId"] = None
        basicSettings["hasGenomicRegions"] = False 
        basicSettings["hasFeatures"] = False
        basicSettings["canHaveFeatures"] = True
        basicSettings["insertSQL"] = ""
        basicSettings["useStrand"] = self.useStrand
        basicSettings["useScore"] = self.useScore
        return basicSettings
        
    ## getWordsDescription
    #
    # retrives a string with the description of the text words this method retrieves
    def getWordsDescription(self):
        raise Exception, "getWordsDescription not implemented for "+self.datasetSimpleName
    ## exportExtraData
    #
    # This method should be defined only for Datasets that returndat in addition to their 
    # regions and features such as gene descriptions or II scores
    # The expected return format is as follows
    # returnData := [[document title,document body,document link,document words], ...]                
    # document words := [[wordParts,score], ...]
    # wordParts := [wordPart1,wordPart2,wordPart3, ...]] 
    def exportExtraData(self,documentID,fdd,fwd,cgsAS):
        return documentID
    
    def uploadSingleRegionPropertiesToStoreStructure(self, properties, cgsAS, dataConnections):
        if not cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"insertSQL") and len(properties) > 0:
            cgsAS.setFeatureDatasetProperty(self.datasetSimpleName,"insertSQL","INSERT INTO " + self.datasetSimpleName + "_data VALUES ("+"?,"*(len(properties[0])-1)+"?)")
        for el in properties:             
            dataConnections[0][1].execute(cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"insertSQL"),tuple(el))
            
    def computeRegionsProperties(self,cgsAS):
        regionsData = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(regionsData):
            log(self.datasetSimpleName+": The data has already been computed "+regionsData)
            return
        
        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"hasFeatures") == False:
            return         
        # Open the database connections
           
        regionsFile = getRegionsCollectionName(cgsAS.datasetCollectionName,self.genome)
        connRegions = sqlite3.connect(regionsFile)
        cR = connRegions.cursor()
        
        dataConnections = self.openDBConnections(cgsAS)
        # the first element of the data connections is a list with two obects
        # the database connction ot the data file and the cursor for this connection
        #            
            
        try:
            #initialized the structure in which to store all properties of this dataset w.r.t. another region            
            self.initializePropertiesStoreStructures(cgsAS,dataConnections)
            cR.execute("SELECT COUNT(*) FROM regions")
            nRows = cR.fetchone()[0]
            cR.execute("SELECT regionID,chrom,start,stop,datasetID,score,strand FROM regions ORDER BY chrom,start,stop")
            
            cc = 0
            for row in cR:
                cc += 1
                properties = self.computeSingleRegionProperties(row, cgsAS)
                self.uploadSingleRegionPropertiesToStoreStructure(properties,cgsAS,dataConnections)
                if cc%self.regionsCountMod == 0:
                    log([ self.datasetSimpleName,":",cc,"out of",nRows])
            #print self.datasetSimpleName,cc                
            dataConnections[0][0].commit()
        except:                     
            self.closeDBConnections(dataConnections)           
            os.unlink(getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName))
            raise            
        finally:
            # close the regions connections
            try:
                cR.close()    
                connRegions.close()    
            except:
                pass
            try:
                self.closeDBConnections(dataConnections)
            except:
                pass
                
                
            
            
#        try:
##            self.cleanup()     
#            pass       
#        except Exception,ex:
#            log("Error, while cleaning up"+str(ex))
        #test some values
        self.testValues()
    
    
    
    def __getDatasetId__(self, cgsAS):
        datasetID = cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"datasetId")
        if datasetID == None:
            regionsFile = getRegionsCollectionName(cgsAS.datasetCollectionName,self.genome)
            
            connRegions = sqlite3.connect(regionsFile)
            c = connRegions.cursor()                        
            try:
                c.execute('SELECT datasetID,datasetName FROM datasets' )
                #print regionsFile, list(c.fetchall()),self.datasetSimpleName
                x = c.execute('SELECT datasetID FROM datasets WHERE datasetName=?',(self.datasetSimpleName,))
                datasetID = int(c.fetchone()[0])                            
                cgsAS.setFeatureDatasetProperty(self.datasetSimpleName,"datasetId",datasetID)
            except TypeError:
                # no dataset regions with such ID, make it different than None, 
                # so that it is not computed multiple times
                datasetID = ""     
                cgsAS.setFeatureDatasetProperty(self.datasetSimpleName,"datasetId",datasetID)
                #self.datasetId = ""
            except sqlite3.OperationalError:
                # no such table
                datasetID = ""
                cgsAS.setFeatureDatasetProperty(self.datasetSimpleName,"datasetId",datasetID)
            c.close()
            connRegions.close()
            #print self.datasetId
        return datasetID
    
    def openDBConnections(self,cgsAS):
        regionsData = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)                
        connData = sqlite3.connect(regionsData)
        cD = connData.cursor()
        return [[connData,cD]] 
        
        
    def closeDBConnections(self,dataConnections):
        try:            
            dataConnections[0][1].close()
            dataConnections[0][0].close()
        except:
            pass    
   
    def __downloadSingleFileDataset__(self):
        if self.hasAllDownloadedFiles():
            exText = self.datasetSimpleName + ": the dataset files were already downloaded " + self.getDatasetLocalFile()
            log(exText)            
        else:
            datasetURL = self.datasetFrom
            datasetLocalFile = self.getDatasetLocalFile()
            downloadFile(datasetURL, datasetLocalFile)
            log(self.datasetSimpleName + ": file " + str(os.path.basename(datasetLocalFile) + " was downloaded"))
            
        self.downloadUrls["any"] = self.datasetFrom
        self.downloadDate = fileTimeStr(self.getDatasetLocalFile())
            
    def __hasSingleDownloadedFile__(self):
        absName = self.getDatasetLocalFile()        
        if os.path.isfile(absName):
            self.downloadUrls["any"] = self.datasetFrom
            self.downloadDate = fileTimeStr(self.getDatasetLocalFile())
            return True
        else:
            return False
    def hasPreprocessedFile(self):       
        self.binaryFile = self.getDatasetBinaryName()
        if not os.path.isfile(self.binaryFile):
            return False       
        return True
    
    def getDatasetBinaryName(self):
        return settings.rawDataFolder[self.genome]+self.datasetSimpleName+".sqlite3"
    
    def __getDatasetSingleLocalFile__(self):
        # Expects a single file in the download folder named 
        # simplename + extensions of the html download link
        downloadedLastPart = os.path.basename(self.datasetFrom)
#        downloadedLastPart = downloadedLastPart[downloadedLastPart.find("."):]
        absName = os.path.abspath(settings.downloadDataFolder[self.genome] + downloadedLastPart)
        return absName
    
    def __get_regions_from_local_db__(self,filter):
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM "+self.datasetSimpleName+filter)
        numberOfLines = c.fetchone()[0]                
        #c.execute("SELECT DISTINCT chrom, start, stop FROM "+self.datasetSimpleName+filter)
        c.execute("SELECT chrom, start, stop FROM "+self.datasetSimpleName+filter)
        regions = numpy.zeros((numberOfLines,3),dtype=int)
        i = 0 
        for row in c:
            regions[i,0] = row[0]
            regions[i,1] = row[1]
            regions[i,2] = row[2]            
            i+=1
        c.close()
        conn.close()
        maxIndex = i
        if maxIndex < numberOfLines:            
            regionsNew = numpy.zeros((maxIndex,3),dtype=int)
            regionsNew = regions[0:maxIndex,:]
            return regionsNew
        else:
            return regions
    
    def __get_regions_from_local_bed__(self,bedFile):
        f =  open(bedFile)
        bedLines = map(lambda line: line.strip().split("\t"), f.readlines())
        f.close()
        if len(bedLines[-1]) > 1:
            lbs = len(bedLines)
        else:
            lbs = len(bedLines) -1            
        regions = []
        for line in bedLines[:lbs]:
            try:
                chrom = convertChromToInt(self.genome,line[0])
                regions.append([chrom, int(line[1]), int(line[2])])                    
            except:
                if "_random" in line[0]:
                    continue
                elif "chrM" in line[0]:
                    continue
                elif "hap" in line[0]:
                    continue
                elif line[0].startswith("chrUn"):
                    continue                        
                else:
                    raise
                    
        return numpy.asarray(regions)
    
    def __get_regions_from_local_bed_with_score_or_strand__(self,bedFile):
        f =  open(bedFile)
        bedLines = map(lambda line: line.strip().split("\t"), f.readlines())
        f.close()        
        hasAdditionalScores = self.useScore or self.useStrand
        if hasAdditionalScores:
            regions = numpy.zeros((len(bedLines),5),dtype=int)
        else:  
            regions = numpy.zeros((len(bedLines),3),dtype=int)
        i = 0 
        for line in bedLines:   
            if len(line) < 3:
                pass
            else:         
                regions[i,0] = convertChromToInt(self.genome,line[0])
                regions[i,1] = int(line[1])
                regions[i,2] = int(line[2])
                if hasAdditionalScores:
                    if self.useScore:
                        regions[i,3] = int(line[4])
                    else:
                        regions[i,3] = -1
                    if self.useStrand:
                        regions[i,4] = convertStrandToInt(line[5])
                    else:
                        regions[i,4] = 0            
                i+=1      
          
        return regions
    
    def __init_regions_dataset_for_local_db__(self,ds):
        log(self.datasetSimpleName + ": initializing regions local db ")        
        self.binaryFile = self.getDatasetBinaryName()
        if self.hasPreprocessedFile():
            #what to do if the data was already preprocessed
            extext = self.datasetSimpleName + ": the regions database already exists "+self.binaryFile
            log(extext)
            return 
            raise Exception, extext            
        log(self.datasetSimpleName + ": preprocessing the dataset into local database")
        try:
            conn = sqlite3.connect(self.binaryFile)
            c = conn.cursor()
            c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER)')
    #        rawDataFile = open(self.datasetRawData)
    #        rawDataFile.readline()
    #        line = rawDataFile.readline()
            for lineParts in ds:
    #            lineParts = line.strip().split("\t")
                lineParts[0] = convertChromToInt(self.genome,lineParts[0]) 
                lineParts[1] = int(lineParts[1])
                lineParts[2] = int(lineParts[2])
                c.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?,?,?)',tuple(lineParts[:3]))
    #            line = rawDataFile.readline()
    #        rawDataFile.close()
            conn.commit()
        except Exception,ex:
            log(str(ex))
            # if there was exception, delete the database file
            c.close()
            conn.close()
            os.unlink(self.binaryFile)
            raise ex
            
        c.close()
        conn.close()
        log(self.datasetSimpleName + ": the dataset was preprocessed into local DB "+self.binaryFile)
    
    def getRegionsFromLocalBED(self,bedFile):        
        if not self.hasPreprocessedFile():
            self.preprocessDownloadedDataset()
        if self.useScore or self.useStrand:
            return self.__get_regions_from_local_bed_with_score_or_strand__(bedFile)
        else:
            return self.__get_regions_from_local_bed__(bedFile)
    
    def getRegionsFromLocalDB(self,filter=""):        
        if not self.hasPreprocessedFile():
            self.preprocessDownloadedDataset()
        return self.__get_regions_from_local_db__(filter)
    
    def getIntervalArraybaseName(self,extras=[]):
        return settings.rawDataFolder[self.genome]+"_".join([self.datasetSimpleName]+extras+["CHR.data"])
    
    def calculateCoverage(self, data, chrStart=1, chrEnd=2):        
        chrms = {}        
        begin = 0
        actual = 0
        chr = None
        sum = 0
        chrSum = 0
        for line in data:
            if chr == None:
                chr = int(line[0])
            elif chr is not int(line[0]):
                reduction = gr_reduceRegionSet(data[begin:actual].tolist(), chrStart, chrEnd)
                coverage = gr_Coverage(reduction, None, None, chrStart, chrEnd)                   
                sum += coverage                
                begin = actual
                chr = int(line[0])
            actual = actual + 1
        
        if begin is not actual:
            reduction = gr_reduceRegionSet(data[begin:actual].tolist(), chrStart, chrEnd)   
            coverage = gr_Coverage(reduction, None, None, chrStart, chrEnd)
            sum += coverage
            
        chrSum = 0            
        for k in settings.genomeDataNumbers[self.genome]:
            chrSum += settings.genomeDataNumbers[self.genome][k]
         
        return sum / float(chrSum)
    
    def calculateCoverages(self):
        pass
        
    def getOverlappingText(self):
        pass
    
    def getSubAnnotations(self):
        return []
