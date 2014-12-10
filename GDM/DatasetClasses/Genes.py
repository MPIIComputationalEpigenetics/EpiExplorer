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
import settings
import Dataset
import IntervalTree
import gzip
import subprocess


class Genes(Dataset.Dataset):
    
    def init(self,initCompute=True): 
        self.datasetCoordinatesFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetCoordinatesFile)
        if self.geneProperty == "exons":
            self.datasetExonsFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetExonsFile)
            self.geneExons = {}
        if self.geneProperty == "genes":
            self.datasetTranscriptsFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetTranscriptsFile)            
            self.datasetDescriptionsFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetDescriptionsFile)
            self.includeGO = bool(int(self.includeGO))
            #if self.includeGO:
            self.datasetGOBPFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetGOBPFile)
            self.datasetGOCCFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetGOCCFile)
            self.datasetGOMFFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetGOMFFile)
            self.includeOMIM = bool(int(self.includeOMIM))
            if self.includeOMIM:
                self.datasetOMIMgeneFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetOMIMgeneFile)
                self.datasetOMIMmorbidFile = os.path.abspath(settings.downloadDataFolder[self.genome] + self.datasetOMIMmorbidFile)
            self.goOntology = os.path.abspath(settings.downloadDataFolder[self.genome] + self.goOntology)
                        
            self.includeGenesUpTo = int(self.includeGenesUpTo)
            
            
            self.includeGeneDescriptions = bool(int(self.includeGeneDescriptions))
            self.includeGeneTranscripts = bool(int(self.includeGeneTranscripts))
        self.geneLocations = {}
        self.genePropertiesInitiated = False        
        self.useScore = False
        self.useStrand = True
        
        Dataset.Dataset.init(self,initCompute)
        self.initialized = True   
        
        
        self.stopWords = {"OF":True,
                          "TO":True,
                          "IN":True,
                          "BY":True,
                          "OR":True,
                          "ON":True,
                          "AND":True,
                          "VIA":True,
                          "AS":True,
                          "A":True,
                          "1":True,
                          "2":True,
                          "AT":True,
                          "THE":True,
                          "FROM":True,
                          "T":True,
                          "B":True,
                          "S":True,
                          "2":True,
                          "3":True,
                          "4":True,
                          "5":True,
                          "I":True,
                          "II":True,
                          "TISSUE":True,#special word in the frontend
                          "OVERLAP":True,#special word in the frontend
                          }     
    
        
    
#    def __extractRegionsFor_Property_FromLine__Old(self, lineParts, cursor):        
#        if self.geneProperty == "genes":
#            self.__extractRegionsFor_Genes_FromLine__Old(lineParts, cursor)                        
#        elif self.geneProperty == "TSS":
#            self.__extractRegionsFor_TSS_FromLine__Old(lineParts, cursor)            
#        elif "promoters" in self.geneProperty:
#            self.__extractRegionsFor_Promoters_FromLine__Old(lineParts, cursor)            
#        elif self.geneProperty == "exons":
#            self.__extractRegionsFor_Exons_FromLine__Old(lineParts, cursor)            
#        elif self.geneProperty == "introns":
#            self.__extractRegionsFor_Introns_FromLine__Old(lineParts, cursor)            
#        else:
#            extext = self.datasetSimpleName+": Property "+self.geneProperty+" is currently unsupported"
#            log(extext)
#            raise GDMException, extext
#    def __extractRegionsFor_Genes_FromLine__Old(self,lineParts, cursor):
#        geneName = lineParts[self.geneNameIndex]
#        if not self.geneLocations.has_key(geneName):
#            if self.geneTrnascriptsRev.has_key(lineParts[self.transcriptNameIndex]) and self.geneLocations.has_key(self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]):
#                geneName = self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]
#            else:
#                return
#                
#                #raise GDMException, "No gene location data for "+geneName
#        if self.geneLocations.has_key(geneName):
#            if self.geneLocations[geneName][4]:
#                #This gene has already been processed
#                return
#        else:
#            raise GDMException, "No gene location data for "+geneName
#            print "No gene location data for "+geneName
#        self.geneLocations[geneName][4] = True
#            
#        cursor.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?, ?, ?, ?, ?)',
#                       tuple([self.geneLocations[geneName][0],
#                             self.geneLocations[geneName][1],
#                             self.geneLocations[geneName][2],
#                             self.geneLocations[geneName][3],                             
#                             getSafeWord(geneName)]))
#        
#        #initialize gene descriptions 
#        if self.includeGeneDescriptions:
#            cursor.execute('INSERT INTO gene_descriptions VALUES (?, ?, ?)',
#                           tuple([getSafeWord(geneName),
#                                  self.geneDescriptions[geneName][0],
#                                  self.geneDescriptions[geneName][1]]))                
#        if self.includeGeneTranscripts: 
#            for geneTrnascript in self.geneTrnascripts[geneName]:
#                cursor.execute('INSERT INTO gene_transcripts VALUES (?, ?)',
#                               tuple([getSafeWord(geneName),geneTrnascript]))                                  
#                
#        if self.includeGO:
#            for goCategory in ["BP","CC","MF"]:
#                if not self.geneGOs.has_key(geneName) or not self.geneGOs[geneName].has_key(goCategory):
#                    continue
#                for goTerm in self.geneGOs[geneName][goCategory]:
#                    cursor.execute('INSERT INTO gene_GOs VALUES (?, ?, ?)',
#                               tuple([getSafeWord(geneName),goTerm,goCategory]))
#            
#        
#    def __extractRegionsFor_TSS_FromLine__Old(self, lineParts, cursor):
#        geneName = lineParts[self.geneNameIndex]
#        if not self.geneLocations.has_key(geneName):
#            if self.geneTrnascriptsRev.has_key(lineParts[self.transcriptNameIndex]) and self.geneLocations.has_key(self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]):
#                geneName = self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]
#            else:
#                return
#                #raise GDMException, "No gene location data for "+geneName
#        if self.geneLocations.has_key(geneName):
#            if self.geneLocations[geneName][4]:
#                #This gene has already been processed
#                return
#        else:
#            raise GDMException, "No gene location data for "+geneName
#            print "No gene location data for "+geneName
#            self.geneLocations[geneName] = [convertChromToInt(self.genome,lineParts[self.chromIndex]),lineParts[self.chromStartIndex],
#                                            lineParts[self.chromEndIndex],lineParts[self.strandIndex],
#                                            False]
#        if self.geneLocations[geneName][3] == 1:        
#            tssS =  self.geneLocations[geneName][1]
#            tssE =  self.geneLocations[geneName][1]+1
#        elif self.geneLocations[geneName][3] == -1:
#            tssS =  self.geneLocations[geneName][2]-1
#            tssE =  self.geneLocations[geneName][2]
#        else:
#            raise GDMException, "Invalid strand "+str(self.geneLocations[geneName][3]) 
#        tssS,tssE = getCorrectedCoordinates(self.genome,self.geneLocations[geneName][0],tssS,tssE)
#        cursor.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?, ?, ?, ?,  ?)',
#                       tuple([lineParts[self.chromIndex],
#                              tssS,
#                              tssE,
#                              lineParts[self.strandIndex],                              
#                              getSafeWord(geneName)]))
#        self.geneLocations[geneName][4] = True
#        
#    def __extractRegionsFor_Promoters_FromLine__Old(self, lineParts, cursor):
#        geneName = lineParts[self.geneNameIndex]
#        if not self.geneLocations.has_key(geneName):
#            if self.geneTrnascriptsRev.has_key(lineParts[self.transcriptNameIndex]) and self.geneLocations.has_key(self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]):
#                geneName = self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]
#            else:
#                return
#                
#                #raise GDMException, "No gene location data for "+geneName
#        if self.geneLocations.has_key(geneName):
#            if self.geneLocations[geneName][4]:
#                #This gene has already been processed
#                return
#        else:
#            raise GDMException, "No gene location data for "+geneName
#            print "No gene location data for "+geneName
#            self.geneLocations[geneName] = [convertChromToInt(self.genome,lineParts[self.chromIndex]),lineParts[self.chromStartIndex],
#                                            lineParts[self.chromEndIndex],lineParts[self.strandIndex],
#                                            False]
#        if self.geneLocations[geneName][3] == 1:        
#            start =  self.geneLocations[geneName][1] + self.promoterStartWrtTSS
#            end =  self.geneLocations[geneName][1] + self.promoterEndWrtTSS
#        elif self.geneLocations[geneName][3] == -1:
#            start =  self.geneLocations[geneName][2] - self.promoterEndWrtTSS
#            end =  self.geneLocations[geneName][2] - self.promoterStartWrtTSS
#        else:
#            raise GDMException, "Invalid strand "+str(self.geneLocations[geneName][3])
#        try:
#            start,end = getCorrectedCoordinates(self.genome,lineParts[self.chromIndex],start,end)
#        except:
#            print geneName,self.geneLocations[geneName],lineParts
#            raise
#        cursor.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?, ?, ?, ?, ?)',
#                       tuple([lineParts[self.chromIndex],
#                              start,
#                              end,
#                              lineParts[self.strandIndex],                              
#                              getSafeWord(geneName)]))
        
