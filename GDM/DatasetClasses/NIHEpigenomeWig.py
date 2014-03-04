# the regions are stored in a local file DB and the search structure is inteval tree
import os
import os.path
import numpy
import sqlite3
import gc
import sys
import gzip
import shutil
import zipfile
import threading 

if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM\\Tests")
else:    
    mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep    
    sys.path.insert(0,mainFolder)    
    sys.path.insert(0,mainFolder+"Tests")

from utilities import *
import Dataset
import IntervalArray
import IntervalTree
import settings
import ThreadPool
    


class NIHEpigenomeWig(Dataset.Dataset):
    
    def init(self,initCompute=True):
        if isinstance(self.computeRegionSizeRelative,str):
            self.computeRegionSizeRelative = self.computeRegionSizeRelative == "True"
        
        self.nullFromLinks = map(lambda x: x.strip(),self.nullFrom.split(";"))  
        self.datasetFromLinks = map(lambda x: x.strip(),self.datasetFrom.split(";"))
        #self.markDatasetNumpyType = numpy.uint8
        #self.nullDatasetNumpyType = numpy.uint16
        self.dataArrays = {}
        self.nullDataArrays = {}
        self.dataTotalSum = 0
        self.nullTotalSum = 0
        self.totalNullConstant = None
        self.windowArrays = {}
        self.slidingWindowSizes = []
        self.useWindowThreading = True
        self.initSlidingWindowSizes()
        
        
        Dataset.Dataset.init(self,initCompute)       
        self.initialized = True         
    
    def initSlidingWindowSizes(self):
        self.slidingWindowSizes = []
        currentSize = 20
        currentStep = 20
        #print currentSize,currentStep,self.slidingWindowSizes
        while currentSize <= 1000000:                    
            self.slidingWindowSizes.append(currentSize)
            currentSize = currentSize + currentStep 
            currentStep = (max(20,currentSize/10)/20)*20
            #print currentSize,currentStep,self.slidingWindowSizes
        self.slidingWindowSizes.append(currentSize)
        #print self.slidingWindowSizes,len(self.slidingWindowSizes)
        self.slidingWindowSizes = [20,40,60,80,120,160,200,
                                   260,320,380,460,540,620,720,
                                   820,920,1000,1200,1500,1750,2000,
                                   2400,3000,3500,4000,5000,7000,10000,
                                   15000,20000,27000,35000,50000]
        self.slidingWindowSizes.sort()        
        self.slidingWindowSizes = numpy.array(self.slidingWindowSizes)
        #print self.slidingWindowSizes.size,self.slidingWindowSizes
        
         
            
                  
    def downloadDataset(self):
        for datasetName in self.datasetFromLinks:            
            absName = self.getDatasetLocalFile(datasetName)            
            if not os.path.isfile(absName):
                downloadFile(datasetName, absName)
                log(self.datasetSimpleName + ": file " + str(os.path.basename(absName) + " was downloaded"))
                self.downloadUrls[absName] = datasetName
                self.downloadDate = fileTimeStr(absName)  
                
        for nullInput in self.nullFromLinks:
            nullAbsName = self.getDatasetLocalFile(nullInput)
            if not os.path.isfile(nullAbsName):                
                downloadFile(nullInput, nullAbsName)
                log(self.datasetSimpleName + ": file " + str(os.path.basename(nullAbsName) + " was downloaded"))
                self.downloadUrls[nullAbsName] = nullInput
                self.downloadDate = fileTimeStr(nullAbsName)
    
    def hasAllDownloadedFiles(self):
        for datasetName in self.datasetFromLinks:            
            absName = self.getDatasetLocalFile(datasetName)            
            if os.path.isfile(absName):
                self.downloadUrls[absName] = datasetName
                self.downloadDate = fileTimeStr(absName)
            else:  
                return False
        for nullInput in self.nullFromLinks:                
            nullAbsName = self.getDatasetLocalFile(nullInput)
            if os.path.isfile(nullAbsName):
                self.downloadUrls[nullAbsName] = nullInput
                self.downloadDate = fileTimeStr(nullAbsName)
            else:
                return False        
        return True
        
    
    def getDatasetLocalFile(self,datasetName):
        return os.path.abspath(settings.downloadDataFolder[self.genome] + os.path.basename(datasetName))
    
    def getDatasetSlidingSizesFile(self):            
        return settings.rawDataFolder[self.genome]+self.datasetSimpleName+".distributions.zip"
    
    
    def hasPreprocessedFile(self):
        for chrom in settings.genomeDataStr[self.genome].keys():
            if "Y" in chrom:
                continue                   
            chromBinaryFile = self.getMarkChromArrayFile(chrom)
            if not os.path.isfile(chromBinaryFile):
                return False       
            
            chromNullBinaryFile = self.getNullChromArrayFile(chrom)
            if not os.path.isfile(chromNullBinaryFile):
                return False
        # Check for the ratios distribution
        if self.computeRegionSizeRelative and not os.path.isfile(self.getDatasetSlidingSizesFile()):
            return False
        return True
    
    def preprocessDownloadedDataset(self):        
        if not self.hasAllDownloadedFiles():
           exText = self.datasetSimpleName + ": the dataset files are not downloadeded "
           log(exText)
           raise GDMException, exText
        if self.hasPreprocessedFile():
            #what to do if the data was already preprocessed
            extext = self.datasetSimpleName + ": the dataset was already preprocessed"
            log(extext)
            return           
        #preprocess the mark dataset
        self.preptocessMarkDataset()
        # preprocess the null datasets         
        self.preptocessNullDataset()
        if self.computeRegionSizeRelative:
            #preprocess the percentile datasets        
            self.preprocessPercentileRatios()
    
    def preprocessPercentileRatios(self):
        print "preprocessPercentileRatios start"
        distributionsFile = self.getDatasetSlidingSizesFile()
        if os.path.isfile(distributionsFile):
            #Teh distributions file is processed
            print "The distribution file exists"
            return
        self.initializePropertiesComputeStructures(False)
        
        print "computing the ratios"
        try:
            zpa = zipfile.ZipFile(distributionsFile,"w",zipfile.ZIP_DEFLATED)
            zpa.writestr("dummy.txt","dummy file")
            zpa.close()
            self.ziplock = threading.Lock()
            # Create a pool with three worker threads
            pool = ThreadPool.ThreadPool(5)  
            sys.setcheckinterval(1000)          
            for windowSize in self.slidingWindowSizes:
                if self.useWindowThreading:
                    pool.queueTask(self.preprocessWindowSize, windowSize, None)
                else:
                    self.preprocessWindowSize(windowSize)
            # When all tasks are finished, allow the threads to terminate
            if self.useWindowThreading:
                print "Joining the threads"
                pool.joinAll()             
        except:            
            os.unlink(distributionsFile)
            raise
        print "preprocessPercentileRatios end"
        
    def preprocessWindowSize(self, windowSize):
        log(["Starting",windowSize])
        ratios = self.preprocessOddsRatiosForWindowSize(windowSize)
        #ratios = self.preprocessOddsRatiosForWindowSize2(windowSize)        
        ratioKeys = ratios.keys()
        ratioKeys.sort()
        totalNumber = sum(ratios.values())
        print windowSize,"Number of ratios", len(ratioKeys), totalNumber,ratioKeys[0],ratioKeys[-1]
        x = numpy.zeros((len(ratioKeys), 2),dtype=numpy.float)
        totalUntilNow = 0
        for i in xrange(len(ratioKeys)):
            totalUntilNow += ratios[ratioKeys[i]]
            x[i, 0] = ratioKeys[i]
            x[i, 1] = totalUntilNow / float(totalNumber)
        distributionsFile = self.getDatasetSlidingSizesFile()
        fileName = distributionsFile + "." + str(windowSize) + ".dis"
        x.tofile(fileName)
        self.ziplock.acquire()
        try:
            zpa = zipfile.ZipFile(distributionsFile,"a",zipfile.ZIP_DEFLATED)            
            zpa.write(fileName, str(windowSize) + ".dis")
            zpa.close()            
        finally:
            os.unlink(fileName)
            self.ziplock.release()
        log("Processing for window "+str(windowSize)+" is complete")
    
    def preprocessOddsRatiosForWindowSize2(self,windowSize):
        windowSizeConverted = windowSize/20
        print "Processing ratios for window",windowSize,windowSizeConverted        
        ratios = {}
        for chrom in settings.genomeDataStr[self.genome].keys():
            if chrom != "chrY":
                continue
            dac = self.dataArrays[chrom]
            nac = self.nullDataArrays[chrom]    
            if not self.dataArrays.has_key(chrom) or not self.nullDataArrays.has_key(chrom):
                continue          
            markScore = numpy.sum(dac[:windowSizeConverted])+1
            nullScore = numpy.sum(nac[:windowSizeConverted])+1
            print windowSizeConverted,markScore,nullScore
            log(["Start computing ",windowSize,chrom,self.dataArrays[chrom].size,windowSizeConverted])                        
            for i in xrange(0,dac.size-windowSizeConverted-1):
                try:
                   ratios[markScore/float(nullScore)] += 1
                except:
                   ratios[markScore/float(nullScore)] = 1
                markScore += dac[i+windowSizeConverted] - dac[i] 
                nullScore += nac[i+windowSizeConverted]- nac[i]             
            try:
               ratios[markScore/float(nullScore)] += 1
            except:
               ratios[markScore/float(nullScore)] = 1
            log(["Ratios computed",chrom,windowSize])            
        return ratios    
    def preprocessOddsRatiosForWindowSize(self,windowSize):
        windowSizeConverted = windowSize/20
        print "Processing ratios for window",windowSize,windowSizeConverted        
        ratios = {}
        for chrom in settings.genomeDataStr[self.genome].keys():
           
            if not self.dataArrays.has_key(chrom) or not self.nullDataArrays.has_key(chrom):
                continue
            dac = self.dataArrays[chrom]
