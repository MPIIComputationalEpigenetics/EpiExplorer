
## class DatasetRegions
# 
# this is an interface class for datasets that define only regions and
# as features define only overlap_ratio,overlap_count, distance_upstream and distance_downstream
# the regions are stored in a local file DB and the search structure is inteval tree
import os
import os.path
import numpy
import sqlite3
import gc
import sys
import gzip
import time

if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
else:    
    mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep    
    sys.path.insert(0,mainFolder)

from utilities import *
import settings
import Dataset
import IntervalTree
import IntervalArray
import cPickle
import subprocess

class DatasetRegions(Dataset.Dataset):        
    def init(self,initCompute=True):
        self.mergeOverlaps = hasattr(self, "mergeOverlaps") and self.mergeOverlaps == "True"
        self.useScore = hasattr(self, "useScore") and self.useScore == "True"
        self.useStrand = hasattr(self, "useStrand") and self.useStrand == "True"
		    
        Dataset.Dataset.init(self,initCompute)       
        self.initialized = True
        
        
    ## getRegions
    #
    # retrieves all genomic regions from this dataset
    # this function is relevant only for datasets with hasGenomicRegion = True
    def getRegions(self):
        return self.getRegionsFromLocalBED(self.getBedFile())
    
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):  
        #regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, isOfType INTEGER
        #ucsc_CpG_Islands [1, 1.0, 1, 0, 0, 1]
        # MOVE_TO_BEDTOOLS END              
        #ucsc_CpG_Islands [1, 1.0, 0]
        regionData = []
        regionDataWithScores = []
        #print self.datasetSimpleName,str(result)
        if result[1] > 0:
            # the region overlaps with this type of region
            regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName])
            if result[1] >= 0.1:
                regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName])
            if result[1] >= 0.5:
                regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName])
                
            #score overlap ratio between 00--99
            regionData.append([settings.wordPrefixes["overlapRatio"],self.datasetWordName,wordFloat(result[1],2)])
            #score overlap count an integer score        
#            regionData.append(["oc",self.datasetSimpleName,result[2]])
        else:
            md = wordMagnitude(result[2])
            regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(md)])
            # MOVE_TO_BEDTOOLS END
#            # a word indicating that more than half or less than half of the region overlap
##            if result[1] > 0.5:
##                regionData.append(["omh",self.datasetSimpleName])
##            else:
##                regionData.append(["olh",self.datasetSimpleName])
#            if result[3] < settings.MAX_DISTANCE:
##                du = wordMagnitude(result[3])         
#                # score to indicate the distance upstream to the nearest region of this type
##                regionData.append(["sdu",self.datasetSimpleName,result[3]])
#                # the magnitude of the distance upstream to the nearest such region
#                try:                
#                    mu = wordMagnitude(result[3])
#                except:
#                    print self.datasetSimpleName,result
#                    raise
#                regionData.append([settings.wordPrefixes["minimumDistanceUpstream"],self.datasetWordName,mu])
#            if result[4] < settings.MAX_DISTANCE:
#                
#                # score to indicate the distance downstream to the nearest region of this type
##                regionData.append(["sdd",self.datasetSimpleName,result[4]])
#                # the magnitude of the distance upstream to the nearest such region
#                md = wordMagnitude(result[4])
#                regionData.append([settings.wordPrefixes["minimumDistanceDownstream"],self.datasetWordName,str(md)])
#        #        # score to indicate the distance to the nearest region of this type
#        #        regionData.append(["sd",self.datasetSimpleName,min(result[3],result[4])])
#            if result[3] < result[4]:
#                # the magnitude of the distance upstream to the nearest such region
#                regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(mu)])
#            elif result[4] < result[3]:
#                regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(md)])
#            elif result[3] < settings.MAX_DISTANCE:
#                regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(mu)])
##        # if the region is of this type write it down
##        if result[5] == "1":            
##            regionData.append(["ct","region",str(self.datasetSimpleName).lower(),str(self.datasetSimpleName).lower()])
        return regionData,regionDataWithScores
    
    def getWordPrefixes(self,cgsAS):
        return [settings.wordPrefixes["overlap"],
                settings.wordPrefixes["overlap10p"],
                settings.wordPrefixes["overlap50p"],
                settings.wordPrefixes["overlapRatio"],
#                settings.wordPrefixes["minimumDistanceDownstream"],
#                settings.wordPrefixes["minimumDistanceUpstream"],
                settings.wordPrefixes["minimumDistance"]]
    
    def getWordsDescription(self):
        doc = []
        doc.append(["overlaps:enhancers","This region overlaps with enhancers",["overlaps:"+self.datasetSimpleName]])
        doc.append(["or:enhancers:78","Indicates that 78% of this region overlaps with an enhancer",["or:"+self.datasetSimpleName+":"]])
