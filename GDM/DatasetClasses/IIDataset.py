# the regions are stored in a local file DB and the search structure is inteval tree
import os
import os.path
import numpy
import sqlite3
import gc
import sys
import gzip
import shutil

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

class IIDataset(Dataset.Dataset):    
    def init(self,initCompute=True):
        self.binaryRegionsFile = settings.rawDataFolder[self.genome]+"IIcoordinates.sqlite3"
        self.binaryFile = self.getDatasetBinaryName()        
        
        Dataset.Dataset.init(self,initCompute)
        if isinstance(self.withVariance,str):
            self.withVariance = self.withVariance == "True" 
        self.cpgData = {}
        self.datasetType = "II27"
        self.initialized = True
        
        
        
    def hasAllDownloadedFiles(self):        
        datasetClinicalDataFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetClinicalData)
        datasetBetasFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetBetas)
        datasetCoordinatesFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetCoordinates)        
        if os.path.isfile(datasetClinicalDataFile) and os.path.isfile(datasetBetasFile) and os.path.isfile(datasetCoordinatesFile):
            return True
        else:
            return False     
    
    
    def downloadDataset(self):
        if not self.hasAllDownloadedFiles():
            datasetClinicalDataFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetClinicalData)
            shutil.copy2(self.datasetFrom + self.datasetClinicalData,datasetClinicalDataFile)
            datasetBetasFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetBetas)
            shutil.copy2(self.datasetFrom + self.datasetBetas,datasetBetasFile)
            datasetCoordinatesFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetCoordinates)
            shutil.copy2(self.datasetFrom + self.datasetCoordinates,datasetCoordinatesFile)
    
    def hasPreprocessedFile(self):
        self.binaryRegionsFile = settings.rawDataFolder[self.genome]+"IIcoordinates.sqlite3"
        self.binaryFile = self.getDatasetBinaryName() 
        if os.path.isfile(self.binaryFile) and os.path.isfile(self.binaryRegionsFile):
            return True       
        return False
    
    def preprocessClinicalAndBetaFile(self):        
        if os.path.isfile(self.binaryFile):
            extext = self.datasetSimpleName + ": the dataset clinical information and betas are already preprocessed in  "+self.binaryFile
            log(extext)
            return
        # Preprocess the coordinates into a local file
        # collect the 3 files that need to be preprocessed  
        datasetClinicalDataFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetClinicalData)
        datasetBetasFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetBetas)
        #Example of the betas info 
#        probe_id    S_0    S_1    S_2    S_3
#        cg00000292    0.7563667    0.834702    0.7741646    0.7995169
#        cg00002426    0.7978592    0.8595381    0.7696609    0.8543279
#        cg00003994    0.06860531    0.06746928    0.05693665    0.06380174



        #Exmaple of the collected clinical information
