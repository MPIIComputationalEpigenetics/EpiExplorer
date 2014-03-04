
## class Repeats
# 
# this is an interface class for the RepeatMasker dataset of all repeats included in the EpiGRAPH database
# If it includes regions in includes which regions include which type of repeats
# otherwise for every region it defines proximity(???) and overlap with
import os
import os.path
import numpy
import sqlite3
import gc
import sys
import gzip
if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
else:    
    mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep    
    sys.path.insert(0,mainFolder)

from utilities import *
import settings
import Dataset
import IntervalArray
#import cPickle
#import cx_Oracle

class ChromosomeBand(Dataset.Dataset):
        
    def init(self,initCompute=True):
        Dataset.Dataset.init(self,initCompute)
        self.regionsCountMod = 1000000
        self.binaryFile = self.getDatasetBinaryName()
        self.initialized = True
        
    def hasAllDownloadedFiles(self):
        absName = self.getDatasetLocalFile()
        if os.path.isfile(absName):
            self.downloadUrls["any"] = self.datasetFrom
            self.downloadDate = fileTimeStr(self.getDatasetLocalFile())
            return True
        else:
            return False
            
    def getDatasetLocalFile(self):
        return self.__getDatasetSingleLocalFile__()
    
    def downloadDataset(self):
       self.__downloadSingleFileDataset__()
   
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
                    
        datasetLocalFile = self.getDatasetLocalFile()
        if datasetLocalFile.endswith(".gz"):
            f = gzip.GzipFile(datasetLocalFile,"rb")            
        elif datasetLocalFile.endswith(".txt") or datasetLocalFile.endswith(".user"):
            f = open(datasetLocalFile,"r")
        else:
            raise GDMException, "unsupported file extension for "+datasetLocalFile
        import dataset_methods
        lines = f.readlines()                
                
        log(self.datasetSimpleName + " was read. "+str(len(lines))+" lines")
        f.close()
        # Save the file into a local DB
        self.binaryFile = self.getDatasetBinaryName()
        
        try:
            conn = sqlite3.connect(self.binaryFile)
            c = conn.cursor()
            c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER, chrband TEXT)')
            for line in lines:
                if not line:
                    continue
                lineParts = line.strip().split("\t")
                c.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?,?,?,?)',(convertChromToInt(self.genome,lineParts[0]),int(lineParts[1]),int(lineParts[2]),lineParts[3]))
            conn.commit()
            c.close()
            conn.close()
        except:
            c.close()
            conn.close()
            os.unlink(self.binaryFile)
            raise
                  
        
    def initializePropertiesComputeStructures(self):
        self.intervalArray = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName([]),numpy.uint32,2)
        
        self.chrBandByID = {}
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()                
        for chr in settings.genomeDataStr[self.genome].keys():           
           chrInt = convertChromToInt(self.genome,chr)
           c.execute("SELECT start,stop,chrband FROM "+self.datasetSimpleName+" WHERE chrom=? ORDER BY start",tuple([chrInt]))
           
           data = c.fetchall()
           for d in data:
               self.chrBandByID[str(chrInt)+":"+str(d[0])+"-"+str(d[1])] = convertIntToChrom(self.genome,chrInt)[3:]+d[2]
           if len(data):               
               self.intervalArray.addChromosomeArray(chrInt,map(lambda x:x[:2],data),True)
        c.close()
        conn.close()        
        log(self.datasetSimpleName+" interval array computed")      
            
    
    # This method created the data structure in which the properties will be stored and initiates any suppost structures
     
    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):
        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, chrband TEXT)")
    
    def computeSingleRegionProperties(self,   row , cgsAS):        
        # regionID, overlap_ratio, overlap_count, distance_upstream ,distance_downstream, isOfType
        isOfType = 0
        chrom = row[1]
        start = row[2]
        stop = row[3]
        raise Exception, "Has to be updated"
        overlapingRegionsInterval = self.intervalArray.findTwoDimentionalWithAdditionalInfo(chrom, start, stop)
        if len(overlapingRegionsInterval) > 0:
            return [(row[0],self.chrBandByID[str(chrom)+":"+str(el[0])+"-"+str(el[1])]) for el in overlapingRegionsInterval]
        else:
            raise Exception, "Every regions should overlap with a chromosome band "+str(row)
        

    def cleanup(self,cgsAS):
        #CLEANUP IMPROVE
        pass
#       self.intervalArray.cleanup()
       
    
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):  
        # regionID, chrband                      
        return  [[settings.wordPrefixes["chrband"],result[1].replace(".","_")]],[]
    
    def getWordPrefixes(self,cgsAS):
        return [settings.wordPrefixes["chrband"]]
    
    def getWordsDescription(self):
        doc = []
        doc.append(["result[1]","Indicates that the region is in the p31_2 band",[]])       
        return doc
    
    def getDefaultAnnotationSettings(self):        
        # obtain the default settings
        settings = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settings["hasGenomicRegions"] = self.hasGenomicRegions
        settings["hasFeatures"] = self.hasFeatures
        #retrun them
        return settings
        
            
        

        