#        doc.append(["oc:enhancers:2","Indicates that this region overlaps with two enhancers"
#        doc.append(["dum:enhancers:43","The magnitude of the distance to the closest enhancer upstream is between 10^4*3 and 10^4*4",["dum:"+self.datasetSimpleName+":"]])        
#        doc.append(["ddm:enhancers:43","The magnitude of the distance to the closest enhancer downstream is between 10^4*3 and 10^4*4",["ddm:"+self.datasetSimpleName+":"]])
        doc.append(["dmm:enhancers:54","The magnitude of the distance to the closest enhancer upstream or downstream is between 10^5*4 and 10^5*5",["dmm:"+self.datasetSimpleName+":"]])

       
        return doc
            
          
    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):
#        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, isOfType INTEGER)")
        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, min_distance INTEGER)")
        # MOVE_TO_BEDTOOLS END
        log("Before annotate with bed")
        fnBed =  getRegionsCollectionName(cgsAS.datasetCollectionName,self.genome)[:-8]+".bed"
        annotateFnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".annotated"
        closestFnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".closest"
        if not os.path.isfile(annotateFnBed):
            annotateCommand = settings.bedToolsFolder+"annotateBed -i "+fnBed+" -files "+self.getBedFile()+" > "+annotateFnBed        
            log(annotateCommand)
            subprocess.Popen(annotateCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        f = open(annotateFnBed)
        for rl in f:
            rlParts = rl.strip().split("\t")
            # the previous indeces are chrom, start,end, id, score,strand,annotate
            cgsAS.featuresDatasets[self.datasetSimpleName]["data"][int(rlParts[3])] = [float(rlParts[6]),0]
        f.close()
        
        if not os.path.isfile(closestFnBed):
            closestCommand = settings.bedToolsFolder+"closestBed -a "+fnBed+" -b "+self.getBedFile()+" -d "+" > "+closestFnBed
            log(closestCommand)        
            subprocess.Popen(closestCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        f = open(closestFnBed)
        for rl in f:
            rlParts = rl.strip().split("\t")
            if int(rlParts[-1]) > -1: 
                cgsAS.featuresDatasets[self.datasetSimpleName]["data"][int(rlParts[3])][1] = int(rlParts[-1])
            else:
                cgsAS.featuresDatasets[self.datasetSimpleName]["data"][int(rlParts[3])][1] = settings.MAX_DISTANCE
        f.close()
        log("After annotate with bed")
    
    def initializePropertiesComputeStructures(self):
#    	self.intervalArray = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName([]),numpy.uint32,2)
#        if self.intervalArray.exist(1) and self.intervalArray.exist(5) and self.intervalArray.exist(11) and self.intervalArray.exist(15):
#            log(self.datasetSimpleName+" intervalArray already exists")            
#            return
#
#        log(self.datasetSimpleName+": Computing interval array")
#        conn = sqlite3.connect(self.binaryFile)
#        c = conn.cursor()
#        try:
#            c.execute("SELECT chrom,start,stop FROM "+self.datasetSimpleName+" ORDER BY chrom,start,stop")                    
#            datasetRegions = []
#            currentChrom = None
#            count = 0
#            for row in c:
#                count += 1
#                if currentChrom != row[0]:
#                    if currentChrom == None:
#                        currentChrom = row[0]
#                    else:
#                        self.intervalArray.addChromosomeArray(currentChrom,datasetRegions,False)
#    #                    log(self.datasetSimpleName+" added chromosome "+str(currentChrom)+" "+str(len(datasetRegions)))
#                        datasetRegions = []
#                        currentChrom = row[0]
#                datasetRegions.append(list(row)[1:])            
#            self.intervalArray.addChromosomeArray(currentChrom,datasetRegions,False)
#            log(self.datasetSimpleName+" interval array computed "+str(count))
#            self.intervalArray.store()
#    
#            self.intervalArray.cleanup()
#            log(self.datasetSimpleName+" interval array stored ")
#            c.close()
#            conn.close()
#        except:
#            c.close()
#            conn.close()
        pass
        


    def computeSingleRegionProperties(self, row, cgsAS):        
        # regionID, overlap_ratio, overlap_count, distance_upstream ,distance_downstream, isOfType        
        if row[4] == self.__getDatasetId__(cgsAS):
#            isOfType = 1
#            return [(row[0], 1,1, 0,0, isOfType)]
            return [(row[0], 1, 0)]
        else:
            # MOVE_TO_BEDTOOLS START
#            isOfType = 0
#            chrom = row[1]
#            start = row[2]
#            stop = row[3]
#            overlapingRegionsInterval = self.intervalArray.findTwoDimentionalWithAdditionalInfo(chrom, start, stop)
#            if len(overlapingRegionsInterval) > 0:
#                overlap_count = len(overlapingRegionsInterval)
#                reducedGR = gr_reduceRegionSet(list(overlapingRegionsInterval))                                
#                overlap_ratio = gr_Coverage(reducedGR, start, stop) / float(stop - start)
#                distance_upstream = 0
#                distance_downstream = 0
#                if numpy.abs(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][0] - overlap_ratio) > 0.00001 or cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][1] != 0:
#                    raise GDMValueException, str(row)+str(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]])+" or:"+str(overlap_ratio)
#                
#            else:
#                overlap_ratio = 0
#                overlap_count = 0
#                distance_upstream = self.intervalArray.distanceUpstream
#                distance_downstream = self.intervalArray.distanceDownstream
#                if cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][0] != 0 or cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][1] != min(distance_upstream,distance_downstream):
#                    raise GDMValueException, str(row)+str(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]])+"u: "+str(distance_upstream)+" d:"+str(distance_downstream)
#            return [(row[0], overlap_ratio, overlap_count, distance_upstream, distance_downstream, isOfType)]
            # MOVE_TO_BEDTOOLS END
            return [(row[0], float(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][0]), cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][1])]
        
    
    def cleanup(self,cgsAS):
        #CLEANUP IMPROVE
        annotateFnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".annotated"
        if os.path.isfile(annotateFnBed):
            os.unlink(annotateFnBed)
        
        closestFnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".closest"
        if os.path.isfile(closestFnBed):
            os.unlink(closestFnBed)
        
        sqlite3Data = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(sqlite3Data):
            os.unlink(sqlite3Data)
            
        sortedBedName = self.getBedFile()+".sorted"
        if os.path.isfile(sortedBedName):
            os.unlink(sortedBedName)
