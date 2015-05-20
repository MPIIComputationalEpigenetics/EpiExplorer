## class RRBSmethylation
# 
# this is an interface class for datasets that RRBS methylation for a tissue
# as features define only overlap_ratio,overlap_count, distance_upstream and distance_downstream
# these 
import os
import os.path
import numpy
import sqlite3
import gzip
import gc
import sys
if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
else:    
    mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep    
    sys.path.insert(0,mainFolder)    
from utilities import *
import Dataset
import numpy
import IntervalArray


class RRBSmethylation(Dataset.Dataset):    
    
    
    def init(self,initCompute=True):
        self.intervalArray = None
        self.chromIndex = int(self.chromIndex)
        self.chromStartIndex = int(self.chromStartIndex)
        self.chromEndIndex = int(self.chromEndIndex)
        self.scoreIndex = int(self.scoreIndex)        
        self.scoreBase = float(self.scoreBase)/100
        self.hasHeader = int(self.hasHeader)
        Dataset.Dataset.init(self,initCompute)                
        self.initialized = True
    
    
    def getDownloadInfo(self,tissue):
        if tissue == "HSMMtube":
            datasetURL = self.datasetFrom.replace("TISSUE","Hsmmt")   
        else:
            datasetURL = self.datasetFrom.replace("TISSUE",tissue.capitalize())
        
        #print datasetURL                
        downloadedLastPart = os.path.basename(datasetURL)
        datasetLocalFile = os.path.abspath(settings.downloadDataFolder[self.genome] + downloadedLastPart)
        return datasetURL,datasetLocalFile
        
    def hasAllDownloadedFiles(self):
        datasetURL,datasetLocalFile = self.getDownloadInfo(self.tissue)        
        if os.path.isfile(datasetLocalFile):
            self.downloadUrls["any"] = datasetURL
            self.downloadDate = fileTimeStr(datasetLocalFile)
            return True
        return False  
    
    def downloadDataset(self):
        if self.hasAllDownloadedFiles():
            return
        datasetURL,datasetLocalFile = self.getDownloadInfo(self.tissue)
        if not os.path.isfile(datasetLocalFile):        
            downloadFile(datasetURL, datasetLocalFile)
            self.downloadUrls["any"] = datasetURL
            self.downloadDate = fileTimeStr(datasetLocalFile)  

        #raise GDMException, "The RRBS dataset "+self.datasetSimpleName+" is not available"  
    
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
            c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER, signalValue INTEGER)')
            
            datasetURL,datasetLocalFile = self.getDownloadInfo(self.tissue)
            f = gzip.GzipFile(datasetLocalFile,"rb")
            lines = map(lambda x:x.strip().split("\t"),f.readlines())
            f.close()
            if self.datasetFormat == 'BED':                
                for i in xrange(self.hasHeader,len(lines)):   
                    try:
                        chrom = convertChromToInt(self.genome,lines[i][self.chromIndex])
                    except GDMException, ex:
                        continue

                    score = 0 if lines[i][self.scoreIndex] == "0" else int(float(lines[i][self.scoreIndex])/self.scoreBase)
                    c.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?,?,?,?)',
                              tuple([chrom,
                                     int(lines[i][self.chromStartIndex])+1,
                                     int(lines[i][self.chromEndIndex]),
                                     score]))
            else:
                raise GDMException, "Alternative dataset format is not supported yet"
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
    
    def initializePropertiesComputeStructures(self):
        log("computing interval array for " + self.datasetSimpleName)
        chromData = {}
        chromSizes = {}
       
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()
        try:
            # initializing the IntervalArray
            self.intervalArray = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName([self.tissue]),numpy.int32,3)            
                        
            if self.intervalArray.exist(1) and self.intervalArray.exist(5) and self.intervalArray.exist(11) and self.intervalArray.exist(15):
                log(self.datasetSimpleName+" have stored precomputed arrays")
                c.close()
                conn.close()
                return
            else:
                log(self.datasetSimpleName+" "+self.tissue+" has no stored computed array for some chromosomes")
            
            c.execute("SELECT chrom, start, stop,  signalValue FROM "+self.datasetSimpleName+" ORDER BY chrom,start")
                        
            data = c.fetchall()
        except:
            c.close()
            conn.close()
            raise 
        c.close()
        conn.close()
        #log("MARK: all data was fetched")
        if len(data):            
            self.intervalArray.loadFullDataSortedbyChrom(data,True)
            log("\ttissue "+self.tissue+" is ready")
            
        log("Interval array computed for "+self.datasetSimpleName)
                    
        self.intervalArray.store()
            
        self.intervalArray.cleanup()
        log("Interval array stored for "+self.datasetSimpleName)
    
        
    def initializePropertiesStoreStructures(self,cgsAS, dataConnections):        
        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, numberCpGs INTEGER, methRatio INTEGER, methMin INTEGER, methMax INTEGER, methStd INTEGER)")
        
    def computeSingleRegionProperties(self, row, cgsAS):
                
        # regionID, overlap_ratio, overlap_count, distance_upstream, distance_downstream, tissue, histoneMark
        results = []        
        isOfType = 0
        chrom = row[1]
        start = row[2]
        stop = row[3]
        
        overlapingRegions = self.intervalArray.findTwoDimentionalWithAdditionalInfo(chrom, start, stop,cgsAS.featuresDatasets[self.datasetSimpleName]['data'])
        
        overlap_count = len(overlapingRegions)
        
        if overlap_count == 0:   
            #regionID INTEGER, numberCpGs INTEGER, methRatio INTEGER, methMin INTEGER, methMax INTEGER, methStd INTEGER             
            results = [[row[0], 0, 0, 0, 0, 0]]
        else:

            results = [[row[0], 
                      overlap_count, #numberCpGs INTEGER,
                      int(overlapingRegions[:,2].mean()), #methRatio INTEGER
                      int(overlapingRegions[:,2].min()), #methMin INTEGER
                      int(overlapingRegions[:,2].max()), # methMax INTEGER
                      int(overlapingRegions[:,2].std()), #methStd INTEGER
                      ]]
            #print row,overlapingRegions,results
        #if start > 11082980:
        #    raise GDMException, "Not implemented yet"
        return results
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
#        #regionID INTEGER, numberCpGs INTEGER, methRatio INTEGER, methMin INTEGER, methMax INTEGER, methStd INTEGER
        regionData = []
        regionDataWithScores = [] 
        if result[1] >= 1000:
            result[1] = 999
        #regionData.append([settings.wordPrefixes["methCpGcount"],self.datasetWordName,self.tissue,wordMagnitude(result[1],3)])
        regionData.append([settings.wordPrefixes["methCpGcount"],self.datasetWordName,self.tissue,wordFixed(result[1],3)])
              
        if result[1] > 0:
            for i in [2,3,4,5]:
                if result[i] >= 100:
                    result[i] = 99                
            regionData.append([settings.wordPrefixes["methRatio"],self.datasetWordName,self.tissue,wordFixed(result[2],2)])
            regionData.append([settings.wordPrefixes["methRatioMin"],self.datasetWordName,self.tissue,wordFixed(result[3],2)])
            regionData.append([settings.wordPrefixes["methRatioMax"],self.datasetWordName,self.tissue,wordFixed(result[4],2)])
            regionData.append([settings.wordPrefixes["methRatioStd"],self.datasetWordName,self.tissue,wordFixed(result[5],2)])
            if result[2] >= 67:
                regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName,self.tissue,settings.wordPrefixes["methSummaryMeth"]])
                regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName,self.tissue,settings.wordPrefixes["methSummaryMeth"]])
                regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName,self.tissue,settings.wordPrefixes["methSummaryMeth"]])
            if result[2] <= 33:
                regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName,self.tissue,settings.wordPrefixes["methSummaryUnmeth"]])
                regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName,self.tissue,settings.wordPrefixes["methSummaryUnmeth"]])
                regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName,self.tissue,settings.wordPrefixes["methSummaryUnmeth"]])
                
            
        return regionData,regionDataWithScores
    
    # This method returns a list of feature words for the feature listing in the user interface 
    def getVisualizationFeatures(self,annotationFeatures):
        categories = self.dataCategories.strip()
        if len(categories) == 0:
            categoriesPath = [self.datasetSimpleName]
        else:
            categoriesPath = map(lambda x:x.strip(),categories.split("/"))+[self.datasetSimpleName]
        featureWords = []

        featureWords.append(categoriesPath+[":".join([settings.wordPrefixes["methRatio"],self.datasetWordName,self.tissue])+"::2::0"])
        featureWords.append(categoriesPath+[":".join([settings.wordPrefixes["methRatioStd"],self.datasetWordName,self.tissue])+"::2::0"])
        featureWords.append(categoriesPath+[":".join([settings.wordPrefixes["methRatioMin"],self.datasetWordName,self.tissue])+"::2::0"])
        featureWords.append(categoriesPath+[":".join([settings.wordPrefixes["methRatioMax"],self.datasetWordName,self.tissue])+"::2::0"])
        # if the next is considered as ratio
        featureWords.append(categoriesPath+[":".join([settings.wordPrefixes["methCpGcount"],self.datasetWordName,self.tissue])+"::0::0"])
        # if it is considered as range
        #featureWords.append(categoriesPath+[":".join([settings.wordPrefixes["methCpGcount"],self.datasetWordName,self.tissue])+"::3::0"])
        
        return featureWords
    def getRangeNRatioWords(self,annotationFeatures):
        junkWordsList = []
        for i in range(1000):
            junkWordsList.append([settings.wordPrefixes["methCpGcount"],self.datasetWordName,self.tissue,wordFixed(i,3)])
        for t in [settings.wordPrefixes["methRatio"],settings.wordPrefixes["methRatioMin"],settings.wordPrefixes["methRatioMax"],settings.wordPrefixes["methRatioStd"]]:
            for i in range(100):                
                junkWordsList.append([t,self.datasetWordName,self.tissue,wordFixed(i,2)])
                
        return map(lambda x:":".join(x),junkWordsList)
    
    def getWordPrefixes(self,cgsAS):
        prefixes = []        
        prefixes.append(settings.wordPrefixes["methRatio"]+":"+self.datasetWordName+":"+self.tissue)
        prefixes.append(settings.wordPrefixes["methRatioStd"]+":"+self.datasetWordName+":"+self.tissue)
        prefixes.append(settings.wordPrefixes["methRatioMin"]+":"+self.datasetWordName+":"+self.tissue)
        prefixes.append(settings.wordPrefixes["methRatioMax"]+":"+self.datasetWordName+":"+self.tissue)
        prefixes.append(settings.wordPrefixes["methCpGcount"]+":"+self.datasetWordName+":"+self.tissue)
        
        return prefixes
    