#            print dac[0],dac[10],dac[100],dac[1000],dac[10000],dac[100000],dac[1000000],dac[1000000] 
            nac = self.nullDataArrays[chrom]          
#            print nac[0],nac[10],nac[100],nac[1000],nac[10000],nac[100000],nac[1000000],nac[1000000]
            markScore = sum(dac[:windowSizeConverted])+1            
            nullScore = sum(nac[:windowSizeConverted])+1
#            print markScore,nullScore
            log(["Start computing ",windowSize,chrom,self.dataArrays[chrom].size,windowSizeConverted])
            ratiosArray = numpy.zeros(dac.size-windowSizeConverted)            
            
            maxRatio = 1
            minRatio = 1                 
            for i in xrange(0,dac.size-windowSizeConverted-1):
                ratiosArray[i] = markScore/float(nullScore)
#                if ratiosArray[i] > maxRatio:
#                    maxRatio = ratiosArray[i]  
#                    print windowSize,i,"max","Ratio",markScore,nullScore,ratiosArray[i]
#                    print windowSize,"max","Mark update",markScore,dac[i+windowSizeConverted], dac[i]
#                    print windowSize,"max","Null update",nullScore,nac[i+windowSizeConverted], nac[i]
#                if ratiosArray[i] < minRatio:
#                    minRatio = ratiosArray[i]  
#                    print windowSize,i,"min","Ratio",markScore,nullScore,ratiosArray[i]
#                    print windowSize,"min","Mark update",markScore,dac[i+windowSizeConverted], dac[i]
#                    print windowSize,"min","Null update",nullScore,nac[i+windowSizeConverted], nac[i]
                markScore = markScore + dac[i+windowSizeConverted] - dac[i] 
                nullScore = nullScore + nac[i+windowSizeConverted] - nac[i]
                             
            ratiosArray[self.dataArrays[chrom].size-windowSizeConverted-1] = markScore/float(nullScore)            
            log(["Ratio array computed",chrom,windowSize,ratiosArray.max(),ratiosArray.min(),ratiosArray.mean()])
            ratiosArray.sort()
            log(["Ratio array sorted",chrom,windowSize,ratiosArray[0],ratiosArray[-1]])
            count1 = 1
            currentScore = ratiosArray[0]
            for j in xrange(1,ratiosArray.size):
                if ratiosArray[j] == currentScore:
                   count1 += 1
                else:
                   try:
                       ratios[currentScore] += count1
                   except:
                       ratios[currentScore] = count1
                   count1 = 1
                   currentScore = ratiosArray[j]
            try:
               ratios[currentScore] += count1
            except:
               ratios[currentScore] = count1
            del ratiosArray 
            log(["Ratio array processed",chrom,windowSize])
            
        return ratios
        
    def preprocessDatasetFromFileToArray(self,datasetLocalName,dataArrays):
        if datasetLocalName.endswith(".gz"):
            f = gzip.GzipFile(datasetLocalName,"rb")
        else:
            raise GDMException, "unsupported file extension for "+nullAbsName
        # first line is summary information            
        log(f.readline().strip())        
        lines = f.read().split("\n")
        f.close()
        log("Lines read "+str(len(lines)))
        foundNextValidLine = True
        lineIndex = None
        currentChrom = None
        currentPosition = -100000
        for lineIndex in xrange(len(lines)-1):
            if not foundNextValidLine:
                # we are nto sure what to expect here                
                try:
                    # update the current position
                    currentPosition += 1
                    #try if the line is an integer
                    x = int(lines[lineIndex])                    
                    try:                                                                 
                        dataArrays[currentChrom][currentPosition] += x
                    except KeyError:
                        # probably invalid chromosome
                        pass
                except ValueError:
                    #this should be thrown by x = int(lines[lineIndex])
                    # in this case check if it is a settings line
                    lineParts = lines[lineIndex].split(" ")
                    if lineParts[0] == "fixedStep" and lineParts[3] == "step=20" and lineParts[4] == "span=20":
                        #looks like a settingsa line
                        foundNextValidLine = True
                    else:
                        # here wea re unsure what is this line 
                        raise GDMException, "Invalid line (neither lone integer nor settings)" +str(lines[lineIndex])                    
                    
            if foundNextValidLine: 
                #fixedStep chrom=chr10 start=51001 step=20 span=20               
                lineParts = lines[lineIndex].split(" ")
                if lineParts[0] != "fixedStep" or lineParts[3] != "step=20" or lineParts[4] != "span=20":
                    raise GDMException, "Unexpected line :"+str(lineIndex)+lines[lineIndex]+str(lineParts)
                #read the chromosome  
                currentChrom = lineParts[1][lineParts[1].find("=")+1:]                            
                try: 
                    # if it is nto a valid chromosome, throw an exception and disregard the reads for it from now on                       
                    settings.genomeDataStr[self.genome][currentChrom]
                except KeyError:                    
                    currentChrom = None
                    currentPosition = -100000
                # if it is a valid chromosome                                
                if currentChrom:
                    # check if the array for this chromosome was already rpocessed
                    if not dataArrays.has_key(currentChrom):
                        # otherwise initialize it
                        dataArrays[currentChrom] = numpy.zeros(settings.genomeDataStr[self.genome][currentChrom]/20 + 1,numpy.uint16)
                    #initialize the current index position that shoudl be updated next
                    start = int(lineParts[2][lineParts[2].find("=")+1:])
                    currentPosition = (start-1)/20
                # from this point on, we expect a number of only int lines
                foundNextValidLine = False    
       
        log("preprocessDatasetFromFileToArray completes "+datasetLocalName)
        
        
    def preptocessNullDataset(self):
        allChroms = True
        for chrom in settings.genomeDataStr[self.genome].keys():
            if "Y" in chrom:
                continue                   
            chromNullBinaryFile = self.getNullChromArrayFile(chrom)
            if not os.path.isfile(chromNullBinaryFile):
                print "Not found",chromNullBinaryFile                            
                allChroms = False
                break 
        if allChroms:
            # dataset was already preprocessed
            return
        #compute the array files
        self.nullDataArrays = {}
        for nullInput in self.nullFromLinks:
            nullAbsName = self.getDatasetLocalFile(nullInput)                
            self.preprocessDatasetFromFileToArray(nullAbsName,self.nullDataArrays)
        #store the array files
        for chrom in self.nullDataArrays.keys():
            chromNullBinaryFile = self.getNullChromArrayFile(chrom)
            self.nullDataArrays[chrom].tofile(chromNullBinaryFile)
            del self.nullDataArrays[chrom]    
            
    def preptocessMarkDataset(self):
        allChroms = True
        for chrom in settings.genomeDataStr[self.genome].keys():                   
            if "Y" in chrom:
                continue 
            chromBinaryFile = self.getMarkChromArrayFile(chrom)            
            if not os.path.isfile(chromBinaryFile):
                print "Not found",chromBinaryFile
                allChroms = False
                break 
        if allChroms:
            # dataset was already preprocessed
            return
        
        self.dataArrays = {}
        for datasetName in self.datasetFromLinks:
            datasetLocalFile = self.getDatasetLocalFile(datasetName)
            #preprocess the data to an array
            self.preprocessDatasetFromFileToArray(datasetLocalFile,self.dataArrays)
        # save the data to an array 
        for chrom in self.dataArrays.keys():
            chromArrayFile = self.getMarkChromArrayFile(chrom)
            self.dataArrays[chrom].tofile(chromArrayFile)
            del self.dataArrays[chrom]
    
    def getMarkChromArrayFile(self,chrom):
        return settings.rawDataFolder[self.genome]+self.datasetSimpleName+"_"+chrom+".dat"
    
    def getNullChromArrayFile(self,chrom):
        return settings.rawDataFolder[self.genome]+"null_"+chrom+".dat"
                
    def getDefaultAnnotationSettings(self):        
        # obtain the default settings
        settings = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settings["hasGenomicRegions"] = self.hasGenomicRegions
        settings["hasFeatures"] = self.hasFeatures
        #retrun them
        return settings
    
    def initializePropertiesComputeStructures(self,initRatios = True):
        # If all files are downloaded and preprocessed, there is nothing else to do 
        log(["initializePropertiesComputeStructures",self.datasetSimpleName,"Loading the arrays"])           
              
        for chrom in settings.genomeDataStr[self.genome].keys():            
            if not self.dataArrays.has_key(chrom):
                chromBinaryFile = self.getMarkChromArrayFile(chrom)
                self.dataArrays[chrom] = numpy.fromfile(chromBinaryFile,dtype=numpy.uint16)
            if not self.nullDataArrays.has_key(chrom):            
                chromNullBinaryFile = self.getNullChromArrayFile(chrom)
                self.nullDataArrays[chrom] = numpy.fromfile(chromNullBinaryFile,dtype=numpy.uint16)           
            if self.dataArrays[chrom].size != self.nullDataArrays[chrom].size:
                raise GDMException, " Wrong sizes "+str(self.dataArrays[chrom].size)+" "+str(self.nullDataArrays[chrom].size)
        log(["initializePropertiesComputeStructures",self.datasetSimpleName,"arrays loaded"])  
        #initializing the total sums
        if self.dataTotalSum == 0 or self.nullTotalSum == 0:
            #sums are not initiated
            for chrom in settings.genomeDataStr[self.genome].keys():                
                if self.dataArrays.has_key(chrom):
                    s1 = numpy.sum(self.dataArrays[chrom])
                    #s2 = sum(self.dataArrays[chrom])
                    #if s1 != s2:
                    #    raise GDMException, "Sums are different "+str(s1) +" - "+str(s2)
                    self.dataTotalSum += s1
                if self.nullDataArrays.has_key(chrom):
                    s1 = numpy.sum(self.nullDataArrays[chrom])
                    #s2 = sum(self.nullDataArrays[chrom])
                    #if s1 != s2:
                    #    raise GDMException, "Sums are different "+str(s1) +" - "+str(s2)
                    self.nullTotalSum += s1
            self.totalNullConstant = float(self.nullTotalSum)/self.dataTotalSum 
        log(["initializePropertiesComputeStructures",self.datasetSimpleName,"sums",self.dataTotalSum,self.nullTotalSum,self.totalNullConstant])
        if self.dataTotalSum <= 0 or self.nullTotalSum <= 0:
            raise GDMException, "One fo the sums is 0, right after they were supposed to be initialized "+str(self.dataTotalSum)+" : "+str(self.nullTotalSum)
        # Now load the regions percentiles
        if self.computeRegionSizeRelative and initRatios:
            log(["initializePropertiesComputeStructures",self.datasetSimpleName,"Loading percentiles"])
            distributionsFile = self.getDatasetSlidingSizesFile()
            zpa = zipfile.ZipFile(distributionsFile)
            for windowSize in self.slidingWindowSizes:
                if not self.windowArrays.has_key(windowSize):
                    print "Loading window array for "+str(windowSize)
                    buffer = zpa.read(str(int(windowSize))+".dis")
                    tempArray = numpy.frombuffer(buffer,dtype=numpy.float)
                    self.windowArrays[int(windowSize)] = numpy.reshape(tempArray,(-1,2))
            zpa.close()
         
    
    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):
        if self.computeRegionSizeRelative:
            dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, odds_ratio REAL, odds_difference REAL, percentile REAL)")
        else:
            dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, odds_ratio REAL, odds_difference REAL)")
        
    def computeSingleRegionProperties(self, row, cgsAS):        
        # regionID INTEGER, odds_ratio REAL, percentile INTEGER
        chrom = row[1]
        chromStr = convertIntToChrom(self.genome,chrom)
        start = row[2]
        stop = row[3]
        length = row[3] - row[2]
         
        #get data counts
        ss = start/20
        es = stop/20
        #print row[0],"chrom=",chromStr,"start=",start,"stop=",stop,"ss=",ss,"es=",es        
        if ss == es:        
            dataCount = self.dataArrays[chromStr][ss]+1
            nullCount = self.nullDataArrays[chromStr][ss]+1
        else:
            dataCount = numpy.sum(self.dataArrays[chromStr][ss:es+1])+1
            nullCount = numpy.sum(self.nullDataArrays[chromStr][ss:es+1])+1
        #print row[0],"dataCount=",dataCount,"nullCount=",nullCount
        #calculate oddsRatio
        oddsRatioAbs = dataCount/float(nullCount)
        oddsRatio = oddsRatioAbs*self.totalNullConstant
        #print row[0],"oddsRatioAbs=",oddsRatioAbs,"oddsRatio=",oddsRatio
        #calculate oddsDifference
        oddsDifference =  dataCount/float(self.dataTotalSum) - nullCount/float(self.nullTotalSum)
        
        if self.computeRegionSizeRelative:
            #calculate percentile
            targetLength = (es+1-ss)*20
            targetLengthIndex = self.slidingWindowSizes.searchsorted(targetLength)
            #print row[0],"targetLength=",targetLength,"targetLengthIndex=",targetLengthIndex        
            checkLengths = {}
            count = 1
            if targetLengthIndex == self.slidingWindowSizes.size:
                # the size is larger than all processed windows. Settle for the largest            
                checkLengths[self.slidingWindowSizes[-1]] = 1             
            elif targetLengthIndex == 0:
                # returned 0, it is either equal or smaller than the smallest window(?20)
                # Check only this window
                checkLengths[self.slidingWindowSizes[0]] = 1            
            else:
                #in between stuff
                if self.slidingWindowSizes[targetLengthIndex] == targetLength:
                    checkLengths[self.slidingWindowSizes[targetLengthIndex]] = 1
                else:
                    # targetLength is between self.slidingWindowSizes[targetLengthIndex] and self.slidingWindowSizes[targetLengthIndex+1]
                    # make the percentile evenly spread between the two
                    df = float(self.slidingWindowSizes[targetLengthIndex]-self.slidingWindowSizes[targetLengthIndex-1])
                    tf = (targetLength-self.slidingWindowSizes[targetLengthIndex-1])
                    checkLengths[self.slidingWindowSizes[targetLengthIndex-1]] = tf/df
                    checkLengths[self.slidingWindowSizes[targetLengthIndex]] = 1-checkLengths[self.slidingWindowSizes[targetLengthIndex-1]]
                    count = 2
            #print row[0],"checkLengths=",checkLengths
            percentile = 0
            for l in checkLengths.keys():
                index = self.windowArrays[l][:,0].searchsorted(oddsRatioAbs)
                #print row[0],l,index,self.windowArrays[l][:,0].size
                if index == self.windowArrays[l][:,0].size:                
                    percentile += 1
                    #print row[0],"length=",l,"percentile=",1,"lastbefore=",self.windowArrays[l][self.windowArrays[l][:,0].size-1,:]
                elif index == 0:
                    pass
                    #percentile += 0
                    #print row[0],"length=",l,"percentile=",self.windowArrays[l][index,1],"lastbefore=",self.windowArrays[l][index,:],"nextAfter=",self.windowArrays[l][index+1,:]
                else:
                    percentile += self.windowArrays[l][index,1]
                    #print row[0],"length=",l,"percentile=",self.windowArrays[l][index-1,1],"lastbefore=",self.windowArrays[l][index-1,:],"nextAfter=",self.windowArrays[l][index,:]
            if count == 2:
                percentile = percentile/count     
            #print row[0],"oddsRatio=",oddsRatio,"percentile=",percentile             
            result = [(row[0],oddsRatio,oddsDifference,percentile)]
        else:
            #print row[0],"oddsRatio=",oddsRatio,"oddsDifference=",oddsDifference
            result = [(row[0],oddsRatio,oddsDifference)]
        return result
    
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
#        regionID INTEGER, oddsRatio REAL, oddsDifference REAL,
#        if not hasattr(self, "countPrint"):
#            self.countPrint = 0
#        try:
        regionData = []
        regionDataWithScores = []
        regionData.append([self.datasetWordName,self.histoneMark,self.tissue,"oddsratio",wordMagnitude(int(result[1]*numpy.power(10,5)),3)])
        if result[2] > 0:
            regionData.append([self.datasetWordName,self.histoneMark,self.tissue,"oddsdif",wordMagnitude(int(result[2]*numpy.power(10,9)),3)])
        else:
            regionData.append([self.datasetWordName,self.histoneMark,self.tissue,"oddsdif","n"+wordMagnitude(int(-1*result[2]*numpy.power(10,9)),3)])
#        except ex:
#            log(["Error",str(ex),str(result)])
#            raise
#        print result,regionData
#        self.countPrint += 1
#        if self.countPrint >= 20:
#            raise GDMException, "Explore the printouts"
        return regionData,regionDataWithScores
    
    def getWordPrefixes(self,cgsAS):
        return [self.datasetWordName+":"+self.histoneMark+":"+self.tissue]
        

        
                
