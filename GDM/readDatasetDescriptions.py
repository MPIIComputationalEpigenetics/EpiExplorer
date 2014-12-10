## @package readDataset descriptions
# 
# This module reads dataset descriptions and retrieves objects of type dataset for each

import os.path
import re

from utilities import *
import settings

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
    
    #Allow full path over-ride for plug in outside of code dir
    #Maintain support for old relative path config ../GDM/DatasetClasses
    #else assume non-full path is rooted in that directory
    datasetPythonClass = datasetBaseDescription["datasetPythonClass"] 
    fullPathMatch      = re.match(r'/.*', datasetPythonClass)     #Matches from start by default

    if not fullPathMatch:

      relPathMatch = re.match(r'(\.\./)+GDM/DatasetClasses/(.*)', datasetPythonClass)

      if relPathMatch:
        datasetPythonClass = relPathMatch.group(2)
      #endif

      datasetPythonClass = settings.baseFolder + "GDM/DatasetClasses/" + datasetPythonClass
    #endif

    #lead the module from the file
    pythonModuleName = getFileName(datasetPythonClass,datasetElements[1])    
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
    
    
    
        
    
    