#    def __extractRegionsFor_Exons_FromLine__Old(self,lineParts, cursor):
#        geneName = lineParts[self.geneNameIndex]
#        if not self.geneLocations.has_key(geneName):
#            if self.geneTrnascriptsRev.has_key(lineParts[self.transcriptNameIndex]) and self.geneLocations.has_key(self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]):
#                geneName = self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]
#            else:
#                return
##                self.geneLocations[geneName] = [convertChromToInt(self.genome,lineParts[self.chromIndex]),lineParts[self.chromStartIndex],
##                                            lineParts[self.chromEndIndex],lineParts[self.strandIndex],
##                                            False]
#                #raise GDMException, "No gene location data for "+geneName
#        if not self.geneLocations[geneName][4]:                
#            self.geneLocations[geneName][4] = {}
#        
#        exonStarts = lineParts[self.exonStartsIndex][:-1].split(",")
#        exonEnds = lineParts[self.exonEndsIndex][:-1].split(",")            
#        if len(exonStarts) != len(exonStarts):
#            raise GDMException, "Unmatching exon start and exon end sites" +str(lineParts)
#        for i in range(len(exonStarts)):
#            exonID = str(exonStarts[i])+":"+str(exonEnds[i])
#            if self.geneLocations[geneName][4].has_key(exonID):
#                # this exon was already preprocessed
#                continue                
#            cursor.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?, ?, ?, ?, ?)',
#                           tuple([lineParts[self.chromIndex],
#                                  exonStarts[i],
#                                  exonEnds[i],
#                                  lineParts[self.strandIndex],                                  
#                                  getSafeWord(geneName)]))
#            #save it as processed
#            self.geneLocations[geneName][4][exonID] = True
#            
#    def __extractRegionsFor_Introns_FromLine__Old(self,lineParts, cursor):
#        geneName = lineParts[self.geneNameIndex]
#        if not self.geneLocations.has_key(geneName):
#            if self.geneTrnascriptsRev.has_key(lineParts[self.transcriptNameIndex]) and self.geneLocations.has_key(self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]):
#                geneName = self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]
#            else:
#                return
#                
#                #raise GDMException, "No gene location data for "+geneName
#        if self.geneLocations.has_key(geneName):
#            if not self.geneLocations[geneName][4]:                
#                self.geneLocations[geneName][4] = {}
#        else:
#            raise GDMException, "No gene location data for "+geneName
#        #chrom , start , stop , strand , count , geneName 
#        exonStarts = lineParts[self.exonStartsIndex][:-1].split(",")
#        exonEnds = lineParts[self.exonEndsIndex][:-1].split(",")
#        if len(exonStarts) != len(exonStarts):
#            raise GDMException, "Unmatching exon start and exon end sites" +str(lineParts)
#        for i in range(1,len(exonStarts)):
#            intronID = str(exonEnds[i-1])+":"+str(exonStarts[i])
#            if self.geneLocations[geneName][4].has_key(intronID):
#                # this intron was already preprocessed
#                continue            
#            cursor.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?, ?, ?, ?, ?)',
#                           tuple([lineParts[self.chromIndex],
#                                  exonEnds[i-1],
#                                  exonStarts[i],
#                                  lineParts[self.strandIndex],                                  
#                                  getSafeWord(geneName)]))
#            #save it as processed
#            self.geneLocations[geneName][4][intronID] = True
            
    
            
    def initializePropertiesStoreStructures(self, cgsAS, dataConnections):
        # INTTREE -> BEDTOOLS START
        #dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, overlap_count INTEGER, distance_upstream INTEGER, distance_downstream INTEGER, strand INTEGER, isofType INTEGER, geneName TEXT)")
        dataConnections[0][1].execute("CREATE TABLE " + self.datasetSimpleName + "_data (regionID INTEGER, overlap_ratio REAL, min_distance INTEGER, strand INTEGER, geneName TEXT)")
        # INTTREE -> BEDTOOLS END
        # also fetch gene names structure        
        dataConnections[1][1].execute("SELECT chrom, start, stop, strand, geneName FROM "+self.datasetSimpleName+" ORDER BY chrom,start,stop")
        currentLocalRegionRow = dataConnections[1][1].fetchone()
        
        #currentLocalRegionRow = cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"localRegionRow")        
        cgsAS.setFeatureDatasetProperty(self.datasetSimpleName,"localRegionRow",currentLocalRegionRow)
        cgsAS.setFeatureDatasetProperty(self.datasetSimpleName,"localRegionCursor",dataConnections[1][1])        
        
        log(self.datasetSimpleName+": Before annotate with bed")
        
        fnBed =  getRegionsCollectionName(cgsAS.datasetCollectionName,self.genome)[:-8]+".bed"
        annotatefnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".annotated"
        closestfnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".closest"
        if not os.path.isfile(annotatefnBed):
            annotateCommand = settings.bedToolsFolder+"annotateBed -i "+fnBed+" -files "+self.getBedFile()+" > "+annotatefnBed        
            log(annotateCommand)
            subprocess.Popen(annotateCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        f = open(annotatefnBed)
        for rl in f:
            rlParts = rl.strip().split("\t")
            # the previous indeces are chrom, start,end, id, score,strand,annotate            
            cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["data"][int(rlParts[3])] = [float(rlParts[6]),0,[]]
        f.close()
        if not os.path.isfile(closestfnBed):
            closestCommand = settings.bedToolsFolder+"closestBed -a "+fnBed+" -b "+self.getBedFile()+" -d "+" > "+closestfnBed
            log(closestCommand)        
            subprocess.Popen(closestCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        f = open(closestfnBed)
        for rl in f:
            rlParts = rl.strip().split("\t")
            if int(rlParts[-1]) > -1:
                cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["data"][int(rlParts[3])][1] = int(rlParts[-1])
            else:
                cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["data"][int(rlParts[3])][1] = settings.MAX_DISTANCE
        f.close()
        if self.geneProperty == "genes":
            windowfnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".windowed"
            if not os.path.isfile(windowfnBed):
                windowCommand = settings.bedToolsFolder+"windowBed -a "+fnBed+" -b "+self.getBedFile()+" -l "+str(self.includeGenesUpTo+1)+" -r "+str(self.includeGenesUpTo)+" > "+windowfnBed            
                log(windowCommand)
                subprocess.Popen(windowCommand,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
            f = open(windowfnBed)
            for rl in f:
                rlParts = rl.strip().split("\t")
                cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["data"][int(rlParts[3])][2].append(rlParts[-3])
            f.close()
        log(self.datasetSimpleName+": After annotate with bed")
        

    
    def initializePropertiesComputeStructures(self):
        # INTTREE -> BEDTOOLS START
#        log(self.datasetSimpleName+": Computing interval tree")        
#        localRegionsConn = sqlite3.connect(self.binaryFile)
#        localRegionsCursor = localRegionsConn.cursor()
#        # extract the regions from the gene region data as they have there gene names also
#        localRegionsCursor.execute("SELECT chrom, start, stop, strand, geneName FROM "+self.datasetSimpleName+" ORDER BY chrom,start,stop")
#        
#        try:
#            self.intervalTree = IntervalTree.GenomeIntervalTree()
#            datasetRegions = []
#            currentChrom = None
#            for row in localRegionsCursor:
#                i = IntervalTree.Interval(row)
#                i.strand = str(row[3])            
#                i.geneName = str(row[4])                                     
#                if currentChrom != i.chrom:
#                   if currentChrom == None:
#                       currentChrom = i.chrom
#                   else:
#                       self.intervalTree.addChromosomeArray(currentChrom,datasetRegions)
#                       datasetRegions = []     
#                       currentChrom = i.chrom           
#                datasetRegions.append(i)            
#            self.intervalTree.addChromosomeArray(currentChrom,datasetRegions)        
#            log(self.datasetSimpleName+": interval tree computed")
#        except:
#            localRegionsCursor.close()
#            localRegionsConn.close()
#            raise
#        localRegionsCursor.close()
#        localRegionsConn.close()
        # INTTREE -> BEDTOOLS END
        #inititiate gene properties if needed
        if self.genePropertiesInitiated == False:
            self.__initGeneProperties__()
        
         
        
        
    def openDBConnections(self,cgsAS):                        
        regionsData = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)                
        connData = sqlite3.connect(regionsData)
        cD = connData.cursor()
        localRegionsConn = sqlite3.connect(self.binaryFile)
        localRegionsCursor = localRegionsConn.cursor()        
        return [[connData,cD],[localRegionsConn,localRegionsCursor]] 
         
        
    def closeDBConnections(self,dataConnections):
        try:
            dataConnections[0][1].close()        
            dataConnections[0][0].close()
        except:
            pass        
        # also close the local regions structure
        try:
            dataConnections[1][1].close()
            dataConnections[1][0].close()
        except:
            pass
    
    def cleanup(self,cgsAS): 
        # INTTREE -> BEDTOOLS START
        #del self.intervalTree
        # INTTREE -> BEDTOOLS END
        annotatefnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".annotated"
        if os.path.isfile(annotatefnBed):
            os.unlink(annotatefnBed)
        closestfnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".closest"
        if os.path.isfile(closestfnBed):
            os.unlink(closestfnBed)
        windowfnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".windowed"
        if os.path.isfile(windowfnBed):
            os.unlink(windowfnBed)
        windowfnBed = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)[:-8]+".windowed"
        if os.path.isfile(windowfnBed):
            os.unlink(windowfnBed)            
        sqlite3Data = getDatasetDataName(cgsAS.datasetCollectionName, self.genome, self.datasetSimpleName)
        if os.path.isfile(sqlite3Data):
            os.unlink(sqlite3Data)
                
    def getRegions(self):
        return self.getRegionsFromLocalBED(self.getBedFile())         
    
    def computeSingleRegionProperties(self, row, cgsAS):   
        results = []     
        # result: regionID, overlap_ratio, overlap_count,distance_upstream, 
        #         distance_downstream, strand, isofType, geneName
        # row : regionID, chrom, start, stop, datasetID
        # localRegionRow: chrom, start, stop, strand, geneName        
        if row[4] == self.__getDatasetId__(cgsAS):
            isofType = 1
            atLeastOne =  False
            currentLocalRegionRow = cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"localRegionRow")
            localRegionsCursor = cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"localRegionCursor")                                 
            
            if currentLocalRegionRow[0] == row[1] and currentLocalRegionRow[1] == row[2] and currentLocalRegionRow[2] == row[3]:
                atLeastOne = True                
                results.append((row[0],1,0,currentLocalRegionRow[3],currentLocalRegionRow[4]))               
                currentLocalRegionRow = localRegionsCursor.fetchone()                
                #if not currentLocalRegionRow:
                #    break
                    
            cgsAS.setFeatureDatasetProperty(self.datasetSimpleName,"localRegionRow",currentLocalRegionRow)
            if not atLeastOne:
                raise GDMException, "Somehow they are not synchronized "+str(currentLocalRegionRow) + " "+str(row)+" "+str(self.geneProperty)
        else:
            if self.geneProperty != "genes":
                self.__computeSingleRegionPropertiesNotOfTypeNotGene__(row, results, cgsAS)
            else:
                self.__computeSingleRegionPropertiesNotOfTypesGenes__(row, results, cgsAS)          
                
        return results  
    
    def __computeSingleRegionPropertiesNotOfTypesGenes__(self, row, results, cgsAS):
        isofType = 0
        chrom = row[1]
        start = row[2]
        stop = row[3]        
        # INTTREE -> BEDTOOLS START
        overlap_ratio = cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["data"][row[0]][0]
        mindistance = cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["data"][row[0]][1]                
    
        results.append((row[0],overlap_ratio, 
                        mindistance,
                         0,#strand                         
                         ""))#gene name 
        for geneName in cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["data"][row[0]][2]:
        
          results.append((row[0],1,
                          0,#distance upstream 
                          self.geneLocations[geneName][3],#strand of the gene
                          str(geneName)))
        
        # INTTREE -> BEDTOOLS START
