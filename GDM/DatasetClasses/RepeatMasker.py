
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
import subprocess
#import cPickle
#import cx_Oracle

class RepeatMasker(Dataset.Dataset):
        
    def init(self,initCompute=True):        
        self.repeatClasses = {}
        self.repeatClassesRev = {}
        self.repeatClassesMax = 0        
        self.repeatFamilies = {}
        self.repeatFamiliesMax = 0
        self.intervalArrays = {}       
        Dataset.Dataset.init(self,initCompute)
        self.regionsCountMod = 100000
        self.binaryFile = self.getDatasetBinaryName()
        self.initialized = True
        self.annotateIndeces = {}
    
    def hasPreprocessedFile(self):       
        self.binaryFile = self.getDatasetBinaryName()
        if not os.path.isfile(self.binaryFile):
            return False      
        if not os.path.isfile(self.getBedFile("any","any")):
            return False
        #what to do if the data was already preprocessed
        if not hasattr(self, "bedFilesRaw"):
            self.bedFilesRaw = {}
            conn = sqlite3.connect(self.binaryFile)
            c = conn.cursor()
            c.execute('SELECT repeatClass FROM '+self.datasetSimpleName+'_class')
            self.bedFilesRaw = {"any":{"any":self.getBedFile("any","any")}}
            for r in c:
                rc = str(r[0])
                self.bedFilesRaw[rc] = {}
                if os.path.isfile(self.getBedFile(rc,"any")):
                    self.bedFilesRaw[rc]["any"] = self.getBedFile(rc,"any")
        return True   
     
    def getBedFile(self,repeatClass,repeatFamily):
        return settings.rawDataFolder[self.genome]+self.datasetSimpleName+"_"+repeatClass+"_"+repeatFamily+".bed"
    
    def preprocessDownloadedDataset(self):
        if not self.hasAllDownloadedFiles():
           exText = self.datasetSimpleName + ": the dataset files are not downloadeded "
           log(exText)
           raise GDMException, exText
        if self.hasPreprocessedFile():
            extext = self.datasetSimpleName + ": the dataset was already preprocessed in "+self.getBedFile("any","any")
            log(extext)
#            c.execute('SELECT repeatFamily FROM '+self.datasetSimpleName+'_family')
#            for r in c:
#                rf = str(r[0])
#                for rc in self.bedFilesRaw.keys():
#                    if os.path.isfile(self.getBedFile(rc,rf)):
#                        self.bedFilesRaw[rc][rf] = self.getBedFile(rc,rf)
#            log(str(self.bedFilesRaw))                    
            return
        log(self.datasetSimpleName + ": preprocessing the dataset into local database")
        self.binaryFile = self.getDatasetBinaryName()
        try:
            conn = sqlite3.connect(self.binaryFile)
            c = conn.cursor()
# MOVE_TO_BEDTOOLS START                    c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER, repeatClass INTEGER, repeatFamily INTEGER)')
            c.execute('CREATE TABLE '+self.datasetSimpleName+'_family(repeatFamily TEXT, id INTEGER)')
            c.execute('CREATE TABLE '+self.datasetSimpleName+'_class(repeatClass TEXT, id INTEGER)')
            self.chromIndex = int(self.chromIndex)
            self.chromStartIndex = int(self.chromStartIndex)
            self.chromEndIndex = int(self.chromEndIndex)
            self.repeatClass = int(self.repeatClass)
            self.repeatFamily = int(self.repeatFamily)
            repeatFamilies = {}
            repFamiliesIndex = 1
            repeatClasses = {}
            repClassesIndex = 1
            bedFiles = {}
            self.bedFilesRaw = {}
            processedLocalFiles = {}
            for chr in settings.genomeDataStr[self.genome].keys():            
                datasetURL,datasetLocalFile = self.getDownloadInfo(chr)
                if processedLocalFiles.has_key(datasetLocalFile):
                    continue
                else:
                    processedLocalFiles[datasetLocalFile] = True                
                f = gzip.GzipFile(datasetLocalFile,"rb")                
                lines = f.readlines()                
                for line in lines:
                    line = line.strip().split("\t")
                    try:
                        chrom = convertChromToInt(self.genome,line[self.chromIndex])
                    except GDMException, ex:
                        if "_random" in line[self.chromIndex] or "hap" in line[self.chromIndex] or "chrM" in line[self.chromIndex] or "chrUn" in line[self.chromIndex]:
                            continue
                        else:
                            raise ex
                    repFamily = getSafeWord(line[self.repeatFamily])
                    if not repeatFamilies.has_key(repFamily):                        
                        repeatFamilies[repFamily] = repFamiliesIndex
                        c.execute('INSERT INTO '+self.datasetSimpleName+'_family VALUES (?,?)',tuple([repFamily,repFamiliesIndex]))
                        repFamiliesIndex += 1
                    repClass = getSafeWord(line[self.repeatClass])
                    if not repeatClasses.has_key(repClass):
                        repeatClasses[repClass] = repClassesIndex
                        c.execute('INSERT INTO '+self.datasetSimpleName+'_class VALUES (?,?)',tuple([repClass,repClassesIndex]))
                        repClassesIndex += 1
                    # MOVE_TO_BEDTOOLS START        
