from utilities import *
import settings


#------------------------------------------------------------------------------ 
# CGSAnnotationsSettings class defines the settings for one annotation calculation.
# These settings should be passed to any of the feature datasets as they define which 
# subset of all defualt features should be calculated
# 
#------------------------------------------------------------------------------ 

class CGSAnnotationsSettings:
    def __init__(self,datasetCollectionName,genome,regionsDatasetSettings,featuresDatasetSettings):
        #if not (featuresDatasetSettings or regionsDatasetSettings):
        #    raise GDMException, "No settings specified"
        self.genome = genome
        self.datasetCollectionName = datasetCollectionName        
        self.regionDatasets = regionsDatasetSettings
        self.featuresDatasets = featuresDatasetSettings        
    
    def addRegionDataset(self,regionsDatasetSettings):
        for datasetName in regionsDatasetSettings.keys():
            if not self.regionDatasets.has_key(datasetName):
                self.regionDatasets[datasetName] = {}                 
            self.regionDatasets[datasetName].update(regionsDatasetSettings[datasetName])        
        
    def addFeatureDataset(self,featuresDatasetSettings):
        for datasetName in featuresDatasetSettings.keys():
            if not self.featuresDatasets.has_key(datasetName):
                self.featuresDatasets[datasetName] = {}                 
            self.featuresDatasets[datasetName].update(featuresDatasetSettings[datasetName])        
    
    #getter    
    def getFeatureDatasetProperty(self,datasetName,propertyName):
        if not self.featuresDatasets.has_key(datasetName):
            raise GDMException, "No dataset properties defined for '"+datasetName +"' only for datasets: "+str(self.featuresDatasets.keys())
        if not self.featuresDatasets[datasetName].has_key(propertyName):             
            raise GDMException, "The property '"+propertyName+"' is not defined for '"+datasetName+"' only properties: "+str(self.featuresDatasets[datasetName].keys()) 
        return self.featuresDatasets[datasetName][propertyName]
    #setter
    def setFeatureDatasetProperty(self,datasetName,propertyName,value):
        if not self.featuresDatasets.has_key(datasetName):
            raise GDMException, "No dataset properties defined for '"+datasetName +"' only for datasets: "+str(self.featuresDatasets.keys())        
        self.featuresDatasets[datasetName][propertyName] = value
    
    def __toFileDataset__(self,datasetName,dataset):
        lines = []
        lines.append(datasetName)
        datasetProperties = dataset.keys()
        datasetProperties.sort() 
        for property in datasetProperties:
            if isinstance(dataset[property], str):                
                lines.append(property+"===ST:" +dataset[property])
            elif isinstance(dataset[property], bool):
                lines.append(property+"===BO:" +str(int(dataset[property])))
            elif isinstance(dataset[property], int):
                lines.append(property+"===IN:" +str(dataset[property]))            
            elif dataset[property] is None:
                lines.append(property+"===NO:")
            elif isinstance(dataset[property], list):
                if len(dataset[property]) > 0:
                    if isinstance(dataset[property][0], str):
                        lines.append(property+"===LS:" +"###".join(dataset[property]))
                    elif isinstance(dataset[property][0], int):
                        lines.append(property+"===LI:" +"###".join(map(str,dataset[property])))
                    else:
                        raise GDMException, ", ".join(["Invalid type",str(datasetName),str(property),str(dataset[property])])
            else:
                raise GDMException, ", ".join(["Invalid type",str(datasetName),str(property),str(dataset[property])])                    
        lines.append("")
        return lines  
    
    def __fromFileDatasetProperty__(self,line):
        propertyParts = line.split("===")
        result = None
        propertyParts[1] = "===".join(propertyParts[1:])
        if propertyParts[1].startswith("ST:"):                    
            result = [propertyParts[0],propertyParts[1][3:]]
        elif propertyParts[1].startswith("IN:"):
            result = [propertyParts[0],int(propertyParts[1][3:])]
        elif propertyParts[1].startswith("BO:"):
            result = [propertyParts[0],bool(int(propertyParts[1][3:]))]
        elif propertyParts[1].startswith("NO:"):
            result = [propertyParts[0],None]
        elif propertyParts[1].startswith("LS:"):
            l = propertyParts[1][3:].split("###")
            if len(l) == 1 and l[0] == "":
                l = []
            result = [propertyParts[0],l]
        elif propertyParts[1].startswith("LI:"):
            l = propertyParts[1][3:].split("###")                    
            result = [propertyParts[0],map(int,l)]
        else:
            raise GDMException, "Unexpected line "+line
        
        return result
        
                 
      
    def toFile(self,fileName):        
        lines = [self.genome,self.datasetCollectionName,"","Regions",""]
        #print "1",lines
        regions = self.regionDatasets.keys()
        regions.sort()
        for datasetName in regions:
            lines += self.__toFileDataset__(datasetName, self.regionDatasets[datasetName])
            #print "2",datasetName,lines  
        lines.append("Features")
        lines.append("")
        #print "3",lines
        features = self.featuresDatasets.keys()
        features.sort()
        for datasetName in features:
            lines += self.__toFileDataset__(datasetName, self.featuresDatasets[datasetName])
            #print "4",datasetName,lines
        lines.append("THEEND")
        f = open(fileName,"w")
        f.write("\n".join(map(str,lines)))
        f.close()
        
    def fromFile(self,fileName):
        f = open(fileName)
        lines = map(lambda x:x.strip(),f.readlines())
        f.close()
        self.genome = lines[0]
        self.datasetCollectionName = lines[1]
        index = 3
        if lines[index] != "Regions" or lines[index+1] != "":
            raise GDMException,fileName+" is not a valid settings file"
        self.regionDatasets = {}
        index = index+2
        #read the regions
        while lines[index] != "Features":
            regionDataset = lines[index]
            print "Regiondataset '"+regionDataset+"'","Features"
            self.regionDatasets[regionDataset] = {}
            index += 1
            while lines[index] != "":
                result = self.__fromFileDatasetProperty__(lines[index])
                self.regionDatasets[regionDataset][result[0]] = result[1]
                index += 1
            index += 1
        if lines[index] != "Features" or lines[index+1] != "":
            raise GDMException,fileName+" is not a valid settings file"
        index = index+2
        #read the features
        while lines[index] != "THEEND":
            featureDataset = lines[index]
            self.featuresDatasets[featureDataset] = {}
            index += 1
            while lines[index] != "":
                result = self.__fromFileDatasetProperty__(lines[index])
                self.featuresDatasets[featureDataset][result[0]] = result[1]                
                index += 1
            index += 1            
        
                
        
    