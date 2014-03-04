# the regions are stored in a local file DB and the search structure is inteval tree
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
import Dataset
import IntervalArray
import IntervalTree
import settings
import cPickle
import subprocess

class DatasetRegionsWithTissues(Dataset.Dataset):
    
    def init(self,initCompute=True):
        self.intervalArrays = {}
        if hasattr(self, "filterByColumn"):
            self.filterByColumn = int(self.filterByColumn)
        else:
            self.filterByColumn = -1            
        Dataset.Dataset.init(self,initCompute)
        self.initialized = True
        self.annotateIndeces = {}
        
        # The starting index for th e tissues in the result annotated file
        # the previous indeces are chrom, start,end, id, score,strand
        index = 6
        for tissue in self.tissues+["any"]:            
            self.annotateIndeces[tissue] = index
            index += 1
        
        
    
    def getDownloadInfo(self,tissueIndex):
        tissue = self.tissues[tissueIndex]
        if len(self.datasetFrom) > 1:
            datasetFrom = self.datasetFrom[tissueIndex]
        else:
            datasetFrom = self.datasetFrom[0]
        if self.genome == "hg18" and self.datasetWordName == "DNaseI" and  tissue == "H1hESC":
            datasetURL = datasetFrom.replace("TISSUE","H1es")
        elif self.genome == "hg19" and self.datasetWordName == "DNaseI" and  tissue == "HUVEC":
            datasetURL = datasetFrom.replace("TISSUEPk","HuvecHotspots")
        else:
            datasetURL = datasetFrom.replace("TISSUE",tissue.capitalize())
        #print datasetURL                
        downloadedLastPart = os.path.basename(datasetURL)
        datasetLocalFile = os.path.abspath(settings.downloadDataFolder[self.genome] + downloadedLastPart)
        return datasetURL,datasetLocalFile
    
    def downloadDataset(self):
        if isinstance(self.tissues,str):
            self.processTissues()
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

        
    def processTissues(self):
        self.tissueMarks = {}
        self.tissues = map(lambda x:x.strip(),self.tissues.split(","))    
        if isinstance(self.tissues,str):
            self.tissues = map(lambda x:x.strip(),self.tissues.split(","))        
        if isinstance(self.datasetFrom,str):
            self.datasetFrom = map(lambda x:x.strip(),self.datasetFrom.split(","))
        if len(self.datasetFrom) != 1 and len(self.datasetFrom) != len(self.tissues):
            raise GDMException, "Invalid length of self.datasetFrom "+str(len(self.datasetFrom))
            
    
    def hasAllDownloadedFiles(self):
        if isinstance(self.tissues,str):
            self.processTissues()
        for tissueIndex in range(len(self.tissues)):
            tissue = self.tissues[tissueIndex]            
            datasetURL,datasetLocalFile = self.getDownloadInfo(tissueIndex)
            if os.path.isfile(datasetLocalFile):
                self.downloadUrls[tissue] = datasetURL
                self.downloadDate = fileTimeStr(datasetLocalFile)
            else:
                return False
        return True
                
    def hasPreprocessedFile(self):       
#        self.binaryFile = self.getDatasetBinaryName()
#        if not os.path.isfile(self.binaryFile):
#            return False     
        self.binaryFile = self.getBedFile("any")
        for tissue in self.tissues+["any"]:
            if not os.path.isfile(self.getBedFile(tissue)):
                return False
        return True 
            


    

    def cleanup(self,cgsAS):
        #CLEANUP IMPROVE
        annotateFnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".annotated"
        if os.path.isfile(annotateFnBed):
            os.unlink(annotateFnBed)
        for tissue in self.tissues+["any"]:
            closestFnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+"."+tissue+".closest"
            if os.path.isfile(closestFnBed):
                os.unlink(closestFnBed)
        sqlDataFile = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(sqlDataFile):
            os.unlink(sqlDataFile)
#        for tissue in self.intervalArrays.keys(): 
#            self.intervalArrays[tissue].cleanup()
       
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
#        log(self.datasetSimpleName + ": preprocessing the dataset into local database")
#        self.binaryFile = self.getDatasetBinaryName()
        bedFiles = {}
        for tissue in self.tissues+["any"]:
            bedFiles[tissue] = open(self.getBedFile(tissue)+".unsorted","w")
        try:
#            conn = sqlite3.connect(self.binaryFile)
#            c = conn.cursor()
#            c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER,tissueIndex INTEGER)')
#            c.execute('CREATE TABLE '+self.datasetSimpleName+'_tissues(tissueName TEXT, tissueIndex INTEGER)')
#            self.tissueIndeces = {}
#            tissueIndex = 1 
#            for tissue in  self.tissues:
#                self.tissueIndeces[tissue] = tissueIndex                
##                c.execute('INSERT INTO '+self.datasetSimpleName+'_tissues VALUES (?,?)',tuple([tissue,tissueIndex]))                
#                tissueIndex += 1          
            self.chromIndex = int(self.chromIndex)
            self.chromStartIndex = int(self.chromStartIndex)
            self.chromEndIndex = int(self.chromEndIndex)            
            for tissueIndex in range(len(self.tissues)):
                tissue = self.tissues[tissueIndex]             
                datasetURL,datasetLocalFile = self.getDownloadInfo(tissueIndex)
                f = gzip.GzipFile(datasetLocalFile,"rb")
                lines = f.readlines()
                f.close() 
                log(["Preprocessing",self.datasetSimpleName,tissue,len(lines)])               
                for line in lines:
                    line = line.strip().split("\t")
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
                    if self.filterByColumn == -1 or self.filterValue == line[self.filterByColumn]:  
                        bedLine = "\t".join([line[self.chromIndex],line[self.chromStartIndex],line[self.chromEndIndex]])+"\n"
                        bedFiles[tissue].write(bedLine)
                        bedFiles["any"].write(bedLine)                        
                         
