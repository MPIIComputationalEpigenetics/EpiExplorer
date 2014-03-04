## class TilingRegions
# 
# this is an interface class for datasets that define only regions and no features
import os
import os.path
import numpy
import sqlite3
import sys
if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
else:    
    mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep    
    sys.path.insert(0,mainFolder)    

from utilities import *
import Dataset
import dataset_methods
import settings
import readDatasetDescriptions

class TilingRegions(Dataset.Dataset):
    
    def init(self,initCompute=True):
        Dataset.Dataset.init(self,initCompute)
        self.initialized = True  
    
    
    def cleanup(self,cgsAS):
        pass

    def initializePropertiesComputeStructures(self):
        pass
    
    def hasAllDownloadedFiles(self):
        # no downloads needed
        return True
         
    def preprocessDownloadedDataset(self):
        if self.hasPreprocessedFile():
            #what to do if the data was already preprocessed
            extext = self.datasetSimpleName + ": the dataset was already preprocessed in "+self.binaryFile
            log(extext)
            return                
        self.maxNNRatio = float(self.maxNNRatio)
        if not self.coverage in ["genome","around dataset regions"]:
            raise GDMException, "Invalid coverage "+self.coverage
        self.tilingRegionSizes = self.tilingRegionSizes.split(",")
        self.tilingRegionSteps = self.tilingRegionSteps.split(",")
        dsFull = []
        if self.coverage == "genome":            
            for i in range(len(self.tilingRegionSizes)):
                tilingRegionSize = int(self.tilingRegionSizes[i].strip())
                tilingRegionStep = int(self.tilingRegionSteps[i].strip())
                list_of_chr =  [[c,0,settings.genomeData[self.genome][c]] for c in settings.genomeDataStr[self.genome].keys()]
                ds = dataset_methods.getTilingRegions(list_of_chr,self.genome,tilingRegionSize,tilingRegionStep)
                #dataset_methods.saveDataset(ds,"trail",False)
                if self.maxNNRatio > 0:
                    ds = dataset_methods.filterMinNNContent(ds,self.genome,self.maxNNRatio)
                dsFull.extend(ds)
        elif self.coverage == "around dataset regions":
            datasetParts = map(lambda x:x.strip(),self.aroundDataset.split(":"))
            # get the Main index file for the whole genome, Tiling regions are never precomputed otherwise
            datasetParts.append(getMainDatasetIndexFileName(self.genome))
            aroundDataset = readDatasetDescriptions.readDataset(datasetParts)
            aroundDataset.init(False)
            datasetRegions = aroundDataset.getRegions()
            f = open(settings.baseFolder+"temp.txt","w")
            f.write(str(datasetRegions))
            f.close()
            self.datasetShore = int(self.datasetShore)
#            dataset_methods.defaultFolder = "/TL/epigenetics/work/completesearch/Datasets/hg18_RawDatasets/"
            datasetRegionsExtended =  []
            for i in xrange(datasetRegions.shape[0]):
                chr = convertIntToChrom(self.genome,datasetRegions[i,0])
#                if chr == "chr0":
#                    print datasetRegions[i]
                start = datasetRegions[i,1]-self.datasetShore
                end = datasetRegions[i,2]+self.datasetShore
                start,end = getCorrectedCoordinates(self.genome,chr,start,end)
                datasetRegionsExtended.append([chr,start,end])    
                
#            dataset_methods.saveDataset(datasetRegionsExtended,"raw",False)
            nonOverlappingDatasetRegions = dataset_methods.mergeOverlappingMax(datasetRegionsExtended)            
#            dataset_methods.saveDataset(nonOverlappingDatasetRegions,"overlapping",False)
            for i in range(len(self.tilingRegionSizes)):
                tilingRegionSize = int(self.tilingRegionSizes[i].strip())
                tilingRegionStep = int(self.tilingRegionSteps[i].strip())                
                ds = dataset_methods.getTilingRegions(nonOverlappingDatasetRegions,self.genome,tilingRegionSize,tilingRegionStep)
#                dataset_methods.saveDataset(ds,"trail",False)
                if self.maxNNRatio > 0:
                    ds = dataset_methods.filterMinNNContent(ds,self.genome,maxNNRatio)
                dsFull.extend(ds)            
            
        self.__init_regions_dataset_for_local_db__(dsFull) 
        
 
        
    def getRegions(self):
        return self.getRegionsFromLocalDB()
    
    def getDefaultAnnotationSettings(self):        
        # obtain the default settings
        settings = self.__getDefaultAnnotationSettingsBasic__()
        # add/change the specific settings for this dataset type 
        settings["hasGenomicRegions"] = self.hasGenomicRegions
        settings["canHaveFeatures"] = False
        settings["hasFeatures"] = False
        #retrun them
        return settings
    
    def calculateCoverages(self):
        pass
    
    def getSubAnnotations(self):
        return []