#sampleID    individualID    replicateGroupID    id_org    dataset    performingLab    cellType    tissueType    knownMutations    isDisease    isCancer    isCellLine    isPluripotent    isArtificialControl    age    sex    sourceDB    taggedString
#S_1607    I_1264    R_1596    GSM401997    GIBBS_BRAIN_QTL    Singleton    temporalCortex    brain    0    None    None    FALSE    FALSE    FALSE    83    M    GEO    sampleTitle:BLSA-1924-TCTX-CpG#patientID:BLSA-1924#postMortemIntervalH:6#tissueBank:BLSA#prep_hyb_batch:Z
#S_1578    I_1289    R_1567    GSM401773    GIBBS_BRAIN_QTL    Singleton    frontalCortex    brain    0    None    None    FALSE    FALSE    FALSE    45    M    GEO    sampleTitle:UMARY-4598-FCTX-CpG#patientID:UMARY-4598#postMortemIntervalH:6#tissueBank:UMARY#prep_hyb_batch:S
#S_2169    I_1725    R_2144    GSM532529    WALKER_MYELOMA    Morgan    boneMarrow    blood    0    TRUE    TRUE    FALSE    FALSE    FALSE    None    None    GEO    sampleTitle:Myeloma-159#cellType:CD138+_bone_marrow_cells
#S_2168    I_1724    R_2143    GSM532528    WALKER_MYELOMA    Morgan    boneMarrow    blood    0    TRUE    TRUE    FALSE    FALSE    FALSE    None    None    GEO    sampleTitle:Myeloma-158#cellType:CD138+_bone_marrow_cells

        #
        # Extract the information from these files into
         
        log(self.datasetSimpleName + ": initializing clinical data and scores in the local db ")       
                
        try:
            conn = sqlite3.connect(self.binaryFile)
            c = conn.cursor()
            c.execute('CREATE TABLE betas(sampleID TEXT, cpgID TEXT, beta FLOAT)')
            c.execute('CREATE TABLE clinical(sampleID TEXT,individualID TEXT,replicateGroupID TEXT,id_org TEXT,dataset TEXT,performingLab TEXT,cellType TEXT,tissueType TEXT,knownMutations TEXT,isDisease TEXT,isCancer TEXT,isCellLine TEXT,isPluripotent TEXT,isArtificialControl TEXT,age TEXT,sex TEXT,sourceDB TEXT,taggedString TEXT)')
            f = open(datasetClinicalDataFile)
            sampleLines = map(lambda x:x.split("\t"),f.readlines())
            f.close()
            sampleIDs = []
            if self.datasetInternalName == "IIAll":
                for i in xrange(1,len(sampleLines)):
                    sampleIDs.append(sampleLines[i][0])
                    if len(sampleLines[i]) != 18:
                        raise Exception, "length of line "+str(i)+"is not 18, but "+str(len(sampleLines[i]))+" with values "+str(sampleLines[i])
                    c.execute('INSERT INTO clinical VALUES ('+'?,'*17+'?)',tuple(sampleLines[i]))            
            else:
                for i in xrange(1,len(sampleLines)):
                    if sampleLines[i][4] == self.datasetInternalName:
                        sampleIDs.append(sampleLines[i][0])
                        if len(sampleLines[i]) != 18:
                            raise Exception, "length of line "+str(i)+"is not 18, but "+str(len(sampleLines[i]))+" with values "+str(sampleLines[i])
                        c.execute('INSERT INTO clinical VALUES ('+'?,'*17+'?)',tuple(sampleLines[i]))
            log( "Dataset "+ self.datasetInternalName+" has "+str(len(sampleIDs))+" samples")
                       
            #now initialize all the betas
            sampleHeaders = {}
            fb = open(datasetBetasFile)
            headers = fb.readline().strip().split("\t")
            for i in range(len(headers)):
                if headers[i] in sampleIDs:
                    sampleHeaders[i] = headers[i]
            sampleHeaderIndeces = sampleHeaders.keys()
            counter = 0 
            for line in fb:
                lineParts = line.strip().split("\t")
                for sampleIDIndex in sampleHeaderIndeces:
                    if lineParts[sampleIDIndex] == "NA":
                        c.execute('INSERT INTO betas VALUES (?,?,?)',(sampleHeaders[sampleIDIndex],lineParts[0],-1))
                    else:
                        c.execute('INSERT INTO betas VALUES (?,?,?)',(sampleHeaders[sampleIDIndex],lineParts[0],float(lineParts[sampleIDIndex])))
                    counter += 1
            log( "Dataset "+ self.datasetInternalName+" has "+str(counter)+" betas")                    
            fb.close()
            conn.commit()            
        except Exception,ex:
            log(["Error:",str(ex)])            
            c.close()
            conn.close()
            os.unlink(self.binaryFile)            
            raise ex        
        c.close()
        conn.close()
        log(self.datasetSimpleName + ": the dataset clinical data was preprocessed into local DB "+self.binaryFile)
        
    def preprocessCoordinatesFile(self):        
        if os.path.isfile(self.binaryRegionsFile):
            extext = self.datasetSimpleName + ": the dataset coordinates are laready preprocessed in  "+self.binaryRegionsFile
            log(extext)
            return
        # Preprocess the coordinates into a local file
        datasetCoordinatesFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetCoordinates)
        f = open(datasetCoordinatesFile)
        coordinateLines = map(lambda x:x.split("\t"),f.readlines())
        try:
            conn = sqlite3.connect(self.binaryRegionsFile)
            c = conn.cursor()
            c.execute('CREATE TABLE IIcoordinates (chrom INTEGER, start INTEGER, stop INTEGER, name TEXT, nextBase TEXT, distanceToTSS INTEGER, isCGI INTEGER)')
            for i in xrange(1,len(coordinateLines)):    
                chrom = convertChromToInt(self.genome,coordinateLines[i][8]) 
                start = int(coordinateLines[i][9])
                end = start+1
                name = coordinateLines[i][1]
                nextBase = coordinateLines[i][17]
                if coordinateLines[i][28] == "":
                    distanceToTSS = settings.MAX_DISTANCE
                else:
                    distanceToTSS = int(coordinateLines[i][28])
                isCGI = int(coordinateLines[i][29] == "TRUE")
                c.execute('INSERT INTO IIcoordinates VALUES (?,?,?,?,?,?,?)',(chrom,start,end,name,nextBase,distanceToTSS,isCGI))
            conn.commit()
        except Exception,ex:
            log("Error: "+str(ex))            
            c.close()
            conn.close()
            os.unlink(self.binaryRegionsFile)
            raise ex
            
        c.close()
        conn.close()
        log(self.datasetSimpleName + ": the dataset coordinates were preprocessed into local DB "+self.binaryRegionsFile)
            
    def preprocessDownloadedDataset(self):        
        if not self.hasAllDownloadedFiles():
           exText = self.datasetSimpleName + ": the dataset files are not downloadeded "
           log(exText)
           raise GDMException, exText
       
        if self.hasPreprocessedFile():
            #what to do if the data was already preprocessed
            extext = self.datasetSimpleName + ": the dataset was already preprocessed in "+self.binaryFile+" and "+self.binaryRegionsFile
            log(extext)
            return
        self.preprocessCoordinatesFile()
        self.preprocessClinicalAndBetaFile()
        log(self.datasetSimpleName + ": the dataset coordinates were preprocessed into local DB "+self.binaryRegionsFile)
        
    def initializePropertiesComputeStructures(self):
        # This regions shoudl not be computed as properties of other dataset and hence does not have compute structures 
        pass
    def getRegions(self):
        if not self.hasPreprocessedFile():
            self.preprocessDownloadedDataset()
        conn = sqlite3.connect(self.binaryRegionsFile)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM IIcoordinates")
        try:
            numberOfLines = c.fetchone()[0]                
            c.execute("SELECT DISTINCT chrom, start, stop FROM IIcoordinates")
            regions = numpy.zeros((numberOfLines,3),dtype=int)
            i = 0 
            for row in c:
                regions[i,0] = row[0]
                regions[i,1] = row[1]
                regions[i,2] = row[2]            
                i+=1
            c.close()
            conn.close()
        except:
            c.close()
            conn.close()
        maxIndex = i
        if maxIndex < numberOfLines:                        
            regionsNew = numpy.zeros((maxIndex,3),dtype=int)
            regionsNew = regions[0:maxIndex,:]
            return regionsNew
        else:            
            return regions
    
    def __convert_to_id__(self,row):
        return "_".join(map(str,row[1:4]))
    
    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):
        #log("II initializePropertiesStoreStructures start")
        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER,cpgID TEXT)")
        self.cpgIDs = {}
        conn = sqlite3.connect(self.binaryRegionsFile)
        c = conn.cursor()
        c.execute('SELECT name,chrom,start,stop FROM IIcoordinates ')
        for row in c:
            self.cpgIDs[self.__convert_to_id__(row)] = row[0]
        c.close()
        conn.close()        
        #log("II initializePropertiesStoreStructures end "+str(len(self.cpgIDs.keys())))
        
    def computeSingleRegionProperties(self,row, cgsAS):
        return [(row[0],self.cpgIDs[self.__convert_to_id__(row)])] 
    
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
        if not self.cpgData:
            log("II getRegionComputedDataFromExtractedLine init cpgData")
            conn = sqlite3.connect(self.binaryRegionsFile)
            c = conn.cursor()
            c.execute("SELECT name, nextBase, distanceToTSS, isCGI FROM IIcoordinates")
            for row in c:
                self.cpgData[row[0]] = row[1:4]
            c.close()
            conn.close
            log("II getRegionComputedDataFromExtractedLine init cpgData end "+str(len(self.cpgData.keys())))
        #regionID INTEGER, name TEXT
        # currently the family is not used        
        regionData = []                        
        
        regionData.append([result[1]])
        if self.withVariance:
            regionData.append(["II","var",result[1]])
        
        # store the next base            
        regionData.append(["II","nextbase",self.cpgData[result[1]][0]])
        #store the distance to TSS
        regionData.append(["II","distanceToTSS",self.cpgData[result[1]][1]])
        # store if it is CGI based on the II processing
        regionData.append(["II","isCGI",self.cpgData[result[1]][2]])
        
        return regionData
    
    def getWordsDescription(self):
        doc = []
        doc.append(["cg27655855","the name of the CpG",[]])
        doc.append(["II:nextbase:T","the next base is T",[]])
        doc.append(["II:distanceToTSS","Distance to TSS according to the II file",[]])        
        doc.append(["II:isCGI","if it is a CGI according to the II file",[]])
        return doc
    ## exportExtraData
    #
    # This method should be defined only for Datasets that returndat in addition to their 
    # regions and features such as gene descriptions or II scores
    # The expected return format is as follows
    # returnData := [[document title,document body,document link,document words], ...]                
    # document words := [[wordParts,score], ...]
    # wordParts := [wordPart1,wordPart2,wordPart3, ...]] 
    def exportExtraData(self,documentID,fdd,fwd,cgsAS):
        log("Exporting extra data for "+self.datasetSimpleName)
        document = []
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()
        #preprocessing the clinical information
        clinicalID = ["sampleID","individualID","replicateGroupID","id_org","dataset","performingLab","cellType","tissueType","knownMutations","isDisease","isCancer","isCellLine","isPluripotent","isArtificialControl","age","sex","sourceDB"]
        c.execute('SELECT * FROM clinical ORDER BY sampleID')
        sampleAllData = map(list,c.fetchall())
        
        sampleDocIDs = {}
        for sIndex in xrange(len(sampleAllData)):
            sample = sampleAllData[sIndex]
            sampleData = [[["IIS","sample"],"0"]]
            try:
                for i in xrange(len(clinicalID)):
                    if clinicalID[i] in ["sampleID","individualID","replicateGroupID","id_org","dataset","performingLab","cellType","tissueType","sourceDB"]:
                        clinicalValue = getSafeWord(str(sample[i]))
                    elif clinicalID[i] in  ["knownMutations"]:
                        clinicalValue = int(sample[i])
                    elif clinicalID[i] == "age":
                        if sample[i] == "None":
                            clinicalValue = "None"
                        else:
                            clinicalValue = wordFixed(int(round(float(sample[i]))),3)
                    elif clinicalID[i] in ["isDisease","isCancer","isCellLine","isPluripotent","isArtificialControl","sex"]:                    
                        # Only values are None,FALSE and TRUE
                        # Or None, M,F in the case of sex
                        clinicalValue = getSafeWord(str(sample[i]))
                    else:
                        raise Exception, "Error: Invalid clinical ID "+str(clinicalID[i])
                        
                    sampleData.append([["IIS",clinicalID[i],clinicalValue],"0"])    
                                        
            except:
                log([sIndex,i,clinicalID[i],str(sample[i])])
                raise
            
            document = [sample[0],"","",sampleData]            
            wdbuffer = ""
            ddbuffer = ""            
            documentID += 1             
            # extraData := [[document title,document body,document link,document words], ...]                
            # document words := [[wordParts,score], ...]
            # wordParts := [wordPart1,wordPart2,wordPart3, ...]]             
            for wordInfo in document[3]:
                wdbuffer += "\t".join([":".join(map(str,wordInfo[0])),str(documentID),str(wordInfo[1]),"0\n"])
            fdd.write("\t".join([str(documentID),"u:"+str(document[2]),"t:"+document[0],"H:"+document[0]+"\n"]))
            fwd.write(wdbuffer)
            sampleDocIDs[sample[0]] = str(documentID)
        log([sample[0],documentID])
        #process all betas 
        c.execute('SELECT sampleID, cpgID, beta FROM betas')
        stored = []       
        count = 0 
        for score in c:
            count += 1
            if score[2] >= 0:
                stored.append(score)
                if self.withVariance:
                    # adding the varinace word for this CpG with the variance score
                    stored.append([score[0],"II:var:"+score[1],(score[2]*score[2])])
                if count % 100000 == 0:
                    print count                
                    fwd.write("\n".join(map(lambda x:"\t".join([x[1],sampleDocIDs[x[0]],str(int(100*x[2])),"0"]),stored))+"\n")
                    stored = []
        fwd.write("\n".join(map(lambda x:"\t".join([x[1],sampleDocIDs[x[0]],str(int(round(100*x[2]))),"0"]),stored))+"\n")
        stored = []
        c.close()
        conn.close()
        
        log("Extra data exported for "+self.datasetSimpleName)   
        return documentID
    
    
    def getDefaultAnnotationSettings(self):        
        # obtain the default settings
        settings = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settings["hasGenomicRegions"] = self.hasGenomicRegions
        settings["hasFeatures"] = self.hasFeatures
        #retrun them
        return settings
    
    
# Exmaple queries to this server
# this query shows all the II words for the loci
# http://infao3806:8912/?q=II:*&h=0&c=10
# These are the cpgs that according to the table are not in CGI, but CGS shows them in CGI  
# http://infao3806:8912/?q=II:isCGI:0%20Eoverlaps:ucscCGI%20cg*&h=20&c=10

# All words about the samples 
# http://infao3806:8912/?q=IIS:*&h=0&c=10
# selecting only disease datasets and show sample IDS
# http://infao3806:8912/?q=IIS:isDisease:True IIS:samp*&h=0&c=10

# AND THIS IS THE MAJOR ONE, SHOW THE AVERAGE BETAS FOR THE cpgs that have controversial CGI status, BUT ONLY for the disease samples
# http://infao3806:8890/?q=[IIS:isDisease:True cg*#II:isCGI:0 Eoverlaps:ucscCGI cg*]&h=0&c=10


        