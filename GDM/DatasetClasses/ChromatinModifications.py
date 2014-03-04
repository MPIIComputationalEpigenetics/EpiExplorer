
## class ChromatinModifications
# 
# this is an interface class for the Barski dataset of all chromatin modifications included in the EpiGRAPH database
# If it includes regions in includes which regions include which chromatin modificatins
# otherwise for every region it defines proximity and overlap with every chromatin modifications
import os
import os.path
import numpy
import sqlite3
import gc
import sys
if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
else:    
    mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep    
    sys.path.insert(0,mainFolder)

from utilities import *
import Dataset
import IntervalArray
#import cPickle
#import cx_Oracle

class ChromatinModifications(Dataset.Dataset):
        
    def init(self): 
        Dataset.Dataset.init(self,initCompute)       
        self.initialized = True 
        self.datasetRawData = getFileName(self.datasetRawData ,self.iniLongName)       
        
        self.chromModification = self.chromatin_modification
        #"regionOverlapSQL": "SELECT chromstart, chromend, chrommod FROM "+self.dbName+" WHERE chrom = :1 AND chromstart <= :3 AND chromend >= :2 AND chrommod = '"+self.chromModifications+"' ORDER BY chrommod, chromstart",
        
    # This method created the data structure in which the properties will be stored and initiates any suppost structures 
    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):        
            
        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER)")
    
    def initializePropertiesComputeStructures(self):
        chromData = {}
        chromSizes = {}
        lineCounts = line_count(self.datasetRawData)
        self.intervalArray = IntervalArray.GenomeIntervalArray()
        f = open(self.datasetRawData)
        line = f.readline()
        line = f.readline()        
        while line:
            try:
                # expected format
                # chr7    40271388    40271411    U0    0    +           
                lineParts = line.strip().split("\t")                            
                chrom = convertChromToInt(self.genome,lineParts[0])
                if not chromData.has_key(chrom):
                    chromData[chrom] = numpy.zeros((lineCounts/10,2),dtype=int)
                    chromSizes[chrom] = 0
                    #print chromData[chrom][0]
                #print chromData[chrom][chromSizes[chrom],:]
                chromData[chrom][chromSizes[chrom],:] = [int(lineParts[1]),int(lineParts[2])]                
                chromSizes[chrom] += 1
            except GDMException,ex:
                #print "GDM exception",ex
                pass
            line = f.readline()
        f.close()
        print "Dataset read"
        for chrom in chromData.keys():
            aS =  chromData[chrom][0:chromSizes[chrom],:].argsort(axis=0)
            a = numpy.array(chromData[chrom][aS[:,0]])
            self.intervalArray.addChromosomeArray(chrom,a)
            del chromData[chrom]
    # computed the properties for this daset for the given region and stores them in the properties structure
    # @return: this method should not return the properties but store them
    def computeSingleRegionProperties(self, row , cgsAS):
        isOfType = 0
        chr = convertIntToChrom(self.genome,row[1])
        start = row[2]
        stop = row[3]
        raise Exception, "Has to be updated"
        overlapingRegionsInterval = self.intervalArray.findTwoDimentionalWithAdditionalInfo(row[1], start, stop)
#        print row[1],row[2],row[3]
        #self.dbcur.execute(self.statements["regionOverlapSQL"],[chr,start,end])        
        #results = self.dbcur.fetchall()
#        print len(results),len(overlapingRegionsInterval)
        overlap_count = len(overlapingRegionsInterval)
        if overlap_count == 0:
#            self.cD.execute("INSERT INTO " + self.datasetSimpleName + "_data VALUES (?,?,?)", (row[0], 0, 0))
            pass
        else:
#            chromMod = results[0][2]
#            prevI = 0
#            for i in range(1,len(results)):
#                if results[i][2] != chromMod:                     
#                    overlapingRegionsInterval = results[prevI:i]
#                    overlap_count = len(overlapingRegionsInterval)
#                    reducedGR = gr_reduceRegionSet(overlapingRegionsInterval)
#                    overlap_ratio = gr_Coverage(reducedGR, start, stop) / float(stop - start)
#                    self.cD.execute("INSERT INTO " + self.datasetSimpleName + "_data VALUES (?,?,?,?)", (row[0], overlap_count, overlap_ratio, chromMod))
#                    chromMod = results[i][2]
#                    prevI = i
#            overlapingRegionsInterval = results[prevI:]            
            reducedGR = gr_reduceRegionSet(list(overlapingRegionsInterval))
            overlap_ratio = gr_Coverage(reducedGR, start, stop) / float(stop - start)
            self.cD.execute("INSERT INTO " + self.datasetSimpleName + "_data VALUES (?,?,?)", (row[0], overlap_ratio, overlap_count))
    ## cleanup
    #
    # this method is called after all the properties re computed and stored. The purpose is to clean up all the 
    # unnecessary structures
    
    def cleanup(self,cgsAS):
        #CLEANUP IMPROVE
        pass 
#        for chrom in self.intervalArray.chroms.keys():
#            del self.intervalArray.chroms[chrom]
          
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
        print self.datasetSimpleName, list(result)
        raise GDMException
        regionData = []
        regionDataWithScores = []
        #print self.datasetSimpleName,str(result)
        #regionID INTEGER, overlap_ratio REAL, overlap_count INTERGER        
        if result[2] > 0:
            regionData.append(["cm",self.chromModification])
            # store the overlap ratio as score            
            regionData.append(["scmr",str(self.chromModification),wordFloat(result[1],2)])
            # add one more score aobut the number of chrom mod regions overlapping
            regionData.append(["scmc",str(self.chromModification),str(result[2])])            
                    
        return regionData,regionDataWithScores
    
    def getWordsDescription(self):
        doc = ""
        doc += "cm:CTCF indicates that this region has a chromatin modification CTCF\n"
        doc += "scmr:CTCF:05 indicates that 5% of this region is covered by regions indicated with the chromatin modification CTCF\n"
        doc += "scmc:CTCF:3 indicates that there were 3 regions with chromatin modification CTCF overlapping with this region \n"        
        return doc
    
    def getDefaultAnnotationSettings(self):        
        # obtain the default settings
        settings = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settings["hasGenomicRegions"] = self.hasGenomicRegions
        settings["hasFeatures"] = self.hasFeatures
        #retrun them
        return settings
            