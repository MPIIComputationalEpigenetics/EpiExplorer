import os
import os.path
import md5
import numpy
import imp
import traceback
import sys
import shutil
import urllib

import settings
import time


class GDMException(Exception):    
    pass

class GDMValueException(Exception):    
    pass

class RegionsInclusionException(GDMException):
    pass

class CGSInvalidFormatException(GDMException):
    pass

def log(s):    
    if isinstance(s,list):                
        s = time.strftime(settings.logTimeFormat)+ " " +" , ".join(map(str,s))        
    else:
        s = time.strftime(settings.logTimeFormat)+ " " + str(s)
    print s
    settings.logSemaphore.acquire()
    try:
        f = open(settings.logFile,"a")
        f.write(s + "\n")
        f.close()
    finally:
        settings.logSemaphore.release()

def log_CFS(s):
    if isinstance(s,list):                
        s = ["CFS"]+s        
    else:
        s = "CFS "+s
    log(s)

def log_CDS(s):
    if isinstance(s,list):                
        s = ["CDS"]+s        
    else:
        s = "CDS "+s
    log(s)
        
def log_CQS(s):
    if isinstance(s,list):                
        s = ["CQS"]+s        
    else:
        s = "CQS "+s
    log(s)
    
def log_CSQuery(s):
    if isinstance(s,list):                
        s = ["CSQuery"]+s        
    else:
        s = "CSQuery "+s
    log(s)
    
def log_CSEngine(s):
    if isinstance(s,list):                
        s = ["CSEngine"]+s        
    else:
        s = "CSEngine "+s
    log(s)
    
def getFileName(name,absName):
    if not os.path.isfile(name):
        ff = os.path.join(os.path.dirname(absName),name)
        if not os.path.isfile(ff):
            raise Exception, "Error: No valid file name from "+name+" and " +absName
        name = ff
    return os.path.abspath(name)


def load_dataset_subclass(code_path,otherClasses):
    if False:
        completeCode = ""
        for oc in otherClasses:
            f = open(oc)
            datasetClassText = f.read()
            f.close()
            completeCode = datasetClassText + "\n"
        f = open(code_path)
        code = f.read()
        f.close()
        fn_with_dataset = code_path[:-3]+"_withDataset.py"
        fw = open(fn_with_dataset,"w")
        fw.write(completeCode+code)
        fw.close()
    else:
        fn_with_dataset = code_path
    
    return load_module(fn_with_dataset)
    
def load_module(code_path):
    try:
        try:
            code_dir = os.path.dirname(code_path)
            code_file = os.path.basename(code_path)

            fin = open(code_path, 'rb')

            return imp.load_source(md5.new(code_path).hexdigest(), code_path, fin)
        finally:
            try: fin.close()
            except: pass
    except ImportError, x:
        traceback.print_exc(file = sys.stderr)
        raise
    except:
        traceback.print_exc(file = sys.stderr)
        raise
## readSettingsFile
# 
# Reads an ini settings file and loads it into dictionary
def readSettingsFile(fileName):
    
    ## Format of the dataset index file
    # datasetName=datasetfile
    # where datasetfile is the file describing the dataset
    result = {}
    if not os.path.isfile(fileName):
        log(["Settings file",fileName,"does not exist!"])        
        return result
    f = open(fileName)
    line = f.readline()    
    while line:
        if line[0] != '#':
            if len(line.strip())> 0:
                lineParts = line.strip().split("=") 
                lineParts = map(lambda x:x.strip(),lineParts)
                if len(lineParts) < 2:
                    raise Exception, "Error:Invalid line "+line+" in "+fileName
                if len(lineParts) == 2:
                    result[lineParts[0]] = lineParts[1]
                else:
                    result[lineParts[0]] = "=".join(lineParts[1:])
        line = f.readline() 
    f.close()
    return result    
def convertStrandToInt(strand):
    if strand == "+":
        return 2
    elif strand=="-":
        return 1
    else:
        return 0
def convertIntToStrand(strand):
    if strand == 2:
        return "+"
    elif strand==1:
        return "-"
    else:
        return "."
def convertChromToInt(genome,chr):
    chr = chr.strip()
    if isinstance(chr,int):
        return chr
    try:
        return settings.genomeChromToInt[genome][str(chr)]
    except:
        raise GDMException, "Invalid chromosome string '"+chr+"' for  "+genome + str(settings.genomeChromToInt[genome].keys())

