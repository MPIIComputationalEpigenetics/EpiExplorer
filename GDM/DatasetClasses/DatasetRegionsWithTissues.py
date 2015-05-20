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
        bedFiles = {}
        for tissue in self.tissues+["any"]:
            bedFiles[tissue] = open(self.getBedFile(tissue)+".unsorted","w")
        try:
            self.chromIndex = int(self.chromIndex)
            self.chromStartIndex = int(self.chromStartIndex)
            self.chromEndIndex = int(self.chromEndIndex)

            for tissueIndex in range(len(self.tissues)):
                tissue = self.tissues[tissueIndex]
                datasetURL,datasetLocalFile = self.getDownloadInfo(tissueIndex)
                f = gzip.GzipFile(datasetLocalFile, "rb")
                lines = f.readlines()
                f.close()
                log("Preprocessing " + str(len(lines)) + " " + tissue + " features")

                for line in lines:
                    line = line.strip().split("\t")

                    try:
                        chrom = convertChromToInt(self.genome, line[self.chromIndex])
                    except:
                        if line[self.chromIndex] in ["_random", "chrM", "hap"]:
                            continue
                        elif line[self.chromIndex].startswith("chrUn"):
                            continue
                        else:
                            raise

                    if self.filterByColumn == -1 or (self.filterValue == line[self.filterByColumn]):
                        bedLine = "\t".join([line[self.chromIndex],
                                             line[self.chromStartIndex],
                                             line[self.chromEndIndex]]) + "\n"
                        bedFiles[tissue].write(bedLine)
                        bedFiles["any"].write(bedLine)

#                conn.commit()


            for tissue in bedFiles.keys():
                bedFiles[tissue].close()
                fileNameOrig = self.getBedFile(tissue)+".unsorted"
                fileNameSorted = self.getBedFile(tissue)+".sorted"
                fileNameMerged = self.getBedFile(tissue)
                subprocess.Popen(settings.bedToolsFolder+"sortBed -i "+fileNameOrig+" > "+fileNameSorted,
                                 shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                subprocess.Popen(settings.bedToolsFolder+"mergeBed -i "+fileNameSorted+" > "+fileNameMerged,
                                 shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

                # Error catching is not working here, sorted file is not being written in some circumstances
                # (reserved/meta characters in file name)
                # Hence the unlink fails below to remove it
                # The unsorted file is also removed, so hard to investigate without hacking the code
                os.unlink(fileNameOrig)
                os.unlink(fileNameSorted)

        except:
            raise

        log(self.datasetSimpleName + ": the dataset was preprocessed into local DB "+self.binaryFile)

    # This method created the data structure in which the properties will be stored and initiates any suppose structures
    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):
        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, min_distance INTEGER, tissue TEXT)")
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

    def computeSingleRegionProperties(self,row, cgsAS):
        results = []

        for tissue in self.tissues+["any"]:
            tissueIndex = self.annotateIndeces[tissue]
            results.append((row[0],
                            float(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][tissueIndex][0]),
                            int(cgsAS.featuresDatasets[self.datasetSimpleName]["data"][row[0]][tissueIndex][1]),
                            tissue))

        return results

    def getRegions(self):
        return self.getRegionsFromLocalBED(self.getBedFile("any"))

    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
        #regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, tissue TEXT
        # uw_dnaseI [1, 0.0, 0, 18268, 205787, u'all']
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
        doc.append(["mmd:DNaseI:34","Measures the magnitude of the distance (between 10^3*4 and 10^3 *5) to the nearest hypersensitive site",["mmd:DNaseI:"]])
        return doc

    def getDefaultAnnotationSettings(self):
        # obtain the default settings
        settings = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type
        settings["hasGenomicRegions"] = self.hasGenomicRegions
        settings["hasFeatures"] = self.hasFeatures
        settings["data"] = {}
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
        for tissue in self.tissues+["any"]:
            log("Calculating coverages for:\t" + self.getBedFile(tissue))
            data =  self.getRegionsFromLocalBED(self.getBedFile(tissue))
            coverage = self.calculateCoverage(numpy.asarray(data))
            self.coverages[tissue] = coverage

    def getOverlappingText(self):
        return self.datasetWordName

    def getSubAnnotations(self):
        return self.tissues + ["any"]