#    def initializePropertiesStructures(self):
#        raise GDMException, "Not implemented yet"
#        log("computing interval array for "+self.datasetSimpleName)
#        #computing the interval tree
#        lineCounts = line_count(self.datasetRawData)
#        log([lineCounts," lines ot be processed"])
#        datasetRegions = []
#        self.intervalArray = IntervalArray.GenomeIntervalArray()
#        f = open(self.datasetRawData)
#        line = f.readline()
#        index = 0
#        
#        currentChrom = None
#        while line:
#            try:
#                # expected format
#                # chr1    496    498    '230/270'    851    +                
#                lineParts = line.strip().split("\t")
#                index += 1
#                chrom = convertChromToInt(self.genome,lineParts[0])
#                if currentChrom != chrom:
#                    if currentChrom:
#                        self.intervalArray.addChromosomeArray(currentChrom,numpy.array(datasetRegions,dtype=int))
#                        datasetRegions = []
#                        currentChrom = chrom
#                    else:
#                        datasetRegions = []
#                        currentChrom = chrom
#                pos = int(lineParts[1])+1
#                methRatio = int(lineParts[4])
#                obsCount = int(lineParts[3].split("/")[1][:-1])                
#                datasetRegions.append([pos,methRatio,obsCount])
#            except Exception,ex:
#                print str(ex)                
#            line = f.readline()
#            if index % 50000 == 0:
#                print index, "out of ",lineCounts
#        
#        self.intervalArray.addChromosomeArray(currentChrom,numpy.array(datasetRegions,dtype=int))
#        log("interval array computed and stored for "+self.datasetSimpleName)    
#        #creating the data table
#        createTableQuery = "CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, methRatio REAL, cpgCount INTERGER, obsPerCpG INTEGER)"        
#        self.cD.execute(createTableQuery)
        