#                    c.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?,?,?,?,?)',
#                               tuple([chrom,
#                                      int(line[self.chromStartIndex]),
#                                      int(line[self.chromEndIndex]),
#                                      repeatClasses[repClass],
#                                      repeatFamilies[repFamily]
#                                      ]))
                    # MOVE_TO_BEDTOOLS EDN        
# MOVE_TO_BEDTOOLS EDN                    for fileIDs in [(repClass,repFamily),(repClass,"any"),("any","any")]:
                    for fileIDs in [(repClass,"any"),("any","any")]:
                        fileID = "_".join(fileIDs)
                        try:
                            bedFiles[fileID].write("\t".join([line[self.chromIndex],line[self.chromStartIndex],line[self.chromEndIndex]])+"\n")
                        except:
                            if not bedFiles.has_key(fileID):
                                bedFiles[fileID] = open(self.getBedFile(fileIDs[0], fileIDs[1])+".unsorted","w")
                                if not self.bedFilesRaw.has_key(fileIDs[0]):
                                    self.bedFilesRaw[fileIDs[0]] = {}
                                if not self.bedFilesRaw[fileIDs[0]].has_key(fileIDs[1]):
                                    self.bedFilesRaw[fileIDs[0]][fileIDs[1]] = self.getBedFile(fileIDs[0], fileIDs[1])
                                bedFiles[fileID].write("\t".join([line[self.chromIndex],line[self.chromStartIndex],line[self.chromEndIndex]])+"\n")
                            else:
                                raise         
                            
                conn.commit()
                f.close()   
                
            for fid in bedFiles.keys():
                bedFiles[fid].close()
                fileNameOrig = settings.rawDataFolder[self.genome]+self.datasetSimpleName+"_"+fid+".bed.unsorted"
                fileNameMerged = settings.rawDataFolder[self.genome]+self.datasetSimpleName+"_"+fid+".bed"
                fileNameSorted = settings.rawDataFolder[self.genome]+self.datasetSimpleName+"_"+fid+".bed.sorted"                
                print fid
                subprocess.Popen(settings.bedToolsFolder+"sortBed -i "+fileNameOrig+" > "+fileNameSorted,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
                subprocess.Popen(settings.bedToolsFolder+"mergeBed -i "+fileNameSorted+" > "+fileNameMerged,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
                os.unlink(fileNameOrig)
                os.unlink(fileNameSorted)              
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
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()        
        c.execute("SELECT repeatFamily, id FROM "+self.datasetSimpleName+"_family")
        for rc in c:
            self.repeatFamilies[rc[0]] = rc[1]
#        #print self.repeatFamilies            
        c.execute("SELECT repeatClass, id FROM "+self.datasetSimpleName+"_class")
        for rc in c:
            self.repeatClasses[rc[0]] = rc[1]
            self.repeatClassesRev[rc[1]] = rc[0]
        c.close()
        conn.close()
            
    def getRegions(self):
        return self.getRegionsFromLocalBED(self.getBedFile("any","any")) 
    
    # This method created the data structure in which the properties will be stored and initiates any suppost structures
     
    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):
        # MOVE_TO_BEDTOOLS START
#        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, class TEXT, family TEXT)")
        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, class TEXT)")
        # MOVE_TO_BEDTOOLS END
        fnBed =  getRegionsCollectionName(cgsAS.datasetCollectionName,self.genome)[:-8]+".bed"

        annotateCommand = settings.bedToolsFolder+"annotateBed -i "+fnBed+" -files"   
        annotateFnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".annotated"
        self.annotateIndeces = {}
        # The starting index for th e tissues in the result annotated file
        # the previous indeces are chrom, start,end, id, score,strand
        index = 6
        for repClass in self.bedFilesRaw.keys():
            repFamily = "any"