#        addedOverlapInfo = {}     
#        overlapingRegionsInterval = self.intervalTree.find(chrom, start, stop)
#        if len(overlapingRegionsInterval) > 0:
#            # The regions overlaps
#            overlap_count = len(overlapingRegionsInterval)
#            for gene in overlapingRegionsInterval:                
#                overlap_ratio_gene = gr_Coverage([[gene.start,gene.stop]], start, stop) / float(stop - start)
#                results.append((row[0], 
#                         overlap_ratio_gene, 
#                         1,#overlap count 
#                         0,#distance upstream 
#                         0,#distance downstream
#                         gene.strand,#strand of the gene                          
#                         isofType, 
#                         str(gene.geneName)))
#                addedOverlapInfo[gene.geneName] = True
#                try:
#                    self.bedData[row[0]][2].index(gene.geneName)
#                except Exception, ex:
#                    print ex
#                    raise GDMValueException, str(row)+str(self.bedData[row[0]])+" gene:"+str(gene.geneName)
#                    
##                print "Added",gene.geneName,[gene.start,gene.stop,gene.strand],overlap_ratio_gene,[chrom,start,stop],self.geneLocations[str(gene.geneName)]
#            
#            reducedGRInterval = gr_reduceRegionSetInterval(overlapingRegionsInterval)
#            overlap_ratio = gr_Coverage(reducedGRInterval, start, stop) / float(stop - start)
#            if numpy.abs(self.bedData[row[0]][0] - overlap_ratio) > 0.00001 or self.bedData[row[0]][1] != 0:
#                raise GDMValueException, str(row)+str(self.bedData[row[0]])+" or:"+str(overlap_ratio)
#            distance_upstream = 0
#            distance_downstream = 0
#        else:
#            overlap_ratio = 0
#            overlap_count = 0
#            resultUpInterval = self.intervalTree.getLargestStop(chrom, start)
#            if resultUpInterval:
#                distance_upstream = start - resultUpInterval.stop
#            else:
#                distance_upstream = settings.MAX_DISTANCE
#                #                   print "upstream",resultUp,distance_upstream
#            resultDownInterval = self.intervalTree.getSmallestStart(chrom, stop)
#            if resultDownInterval:
#                distance_downstream = resultDownInterval.start - stop
#            else:
#                distance_downstream = settings.MAX_DISTANCE
#            if self.bedData[row[0]][0] != 0 or self.bedData[row[0]][1] != min(distance_upstream,distance_downstream):
#                raise GDMValueException, str(row)+str(self.bedData[row[0]])+"u: "+str(distance_upstream)+" d:"+str(distance_downstream)
#        overlap_ratio = self.bedData[row[0]][0]
#        mindistance = self.bedData[row[0]][1]        
#            
#        results.append((row[0],overlap_ratio,0, 
#                        mindistance,0,
#                         0,#strand
#                         isofType,
#                         ""))#gene name
#        #this is the database line with general info. Only distance to closes and total overlap ratio                
#        results.append((row[0], 
#                         overlap_ratio, 
#                         overlap_count, 
#                         distance_upstream, 
#                         distance_downstream,
#                         0,#strand                          
#                         isofType, 
#                         ""))#gene name
#        # If we are supposed to contain extended information
##        if not hasattr(self,"countPrints"):            
##            self.countPrints = 0
#        if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGenesUpTo") > 0:            
#            extendedStart = start - cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGenesUpTo")
#            extededStop =  stop +  cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGenesUpTo")
#            extendedStart,extededStop = getCorrectedCoordinates(self.genome,chrom,extendedStart,extededStop)
#            overlapingRegionsInterval = self.intervalTree.find(chrom, extendedStart,extededStop)            
#            for gene in overlapingRegionsInterval:                
#                if addedOverlapInfo.has_key(gene.geneName):
#                    # this gene was already added as overlapping with the original region
#                    continue
#                if gene.stop <  start:
#                    distance_upstream = start - gene.stop
#                    distance_downstream = settings.MAX_DISTANCE
#                elif gene.start >= stop:
#                    distance_upstream = settings.MAX_DISTANCE
#                    distance_downstream = gene.start - stop + 1
#                else:
#                    raise GDMException,"Invalid gene start,stop found"+ str([gene.geneName,gene.start,gene.stop])+str([extendedStart,start,stop,extededStop])+str(addedOverlapInfo.keys())                    
#                results.append((row[0], 
#                         0, 
#                         0,#overlap count 
#                         distance_upstream,#distance upstream 
#                         distance_downstream,#distance downstream
#                         gene.strand,#strand of the gene                          
#                         isofType, 
#                         gene.geneName))
#                addedOverlapInfo[gene.geneName] = True
#                try:
#                    self.bedData[row[0]][2].index(gene.geneName)
#                except Exception, ex:
#                    print ex
#                    raise GDMValueException, str(row)+str(self.bedData[row[0]])+" gene:"+str(gene.geneName)
##                print "Added nearby genes",gene.geneName,distance_upstream,distance_downstream,[chrom,extendedStart,start,stop,extededStop],self.geneLocations[gene.geneName]
##                self.countPrints += 1
##                if self.countPrints > 20:
##                    raise GDMException, "Check the pintouts"
        # INTTREE -> BEDTOOLS END
            
        
    def __computeSingleRegionPropertiesNotOfTypeNotGene__(self, row, results, cgsAS):
        isofType = 0
        chrom = row[1]
        start = row[2]
        stop = row[3]
        # INTTREE -> BEDTOOLS START            
        overlap_ratio = cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["data"][row[0]][0]
        mindistance = cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["data"][row[0]][1]       
             
        results.append((row[0],overlap_ratio,mindistance,
                        0,#strand                         
                         ""))#gene name   
        # INTTREE -> BEDTOOLS START
#        overlapingRegionsInterval = self.intervalTree.find(chrom, start, stop)
#        if len(overlapingRegionsInterval) > 0:
#            # The regions overlaps
#            overlap_count = len(overlapingRegionsInterval)            
#            
#            reducedGRInterval = gr_reduceRegionSetInterval(overlapingRegionsInterval)
#            overlap_ratio = gr_Coverage(reducedGRInterval, start, stop) / float(stop - start)
#            distance_upstream = 0
#            distance_downstream = 0
#            if numpy.abs(self.bedData[row[0]][0] - overlap_ratio) > 0.00001 or self.bedData[row[0]][1] != 0:
#                raise GDMValueException, str(row)+str(self.bedData[row[0]])+" or:"+str(overlap_ratio)
#        else:
#            overlap_ratio = 0
#            overlap_count = 0
#            resultUpInterval = self.intervalTree.getLargestStop(chrom, start)
#            if resultUpInterval:
#                distance_upstream = start - resultUpInterval.stop
#            else:
#                distance_upstream = settings.MAX_DISTANCE
#                #                   print "upstream",resultUp,distance_upstream
#            resultDownInterval = self.intervalTree.getSmallestStart(chrom, stop)
#            if resultDownInterval:
#                distance_downstream = resultDownInterval.start - stop
#            else:
#                distance_downstream = settings.MAX_DISTANCE  
#            if self.bedData[row[0]][0] != 0 or self.bedData[row[0]][1] != min(distance_upstream,distance_downstream):
#                raise GDMValueException, str(row)+str(self.bedData[row[0]])+"u: "+str(distance_upstream)+" d:"+str(distance_downstream)
#        results.append((row[0],overlap_ratio,overlap_count, 
#                        distance_upstream,distance_downstream,
#                         0,#strand
#                         isofType,
#                         ""))#gene name 
        # INTTREE -> BEDTOOLS END
        
         
    
    
    def getRegionComputedDataFromExtractedLine(self, result, cgsAS):
        # regionID, overlap_ratio, overlap_count, 
        # distance_upstream, distance_downstream, strand, 
        # isofType, geneName 
        #ensembl_gene_TSS [1, 0.00034818941504178273, 1, 0, 0, 0, 0, u'']
        # INTTREE -> BEDTOOLS START
        # regionID, overlap_ratio, 
        # min_distance, strand, 
        # geneName 
        #ensembl_gene_TSS [1, 0.00034818941504178273, 0, 0, u'']
        # INTTREE -> BEDTOOLS END
        
        regionData = []       
        regionDataWithScores = [] 
        strand = int(result[3])        
        # INTTREE -> BEDTOOLS START