#    def computeSingleRegionProperties(self,row, cgsAS):
#        regionID = row[0]        
#        chrom = row[1]
#        start = row[2]
#        stop = row[3]
#        raise Exception, "Has to be updated"
#        overlapingRegionsInterval = self.intervalArray.findTwoDimentionalWithAdditionalInfo(chrom, start, stop,0,0)        
#        if len(overlapingRegionsInterval) > 0:
#            cpgCount = len(overlapingRegionsInterval)
#            obsPerCpG = overlapingRegionsInterval[:,2].mean() 
#            methRatio = overlapingRegionsInterval[:,1].mean()
#            #print start, stop,overlapingRegionsInterval
#            #print cpgCount, methRatio, obsPerCpG
#            #raise Exception                       
#            self.cD.execute("INSERT INTO " + self.datasetSimpleName + "_data VALUES (?, ?, ?, ?)", (regionID,methRatio,cpgCount,obsPerCpG))
#        else:
#            #no data for this region
#            self.cD.execute("INSERT INTO " + self.datasetSimpleName + "_data VALUES (?, ?, ?, ?)", (regionID,-1,0,0))
        
#    def initializePropertiesStructures__intervalTree_version(self):
#        raise Exception, "Too slow...optimizing"        
#        
#        log(self.datasetSimpleName+" computing interval tree ")
#        #computing the interval tree
#        datasetRegions = []
#        f = open(self.datasetRawData)
#        line = f.readline()
#        self.regionId = 1
#        while line:
#            try:
#                i = self.__convertLineToInterval__(line)
#                datasetRegions.append(i)
#            except Exception,ex:
#                print str(ex)
#                
#            line = f.readline()
#            if self.regionId % 50000 == 0:
#                print self.regionId
#        del self.regionId
#        self.intervalTree = IntervalTree.GenomeIntervalTree(datasetRegions)
#        log("interval tree computed and stored for "+self.datasetSimpleName)    
#        #creating the data table
#        createTableQuery = "CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, methRatio REAL, cpgCount INTERGER, obsPerCpG INTEGER)"        
#        self.cD.execute(createTableQuery)

            
#    def computeSingleRegionProperties__intervalTree(self,row, cgsAS):
#        raise GDMException, "Not implemented yet"
#        regionID = row[0]        
#        chrom = row[1]
#        start = row[2]
#        stop = row[3]
#        overlapingRegionsInterval = self.intervalTree.find(chrom, start, stop)        
#        if len(overlapingRegionsInterval) > 0:
#            cpgCount = len(overlapingRegionsInterval)
#            obsPerCpG = 0 
#            methRatio = 0
#            for i in overlapingRegionsInterval:
#                methRatio += i.methRatio
#                obsPerCpG += i.obsCount
#            methRatio = round(methRatio/float(cpgCount*1000),2)
#            obsPerCpG = obsPerCpG/float(cpgCount)
#            self.cD.execute("INSERT INTO " + self.datasetSimpleName + "_data VALUES (?, ?, ?)", tuple(regionID,methRatio,cpgCount,obsPerCpG))
#        else:
#            #no data for this region
#            self.cD.execute("INSERT INTO " + self.datasetSimpleName + "_data VALUES (?, ?, ?)", tuple(regionID,-1,0,0))    
    
    def cleanup(self,cgsAS):
        sqlite3Data = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(sqlite3Data):
            os.unlink(sqlite3Data)