#                conn.commit()
               
                
            for tissue in bedFiles.keys():
                bedFiles[tissue].close()
                fileNameOrig = self.getBedFile(tissue)+".unsorted"
                fileNameSorted = self.getBedFile(tissue)+".sorted"
                fileNameMerged = self.getBedFile(tissue)
                subprocess.Popen(settings.bedToolsFolder+"sortBed -i "+fileNameOrig+" > "+fileNameSorted,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
                subprocess.Popen(settings.bedToolsFolder+"mergeBed -i "+fileNameSorted+" > "+fileNameMerged,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
                os.unlink(fileNameOrig)
                os.unlink(fileNameSorted)
                
        except:            
            # if there was exception, delete the database file
#            c.close()
#            conn.close()
#            os.unlink(self.binaryFile)
            raise
            
#        c.close()
#        conn.close()
        log(self.datasetSimpleName + ": the dataset was preprocessed into local DB "+self.binaryFile)

    # This method created the data structure in which the properties will be stored and initiates any suppost structures 
    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):
        #dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT)")
        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, min_distance INTEGER, tissue TEXT)")
        # MOVE_TO_BEDTOOLS END
        fnBed =  getRegionsCollectionName(cgsAS.datasetCollectionName,self.genome)[:-8]+".bed"

        annotateCommand = settings.bedToolsFolder+"annotateBed -i "+fnBed+" -files"   
        annotateFnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".annotated"
        #self.annotateIndeces = {}
        #index = 4
        for tissue in self.tissues+["any"]:            
            #annotateIndeces[tissue] = index
            #index += 1
            annotateCommand += " "+self.getBedFile(tissue)
        annotateCommand += " | "+settings.bedToolsFolder+"sortBed > "+annotateFnBed
        if not os.path.isfile(annotateFnBed):
            log("Before annotate "+str(annotateCommand))
            subprocess.Popen(annotateCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
            log("After annotate")
        ## A PLACE FOR SPEED OPTIMIZATION
        numberOfLines = line_count(annotateFnBed)        
        f = open(annotateFnBed)
        #annotatedData = map(lambda line:line.strip().split("\t"),f.readlines())
        line = f.readline().strip().split("\t")
        f.close()
        annotateIndecesIntegers = self.annotateIndeces.values()
        annoatedDataArray = numpy.zeros((numberOfLines+1,len(line),2),numpy.float32)
        log("annotate data read "+str((numberOfLines+1,len(line),2)))        
        f = open(annotateFnBed)
        for line in f:
            line = line.strip().split("\t")
            for ai in annotateIndecesIntegers:
                 annoatedDataArray[int(line[3])][ai][0] = float(line[ai])            
            ## A PLACE FOR SPEED OPTIMIZATIONcgsAS.featuresDatasets[self.datasetSimpleName]["data"][int(line[3])] = {}
            ## A PLACE FOR SPEED OPTIMIZATIONfor el in annotateIndeces.keys():
            ## A PLACE FOR SPEED OPTIMIZATION    cgsAS.featuresDatasets[self.datasetSimpleName]["data"][int(line[3])][el] = [float(line[annotateIndeces[el]]),0]        
        f.close()
        ##  A PLACE FOR SPEED OPTIMIZATION
        for tissue in self.tissues+["any"]:
            closestFnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+"."+tissue+".closest"
            if not os.path.isfile(closestFnBed):
                closestCommand = settings.bedToolsFolder+"closestBed -a "+fnBed+" -b "+self.getBedFile(tissue)+" -d "+" > "+closestFnBed
                log(closestCommand)        
                subprocess.Popen(closestCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
            ai = self.annotateIndeces[tissue]
            f = open(closestFnBed)
            for rl in f:
                rlParts = rl.strip().split("\t")
                ##  A PLACE FOR SPEED OPTIMIZATION cgsAS.featuresDatasets[self.datasetSimpleName]["data"][int(rlParts[3])][tissue][1] = int(rlParts[-1])
                if int(rlParts[-1]) > -1:
                    annoatedDataArray[int(rlParts[3])][ai][1] = int(rlParts[-1])
                else:
                    annoatedDataArray[int(rlParts[3])][ai][1] = settings.MAX_DISTANCE
            f.close()
        cgsAS.featuresDatasets[self.datasetSimpleName]["data"] = annoatedDataArray
        log("After load annotate")
    
    def initializePropertiesComputeStructures(self):
        pass
#        chromData = {}
#        chromSizes = {}
#        
##INTTREE->INTARRAY        self.intervalTree = IntervalTree.GenomeIntervalTree()
#        conn = sqlite3.connect(self.binaryFile)
#        c = conn.cursor()
#        self.tissueIndeces = {}
#        self.tissueIndecesRev = {}
#        c.execute("SELECT tissueName, tissueIndex FROM "+self.datasetSimpleName+"_tissues")
#        self.intervalArrays["any"] = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName(["any"]),numpy.uint32,2)
#        for rc in c:
#            self.tissueIndeces[rc[0]] = rc[1]
#            self.tissueIndecesRev[rc[1]] = rc[0]
#            self.intervalArrays[rc[0]] = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName([getSafeWord(str(rc[0]))]),numpy.uint32,2)        
#        
#        exist = True
#        for tissue in self.intervalArrays.keys():            
#            if self.intervalArrays[tissue].exist(1) and self.intervalArrays[tissue].exist(5) and self.intervalArrays[tissue].exist(11) and self.intervalArrays[tissue].exist(15):
#                continue
#            else:
#                log(self.datasetSimpleName+" "+tissue+" has no stored computed array for some chromosomes")
#                exist = False
#                break            
#        if exist:
#            log(self.datasetSimpleName+" have stored precomputed arrays")
#            c.close()
#            conn.close()
#            return
#        for tissue in self.tissueIndeces.keys()+["any"]:
#            #start change #1CHR->ALLCHR
#            #log(["Initializing an array for",self.datasetSimpleName,tissue])            
#            if tissue != "any":
#                c.execute("SELECT chrom, start, stop FROM "+self.datasetSimpleName+" WHERE tissueIndex=? ORDER BY chrom,start",tuple([self.tissueIndeces[tissue]]))
#            else:
#                c.execute("SELECT DISTINCT chrom, start, stop FROM "+self.datasetSimpleName+" ORDER BY chrom,start")
#            data = c.fetchall()
#            
#            self.intervalArrays[tissue].loadFullDataSortedbyChrom(data,True)
##            if tissue == "HepG2":
##                print "Size of the last chromosome",len(data),data[-1],self.intervalArrays[tissue].chroms[24]
#            log("Interval array computed for "+tissue)
#            self.intervalArrays[tissue].store()
#            
#            self.intervalArrays[tissue].cleanup()
#            log("Interval array stored for "+tissue)
#        c.close()
#        conn.close()
   
        
    
    
    def computeSingleRegionProperties(self,row, cgsAS):
        results = []
#        isOfType = 0
#        chrom = row[1]
#        start = row[2]
#        stop = row[3]

        for tissue in self.tissues+["any"]:
            tissueIndex = self.annotateIndeces[tissue]
            results.append((row[0], 
                            float(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][tissueIndex][0]), 
                            int(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][tissueIndex][1]),
                            tissue))
#            overlapingRegions = self.intervalArrays[tissue].findTwoDimentionalWithAdditionalInfo(chrom, start, stop)
#            overlap_count = len(overlapingRegions)
#            if overlap_count == 0:
#                distance_upstream_array = self.intervalArrays[tissue].distanceUpstream
#                distance_downstream_array = self.intervalArrays[tissue].distanceDownstream
#                results.append((row[0], 0, 0,distance_upstream_array,distance_downstream_array,tissue))
#                if cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][tissue][0] != 0 or cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][tissue][1] != min(distance_upstream_array,distance_downstream_array):
#                    raise GDMValueException, str(row)+str(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][tissue])+" tissue:"+tissue+" u: "+str(distance_upstream_array)+" d:"+str(distance_downstream_array)
#            else:
#                try:
#                    reducedGR = gr_reduceRegionSet(list(overlapingRegions))
#                except:
#                    log(str(overlapingRegions))
#                    raise
#                overlap_count = len(reducedGR)
#                overlap_ratio = gr_Coverage(reducedGR, start, stop) / float(stop - start)
#                results.append((row[0], overlap_ratio, overlap_count, 0,0, tissue))
#                if numpy.abs(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][tissue][0] - overlap_ratio) > 0.00001 or cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][tissue][1] != 0:
#                    raise GDMValueException, str(row)+str(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][tissue])+" or:"+str(overlap_ratio)
        return results
    
    def getRegions(self):
        return self.getRegionsFromLocalBED(self.getBedFile("any")) 
    
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
        #regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT
        # uw_dnaseI [1, 0.0, 0, 18268, 205787, u'all']