#            for repFamily in self.bedFilesRaw[repClass]:                
#            annotateIndeces[repClass+"_"+repFamily] = index
            self.annotateIndeces[repClass] = index
            index += 1
            annotateCommand += " "+settings.rawDataFolder[self.genome]+self.datasetSimpleName+"_"+repClass+"_"+repFamily+".bed"
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
        annoatedDataArray = numpy.zeros((numberOfLines+1,len(line)),numpy.float32)        
        f = open(annotateFnBed)
        #annotatedData = map(lambda line:line.strip().split("\t"),f.readlines())
        for line in f:  
            line = line.strip().split("\t")          
            #cgsAS.featuresDatasets[self.datasetSimpleName]["data"][int(line[3])] = {}
            for ai in annotateIndecesIntegers:                
                #cgsAS.featuresDatasets[self.datasetSimpleName]["data"][int(line[3])][el] = float(line[annotateIndeces[el]])
                annoatedDataArray[int(line[3])][ai] = float(line[ai])
        f.close()
        cgsAS.featuresDatasets[self.datasetSimpleName]["data"] = annoatedDataArray
        log("After load annotate")
        
        
    
    # computed the properties for this daset for the given region and stores them in the properties structure
    # @return: this method should not return the properties but store them
    def computeSingleRegionProperties(self, row, cgsAS):
        results = []
        # MOVE_TO_BEDTOOLS START
#        isOfType = 0
#        chrom = row[1]
#        start = row[2]
#        stop = row[3]
#        for repeatClass in self.repeatClasses.keys()+["any"]:
#            overlapingRegions = self.intervalArrays[repeatClass].findTwoDimentionalWithAdditionalInfo(chrom, start, stop)
#            overlap_count = len(overlapingRegions)
#            if overlap_count == 0:
#                if repeatClass == "any":
#                    results.append((row[0], 0, 0,repeatClass,""))
##                if float(self.annotatedData[row[0]][self.annotateIndeces[repeatClass+"_any"]]) != 0:
##                    raise GDMValueException, str(row)+str(self.annotatedData[row[0]])+str(repeatClass)+str(self.annotateIndeces[repeatClass+"_any"])+str(self.annotateIndeces)
#            else:
##                repeatClassRanges = {"any":range(overlap_count)}
##                for i in range(len(overlapingRegionsInterval)):
##                    if not repeatClassRanges.has_key(self.repeatClassesRev[overlapingRegionsInterval[i,2]]):
##                        repeatClassRanges[self.repeatClassesRev[overlapingRegionsInterval[i,2]]] = []
##                    repeatClassRanges[self.repeatClassesRev[overlapingRegionsInterval[i,2]]].append(i)
##            for repeatClass in repeatClassRanges.keys():
#                reducedGR = gr_reduceRegionSet(list(overlapingRegions))
#                overlap_count = len(overlapingRegions)
#                overlap_ratio = gr_Coverage(reducedGR, start, stop) / float(stop - start)
#                results.append((row[0], overlap_ratio, overlap_count, repeatClass, ""))
##                if numpy.abs(float(self.annotatedData[row[0]][self.annotateIndeces[repeatClass+"_any"]]) - float(overlap_ratio)) > 0.00001:
##                    raise GDMValueException, str(row)+str(self.annotatedData[row[0]])+str(self.annotatedData[self.annotateIndeces[repeatClass+"_any"]])+str(repeatClass)+str(overlap_ratio)+str(reducedGR)+str(self.annotateIndeces)
        #for repeatClass in cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]].keys():
        for repeatClass in self.annotateIndeces.keys():
            aiRepeatClass = self.annotateIndeces[repeatClass]
            if float(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][aiRepeatClass]) > 0:
                results.append([row[0], float(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][aiRepeatClass]), repeatClass])
#                print [row[0], cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][repeatClass], repeatClass]            
            
        return results
#               
    def cleanup(self,cgsAS):
        #CLEANUP IMPROVE
        annotateFnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".annotated"
        if os.path.isfile(annotateFnBed):
            os.unlink(annotateFnBed)
               
        sqlite3Data = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(sqlite3Data):
            os.unlink(sqlite3Data)