#        del self.intervalArray
#        gc.collect()
                
        

    def __convertLineToInterval__(self,line):
        raise Exception, "Not used, takes too much space"
        lineParts = line.strip().split("\t")
        lineParts[0] = convertChromToInt(self.genome,lineParts[0])    
        lineParts[1] = int(lineParts[1])
        lineParts[2] = int(lineParts[2])
        obsCount = int(lineParts[3].split("/")[1][:-1]) 
        lineParts[3] = self.regionId
        self.regionId += 1
        interval = IntervalTree.Interval(lineParts)
        interval.obsCount = obsCount         
        interval.methRatio = int(lineParts[4])
        
        return interval
    
#    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
#        raise GDMException, "Not implemented yet"
#        print self.datasetSimpleName, list(result)
#        raise Exception
#        regionData = []
#        #print self.datasetSimpleName,str(result)
#        #regionID INTEGER, methRatio REAL, cpgCount INTERGER, obsPerCpG INTEGER
#        # this is the score representing the DNA methylation ratio for this region
#        if result[1]>= 0:
#            # if -1 then no methylation is known for this region
#            mr = result[1]/1000
#            regionData.append(["smr",self.tissue,wordFloat(mr,2)])
#            #print mr,mr >= self.minmeth,mr <= self.maxunmeth
#            if mr >= self.minmeth:
#                regionData.append(["mr_meth",str(self.tissue).lower()])
#                regionData.append(["ct","methylation","methylated_"+str(self.tissue).lower(),"Methylated_in_tissue_"+self.tissue])
#            elif mr <= self.maxunmeth:
#                regionData.append(["mr_unmeth",str(self.tissue).lower()])
#                regionData.append(["ct","methylation","unmethylated_"+str(self.tissue).lower(),"Unmethylated_in_tissue_"+self.tissue])
#        # the count of the cpgs in this region                    
#        regionData.append(["smc",self.tissue,result[2]])
#        # the count of the cpgs in this region
#        regionData.append(["smo",self.tissue,int(round(result[3]))])
#        # good coverage word
#        if result[3] > self.goodcoverage:
#            regionData.append(["mo_good",str(self.tissue).lower()])
#                    
#        return regionData

    
    def getWordsDescription(self):
        raise GDMException, "Not implemented yet"
        doc = ""
        doc += "smr:ES:78 indicates that this region has a methylation ratio of 0.78\n"
        doc += "smc:ES:12 indicates that this regions has 12 measured CpGs in the tissue ES\n"
        doc += "smo:ES:15 indicates that the CpGs in this region and tissue have on average 15 observations \n"
        doc += "mr_meth:ES this region is methylated(>="+str(self.minmeth)+") in the tissue\n"
        doc += "mr_unmeth:ES this region is unmethylated(<="+str(self.maxunmeth)+") in the tissue\n"
        doc += "ct:methylation:methylated_ES:Methylated_in_tissue_ES this region is methylated(>="+str(self.minmeth)+") in the tissue\n"                
        doc += "ct:methylation:unmethylated_ES:Unmethylated_in_tissue_ES this region is unmethylated(<="+str(self.maxunmeth)+") in the tissue\n"
        doc += "mo_good:ES indicates the method has good (>="+str(self.goodcoverage)+") coverage for the cpgs it measures\n"
        return doc
    
    def getDefaultAnnotationSettings(self):
        # obtain the default settings
        settingsLocal = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settingsLocal["hasGenomicRegions"] = self.hasGenomicRegions
        settingsLocal["hasFeatures"] = self.hasFeatures
                
        settingsLocal["data"] = {'distanceDownstream':settings.MAX_DISTANCE,
                            'distanceUpstream':settings.MAX_DISTANCE,
                            'currentChrom':None,
                            'currentChromStart': 0,
                            'currentStartIndex':None,
                            'currentEndIndex':None}
        #retrun them
        return settingsLocal
        

    #Methylation does not defines overlap.
    def calculateCoverages(self):
        pass
    
    def getSubAnnotations(self):
        return ["any"]
