import os
import os.path
import numpy
import sqlite3
import gzip
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
import settings

class Infinium(Dataset.Dataset):    
    
    def init(self,initCompute=True):
        self.intervalArray = None
        if self.differentiation == "True":
            self.differentiation = True                    
        else:
            self.differentiation = False
        
        if self.differentiation:
            self.reference = self.reference
        else:            
            self.hasHeader = int(self.hasHeader)
            self.chromIndex = int(self.chromIndex)
            self.chromStartIndex = int(self.chromStartIndex)
            self.chromEndIndex = int(self.chromEndIndex) 
            
        Dataset.Dataset.init(self,initCompute)                
        self.initialized = True    
        
    def hasAllDownloadedFiles(self):
        return True
    
    def downloadDataset(self):
        pass
    
    def getRegions(self):
        return self.getRegionsFromLocalBED(self.getBedFile())
    
    def getBedFile(self):
        return self.datasetFrom
    
    def preprocessDownloadedDataset(self):
        if self.hasPreprocessedFile():
            extext = self.datasetSimpleName + ": the dataset was already preprocessed in "+self.binaryFile
            log(extext)
            return
        
        log(self.datasetSimpleName + ": preprocessing the dataset into local database")
                                           
        if not self.differentiation:
            self.binaryFile = self.getDatasetBinaryName()
            conn = sqlite3.connect(self.binaryFile)
            c = conn.cursor()
            f = open(self.datasetFrom,"rb")
            lines = map(lambda x:x.strip().split("\t"),f.readlines())
            f.close()
            c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER)')                        
            for i in xrange(0,len(lines)):
                chrom = convertChromToInt(self.genome,lines[i][self.chromIndex])        
                data = tuple([chrom, int(lines[i][self.chromStartIndex])+1, int(lines[i][self.chromEndIndex])])
                c.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?,?,?)',data)
                    
            conn.commit()                            
            c.close()
            conn.close()
            
        log(self.datasetSimpleName + ": the dataset was preprocessed into local DB "+self.binaryFile)
    
    def initializePropertiesComputeStructures(self):
        log("computing interval array for "+self.datasetSimpleName)
        chromData = {}
        chromSizes = {}
       
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()
        try:
            # initializing the IntervalArray
            self.intervalArray = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName([self.tissue]),numpy.int32, 2)            
                        
            if self.intervalArray.exist(1) and self.intervalArray.exist(5) and self.intervalArray.exist(11) and self.intervalArray.exist(15):
                log(self.datasetSimpleName+" have stored precomputed arrays")
                c.close()
                conn.close()
                return
            else:
                log(self.datasetSimpleName+" "+self.tissue+" has no stored computed array for some chromosomes")
            
            c.execute("SELECT chrom, start, stop FROM "+self.datasetSimpleName+" ORDER BY chrom,start")
                        
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
        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, numberCpGs INTEGER)")
        
    def computeSingleRegionProperties(self, row, cgsAS):
        chrom = row[1]
        start = row[2]
        stop = row[3]
        
        overlapingRegions = self.intervalArray.findTwoDimentionalWithAdditionalInfo(chrom, start, stop,cgsAS.featuresDatasets[self.datasetSimpleName]['data'])        
        overlap_count = len(overlapingRegions)                
        return [[row[0], overlap_count]]
    
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
#        #regionID INTEGER, numberCpGs INTEGER, methRatio INTEGER, methMin INTEGER, methMax INTEGER, methStd INTEGER
        regionData = []
        regionDataWithScores = [] 
        if result[1] >= 1000:
            result[1] = 999
        #regionData.append([settings.wordPrefixes["methCpGcount"],self.datasetWordName,self.tissue,wordMagnitude(result[1],3)])
        regionData.append([settings.wordPrefixes["methCpGcount"],self.datasetWordName,self.tissue,wordFixed(result[1],3)])
        
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
        # if the next is considered as ratio
        featureWords.append(categoriesPath+[":".join([settings.wordPrefixes["methCpGcount"],self.datasetWordName,self.tissue])+"::0::0"])
        # if it is considered as range
        #featureWords.append(categoriesPath+[":".join([settings.wordPrefixes["methCpGcount"],self.datasetWordName,self.tissue])+"::3::0"])
        
        return featureWords
    def getRangeNRatioWords(self,annotationFeatures):
        junkWordsList = []
        for i in range(1000):
            junkWordsList.append([settings.wordPrefixes["methCpGcount"],self.datasetWordName,self.tissue,wordFixed(i,3)])        
                
        return map(lambda x:":".join(x),junkWordsList)
    
    def getWordPrefixes(self,cgsAS):
        prefixes = []        
        prefixes.append(settings.wordPrefixes["methCpGcount"]+":"+self.datasetWordName+":"+self.tissue)
        
        return prefixes
    
    def cleanup(self,cgsAS):
        sqlite3Data = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(sqlite3Data):
            os.unlink(sqlite3Data)

    def __convertLineToInterval__(self,line):
        pass
        
    def getWordsDescription(self):
        pass
    
    def getDefaultAnnotationSettings(self):
        # obtain the default settings
        settingsLocal = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settingsLocal["useScore"] = True
        settingsLocal["hasGenomicRegions"] = self.hasGenomicRegions
        settingsLocal["hasFeatures"] = self.hasFeatures
                
        settingsLocal["data"] = {'distanceDownstream':settings.MAX_DISTANCE,
                            'distanceUpstream':settings.MAX_DISTANCE,
                            'currentChrom':None,
                            'currentChromStart': 0,
                            'currentStartIndex':None,
                            'currentEndIndex':None}
        return settingsLocal
        

    #Methylation does not defines overlap.
    def calculateCoverages(self):
        pass
    
    def getSubAnnotations(self):
        return ["any"]
