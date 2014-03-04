import os
import os.path
import sys
import numpy
import gc

if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
else:
    mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep    
    sys.path.insert(0,mainFolder)

from utilities import *
import Dataset

class DNASequence(Dataset.Dataset):    
    def __init__(self):
        Dataset.Dataset.__init__(self)
        
    def init(self,initCompute=True):
        self.regionsCountMod = 10000        
        Dataset.Dataset.init(self,initCompute)       
        self.initialized = True 
        
        self.basePatterns = ["A","C","G","T"]
        if not self.hasAllDownloadedFiles():
            raise GDMException,"Chromosome files for genome"+str(self.genome)+" are not available in the folder "+self.datasetFrom
        
        self.loadPatterns()

    def downloadDataset(self):
        self.chromFiles = {}
        self.basePatterns = ["A","C","G","T"]
    def hasAllDownloadedFiles(self):
        self.chromFiles = {}
        self.basePatterns = ["A","C","G","T"]
        self.chromFiles = {}
        if os.path.isdir(self.datasetFrom):
            fileNames = os.listdir(self.datasetFrom)
            for filename in fileNames:
                if filename.startswith(self.genome+"_") and filename.endswith("_noLinebreaks.fa"):
                   chr = filename[len(self.genome)+1:-16]
                   if chr[3].isdigit() or chr[3] == "X" or chr[3] == "Y":  
                   #print filename,chr
                       self.chromFiles[convertChromToInt(self.genome,chr)] = self.datasetFrom+filename
        if len(self.chromFiles.keys()) < 1:
            return False
        else:
            return True
    def preprocessDownloadedDataset(self):
        self.chromFiles = {}
        self.basePatterns = ["A","C","G","T"]        
        if not self.hasAllDownloadedFiles():
           exText = self.datasetSimpleName + ": the dataset files are not downloadeded "
           log(exText)
           raise GDMException, exText
        if self.hasPreprocessedFile():
            #what to do if the data was already preprocessed            
            return
        raise GDMException,"Chromosome files for genome"+str(self.genome)+" are not available in the folder "+self.datasetFrom
    def hasPreprocessedFile(self):
        return True         
        
        
    def loadPatterns(self):
        allPatterns = []
        pats = self.patterns.split(",")
        for p in pats:
            try:
                # if pattern is integer, load all patterns of this size
                k = int(p)
                allPatterns = allPatterns + expandPatterns(self.basePatterns,k)
            except:
                #pattern is standard:
                p = p.upper()
                allPatterns.append(p)
        #print allPatterns
        self.patterns = list(set(allPatterns))        
                 
        
    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):
        
        createTableQuery = "CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER,length INTEGER"
        for p in cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"patterns"):
            createTableQuery += ", c_"+p+" REAL"
        createTableQuery += " )"
        dataConnections[0][1].execute(createTableQuery)
        
    def initializePropertiesComputeStructures(self):
        pass
    
    def computeSingleRegionProperties(self,row, cgsAS):
        regionID = row[0]        
        chrom = row[1]
        start = row[2]
        stop = row[3]
        if cgsAS.featuresDatasets[self.datasetSimpleName]["currentLoadedChromosome"] != chrom:
            self.loadChromosome(chrom,cgsAS)
        s = cgsAS.featuresDatasets[self.datasetSimpleName]["currentLoadedChromosomeSeq"][start:stop]
        patterns = cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"patterns")
        scores = numpy.zeros(len(patterns))
        for i in xrange(len(patterns)):
            if patterns[i][0] == "E":                
                scores[i] = overcount(s,patterns[i][1:])
                scores[i] += overcount(s,reverseComplement(patterns[i][1:]))
            else:
                scores[i] = overcount(s,patterns[i])
        scores = scores        
        return [[regionID,int(stop-start)]+list(scores)] 
        
    
    def countSubstringsEfficiently(self,s,patterns):        
        for i in range(len(s)):
            for pattern in patterns:
                pass
    
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
        #print self.datasetSimpleName, list(result)        
        regionData = []
        regionDataWithScores = []
        # for every sequence pattern stop the score (in 3 dgits of the frequence for the pattern)
        # ssAA:003
        #print self.datasetSimpleName,str(result)
        regionLength = float(result[1])
        patterns = cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"patterns")
        for i in range(len(patterns)):