#        if result[6] == 1: # is of type
#            # overlaps with at least one
#            # the next 3 should always be included
#            regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName])
#            if result[1] > 0.1:
#                regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName])
#            if result[1] > 0.5:
#                regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName])
#                
#            #score overlap count an integer score
#            #score overlap ratio between 00--99
#            #regionData.append([settings.wordPrefixes["overlapCount"],self.datasetWordName,result[2]])
#            #score overlap ratio an integer score
#            regionData.append([settings.wordPrefixes["overlapRatio"],self.datasetWordName,wordFloat(result[1],2)])
#            # the associated gene name
#            # INTTREE -> BEDTOOLS START
#            if result[4]:#has gene name
#                regionData.append([settings.wordPrefixes["geneName"],result[4]])
#                if strand == 1:
#                    regionData.append([settings.wordPrefixes["strand"],self.datasetWordName,"plus"])
#                elif strand == -1:
#                    regionData.append([settings.wordPrefixes["strand"],self.datasetWordName,"minus"])
#                else:
#                    #gene name but no strand
#                    raise GDMException, "Error: No strand specified"            
#            else:
#                # no gene name
#                raise GDMException, "Error: No gene name specified for a 'ofType' column"
#            # the count for exons and introns temporary removed
##            if self.geneProperty == "exons" or self.geneProperty == "introns":
##                regionData.append([settings.wordPrefixes["enumerationOfElements"],self.datasetWordName,result[5]])
#            # the region type is already stored in the regions database so we don't need to include it here
#        else:# is not of type, some other region
        # INTTREE -> BEDTOOLS END
        if result[4] and strand and self.geneProperty == "genes":
                # this is a report of a nearby or overlapping gene
                # we should list the properties for this gene so that it is searchable via join                 
#                if self.geneProperty == "genes":                    
                    geneName = result[4]
                    
                    cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["genenames"][geneName] = {}
                    #closest gene name
                    regionData.append([settings.wordPrefixes["geneName"],geneName])
#                    if strand == 1:
#                        regionData.append([settings.wordPrefixes["geneStrand"],"plus",geneName])
#                    elif strand == -1:
#                        regionData.append([settings.wordPrefixes["geneStrand"],"minus",geneName])
                    # check if the gene overlaps with the region
#                    if result[2] > 0:#should be 1 if overlaps and 0 ow
#                         regionData.append([settings.wordPrefixes["geneOverlap"],geneName])
                         
#                         regionData.append([settings.wordPrefixes["geneOverlapRatio"],wordFloat(result[1],2),geneName])                         
                    #add also the distance to gene words
                    # INTTREE -> BEDTOOLS START
#                    if result[4] < settings.MAX_DISTANCE:
#                        dd  = wordMagnitude(result[4])
##                        regionData.append([settings.wordPrefixes["geneDistanceDownstream"],dd,geneName])
#                    if result[3] < settings.MAX_DISTANCE:
#                        du  = wordMagnitude(result[3])
##                        regionData.append([settings.wordPrefixes["geneDistanceUpstream"],du,geneName])
#                    dm  = -1                    
#                    if result[4] < result[3]:
#                        dm = dd                        
#                    elif result[3] < result[4]:
#                        dm = du                        
#                    elif result[3] < settings.MAX_DISTANCE:
#                        dm = du
#                        
#                    if dm != -1:
#                        regionData.append([settings.wordPrefixes["geneDistance"],dm,geneName])
#                        try:
#                            cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["genenames"][geneName][dm] = True
#                        except:
#                            cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["genenames"][geneName] = {}
#                            cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["genenames"][geneName][dm] = True
                    if cgsAS.featuresDatasets[self.datasetSimpleName]["includeGO"]:
                        #include the GOs for this region
                        if self.geneGOs.has_key(geneName):
                            if not cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["regionGOs"].has_key(result[0]):
                                cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["regionGOs"][result[0]] = {} 
                            for geneGO in self.geneGOs[geneName]["all"]:
                                if not cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["regionGOs"][result[0]].has_key(geneGO):
                                    cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["regionGOs"][result[0]][geneGO] = True
                                    regionData.append([settings.wordPrefixes["geneGOterm"],geneGO])                                    
                                    #regionDataWithScores.append([[settings.wordPrefixes["geneGOterm"],geneGO],getWordGOscore(self.fullGO[geneGO][2]),"0"])
                    if cgsAS.featuresDatasets[self.datasetSimpleName]["includeOMIM"]:
                        #include the OMIMs for this region
                        if self.geneOMIMs.has_key(geneName):
                            for geneOMIM in self.geneOMIMs[geneName]:
                                cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["OMIMs"][geneOMIM] = True                                
                                regionData.append([settings.wordPrefixes["omimTermID"],geneOMIM])                                
                                #regionDataWithScores.append([[settings.wordPrefixes["omimTermID"],geneOMIM],getWordOMIMscore(self.fullOMIM[geneOMIM][1]),"0"])
                                                            
                        
#                else:
#                    raise GDMException, "Gene name and strand should be provided only for genes if not 'ofType'"+str(result)+str(self.geneProperty)
        else:
                #summary for all properties(including genes)
                if result[2] == 0:
                    # overlaps with at least one
                    # overlaps with at least one
                    regionData.append([settings.wordPrefixes["overlap"],self.datasetWordName])
                    if result[1] > 0.1:
                        regionData.append([settings.wordPrefixes["overlap10p"],self.datasetWordName])
                    if result[1] > 0.5:
                        regionData.append([settings.wordPrefixes["overlap50p"],self.datasetWordName])
                        
                    #score overlap count an integer score
                    ##score overlap ratio between 00--99
                    #regionData.append([settings.wordPrefixes["overlapCount"],self.datasetWordName,result[2]])
                    #score overlap ratio an integer score
                    regionData.append([settings.wordPrefixes["overlapRatio"],self.datasetWordName,wordFloat(result[1],2)])
                else:
                    #the region does not overlap with a site, report distance to the nearest
#                    if result[4] < settings.MAX_DISTANCE:
#                        dd  = wordMagnitude(result[4])
#                        regionData.append([settings.wordPrefixes["minimumDistanceDownstream"],self.datasetWordName,dd])
#                    if result[3] < settings.MAX_DISTANCE:
#                        du  = wordMagnitude(result[3])
#                        regionData.append([settings.wordPrefixes["minimumDistanceUpstream"],self.datasetWordName,du])
#                    if result[4] < result[3]:
                    dd  = wordMagnitude(result[2])
                    regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,dd])
