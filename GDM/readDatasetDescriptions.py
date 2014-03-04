## @package readDataset descriptions
# 
# This module reads dataset descriptions and retrieves objects of type dataset for each
from utilities import *
import os.path

## readDatasets
# 
# reads all datasets indicated in the index file
# @param datasetsIndexFile: name of the index file    
# @return: retrieves a dictionary with all the dataset descriptions
def readDatasets(datasetsIndexFile):

    log("General: Start reading datasets")
    datasetsSettings = readSettingsFile(datasetsIndexFile)
    datasets = {}          
    for datasetName in datasetsSettings.keys():        
        datasetFile =  datasetsSettings[datasetName]        
        dataset = readDataset([datasetName,datasetFile,datasetsIndexFile])               
        datasets[datasetName] = dataset        
    
    log("General:" + " Over with reading datasets")
    return datasets


## readDataset
# 
# receives a list with the dataset parameters
# datasetElements[0] is the dataset name, datasetElements[1] is the file name of the dataset full description
def readDataset(datasetElements):
    #making sure the dataset file exists    
    datasetElements[1] = getFileName(datasetElements[1],datasetElements[2])
    log("General: " +datasetElements[0] + " was read from "+datasetElements[1])
    datasetBaseDescription = readSettingsFile(datasetElements[1])    
    # read the python class that corresponds how this dataset should be handled
    if not datasetBaseDescription.has_key("datasetPythonClass"):
        raise Exception , "Error:Dataset "+datasetElements[0]+" did not define its python class in "+datasetElements[1]
    #lead the module from the file
    pythonModuleName = getFileName(datasetBaseDescription["datasetPythonClass"],datasetElements[1])    
    m = load_module(pythonModuleName)
    # the class name need to start with d_
    # make an instance from the class
    #print dir(m),dir(m)[getIndexOfActiveModule(m)]    
    
    x = eval("m."+dir(m)[getIndexOfActiveModule(m)])()
    x.name = datasetElements[0]    
    x.iniLongName = datasetElements[1]
    for key in datasetBaseDescription.keys():
        setattr(x,key,datasetBaseDescription[key])
    return x
    
    
    
        
    
    