#            regionData.append([settings.wordPrefixes["dnasequence"],patterns[i],"count",wordFixed(int(result[2 + i]),5)])
            regionData.append([settings.wordPrefixes["dnasequence"],patterns[i],"freq",wordFloat(result[2 + i]/regionLength,3)])        
        return regionData,regionDataWithScores
    
    def getWordPrefixes(self,cgsAS):
        prefixes = []
        patterns = cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"patterns")
        for i in range(len(patterns)):
            prefixes.append(settings.wordPrefixes["dnasequence"]+":"+patterns[i]+":"+"freq")
        return prefixes
    
    def getWordsDescription(self):
        doc = ""
        doc += "Ednaseq:AA:freq:078 the number of times we observe the pattern AA divided by the length of the region is 0.078\n"
        doc += "Ednaseq:AA:count:078 the number of times we observe the pattern AA \n"
        return doc
    
    def loadChromosome(self,chrom,cgsAS):
        del cgsAS.featuresDatasets[self.datasetSimpleName]["currentLoadedChromosome"]
        cgsAS.featuresDatasets[self.datasetSimpleName]["currentLoadedChromosome"] = None
        del cgsAS.featuresDatasets[self.datasetSimpleName]["currentLoadedChromosomeSeq"]
        cgsAS.featuresDatasets[self.datasetSimpleName]["currentLoadedChromosomeSeq"] = None
        
        f = open(self.chromFiles[chrom],"r")
        cgsAS.featuresDatasets[self.datasetSimpleName]["currentLoadedChromosomeSeq"] = f.read().upper()
        f.close()
        cgsAS.featuresDatasets[self.datasetSimpleName]["currentLoadedChromosome"] = chrom
        log("chrom "+str(chrom)+" is loaded")
        
    def cleanup(self,cgsAS):        
        sqlite3Data = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(sqlite3Data):
            os.unlink(sqlite3Data)
        #CLEANUP IMPROVE        
        try:
            del cgsAS.featuresDatasets[self.datasetSimpleName]["currentLoadedChromosomeSeq"]            
            del cgsAS.featuresDatasets[self.datasetSimpleName]["currentLoadedChromosome"]
            gc.collect()            
        except:
            pass                    
        
        
    def getDefaultAnnotationSettings(self):        
        # obtain the default settings
        settings = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settings["hasGenomicRegions"] = self.hasGenomicRegions
        settings["hasFeatures"] = self.hasFeatures
        settings["patterns"] = self.patterns
        settings["currentLoadedChromosome"] = None                
        settings["currentLoadedChromosomeSeq"] = None
        #retrun them
        return settings
        
    ## testValues
    # 
    # every dataset should test a few of the values it computed for user selected regions
    # 
#    def testValues(self):
#        pass
#        regions = [[1,924207,925333], #gene
#                   [1,924507,924633], #inside gene
#                   [7,141949074,141949123],#exons
#                   [7,141949050,141949150],#including an exon    
#                   [14,69156550,69157550],#enhancers
#                   [14,69155320,69155550],#near enhancers downstream (1000bp) and 38170 upstream
#                   [23,153945096,153945737], #within 1100 form TSS downstream and 100 from promoter downstream 
#                   ]
#        for r in regions:
#            if self.currentLoadedChromosome != r[0]:
#                self.loadChromosome(r[0])
#            s = self.currentLoadedChromosomeSeq[r[1]:r[2]]
#            for i in xrange(self.lPatterns):
#                pc = 0
#                lp = len(self.patterns[i])
#                for j in range(len(s)):
#                    if s[j:j+lp] == self.patterns[i]:
#                        pc += 1
                
                        
     # This method returns a list of feature words for the feature listing in the user interface 
    def getVisualizationFeatures(self,annotationFeatures):
        categories = self.dataCategories.strip()
        if len(categories) == 0:
            categoriesPath = [self.datasetSimpleName]
        else:
            categoriesPath = map(lambda x:x.strip(),categories.split("/"))+[self.datasetSimpleName]
        featureWords = []
        for pattern in annotationFeatures["patterns"]:
            featureWords.append(categoriesPath+["Ednaseq:"+pattern+":freq::3::0"])  
        
        return featureWords                   
                        
    def calculateCoverages(self):
        pass   
    
    def getSubAnnotations(self):
        return self.patterns