#                    elif result[3] < result[4]:
#                        regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,du])
#                    elif result[3] < settings.MAX_DISTANCE:
#                        regionData.append([settings.wordPrefixes["minimumDistance"],self.datasetWordName,du])
                
        return regionData,regionDataWithScores
    
    def getWordPrefixes(self,cgsAS):
        prefixes =  [settings.wordPrefixes["overlap"],
                settings.wordPrefixes["overlap10p"],
                settings.wordPrefixes["overlap50p"],
                settings.wordPrefixes["overlapRatio"],
#                settings.wordPrefixes["overlapCount"],                
                settings.wordPrefixes["geneName"],
#                settings.wordPrefixes["geneStrand"],
#                settings.wordPrefixes["geneOverlap"],
#                settings.wordPrefixes["geneOverlapRatio"],
                #settings.wordPrefixes["geneDistanceDownstream"],
                #settings.wordPrefixes["geneDistanceUpstream"],
#                settings.wordPrefixes["geneDistance"],                
                #settings.wordPrefixes["strand"],                
#                settings.wordPrefixes["minimumDistanceDownstream"],
#                settings.wordPrefixes["minimumDistanceUpstream"],
                settings.wordPrefixes["minimumDistance"]]
        if self.geneProperty == "genes":
            if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGO"):
                prefixes.append(settings.wordPrefixes["gene"])
                prefixes.append(settings.wordPrefixes["goTerm"])    
                prefixes.append(settings.wordPrefixes["geneGOterm"])
                prefixes.append(settings.wordPrefixes["GOdescription"])
                prefixes.append(settings.wordPrefixes["geneGOtermParent"])
            if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGeneDescriptions"):  
                prefixes.append(settings.wordPrefixes["geneSymbol"])
                
                #settings.wordPrefixes["geneDescriptionWord"],
            if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGeneTranscripts"):                
                prefixes.append(settings.wordPrefixes["geneTranscript"])
            if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeOMIM"):
                prefixes.append(settings.wordPrefixes["omimTerm"])
                prefixes.append(settings.wordPrefixes["omimTermDescription"])
                prefixes.append(settings.wordPrefixes["omimTermID"])
                
        return prefixes
    
    def getWordsDescription(self):
        doc = []
        doc.append(["strand:plus","This region is on the plus strand",["strand:plus","strand:minus"]])
        doc.append(["genename:SRY","This gene part is ASSOCIATED WITH THE GENE SRY",["genename:"]])
        doc.append(["enum:exons:3","The THIRD exon of the gene",["enum:exons:","enum:introns:"]])
        doc.append(["nearestgenename:SRY","The gene SRY is the CLOSEST GENE to this element",["nearestgenename:"]])
        doc.append(["overlaps:promoters_central","This region OVERLAPS with central promoters",["overlaps:"+self.geneProperty]])
        doc.append(["oc:promoters_central:1","This region overlaps with ONE central promoter",["oc:"+self.geneProperty+":"]])
        doc.append(["or:promoters_central:55","This region OVERLAPS 55% with a central promoter",["or:"+self.geneProperty+":"]])
        doc.append(["mdd:promoters_central:34","Measures the magnitude of the distance (between 10^3*4 and 10^3 *5) to the NEAREST central promoter DOWNSTREAM",["mdd:"+self.geneProperty+":"]])
        doc.append(["mud:promoters_central:34","Measures the magnitude of the distance (between 10^3*4 and 10^3 *5) to the NEAREST central promoter UPSTREAM",["mud:"+self.geneProperty+":"]])
        doc.append(["mmd:promoters_central:34","Measures the magnitude of the distance (between 10^3*4 and 10^3 *5) to the NEAREST central promoter",["mmd:"+self.geneProperty+":"]])
       
        return doc
    def __initAllGO__(self):
        log([self.datasetSimpleName,self.geneProperty,"Initiating the full GO"])
        f = open(self.goOntology)
        activeGO = None        
        count = 1
        line = f.readline()
        
        while line:
            line = line.strip()
            if line == '[Term]':            
                #start new GO term
                activeGO = ["","",[],0,[]]
            elif line == "":
                if activeGO:
                    if activeGO[0] == "" or activeGO[1] == "":
                        raise GDMException, "Invalid activeGO "+str(activeGO)+str(count)      
                    #save the last term
                    self.fullGO[activeGO[0]] = activeGO[1:4]
                    for alternativeId in activeGO[4]:
                        self.fullGO[alternativeId] = activeGO[1:4]
                    activeGO = None                        
            else:
                if activeGO:    
                    lineParts = map(lambda x:x.strip(),line.split(":"))
                    if lineParts > 1:
                        if lineParts[0] == "id":
                            activeGO[0] = ":".join([lineParts[1],lineParts[2]])
                        elif lineParts[0] == "alt_id":
                            activeGO[4].append(":".join([lineParts[1],lineParts[2]]))
                        elif lineParts[0] == "name":
                            activeGO[1] = lineParts[1] 
                        elif lineParts[0] == "is_a":
                            try:
                                goParentParts = map(lambda x:x.strip(),lineParts[2].split("!"))                    
                                activeGO[2].append("".join([lineParts[1],":",goParentParts[0]]))
                            except:
                                raise GDMException, "Invalid parent "+str(lineParts)+str(count)+str(activeGO)+str(len(geneOntology.keys()))        
            line = f.readline()
            count += 1
        f.close()
        log([self.datasetSimpleName,self.geneProperty,"The full GO is loaded",str(len(self.fullGO.keys()))])
    
    def __initGeneOMIM__(self,datasetFileName):
        if datasetFileName.endswith(".gz"):
            f = gzip.GzipFile(datasetFileName,"rb")            
        else:
            raise GDMException, "unsupported file extension for "+datasetFileName
        f.readline()
        lines = f.readlines()
        f.close()
        for line in lines:
            if not line:
                continue
            lineParts = line.strip().split("\t")
            if len(lineParts) < 2:
                continue
            # store them
            if not self.geneOMIMs.has_key(lineParts[0]):
                self.geneOMIMs[lineParts[0]] = set()
            self.geneOMIMs[lineParts[0]].add(lineParts[1])
            
            if not self.fullOMIM.has_key(lineParts[1]):
                try:
                    self.fullOMIM[lineParts[1]] = [lineParts[2],0]
                except Exception,ex:
                    self.fullOMIM[lineParts[1]] = ["",0]
                    print "No description for OMIM",lineParts[1]
            self.fullOMIM[lineParts[1]][1] += 1
                
                
                 
        
    def __initGeneGO__(self,GOCategory,datasetFileName):                
        if datasetFileName.endswith(".gz"):
            f = gzip.GzipFile(datasetFileName,"rb")            
        else:
            raise GDMException, "unsupported file extension for "+datasetFileName
        f.readline()
        lines = f.readlines()
        f.close()
        for line in lines:
            if not line:
                continue
            lineParts = line.strip().split("\t")
            if len(lineParts) < 2:
                continue
            # store them
            if not self.geneGOs.has_key(lineParts[0]):
                self.geneGOs[lineParts[0]] = {"all":set()}
            if not self.geneGOs[lineParts[0]].has_key(GOCategory):
                self.geneGOs[lineParts[0]][GOCategory] = set()
            try:
                self.geneGOs[lineParts[0]][GOCategory].add(lineParts[1])
                # add also the full tree of GOs                
                parentGO = [lineParts[1]]
                while len(parentGO) >0:
                    currentGO = parentGO.pop(0)
                    self.geneGOs[lineParts[0]]["all"].add(currentGO)                    
                    parentGO.extend(self.fullGO[currentGO][1])
            except IndexError:
                print GOCategory,datasetFileName,lineParts
                raise
        
    def __initGeneTranscripts__(self):
        self.geneTrnascripts = {}
        #self.geneTrnascriptsRev = {}
        # initialize the all gene locations by ID        
        if self.datasetTranscriptsFile.endswith(".gz"):
            f = gzip.GzipFile(self.datasetTranscriptsFile,"rb")            
        else:
            raise GDMException, "unsupported file extension for "+self.datasetTranscriptsFile
        f.readline()
        lines = f.readlines()
        f.close()
        for line in lines:
            if not line:
                continue
            lineParts = line.strip().split("\t")
            # store them
            if not self.geneTrnascripts.has_key(lineParts[0]):
                self.geneTrnascripts[lineParts[0]] = []
            self.geneTrnascripts[lineParts[0]].append(lineParts[1])
            #self.geneTrnascriptsRev[lineParts[1]] = lineParts[0] 
                        
    def __initGeneDescriptions__(self):
        self.geneDescriptions = {}
        # initialize the all gene locations by ID        
        if self.datasetDescriptionsFile.endswith(".gz"):
            f = gzip.GzipFile(self.datasetDescriptionsFile,"rb")            
        else:
            raise GDMException, "unsupported file extension for "+self.datasetDescriptionsFile
        f.readline()
        lines = f.readlines()
        f.close()
        for line in lines:
            if not line:
                continue
            lineParts = line.strip().split("\t")
            # store them
            if self.geneDescriptions.has_key(lineParts[0]):
                log("Warning: coordinateLines already has the ID '"+str(lineParts[0])+"'")
            self.geneDescriptions[lineParts[0]] = [lineParts[1],lineParts[2]]
            
    def __initGeneLocations__(self):
        # initialize the all gene locations by ID        
        if self.datasetCoordinatesFile.endswith(".gz"):
            f = gzip.GzipFile(self.datasetCoordinatesFile,"rb")            
        else:
            raise GDMException, "unsupported file extension for "+self.datasetCoordinatesFile
        f.readline()
        coordinateLines = f.readlines()
        f.close()
        for line in coordinateLines:
            if not line:
                continue
            lineParts = line.strip().split("\t")
            #initialize the parts
            try:
                chrom = convertChromToInt(self.genome,"chr"+lineParts[1])
            except GDMException:
                #print "Skipped", lineParts[1]
                continue
                
            geneID = lineParts[0]                
            chromstart = int(lineParts[2])
            chromend = int(lineParts[3])
            strand = int(lineParts[4])
            # store them
            if self.geneLocations.has_key(geneID):
                log("Warning: coordinateLines already has the ID '"+str(geneID)+"'")
            
            self.geneLocations[geneID] = [chrom,chromstart,chromend,strand,False]
            
            
    def __initGeneExons__(self):
        self.geneExons = {}
        # initialize the all gene locations by ID        
        if self.datasetExonsFile.endswith(".gz"):
            f = gzip.GzipFile(self.datasetExonsFile,"rb")            
        else:
            raise GDMException, "unsupported file extension for "+self.datasetExonsFile
        f.readline()
        lines = f.readlines()
        f.close()
        for line in lines:
            if not line:
                continue
            lineParts = line.strip().split("\t")
            try:
                chrom = convertChromToInt(self.genome,"chr"+lineParts[1])
            except GDMException:
                #print "Skipped", lineParts[1]
                continue
            # store them
            if not self.geneExons.has_key(lineParts[0]):
                self.geneExons[lineParts[0]] = []                
            self.geneExons[lineParts[0]].append([chrom]+lineParts[2:])
            
    def __initGeneProperties__(self): 
        # make sure all property specific settings were defined       
        if "promoters" in self.geneProperty:
            try:
                self.promoterStartWrtTSS = int(self.promoterStartWrtTSS) 
                self.promoterEndWrtTSS = int(self.promoterEndWrtTSS)
            except:
                extext = self.datasetSimpleName+ ": ERROR! If you defined promoters, you should also define in the ini file the properties promoterEndWrtTSS and promoterEndWrtTSS that are integer relative positions"
                log(extext)
                raise GDMException,extext 
        
        self.__initGeneLocations__()
        
        if self.geneProperty == "exons":
            self.__initGeneExons__()
            
        if self.geneProperty == "genes":
            #initialize gene descriptions            
            #if self.includeGeneDescriptions:
            self.__initGeneDescriptions__()
            if self.includeGeneTranscripts:
                self.__initGeneTranscripts__()            
            self.fullGO = {}
            self.__initAllGO__()
            #if self.includeGO:
            self.geneGOs = {}                
            self.__initGeneGO__("BP",self.datasetGOBPFile)
            self.__initGeneGO__("CC",self.datasetGOCCFile)
            self.__initGeneGO__("MF",self.datasetGOMFFile)
            for geneName in self.geneGOs.keys():
                for goTerm in self.geneGOs[geneName]["all"]:
                    self.fullGO[goTerm][2] += 1
            self.fullOMIM = {}            
            self.geneOMIMs = {}
            if self.includeOMIM:            
                self.__initGeneOMIM__(self.datasetOMIMgeneFile)
                self.__initGeneOMIM__(self.datasetOMIMmorbidFile)
        self.genePropertiesInitiated = True
                
            
                        
            
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
        processedData = {}
        self.__initGeneProperties__()                    
        log(self.datasetSimpleName+": Initializing regions local db ")
        self.binaryFile = self.getDatasetBinaryName()        

        #print self.binaryFile
        
        #This connection code should be moved to a base Dataset.py method
        #which could use subclass variables to create the tables.
        
        try:
          conn = sqlite3.connect(self.binaryFile)
        except Exception as e:
                   
          if not e.args: 
            e.args=('',)
          #endif
          #e.args[0] += "\nFailed to connect to Genes DB " + self.binaryFile  #'tuple' object does not support item assignment
          e.args = (e.args[0] + "\nFailed to connect to Genes DB " + self.binaryFile,) + e.args[1:]
          
          raise

        try:
            #initialize the database table
            c = conn.cursor()
            c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER, strand INTEGER, geneName TEXT)')
            if self.geneProperty == "genes":
                #if self.includeGeneDescriptions:                    
                c.execute('CREATE TABLE gene_descriptions (geneName TEXT, geneSymbol Text, geneDescription TEXT)')
                if self.includeGeneTranscripts:                    
                    c.execute('CREATE TABLE gene_transcripts (geneName TEXT, geneTrnascriptName Text)')
                #if self.includeGO:                    
                c.execute('CREATE TABLE gene_GOs (geneName TEXT, goName Text, goCategory TEXT)')
            #process the file one line at a time
            for geneName in self.geneLocations.keys():       
                self.__extractRegionsFor_Property_FromLine__(geneName,c)
            
            conn.commit()
            c.close()                                       
            log(self.datasetSimpleName+": The dataset was preprocessed")
            conn.close()
        except:
            # there was an exception            
            try: #close the DB connection
                c.close()
                conn.close()                
            except:
                pass 
          
            rmFiles([self.binaryFile], False) #delete the file as is is empty/corrupt
            raise                             #reraise the exception 

        log(self.datasetSimpleName+": Initializing regions bed file ")
        plainBedName = self.getBedFile()+".plain"                
        fBed = open(self.getBedFile()+".plain","w")
        conn = sqlite3.connect(self.binaryFile)
        c = conn.cursor()
        try:
            #initialize the database table            
            c.execute('SELECT chrom,start,stop,geneName,strand FROM '+self.datasetSimpleName+' ORDER BY chrom,start')
            for geneLine in c:                
                chrom = convertIntToChrom(self.genome,geneLine[0])                
                if geneLine[4] == 1:
                    strand = "+"
                else:
                    strand = "-"                
                fBed.write("\t".join([chrom,str(geneLine[1]),str(geneLine[2]),geneLine[3],"0",strand])+"\n")
        except:            
            os.unlink(self.binaryFile)
            fBed.close()            
            raise
        finally:        
            c.close()
            conn.close()
        fBed.close()
        subprocess.Popen(settings.bedToolsFolder+"sortBed -i "+plainBedName+" > "+self.getBedFile(),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()  
        os.unlink(plainBedName)      
        log(self.datasetSimpleName+": end initializing regions bed file ")
        
    
    def __extractRegionsFor_Property_FromLine__(self, geneName, cursor):        
        if self.geneProperty == "genes":
            self.__extractRegionsFor_Genes_FromLine__(geneName, cursor)                        
        elif self.geneProperty == "TSS":
            self.__extractRegionsFor_TSS_FromLine__(geneName, cursor)            
        elif "promoters" in self.geneProperty:
            self.__extractRegionsFor_Promoters_FromLine__(geneName, cursor)            
        elif self.geneProperty == "exons":
            self.__extractRegionsFor_Exons_FromLine__(geneName, cursor)            
        #elif self.geneProperty == "introns":
        #    self.__extractRegionsFor_Introns_FromLine__(geneName, cursor)            
        else:
            extext = self.datasetSimpleName+": Property "+self.geneProperty+" is currently unsupported"
            log(extext)
            raise GDMException, extext
        
    def __extractRegionsFor_Genes_FromLine__(self,geneName, cursor):        
        if self.geneLocations.has_key(geneName):
            if self.geneLocations[geneName][4]:
                #This gene has already been processed
                return
        else:
            raise GDMException, "No gene location data for "+geneName
            print "No gene location data for "+geneName
        self.geneLocations[geneName][4] = True
            
        cursor.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?, ?, ?, ?, ?)',
                       tuple([self.geneLocations[geneName][0],
                             self.geneLocations[geneName][1],
                             self.geneLocations[geneName][2],
                             self.geneLocations[geneName][3],                             
                             getSafeWord(geneName)]))
        
        #initialize gene descriptions 
        #if self.includeGeneDescriptions:
        if self.geneDescriptions.has_key(geneName):
            values = tuple([getSafeWord(geneName),
                   self.geneDescriptions[geneName][0],
                   self.geneDescriptions[geneName][1]])
        else:
            values = tuple([getSafeWord(geneName),"",""])
        cursor.execute('INSERT INTO gene_descriptions VALUES (?, ?, ?)',
                           values)                
        if self.includeGeneTranscripts: 
            for geneTrnascript in self.geneTrnascripts[geneName]:
                cursor.execute('INSERT INTO gene_transcripts VALUES (?, ?)',
                               tuple([getSafeWord(geneName),geneTrnascript]))                                  
                
        #if self.includeGO:
        for goCategory in ["BP","CC","MF"]:
            if not self.geneGOs.has_key(geneName) or not self.geneGOs[geneName].has_key(goCategory):
                continue
            for goTerm in self.geneGOs[geneName][goCategory]:
                cursor.execute('INSERT INTO gene_GOs VALUES (?, ?, ?)',
                           tuple([getSafeWord(geneName),goTerm,goCategory]))
            
        
    def __extractRegionsFor_TSS_FromLine__(self, geneName, cursor):        
        if self.geneLocations.has_key(geneName):
            if self.geneLocations[geneName][4]:
                #This gene has already been processed
                return
        else:
            raise GDMException, "No gene location data for "+geneName
            
        if self.geneLocations[geneName][3] == 1:        
            tssS =  self.geneLocations[geneName][1]
            tssE =  self.geneLocations[geneName][1]+1
        elif self.geneLocations[geneName][3] == -1:
            tssS =  self.geneLocations[geneName][2]-1
            tssE =  self.geneLocations[geneName][2]
        else:
            raise GDMException, "Invalid strand "+str(self.geneLocations[geneName][3]) 
        tssS,tssE = getCorrectedCoordinates(self.genome,self.geneLocations[geneName][0],tssS,tssE)
        cursor.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?, ?, ?, ?,  ?)',
                       tuple([self.geneLocations[geneName][0],
                              tssS,
                              tssE,
                              self.geneLocations[geneName][3],                              
                              getSafeWord(geneName)]))
        self.geneLocations[geneName][4] = True
        
    def __extractRegionsFor_Promoters_FromLine__(self, geneName, cursor):
        
        if self.geneLocations.has_key(geneName):
            if self.geneLocations[geneName][4]:
                #This gene has already been processed
                return
        else:
            raise GDMException, "No gene location data for "+geneName
        
        if self.geneLocations[geneName][3] == 1:        
            start =  self.geneLocations[geneName][1] + self.promoterStartWrtTSS
            end =  self.geneLocations[geneName][1] + self.promoterEndWrtTSS
        elif self.geneLocations[geneName][3] == -1:
            start =  self.geneLocations[geneName][2] - self.promoterEndWrtTSS
            end =  self.geneLocations[geneName][2] - self.promoterStartWrtTSS
        else:
            raise GDMException, "Invalid strand "+str(self.geneLocations[geneName][3])
        try:
            start,end = getCorrectedCoordinates(self.genome,self.geneLocations[geneName][0],start,end)
        except:
            print geneName,self.geneLocations[geneName]
            raise
        cursor.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?, ?, ?, ?, ?)',
                       tuple([self.geneLocations[geneName][0],
                              start,
                              end,
                              self.geneLocations[geneName][3],                              
                              getSafeWord(geneName)]))
        
    def __extractRegionsFor_Exons_FromLine__(self,geneName, cursor):
                
        if not self.geneLocations[geneName][4]:                
            self.geneLocations[geneName][4] = {}
        if not self.geneExons.has_key(geneName):
            raise GDMException,"No exons loaded for gene "+geneName
        
        for i in range(len(self.geneExons[geneName])):
            exon  = self.geneExons[geneName][i]
            if exon[1] == exon[2]:
                continue
                               
            cursor.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?, ?, ?, ?, ?)',
                           tuple([exon[0],
                                  exon[1],
                                  exon[2],
                                  self.geneLocations[geneName][3],                                  
                                  getSafeWord(geneName)]))
            
            
    def __extractRegionsFor_Introns_FromLine__(self,lineParts, cursor):
        raise GDMException, "Introns are no longer supported"