# MOVED THE CASES TO settings.genomeChromToInt
#def convertChromToInt(genome,chr):
#    if isinstance(chr,int):
#        return chr
#    
#    if len(chr) > 3:
#        chr = chr[3:]    
#    try:    
#        chr = int(chr)       
#    except:
#       if chr[0] == "X":
#           return 23
#       elif chr[0] == "Y":
#           return 24
#       else:
#           raise GDMException, chr  
#    return chr


def convertIntToChrom(genome,chr):
    if isinstance(chr,str):
        return chr
    try:
        return settings.genomeIntToChrom[genome][chr]
    except:
        raise GDMException, "Invalid chromosome number '"+chr+"' for "+genome

# MOVED THE CASES TO settings.genomeIntToChrom
#def convertIntToChrom(genome,chr):
#    if isinstance(chr,str):
#        return chr
#    if chr < 23:
#        return "chr"+str(chr)
#    elif  chr == 23:
#        return "chrX"
#    elif  chr == 24:
#        return "chrY"
#    else:
#        raise Exception

def getRegionsCollectionName(datasetCollectionName,genome):
    return settings.rawDataFolder[genome]+datasetCollectionName+"_regions.sqlite3"

def getDatasetDataName(datasetCollectionName,genome,datasetName):
    return settings.rawDataFolder[genome]+datasetCollectionName+"_data_"+datasetName+".sqlite3"

def getDatasetIntervalTreeName(datasetCollectionName,genome,datasetName):
    return settings.rawDataFolder[genome]+datasetCollectionName+"_intervalTree_"+datasetName+".pickle"


def listDatabaseInfo(databaseFile):
    import sqlite3
    conn = sqlite3.connect(databaseFile)
    c = conn.cursor()
    c.execute("select * from sqlite_master")
    print "Listing data stored in ",databaseFile
    for row in c:
        print row
    c.close()
    conn.close()
    
def getIndexOfActiveModule(m):
    l = dir(m)
    for i in range(len(l)):
        if l[i].startswith('d_'):            
            return i
        if l[i] in settings.datasetClasses:
            return i
    extext = "No regognized dataset module in "+str(l)+"\n is specified in datasetClasses "+str(settings.datasetClasses)
    log(extext)
    raise Exception, extext 
        
def gr_reduceRegionSet(setOfRegions, beginPos=0, endPos=1):
    finalSet = []
    ## the set of regions is ordered by start position
    # we remove all overlaps
    while len(setOfRegions) > 1:                
        if setOfRegions[0][endPos] < setOfRegions[1][beginPos]:
            # the end of the first is smaller by the start of the second
            # they are ordered by start so every other will also be like this
            # hence the first one is not overlapping with any other
            finalSet.append(setOfRegions[0])
            setOfRegions[:1] = []
        else:
            new = [""] * (max(beginPos, endPos) + 1) 
            new[beginPos] = setOfRegions[0][beginPos]
            new[endPos] = max(setOfRegions[0][endPos],setOfRegions[1][endPos])
            setOfRegions[0] = new
            setOfRegions[1:2] = []
    finalSet.extend(setOfRegions)
    return finalSet

def gr_reduceRegionSetIntervalOld(setOfRegions):
    finalSet = []
    ## the set of regions is ordered by start poistion
    # we remove all overlaps
    while len(setOfRegions) > 1:                
        if setOfRegions[0].stop < setOfRegions[1].start:
            # the end of the first is smaller by the start of the second
            # they are ordered by start so every other will also be like this
            # hence the first one is not overlapping with any other
            finalSet.append([setOfRegions[0].start,setOfRegions[0].stop])
            setOfRegions[:1] = []
        else:
            setOfRegions[0].stop = max(setOfRegions[0].stop,setOfRegions[1].stop)
            setOfRegions[1:2] = []
    if len(setOfRegions):        
        finalSet.append([setOfRegions[0].start,setOfRegions[0].stop])
    return finalSet

def gr_reduceRegionSetInterval(setOfRegions):
    finalSet = []
    if len(setOfRegions) == 0:
        return finalSet
    finalSet.append([setOfRegions[0].start,setOfRegions[0].stop])
    setOfRegions[:1] = [] 
    ## the set of regions is ordered by start poistion
    # we remove all overlaps
    while len(setOfRegions) > 0:                
        if finalSet[-1][1] < setOfRegions[0].start:
            # the end of the first is smaller by the start of the second
            # they are ordered by start so every other will also be like this
            # hence the first one is not overlapping with any other
            finalSet.append([setOfRegions[0].start,setOfRegions[0].stop])        
        else:
            #Extend the end of the last added region
            finalSet[-1][1] = max(finalSet[-1][1],setOfRegions[0].stop)
        setOfRegions[:1] = []    
    return finalSet

