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

class Conservation(Dataset.Dataset):

    def init(self,initCompute=True):
        Dataset.Dataset.init(self,initCompute)
        self.combineMultipleConsScores = max
        self.initialized = True

    def downloadDataset(self):
       self.__downloadSingleFileDataset__()

    def hasAllDownloadedFiles(self):
       return self.__hasSingleDownloadedFile__()

    def getDatasetLocalFile(self):
       return self.__getDatasetSingleLocalFile__()

    def preprocessDownloadedDataset(self):
        print "preprocessDownloadedDataset"
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
        # MOVE_TO_BEDTOOLS START
#        log("start preprocessing "+self.datasetSimpleName)
#        self.combineMultipleConsScores = max

#        if datasetLocalFile.endswith(".gz"):
#            f = gzip.GzipFile(datasetLocalFile,"rb")
#        else:
#            raise GDMException, "unsupported file extension for "+datasetLocalFile
#        import dataset_methods
#        ds = dataset_methods.readDatasetFromFileObject(f,self.genome,
#                                                       int(self.chromIndex),
#                                                       int(self.chromStartIndex),
#                                                       int(self.chromEndIndex),
#                                                       [int(self.scoreIndeces)])
#
#        log(self.datasetSimpleName + " was read. "+str(len(ds))+" lines")
#        f.close()
#        # check if there is some region filtering that should be done
#        if self.regionsFiltering:
#            regionsFilters = self.regionsFiltering.split(",")
#            for fil in regionsFilters:
#                fil = fil.strip()
#                if fil == "combineOverlaps":
#                    ds = dataset_methods.mergeOverlappingMax(ds,self.combineMultipleConsScores)
#                    log(self.datasetSimpleName + " was merged for overlaps")
#                else:
#                    extext = fil+" not implemented"
#                    log(extext)
#                    raise GDMException, extext
#
#        #dataset_methods.defaultFolder = "D:/Projects/Integrated_Genome_Profile_Search_Engine/Cosgen/Datasets/hg18_RawDatasets/"
#        #dataset_methods.saveDataset(ds,"test",False)
#        # now save the dataset into a local database
#        self.__init_conservation_regions_dataset_for_local_db__(ds)
        # MOVE_TO_BEDTOOLS END

        print "--" * 20

        log(self.datasetSimpleName+" bed preprocessing start")

        sortedBedName = self.getBedFile()+".sorted"
        plainBedName = self.getBedFile()+".plain"
        print "BED FILE", self.getBedFile()
        if not os.path.isfile(sortedBedName) and not os.path.isfile(self.getBedFile()):
            print "aaa" , datasetLocalFile
            f = gzip.GzipFile(datasetLocalFile,"rb")
            fBed = open(plainBedName,"w")
            ci = int(self.chromIndex)
            csi = int(self.chromStartIndex)
            cei = int(self.chromEndIndex)
            for fl in f:
                flParts = fl.strip().split("\t")
                fBed.write("\t".join([flParts[ci],flParts[csi],flParts[cei]])+"\n")
            f.close()
            fBed.close()
            subprocess.Popen(settings.bedToolsFolder+"sortBed -i "+plainBedName+" > "+sortedBedName,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()

        if not os.path.isfile(self.getBedFile()):
            subprocess.Popen(settings.bedToolsFolder+"mergeBed -i "+sortedBedName+" > "+self.getBedFile(),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        log(self.datasetSimpleName+" bed preprocessing end")


    def getRegions(self):
        return self.getRegionsFromLocalBED(self.getBedFile())

    def __init_conservation_regions_dataset_for_local_db__(self,ds):
        log(self.datasetSimpleName + ": initializing conservation regions local db ")
        self.binaryFile = self.getDatasetBinaryName()
        if self.hasPreprocessedFile():
            #what to do if the data was already preprocessed
            extext = self.datasetSimpleName + ": the regions database already exists "+self.binaryFile
            log(extext)
            return
            raise GDMException, extext
        log(self.datasetSimpleName + ": preprocessing the dataset into local database")
        try:
            conn = sqlite3.connect(self.binaryFile)
            c = conn.cursor()
            c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER, consScore INTEGER)')
    #        rawDataFile = open(self.datasetRawData)
    #        rawDataFile.readline()
    #        line = rawDataFile.readline()
            for lineParts in ds:
    #            lineParts = line.strip().split("\t")
                lineParts[0] = convertChromToInt(self.genome,lineParts[0])
                lineParts[1] = int(lineParts[1])
                lineParts[2] = int(lineParts[2])
                lineParts[3] = int(lineParts[3])
                c.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?,?,?,?)',tuple(lineParts[:4]))
    #            line = rawDataFile.readline()
    #        rawDataFile.close()
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

    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):
        # MOVE_TO_BEDTOOLS START