#        geneName = lineParts[self.geneNameIndex]
#        if not self.geneLocations.has_key(geneName):
#            if self.geneTrnascriptsRev.has_key(lineParts[self.transcriptNameIndex]) and self.geneLocations.has_key(self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]):
#                geneName = self.geneTrnascriptsRev[lineParts[self.transcriptNameIndex]]
#            else:
#                return
#                
#                #raise GDMException, "No gene location data for "+geneName
#        if self.geneLocations.has_key(geneName):
#            if not self.geneLocations[geneName][4]:                
#                self.geneLocations[geneName][4] = {}
#        else:
#            raise GDMException, "No gene location data for "+geneName
#        #chrom , start , stop , strand , count , geneName 
#        exonStarts = lineParts[self.exonStartsIndex][:-1].split(",")
#        exonEnds = lineParts[self.exonEndsIndex][:-1].split(",")
#        if len(exonStarts) != len(exonStarts):
#            raise GDMException, "Unmatching exon start and exon end sites" +str(lineParts)
#        for i in range(1,len(exonStarts)):
#            intronID = str(exonEnds[i-1])+":"+str(exonStarts[i])
#            if self.geneLocations[geneName][4].has_key(intronID):
#                # this intron was already preprocessed
#                continue            
#            cursor.execute('INSERT INTO '+self.datasetSimpleName+' VALUES (?, ?, ?, ?, ?)',
#                           tuple([lineParts[self.chromIndex],
#                                  exonEnds[i-1],
#                                  exonStarts[i],
#                                  lineParts[self.strandIndex],                                  
#                                  getSafeWord(geneName)]))
#            #save it as processed
#            self.geneLocations[geneName][4][intronID] = True
    def preprocessDownloadedDatasetOld(self):        
        if not self.hasAllDownloadedFiles():
           exText = self.datasetSimpleName + ": the dataset files are not downloadeded "
           log(exText)
           raise GDMException, exText
        if self.hasPreprocessedFile():
            #what to do if the data was already preprocessed
            extext = self.datasetSimpleName + ": the dataset was already preprocessed in "+self.binaryFile
            log(extext)
            return
        processedData = {}
        self.__initGeneProperties__()                    
        log(self.datasetSimpleName+": Initializing regions local db ")
        self.binaryFile = self.getDatasetBinaryName()
        self.transcriptNameIndex = 1
        self.chromIndex = 2
        self.chromStartIndex = 4
        self.chromEndIndex = 5
        self.strandIndex = 3
        self.exonStartsIndex = 9 
        self.exonEndsIndex = 10
        self.transcriptNameIndex = 1
        self.geneNameIndex = 12
        
        conn = sqlite3.connect(self.binaryFile)
        try:
            #initialize the database table
            c = conn.cursor()
            c.execute('CREATE TABLE '+self.datasetSimpleName+'(chrom INTEGER, start INTEGER, stop INTEGER, strand INTEGER, geneName TEXT)')
            if self.geneProperty == "genes":
                #if self.includeGeneDescriptions:                    
                c.execute('CREATE TABLE gene_descriptions (geneName TEXT, geneSymbol Text, geneDescription TEXT)')
                if self.includeGeneTranscripts:                    
                    c.execute('CREATE TABLE gene_transcripts (geneName TEXT, geneTrnascriptName Text)')
                #if self.includeGO:                    
                c.execute('CREATE TABLE gene_GOs (geneName TEXT, goName Text, goCategory TEXT)')
            #process the file one line at a time
            datasetLocalFile = self.getDatasetLocalFile()            
            rawDataFile = gzip.GzipFile(datasetLocalFile,"rb")            
            line = rawDataFile.readline()
            while line:
                lineParts = line.strip().split("\t")
                try:
                    lineParts[self.chromIndex] = convertChromToInt(self.genome,lineParts[self.chromIndex])
                except Exception,ex:
                    #print (ex) 
                    line = rawDataFile.readline()
                    continue                
                lineParts[self.chromStartIndex] = int(lineParts[self.chromStartIndex])
                lineParts[self.chromEndIndex] = int(lineParts[self.chromEndIndex])   
                if lineParts[self.strandIndex] == "+": 
                    lineParts[self.strandIndex] = 1
                elif lineParts[self.strandIndex] == "-":
                    lineParts[self.strandIndex] = -1
                else:
                    raise GDMException, "Invalid strand "+lineParts[self.strandIndex]         
                self.__extractRegionsFor_Property_FromLine__Old(lineParts,c) 
                
                line = rawDataFile.readline()
            rawDataFile.close()
            conn.commit()
            c.close()                                       
            log(self.datasetSimpleName+": The dataset was preprocessed")
            conn.close()
        except:
            # there was an exception            
            try:
                #close the DB connection
                c.close()
                conn.close()                
            except:
                pass
            #delete the file
            os.unlink(self.binaryFile)
            #reraise the exception
            raise
    
    def getDefaultAnnotationSettings(self):        
        # obtain the default settings
        settings = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settings["hasGenomicRegions"] = self.hasGenomicRegions
        settings["hasFeatures"] = self.hasFeatures
        settings["data"] = {"data":{}}
        if self.geneProperty == "genes":            
            settings["includeGenesUpTo"] = int(self.includeGenesUpTo)
            settings["includeGO"] = self.includeGO
            settings["includeOMIM"] = self.includeOMIM
            settings["includeGeneDescriptions"] = self.includeGeneDescriptions
            settings["includeGeneTranscripts"] = self.includeGeneTranscripts
            settings["data"] = {"genenames":{},
                                 "regionGOs":{},
                                 "GOs":{},                                     
                                 "OMIMs":{},
                                 "data":{}}
        #retrun them
        settings["localRegionRow"] = None
        settings["localRegionCursor"] = None
        return settings
    
    def getDatasetLocalFile(self):
        return self.__getDatasetSingleLocalFile__()
    
    def downloadDataset(self):
        self.__downloadSingleFileDataset__()
       
    def hasAllDownloadedFiles(self):
        absName = self.getDatasetLocalFile()
        if os.path.isfile(absName):            
            if not os.path.isfile(self.datasetCoordinatesFile):
                raise GDMException, "The file "+self.datasetCoordinatesFile+" is missing"
            if self.geneProperty == "genes":
                for geneFile in [self.datasetTranscriptsFile,self.datasetDescriptionsFile,self.datasetGOBPFile,self.datasetGOCCFile,self.datasetGOMFFile,self.goOntology]:
                    if not os.path.isfile(geneFile):
                        raise GDMException, "The file "+geneFile+" is missing"
            self.downloadUrls["any"] = self.datasetFrom
            self.downloadDate = fileTimeStr(self.getDatasetLocalFile())                                            
            return True
        else:
            return False
        
    def hasPreprocessedFile(self):       
        self.binaryFile = self.getDatasetBinaryName()
        if not os.path.isfile(self.binaryFile):
            return False      
        if not os.path.isfile(self.getBedFile()):
            return False
        return True   
     
    def getBedFile(self):
        return settings.rawDataFolder[self.genome]+self.datasetSimpleName+".bed"
        
    ## exportExtraData
    #
    # This method should be defined only for Datasets that returndat in addition to their 
    # regions and features such as gene descriptions or II scores
    # The expected return format is as follows
    # returnData := [[document title,document body,document link,document words], ...]                
    # document words := [[wordParts,score], ...]
    # wordParts := [wordPart1,wordPart2,wordPart3, ...]] 
    def exportExtraData(self,documentID,fdd,fwd,cgsAS):         
        if self.geneProperty == "genes":
            if not (cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGO") 
                    or cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeOMIM")):
                #none of those is true. No data for genes need to be exported
                return documentID
                        
#            geneDescriptionWord = settings.wordPrefixes["geneDescriptionWord"]
#            geneTranscriptWord = settings.wordPrefixes["geneTranscript"]
            for geneName in self.geneLocations.keys():
                if not cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["genenames"].has_key(geneName):                    
                    continue
                wordsList = self.exportExtraDataGene(geneName,cgsAS)
                
                # add all GO categories
                if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGO"):                    
                    wordsList += self.exportExtraDataGeneGO(geneName,cgsAS)
                # add all GO categories
                if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeOMIM"):                    
                    wordsList += self.exportExtraDataGeneOMIM(geneName,cgsAS)
                #add gene description words and geneSymbol                    
                if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGeneDescriptions"):
                    wordsList += self.exportExtraDataGeneDescriptions(geneName,cgsAS)                    
                # Add the alternative transcripts    
                if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGeneTranscripts"):
                    wordsList += self.exportExtraDataGeneTranscriptions(geneName,cgsAS)
                    
                documentID += 1                 
                wdbuffer = "\n".join(map(lambda word:"\t".join([":".join(map(str,word)),str(documentID),"0","0"]),wordsList))+"\n"
                fwd.write(wdbuffer)
                fdd.write("\t".join([str(documentID),"u:","t:Gene "+geneName+" "+str(self.geneDescriptions[geneName][1])+" "+str(self.geneDescriptions[geneName][0]),"H:\n"]))
                
            if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeGO"):

                for goTerm in  cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["GOs"].keys():                    
                    wordsList = self.exportExtraDataGO(goTerm,cgsAS)                    
                    documentID += 1
                    sdID = str(documentID)
                    wdbuffer = ""                    
                    for word in wordsList:
                        #if word[0] == settings.wordPrefixes["geneGOterm"]:
                        #    score = getWordGOscore(self.fullGO[goTerm][2])
                        #    wdbuffer += "\t".join([":".join(map(str,word)),sdID,score,"0"])+"\n"
                        #else:
                            wdbuffer += "\t".join([":".join(map(str,word)),sdID,"0","0"])+"\n"
                    #wdbuffer = "\n".join(map(lambda word:"\t".join([":".join(map(str,word)),str(documentID),"0","0"]),wordsList))+"\n"
                    fwd.write(wdbuffer)
                    fdd.write("\t".join([sdID,"u:","t:GO "+goTerm+" "+str(self.fullGO[goTerm][2])+" "+self.fullGO[goTerm][0],"H:\n"]))
            
            if cgsAS.getFeatureDatasetProperty(self.datasetSimpleName,"includeOMIM"):
                for omimTerm in  cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["OMIMs"].keys():                    
                    wordsList = self.exportExtraDataOMIM(omimTerm,cgsAS)                    
                    documentID += 1
                    sdID = str(documentID)
                    wdbuffer = ""
                    for word in wordsList:
                        #if word[0] == settings.wordPrefixes["omimTermID"]:
                        #    #score = str(int(wordMagnitude(self.fullOMIM[omimTerm][1],2)))
                        #    score = getWordOMIMscore(self.fullOMIM[omimTerm][1])
                        #    wdbuffer += "\t".join([":".join(map(str,word)),sdID,score,"0"])+"\n"
                        #else:
                            wdbuffer += "\t".join([":".join(map(str,word)),sdID,"0","0"])+"\n"                    
                    
                    fwd.write(wdbuffer)
                    fdd.write("\t".join([sdID,"u:","t:OMIM "+omimTerm+" "+str(self.fullOMIM[omimTerm][1])+" "+str(self.fullOMIM[omimTerm][0]),"H:\n"]))
                
                    
        return documentID
    
    def exportExtraDataGene(self,geneName,cgsAS):
        wordsList = []
#            geneStrandWord = settings.wordPrefixes["geneStrand"]
#            geneOverlapWord = settings.wordPrefixes["geneOverlap"]
#            geneDistanceDownstreamWord = settings.wordPrefixes["geneDistanceDownstream"]
#            geneDistanceUpstreamWord = settings.wordPrefixes["geneDistanceUpstream"]
        geneDistanceWord = settings.wordPrefixes["geneDistance"]
        #check if this gene was processed at all                
        # add the base gene words
        wordsList = [[settings.wordPrefixes["gene"]]]                
        wordsList.append([settings.wordPrefixes["geneName"],geneName])                
#                wordsList.append([geneStrandWord,"plus",geneName])                
#                wordsList.append([geneStrandWord,"minus",geneName])
#                wordsList.append([geneOverlapWord,geneName])
        
#        for geneDistance in cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["genenames"][geneName]:
#            #                for i in range(10):
##                    for j in range(10):
##                        a = str(i)+str(j)
#                #===============================================================
#                # Commented the words to allow join by overlap ratio
#                # wordsList.append([settings.wordPrefixes["geneOverlapRatio"],str(i)+str(j),geneName])
#                #===============================================================
##                        wordsList.append([geneDistanceDownstreamWord,a,geneName])
##                        wordsList.append([geneDistanceUpstreamWord,a,geneName])
#                wordsList.append([settings.wordPrefixes["geneDistance"],geneDistance,geneName])
#            #del cgsAS.featuresDatasets[self.datasetSimpleName]["data"][geneName]
        
        # This method returns a list of feature words for the feature listing in the user interface
        return wordsList
    
    def exportExtraDataGeneGO(self,geneName,cgsAS):
        wordsList = []
        if self.geneGOs.has_key(geneName):
            for category in ["BP","MF","CC"]:
                if self.geneGOs[geneName].has_key(category):
#                    if geneName == "ENSG00000127824":
#                        print geneName,category,self.geneGOs[geneName][category]
                    for goTerm in self.geneGOs[geneName][category]:                         
                        wordsList.append([settings.wordPrefixes["geneGOterm"],goTerm])
                        
            for currentGoTerm in self.geneGOs[geneName]["all"]:                            
                cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["GOs"][currentGoTerm] = True
#        if geneName == "ENSG00000127824":
#            print geneName,wordsList
        return wordsList
    
    def exportExtraDataGeneDescriptions(self,geneName,cgsAS):
        wordsList = []
        if self.geneDescriptions.has_key(geneName):
            # make safe gene symbol
            safeGeneSymbol = self.geneDescriptions[geneName][1].upper().replace("-","d").replace(".","p").replace("_","u").replace("@","").replace("(", "q").replace(")", "w")
            saferGeneSymbol = getSafeWord(safeGeneSymbol)
            if safeGeneSymbol != saferGeneSymbol:
                raise GDMException, "Error: weird symbols in this gene symbol '"+str(self.geneDescriptions[geneName][1])+"'"
            wordsList.append([settings.wordPrefixes["geneSymbol"],safeGeneSymbol])
            # DO NOT INCLUDE GENE DESCRIPTION WORDS
#                        # make safe words from the description
#                        description = self.geneDescriptions[geneName][0].upper()
#                        x = description.find("[Source:")
#                        if x >= 0:
#                            description = description[:x]                        
#                        words = map(getSafeWord,description.replace("("," ").replace(")"," ").replace(","," ").replace("-","d").replace("_","u").replace(" "," ").split(" "))
#                        wordsList.extend(map(lambda w:[geneDescriptionWord,w],words)
        return wordsList
    
    def exportExtraDataGeneTranscriptions(self,geneName,cgsAS):
        wordsList = []
        for transcript in  self.geneTrnascripts[geneName]:
            wordsList.append([geneTranscriptWord,transcript])
            pass
        return wordsList
    
    def exportExtraDataGeneOMIM(self,geneName,cgsAS):
        wordsList = []
        if self.geneOMIMs.has_key(geneName):
            for geneOMIM in self.geneOMIMs[geneName]:
                wordsList.append([settings.wordPrefixes["omimTermID"],geneOMIM])            
        return wordsList
    
    def exportExtraDataOMIM(self,omimTerm,cgsAS):
        wordsList = [[settings.wordPrefixes["omimTerm"]]]
        wordsList.append([settings.wordPrefixes["omimTermID"],omimTerm])
        wordsList.append([settings.wordPrefixes["omimTermNumberGenes"],wordMagnitude(self.fullOMIM[omimTerm][1],2)])
        
        omimDescription = self.fullOMIM[omimTerm][0]
        if omimDescription == "":
            return wordsList         
        words = omimDescription.upper().replace("("," ").replace("@","").replace(";"," ").replace("+","l").replace("["," ").replace("=","").replace("]"," ").replace(")"," ").replace(","," ").replace("/"," ").replace("-","d").replace("_","u").replace("'","r").replace(".","p").replace(" "," ").split(" ")
        for word in words:
            if word:
                try:
                    self.stopWords[word]
                except:
                    #the word is not in the stop list                    
                    wordsList.append([settings.wordPrefixes["omimTermDescription"],word])
                    if word != getSafeWord(word,":"):
                        raise Exception, "'"+word+"' is invalid word"
        return wordsList 
    
    def exportExtraDataGO(self,goTerm,cgsAS):
        wordsList = [[settings.wordPrefixes["goTerm"]]]
        wordsList.append([settings.wordPrefixes["geneGOterm"],goTerm])
        wordsList.append([settings.wordPrefixes["goTermNumberGenes"],wordMagnitude(self.fullGO[goTerm][2],3)])

         
        allParentGOs = set()
        parentGO = [goTerm]
        while len(parentGO) >0:
            currentGO = parentGO.pop(0)
            allParentGOs.add(currentGO)
            parentGO.extend(self.fullGO[currentGO][1])
        for currentGoTerm in list(allParentGOs):   
            wordsList.append([settings.wordPrefixes["geneGOtermParent"],currentGoTerm])                         
            cgsAS.featuresDatasets[self.datasetSimpleName]["data"]["GOs"][currentGoTerm] = True
        goName = self.fullGO[goTerm][0]        
        words = goName.upper().replace("("," ").replace("+","l").replace("["," ").replace("=","").replace("]"," ").replace(")"," ").replace(","," ").replace("/"," ").replace("-","d").replace("_","u").replace("'","r").replace(".","p").replace(" "," ").split(" ")
        for word in words:
            if word:
                try:
                    self.stopWords[word]
                except:
                    #the word is not in the stop list                    
                    wordsList.append([settings.wordPrefixes["GOdescription"],word])
                    if word != getSafeWord(word,":"):
                        raise Exception, "'"+word+"' is invalid word"
        return wordsList                
                
        
        
        
        
     
    def getVisualizationFeatures(self,annotationFeatures):
        categories = self.dataCategories.strip()
        if len(categories) == 0:
            categoriesPath = [self.datasetSimpleName]
        else:
            categoriesPath = map(lambda x:x.strip(),categories.split("/"))+[self.datasetSimpleName]
        featureWords = []
        featureWords.append(categoriesPath+["OVERLAP:"+self.datasetWordName+"::"+"Eor:"+self.datasetWordName+"::2::0"])  
        featureWords.append(categoriesPath+["_OVERLAP:"+self.datasetWordName])
        #featureWords.append(categoriesPath+["distanceTo"]+["Emdd:"+self.datasetWordName+"::2::0"])
        #featureWords.append(categoriesPath+["distanceTo"]+["Emud:"+self.datasetWordName+"::2::0"])
        featureWords.append(categoriesPath+["Emmd:"+self.datasetWordName+"::2::0"])
        if self.geneProperty == "genes":
            if annotationFeatures["includeGeneDescriptions"]:
                featureWords.append(categoriesPath[:-1]+["GENENAME:ENSEMBL"])            
            #    featureWords.append(categoriesPath[:-1]+["GENENAME:SYMBOL"])
            if annotationFeatures["includeGO"]:
                # all GO categories                
                featureWords.append(categoriesPath[:-1]+["GO:ALL"])
                #all GO terms
                featureWords.append(categoriesPath[:-1]+["GO:TERMS"])
            if annotationFeatures["includeOMIM"]:
                # all OMIM categories
                featureWords.append(categoriesPath[:-1]+["OMIM:ALL"])
                #all OMIM terms
                featureWords.append(categoriesPath[:-1]+["OMIM:TERMS"])
        return featureWords  
    
    def getRangeNRatioWords(self,annotationFeatures):
        junkWordsList = []
        if self.geneProperty == "genes":
            if annotationFeatures["includeGO"]:
                for i in range(1000):
                    junkWordsList.append([settings.wordPrefixes["goTermNumberGenes"],wordFixed(i,3)])
            if annotationFeatures["includeOMIM"]:
                for i in range(100):
                    junkWordsList.append([settings.wordPrefixes["omimTermNumberGenes"],wordFixed(i,2)])
        return map(lambda x:":".join(x),junkWordsList)

    def calculateCoverages(self):    
        data = self.getRegions()      
        self.coverages["any"] = self.calculateCoverage(data)                          
        print self.coverages["any"]     
        
    def getOverlappingText(self):
        return self.datasetWordName
    
    def getSubAnnotations(self):
        return [self.geneProperty]