#        for key in self.intervalArrays.keys():             
#            self.intervalArrays[key].cleanup()
        
          
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
        # MOVE_TO_BEDTOOLS START    
        #regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, class TEXT, family TEXT
        #regionID INTEGER, overlap_ratio REAL, class TEXT
        # MOVE_TO_BEDTOOLS END    
        # currently the family is not used        
        regionData = []
        regionDataWithScores = [] 
        #print self.datasetSimpleName,str(result)                
        if result[1] > 0:
            regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName,str(result[2])])
            if result[1] >= 0.1:
                regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName,str(result[2])])
            if result[1] >= 0.5:
                regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName,str(result[2])])
                
            # store the overlap ratio as score            
            regionData.append([settings.wordPrefixes["overlapRatio"],self.datasetWordName,str(result[2]),wordFloat(result[1],2)])
            # add one more score aobut the number of chrom mod regions overlapping
# MOVE_TO_BEDTOOLS START                regionData.append([settings.wordPrefixes["overlapCount"],self.datasetWordName,str(result[3]),str(result[2])])
#        else:            
#            regionData.append(["rpn"])
        return regionData,regionDataWithScores
    
    def getWordPrefixes(self,cgsAS):
        return [settings.wordPrefixes["overlap"],
                settings.wordPrefixes["overlap10p"],
                settings.wordPrefixes["overlap50p"],
                settings.wordPrefixes["overlapRatio"],
#                settings.wordPrefixes["overlapCount"]# MOVE_TO_BEDTOOLS START    
                ]
    
    def getWordsDescription(self):
        doc = []
        doc.append(["overlaps:repeats:SINE","Overlaps with SINE repeats",["overlaps:repeats:","overlaps:repeats:all"]+["overlaps:repeats:"+rc for rc in self.repeatClasses.keys()]])
        doc.append(["or:repeats:SINE:05","Indicates that 5% of this region is covered by SINE repeats",["or:repeats:","or:repeats:all"]+["or:repeats:"+rc+":" for rc in self.repeatClasses.keys()]])
        doc.append(["oc:repeats:SINE:3","Indicates that there were 3 SINE repeats overlapping with this region",["oc:repeats:","oc:repeats:all"]+["oc:repeats:"+rc+":" for rc in self.repeatClasses.keys()]])        
        return doc
    
    def getDownloadInfo(self,chr):
        datasetURL = self.datasetFrom.replace("CHR",chr)
        #print datasetURL                
        downloadedLastPart = os.path.basename(datasetURL)
        datasetLocalFile = os.path.abspath(settings.downloadDataFolder[self.genome] + downloadedLastPart)
        return datasetURL,datasetLocalFile
    
    def downloadDataset(self):
        for chr in settings.genomeDataStr[self.genome].keys():            
            datasetURL,datasetLocalFile = self.getDownloadInfo(chr)
            if not os.path.isfile(datasetLocalFile):        
                downloadFile(datasetURL, datasetLocalFile)
                self.downloadUrls[chr] = datasetURL
                self.downloadDate = fileTimeStr(datasetLocalFile)
                log(self.datasetSimpleName + ": file " + str(os.path.basename(datasetLocalFile) + " was downloaded"))
            else:
                log(self.datasetSimpleName + ": file " + str(os.path.basename(datasetLocalFile) + " exists"))
            self.downloadUrls[chr] = datasetURL
            self.downloadDate = fileTimeStr(datasetLocalFile)
        
    
    def hasAllDownloadedFiles(self):
        for chr in settings.genomeDataStr[self.genome].keys():            
            datasetURL,datasetLocalFile = self.getDownloadInfo(chr)
            if os.path.isfile(datasetLocalFile):
                self.downloadUrls[chr] = datasetURL
                self.downloadDate = fileTimeStr(datasetLocalFile)
            else:
                return False
        return True
    
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
        return featureWords 
                    
    def calculateCoverages(self):        
        for c in self.repeatClasses.keys()+["any"]:
            data =  self.getRegionsFromLocalBED(self.getBedFile(c, "any"))
            coverage = self.calculateCoverage(numpy.asarray(data))
            self.coverages[c] = coverage

    def getOverlappingText(self):
        return self.datasetWordName;
    
    def getSubAnnotations(self):
        return self.repeatClasses.keys()+["any"]