def gr_Coverage(setOfRegions, minStart= None,maxEnd=None, startPos=0, endPos=1):    
    if len(setOfRegions) == 0:
        return 0
    if minStart:
        #only one regions could have start smaller than the region start as
        # the regions are not overlapping due to the gr_reduceRegionSetInterval called
        # end also they all are overlapping with the region in question
        if setOfRegions[0][startPos] < minStart:
            setOfRegions[0][startPos] = minStart
    if maxEnd:
        if setOfRegions[-1][endPos] > maxEnd:
            setOfRegions[-1][endPos] = maxEnd
    s = 0
    return sum(map(lambda x:x[endPos]-x[startPos],setOfRegions))

def expandPatterns(basePatterns,k):
    newPatterns = []
    prevPattern = basePatterns
    for i in range(k-1):
        for p in prevPattern:
            for bp in basePatterns:
               newPatterns.append(p+bp)         
        prevPattern = newPatterns
        newPatterns = []
    return prevPattern


def overcount(s,pattern):
    """Returns how many p on s, works for overlapping"""
    ocu = 0
    x = 0
    while 1:
      try:
        i=s.index(pattern,x)
      except ValueError:
        break
      ocu+=1
      x=i+1
    return ocu
def reverseLetter(a):
    if a == "A":
        return "T"
    elif a == "C":
        return "G"
    elif a == "G":
        return "C"
    elif a == "T":
        return "A"
    else:
        return a
    
def reverseComplement(s):    
    x = map(reverseLetter,s)
    x.reverse()
    return "".join(x)

def getFastTmpCollectionFolder(datasetCollectionName):
    return settings.fastTmpFolder+datasetCollectionName+os.sep

def getCompleteSearchDirectory(genome):
    return settings.indexDataFolder[genome]

def mkdir(path):
    if not os.path.isdir(path):
        print "Mkdir",path
        os.mkdir(path)
        
def getCompleteSearchDocumentsWordsFile(datasetCollectionName,genome):
    path = getFastTmpCollectionFolder(datasetCollectionName)
    mkdir(path)
    return path+datasetCollectionName+".words-unsorted.ascii"
    #return settings.indexDataFolder[genome]+datasetCollectionName+".words-unsorted.ascii"    

def getCompleteSearchDocumentsDescrioptionsFile(datasetCollectionName,genome):
    path = getFastTmpCollectionFolder(datasetCollectionName)
    mkdir(path)    
    return path+datasetCollectionName+".docs-sorted"
    #return settings.indexDataFolder[genome]+datasetCollectionName+".docs-sorted"

def getCompleteSearchPrefixesFile(datasetCollectionName,genome):
    path = getFastTmpCollectionFolder(datasetCollectionName)
    mkdir(path)
    #return the file name for the prefixes to be used when computing this index
    return path+datasetCollectionName+".hybrid.prefixes"
    #return settings.indexDataFolder[genome]+datasetCollectionName+".hybrid.prefixes"

def getCompleteSearchFinalDocumentsWordsFile(datasetCollectionName,genome):
    path = getCompleteSearchDirectory(genome)
    mkdir(path)
    return path+datasetCollectionName+".words-unsorted.ascii"
    #return settings.indexDataFolder[genome]+datasetCollectionName+".words-unsorted.ascii"    

def getCompleteSearchFinalDocumentsDescrioptionsFile(datasetCollectionName,genome):
    path = getCompleteSearchDirectory(genome)
    mkdir(path)    
    return path+datasetCollectionName+".docs-sorted"
    #return settings.indexDataFolder[genome]+datasetCollectionName+".docs-sorted"

def getCompleteSearchFinalPrefixesFile(datasetCollectionName,genome):
    path = getCompleteSearchDirectory(genome)
    mkdir(path)
    #return the file name for the prefixes to be used when computing this index
    return path+datasetCollectionName+".hybrid.prefixes"
    #return settings.indexDataFolder[genome]+datasetCollectionName+".hybrid.prefixes"

def line_count(filename):
    f = open(filename)                  
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
    f.close()
    return lines

def getCorrectedCoordinates(genome,chr,start,stop):
    if start > stop:
        raise Exception, "Error: Start and end are switched"    
    if start < 0:
        start = 0
    if start > settings.genomeData[genome][chr]:
        raise Exception,"Error: Inteval is out of chromosome bounds "+str((chr,start,stop))
    if stop > settings.genomeData[genome][chr]:
        stop = settings.genomeData[genome][chr]
    return start,stop