#        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER,consScore INTEGER, isOfType INTEGER)")
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
            if int(rlParts[-1]) > -1 :
                cgsAS.featuresDatasets[self.datasetSimpleName]["data"][int(rlParts[3])][1] = int(rlParts[-1])
            else:
                cgsAS.featuresDatasets[self.datasetSimpleName]["data"][int(rlParts[3])][1] = settings.MAX_DISTANCE
        f.close()
        log("After annotate with bed")

    def initializePropertiesComputeStructures(self):
        # MOVE_TO_BEDTOOLS START
#        log(self.datasetSimpleName+": Computing interval array")
#        self.intervalArray = IntervalArray.GenomeIntervalArray(self.getIntervalArraybaseName([]),numpy.uint32,3)
#        if self.intervalArray.exist(1) and self.intervalArray.exist(5) and self.intervalArray.exist(11) and self.intervalArray.exist(15):
#            log(self.datasetSimpleName+" intervalArray already exists")
#            return
#
#        connFeatureRegions = sqlite3.connect(self.binaryFile)
#        cFR = connFeatureRegions.cursor()
#        for chr in settings.genomeDataStr[self.genome].keys():
#           #log(["Initializing array ",chr])
#           chrInt = convertChromToInt(self.genome,chr)
#           cFR.execute("SELECT start,stop,consScore FROM "+self.datasetSimpleName+" WHERE chrom=? ORDER BY start",tuple([chrInt]))
#           data = cFR.fetchall()
#           if len(data):
#               self.intervalArray.addChromosomeArray(chrInt,data,True)
##        currentChrom = None
##        datasetRegions = []
##        for row in cFR:
##            d = list(row)
##            if currentChrom != d[0]:
##                if currentChrom == None:
##                    currentChrom = d[0]
##                else:
##                    self.intervalArray.addChromosomeArray(currentChrom,datasetRegions,True)
##                    log([self.datasetSimpleName,currentChrom,len(datasetRegions)])
##                    datasetRegions = []
##                    currentChrom = d[0]
##            datasetRegions.append(d[1:])
##        self.intervalArray.addChromosomeArray(currentChrom,datasetRegions,True)
##        log([self.datasetSimpleName,currentChrom,len(datasetRegions)])
#        cFR.close()
#        connFeatureRegions.close()
#        log(self.datasetSimpleName+" interval array computed")
#        self.intervalArray.store()
#
#        self.intervalArray.cleanup()
#        log(self.datasetSimpleName+" interval array stored")
        pass
        # MOVE_TO_BEDTOOLS END


    def computeSingleRegionProperties(self,   row, cgsAS):
        # regionID, overlap_ratio, overlap_count, distance_upstream ,distance_downstream, isOfType
#        isOfType = 0
#        # MOVE_TO_BEDTOOLS START
#        chrom = row[1]
#        start = row[2]
#        stop = row[3]
#        overlapingRegionsInterval = self.intervalArray.findTwoDimentionalWithAdditionalInfo(chrom, start, stop)
#        if len(overlapingRegionsInterval) > 0:
#            overlap_count = len(overlapingRegionsInterval)
#            consScore = self.combineMultipleConsScores(map(lambda x:x[2],overlapingRegionsInterval))
#            reducedGR = gr_reduceRegionSet(list(overlapingRegionsInterval))
#
#            overlap_ratio = gr_Coverage(reducedGR, start, stop) / float(stop - start)
#            distance_upstream = 0
#            distance_downstream = 0
##            if numpy.abs(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][0] - overlap_ratio) > 0.00001 or self.bedData[row[0]][1] != 0:
##                raise GDMValueException, str(row)+str(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]])+" or:"+str(overlap_ratio)
#        else:
#            overlap_ratio = 0
#            overlap_count = 0
#            consScore = 0
#            distance_upstream = self.intervalArray.distanceUpstream
#            distance_downstream = self.intervalArray.distanceDownstream
##            if cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][0] != 0 or cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][1] != min(distance_upstream,distance_downstream):
##                raise GDMValueException, str(row)+str(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]])+"u: "+str(distance_upstream)+" d:"+str(distance_downstream)
#        return [(row[0], float(overlap_ratio), distance_upstream, distance_downstream, int(consScore), isOfType)]
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