#        self.intervalArray.cleanup()
        
    def hasAllDownloadedFiles(self):
        absName = self.getDatasetLocalFile()
        if os.path.isfile(absName):
            self.downloadUrls["any"] = self.datasetFrom
            self.downloadDate = fileTimeStr(absName)
            return True
        else:
            return False
        
    def hasPreprocessedFile(self):       
        self.binaryFile = self.getDatasetBinaryName()
#        if not os.path.isfile(self.binaryFile):
#            return False     
        
        if not os.path.isfile(self.getBedFile()):
            return False
        return True 
    
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

        log(self.datasetSimpleName+" bed preprocessing start")        
        
        sortedBedName = self.getBedFile()+".sorted"
        plainBedName = self.getBedFile()+".plain"
        if not os.path.isfile(sortedBedName) and not os.path.isfile(self.getBedFile()):
            if datasetLocalFile.endswith(".gz"):
               f = gzip.GzipFile(datasetLocalFile,"rb")            
            elif datasetLocalFile.endswith(".txt") or datasetLocalFile.endswith(".user"):
               f = open(datasetLocalFile,"r")        
            else:
                raise Exception, "Dataset file extention is not recognized"    
            fBed = open(plainBedName,"w")
            ci = int(self.chromIndex) 
            csi = int(self.chromStartIndex)
            cei = int(self.chromEndIndex)
            if self.useScore:
                sci = int(self.scoreIndex)
            if self.useStrand:
                sti = int(self.strandIndex)
            i = -1
            line = -1
            for fl in f:
                line = line + 1
                flParts = fl.strip().split("\t")
                i += 1
                try:
                    #print "'"+flParts[ci]+"'"
                    convertChromToInt(self.genome,flParts[ci])
                    int(flParts[csi])
                    int(flParts[cei])
                except Exception , e:
                    if "_random" in flParts[ci]:
                        continue
                    elif "chrM" in flParts[ci]:
                        continue
                    elif "hap" in flParts[ci]:
                        continue
                    elif flParts[ci].startswith("chrUn"):
                        continue
                    elif i == 0:
                        # potential title, allow it to pass
                        continue
                    else:
                        raise IOError('Error reading file ' + datasetLocalFile + ' at line ' + str(line), e)
                if self.useScore or self.useStrand:                    
                    if self.useScore and self.useStrand:
                        lineEl = [flParts[ci],flParts[csi],flParts[cei],".",flParts[sci],flParts[sti]]
                    elif self.useScore and not self.useStrand:
                        lineEl = [flParts[ci],flParts[csi],flParts[cei],".",flParts[sci],"0"]
                    elif not self.useScore and self.useStrand:
                        lineEl = [flParts[ci],flParts[csi],flParts[cei],".","-1",flParts[sti]]
                else:
                    lineEl = [flParts[ci],flParts[csi],flParts[cei]]
                        
                fBed.write("\t".join(lineEl)+"\n")
                
            f.close()        
            fBed.close()
            if self.mergeOverlaps:
                subprocess.Popen(settings.bedToolsFolder+"sortBed -i "+plainBedName+" > "+sortedBedName,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
            else:
                subprocess.Popen(settings.bedToolsFolder+"sortBed -i "+plainBedName+" > "+self.getBedFile(),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
            if os.path.isfile(plainBedName):
                os.unlink(plainBedName)
        
        if not os.path.isfile(self.getBedFile()) and self.mergeOverlaps:            
            subprocess.Popen(settings.bedToolsFolder+"mergeBed -i "+sortedBedName+" > "+self.getBedFile(),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()            
            if os.path.isfile(sortedBedName):
                os.unlink(sortedBedName)        
        log(self.datasetSimpleName+" bed preprocessing end")
        
    def getDefaultAnnotationSettings(self):        
        # obtain the default settings
        settings = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settings["hasGenomicRegions"] = self.hasGenomicRegions
        settings["hasFeatures"] = self.hasFeatures
        settings["data"] = {}
        
        settings["mergeOverlaps"] = self.mergeOverlaps
        
        #retrun them
        return settings  
    
    # This method returns a list of feature words for the feature listing in the user interface 
    def getVisualizationFeatures(self,annotationFeatures):
        categories = self.dataCategories.strip()
        if len(categories) == 0:
            categoriesPath = [self.datasetSimpleName]
        else:
            categoriesPath = map(lambda x:x.strip(),categories.split("/"))+[self.datasetSimpleName]
        featureWords = []
        featureWords.append(categoriesPath+["OVERLAP:"+self.datasetWordName+"::"+"Eor:"+self.datasetWordName+"::2::0"])  
        featureWords.append(categoriesPath+["_OVERLAP:"+self.datasetWordName])
#        featureWords.append(categoriesPath+["distanceTo"]+["Emdd:"+self.datasetWordName+"::2::0"])
#        featureWords.append(categoriesPath+["distanceTo"]+["Emud:"+self.datasetWordName+"::2::0"])
        featureWords.append(categoriesPath+["Emmd:"+self.datasetWordName+"::2::0"])
        return featureWords
    
    def getBedFile(self):
        return settings.rawDataFolder[self.genome]+self.datasetSimpleName+".bed"
    
    def calculateCoverages(self):    
        data = self.getRegions()      
        self.coverages["any"] = self.calculateCoverage(data)                  
        
    def getOverlappingText(self):
        return self.datasetWordName
    
    def getSubAnnotations(self):
        return ["any"]
     