# DEPRECATED. ALL STORED IN THE SETTINGS NOW
#def getChromosomeLengths(chrs):
#    import DatasetClasses.dnasequence
#    ds = DatasetClasses.dnasequence.DNASequence()
#    ds.hasGenomicRegions = "False"    
#    ds.patterns = "1"
#    ds.datasetRawData = "/TL/epigenetics/nobackup/epigraph/AttributeDatabase_test/upload_workdir/hg18_genome/"
#    ds.genome = "hg18"
#    ds.currentLoadedChromosome = None
#    ds.currentLoadedChromosomeSeq = None
#    ds.init()
#    for chr in chrs:
#        ds.loadChromosome(chr)
#        #print chr,len(ds.currentLoadedChromosomeSeq)
    
    
    
def wordMagnitude(i,size = 2):
    if i:
        y = str(i)[:size-1]
        z = size-1-len(y)
        if z:
            x = str(int(numpy.log10(i))) + "0"*z + y            
        else:
            x = str(int(numpy.log10(i))) + y            
        return x
    else:
        return "0"*size

def wordFloatFixed(f,np,nq):
    #represent each float as xxxxyyyyyyy
    #where #x = np and #y = yyyyyyy
    p = int(f)
    q = f-p                     
    return wordFixed(p,np) + wordFloat(q,nq)
      
def wordFixed(f,n):
    r = str(f)
    lr = len(r)
    if lr < n:
        return "0"*(n-lr) + r
    elif lr == n:
        return r
    else:
        raise Exception, "Cannot normalize "+str(f)+" to "+str(n)+" characters"
    
def wordFloat(f,n):
    if f == 1:
        return "9"*n
    else:
        w = str(int(f*pow(10,n)))        
        return "0"*(n-len(w))+w 
    
def getSafeWord(word,additional=""):
    # if the worh contains only allowed characters then  
    # the translate will delete the whole word and return ""
    allowedChracters = additional +  settings.allowed_chars
    if word.translate(settings.trans_table,allowedChracters):
#        raise Exception, word
        return filter(lambda x:x in allowedChracters,word)            
    return word

def getMainDatasetIndexFileName(datasetCollectionName):
    import sys    
    if sys.platform == "win32":
        datasetsIndexFile = settings.windowsBaseFolder+"Datasets/win_"+datasetCollectionName+".ini"
    else:
        datasetsIndexFile = settings.unixBaseFolder+"Datasets/unix_"+datasetCollectionName+".ini"
    return datasetsIndexFile 

def downloadFile(url,localFile):
    import os.path
    if os.path.isfile(localFile):
        raise Exception, "Error: File already exists "+localFile
    from urllib import FancyURLopener

    # a special opener to simulate firefox queries
    class MyOpener(FancyURLopener):
        version = 'Mozilla/5.0'
    myopener = MyOpener()
    myopener.retrieve(url, localFile)
    
def toTermWordScore(numberOfGenes,base):
    # The idea of this score is to make categories with base or less genes to have the maximum score
    # Thsi ensures that they will be ommited from the list
    # Furthermore the scaling is made such that every power of 4 of the scores represents power of 10 in the number of genes
    # if base = 5
    #    Genes    Scores
    #    1-5        255
    #    6        228
    #    50        64
    #    500        16
    #    5000        4
    #    15,000      1      
    #    >16,000     0
    return int(max(min(numpy.floor(256/numpy.power(4,numpy.log10(numberOfGenes/float(base))))-1,255),0))

def getWordOMIMscore(numberOfGenes):
    return str(toTermWordScore(numberOfGenes,1))    
    #return str(int(wordMagnitude(numberOfGenes,2)))

def getWordGOscore(numberOfGenes):
    return str(toTermWordScore(numberOfGenes,5))    
    #return str(int(wordMagnitude(numberOfGenes,2)))

def getCurrentFolder():
    return settings.baseFolder+"GDM/"
    #return os.path.abspath(os.path.curdir)+os.sep
    

import pickle
class Coverages:
    def __init__(self):
        self.coverages = {}
        
    def getFile(self, genome):
        return settings.rawDataFolder[genome]+"coverages.txt"            
        
    def storeCoverageValues(self, genome, datasetSimpleName, coverageValues):
        fName = self.getFile(genome)
        f = open(fName, "w+");
        try:
            self.coverages[datasetSimpleName] = coverageValues
                        
            pickle.dump(self.coverages, f)
        except Exception, ex:        
            log("Error: "+str(ex))
        finally:
            f.close();

    def _loadCoverageValues(self, genome):        
        if len(self.coverages.items()) == 0:
            if not os.path.exists(self.getFile(genome)):
                self.coverages = {}
            else:    
                f = open(self.getFile(genome), "r");
                self.coverages = pickle.load(f)
                f.close()
            
        return self.coverages        
        
    def getCovarageValues(self, genome, datasetSimpleName):
        self._loadCoverageValues(genome)   
        if self.coverages.has_key(datasetSimpleName): 
            return self.coverages[datasetSimpleName]
        return None
    