#       self.intervalArray.cleanup()


    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
        # MOVE_TO_BEDTOOLS START
        # regionID, overlap_ratio, overlap_count, distance_upstream, distance_downstream,consScore, isOfType
        #conservation , [1, 0.095055710306406679, 4, 0, 0, 564, 0]
        # regionID, overlap_ratio, min_distance
        #conservation , [1, 0.095055710306406679, 0]

        # MOVE_TO_BEDTOOLS END
        regionData = []
        regionDataWithScores = []
        #print self.datasetSimpleName,str(result)
        if result[2] == 0: # MOVE_TO_BEDTOOLS

            # the region overlaps with conserved regions
            regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName])
            if result[1] >= 0.1:
                 regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName])
            if result[1] >= 0.5:
                 regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName])

            #score overlap ratio between 00--99
            regionData.append([settings.wordPrefixes["overlapRatio"],self.datasetWordName,wordFloat(result[1],2)])
            #score overlap count an integer score
#            regionData.append(["oc","conservation",result[2]])
            #score overlap count maximum conservation score of the overlapping regions
#            regionData.append(["consosc",result[2]])
        else:
            # MOVE_TO_BEDTOOLS START
#            if result[3] < settings.MAX_DISTANCE:# MOVE_TO_BEDTOOLS
#                # score to indicate the distance upstream to the nearest region of this type
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
#                # the magnitude of the distance upstream to the nearest such region
#                md = wordMagnitude(result[4])
#                regionData.append([settings.wordPrefixes["minimumDistanceDownstream"],self.datasetWordName,str(md)])
##           # score to indicate the distance to the nearest region of this type
#            if result[3] < result[4]:
#                # the magnitude of the distance upstream to the nearest such region
#                regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(mu)])
#            elif result[4] < result[3]:
#                regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(md)])
#            elif result[3] < settings.MAX_DISTANCE:
#                regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(mu)])
            # MOVE_TO_BEDTOOLS END
            md = wordMagnitude(result[2])
            regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,str(md)])
#
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
        doc.append(["overlaps:conserved","Indicates that the region overlaps with conserved elements",["overlaps:conserved"]])
        doc.append(["or:conservation:55","Indicates that the region overlaps 55% with conserved elements",["or:conservation:"]])
#        doc.append(["oc:conservation:3","Indicates that the region overlaps  with 3 conserved elements",[]])
#        doc.append(["mud:conservation:45","Indicates that the region is within 10^4*5 and 10^4*6 from the nearest conserved region upstream",["mud:conservation:"]])
#        doc.append(["mdd:conservation:45","Indicates that the region is within 10^4*5 and 10^4*6 from the nearest conserved region downstream",["mdd:conservation:"]])
        doc.append(["mmd:conservation:45","Indicates that the region is within 10^4*5 and 10^4*6 from the nearest conserved region",["mmd:conservation:"]])

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
        featureWords.append(categoriesPath+["OVERLAP:"+self.datasetWordName+"::"+"Eor:"+self.datasetWordName+"::2::0"])
        featureWords.append(categoriesPath+["_OVERLAP:"+self.datasetWordName])
        #DISTANCE_DOWNSTREAM_UPSTREAM_OFF
#        featureWords.append(categoriesPath+["distanceTo"]+["Emdd:"+self.datasetWordName+"::2::0"])
#        featureWords.append(categoriesPath+["distanceTo"]+["Emud:"+self.datasetWordName+"::2::0"])
        featureWords.append(categoriesPath+["Emmd:"+self.datasetWordName+"::2::0"])
        return featureWords


    def hasPreprocessedFile(self):
#        self.binaryFile = self.getDatasetBinaryName()
#        if not os.path.isfile(self.binaryFile):
#            return False
        self.binaryFile = self.getBedFile()
        if not os.path.isfile(self.getBedFile()):
            return False
        return True

    def getBedFile(self):
        return settings.rawDataFolder[self.genome]+self.datasetSimpleName+".bed"

    def calculateCoverages(self):
        data = self.getRegions()
        self.coverages["any"] = self.calculateCoverage(data)

    def getOverlappingText(self):
        return [self.datasetWordName]

    def getSubAnnotations(self):
        return ["any"]