#        print self.datasetSimpleName, list(result)
        regionData = []
        regionDataWithScores = [] 
        #print self.datasetSimpleName,str(result)                
        if result[1] > 0:
            # indicates that the regions overlaps with DNaseI hypersensitive site
            regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName,str(result[3])])            
            if result[1] > 0.1:
                regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName,str(result[3])])
            if result[1] > 0.5:
                regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName,str(result[3])])
                
            regionData.append([settings.wordPrefixes["overlapRatio"],self.datasetWordName,str(result[3]),wordFloat(result[1],2)])            
#            regionData.append(["oc","DNaseI",str(result[5]),str(result[2])])            
        else:
            #the region does not overlap with a site, report distance to the nearest
            md  = wordMagnitude(result[2])
            regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(result[3]),md])
            
        return regionData,regionDataWithScores
    
    def getWordPrefixes(self,cgsAS):
        return [settings.wordPrefixes["overlap"],
                settings.wordPrefixes["overlap10p"],
                settings.wordPrefixes["overlap50p"],
                settings.wordPrefixes["overlapRatio"],
                settings.wordPrefixes["minimumDistance"]]
        
    
    def getWordsDescription(self):
        doc = []
        doc.append(["overlaps:DNaseI:all","Overlaps with DNaseI hypersensitive site measured in any tissue",["overlaps:DNaseI:","overlaps:DNaseI:all"]+["overlaps:DNaseI:"+t for t in self.tissues]])
        doc.append(["or:DNaseI:all:77","Overlaps 77% with DNaseI hypersensitive site measured in any tissue",["or:DNaseI:","or:DNaseI:all:"]+["or:DNaseI:"+t+":" for t in self.tissues]])
#        doc.append(["oc:DNaseI:all:2","Overlaps with 2 DNaseI hypersensitive sites measured in any tissue",["oc:DNaseI:","oc:DNaseI:all:"]+["oc:DNaseI:"+t+":" for t in self.tissues]])
#        doc.append(["mdd:DNaseI:34","Measures the magnitude of the distance (between 10^3*4 and 10^3 *5) to the nearest hypersensitive site downstream",["mdd:DNaseI:"]])
#        doc.append(["mud:DNaseI:34","Measures the magnitude of the distance (between 10^3*4 and 10^3 *5) to the nearest hypersensitive site upstream",["mud:DNaseI:"]])
        doc.append(["mmd:DNaseI:34","Measures the magnitude of the distance (between 10^3*4 and 10^3 *5) to the nearest hypersensitive site",["mmd:DNaseI:"]])  
        return doc
    
    def getDefaultAnnotationSettings(self):        
        # obtain the default settings
        settings = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settings["hasGenomicRegions"] = self.hasGenomicRegions
        settings["hasFeatures"] = self.hasFeatures
        settings["data"] = {}
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
        featureWords.append(categoriesPath+["OVERLAP:"+self.datasetWordName+"::"+"Eor:"+self.datasetWordName+":POS2SOP::2::0"])  
        featureWords.append(categoriesPath+["_OVERLAP:"+self.datasetWordName])
        for tissue in self.tissues+["any"]:
            featureWords.append(categoriesPath+["distanceTo"]+["Emmd:"+self.datasetWordName+":"+tissue+"::2::0"])                
        return featureWords 
    
    def getBedFile(self,tissue):
        return settings.rawDataFolder[self.genome]+self.datasetSimpleName+"_"+tissue+".bed"
            
    def calculateCoverages(self):        
        print "Calculating coverage:"
        for tissue in self.tissues+["any"]:
            data =  self.getRegionsFromLocalBED(self.getBedFile(tissue))
            coverage = self.calculateCoverage(numpy.asarray(data))
            self.coverages[tissue] = coverage

    def getOverlappingText(self):
        return self.datasetWordName
    
    def getSubAnnotations(self):
        return self.tissues + ["any"]