c = Coverages()

def storeCoverageValues(genome, datasetSimpleName, coverageValues):
    c.storeCoverageValues(genome, datasetSimpleName, coverageValues)    
    
def getCovarageValues(genome, d):
    return c.getCovarageValues(genome, d)


class DownloadUrls:
    def __init__(self):
        self.downloadUrls = {}
        
    def getFile(self, genome):
        return settings.rawDataFolder[genome]+"download_urls.txt"            
        
    def storeUrls(self, genome, datasetSimpleName, urls, date):
        fName = self.getFile(genome)
        f = open(fName, "w+");
        
        self.downloadUrls[datasetSimpleName] = urls
        self.downloadUrls[datasetSimpleName]["__date"] = date
                        
        pickle.dump(self.downloadUrls, f)        
        f.close();

    def _loadUrls(self, genome):        
        if len(self.downloadUrls.items()) == 0:
            if not os.path.exists(self.getFile(genome)):
                self.downloadUrls = {}
            else:    
                f = open(self.getFile(genome), "r");
                self.downloadUrls = pickle.load(f)
                f.close()
            
        return self.downloadUrls
        
    def getUrls(self, genome, datasetSimpleName):
        self._loadUrls(genome)   
        if self.downloadUrls.has_key(datasetSimpleName): 
            urls = self.downloadUrls[datasetSimpleName].copy()
            date = urls["__date"]
            del(urls["__date"])
            return urls, date
        return None, None
    
dUrls = DownloadUrls()

def storeUrlsValues(genome, datasetSimpleName, urls, date):
    dUrls.storeUrls(genome, datasetSimpleName, urls, date)    
    
def getUrlsValues(genome, d):
    return dUrls.getUrls(genome, d)


def getDatasetStatusAsText(activeStep,activeStepDetailedStatus = ""):
    status = ["Step 1/6: Preparing the set of regions",
              "Step 2/6: Preparing the annotations",
              "Step 3/6: Computing annotations",
              "Step 4/6: Exporting annotation data to text documents",
              "Step 5/6: Building the CompleteSearch index",
              "Step 6/6: Sending notification and cleaning up"]
    for i in range(len(status)):
        if i < activeStep:
            status[i] = '<p style="color:green">'+status[i]+'</p>'
        elif i == activeStep:
            if activeStepDetailedStatus:
                status[i] = activeStepDetailedStatus
            status[i] = '<p><b>'+status[i]+'</b></p>'
        else:
            status[i] = '<p style="color:grey">'+status[i]+'</p>'
    return "\n".join(status)

def fileTimeStr(f):
    fileTime = os.path.getctime(f)
    t = time.gmtime(fileTime)
    s = time.strftime("%d %b %Y", t)
    return s

def moveTmpIndexFilesToIndexFolder(datasetCollectionName,genome):
    fastTmpDir = getFastTmpCollectionFolder(datasetCollectionName)
    completeSearchDir = getCompleteSearchDirectory(genome)

    fileNames = os.listdir(fastTmpDir)
    for fileName in fileNames:
        if os.path.isfile(fastTmpDir+fileName):
            shutil.move(fastTmpDir+fileName, completeSearchDir+fileName)

__servers = {}
def getForwardServer(name):
    if __servers.has_key(name):
        return __servers[name]

    u = urllib.urlopen(settings.webservers[name])
    line = u.read()
    s = line.split(":")
    s = (s[0], int(s[1]))
    __servers[name] = s
    return s

def retryCall(call,times,timeToSleep=0):
    ex = GDMException()
    while times > 0:
        try:            
            return call()
        except Exception, ex:
            times -= 1
            if times == 1:
                raise ex
            else:
                log("retryCall: Error "+str(call)+str(ex))
                time.sleep(timeToSleep)
    raise GDMException, "Failed "+str(call)+" several times "+str(times)
            
            

    

        
#x = {"a":1, "b":2, "c":3}
#y = {"a":10, "b":20, "c":0.1111111111111111111111111111111}
#z = {"a":111, "b":222, "c":0.000000000000000000001}

#storeCoverageValues("hg19", "x", x)
#storeCoverageValues("hg19", "y", y)
#storeCoverageValues("hg19", "z", z)

#print getCovarageValues("hg19", "x")
#print getCovarageValues("hg19", "y")
#print getCovarageValues("hg19", "z")
#print getCovarageValues("hg19", "q")
