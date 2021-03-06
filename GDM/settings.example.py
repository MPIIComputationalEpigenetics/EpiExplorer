# This file contains settings which can vary across instances.
# Copy this file to settings.py and edit as necessary.
# If there are seemingly undeclared variables in here this is
# due to the import * from settings_defaults
# If anything from settings_defaults.py needs redefining, do it 
# in here.

import os
import sys
import string
import threading

from settings_default import * 
#import * is normally python 'Worst Practise' but we specifically want
#this behaviour to allow importing/overriding variables into this namespace
#TODO Catch ImportError Exception here, likely the settings_default.example.py file
#hasn't been copied to setting_default.py

### EpiExplorer GDM/UserInterface Config ###

instanceServer    = "test"
#This is where all instance specific code/data dirs should go
instanceFolder = "/Your/Base/Work/Directory/" + instanceServer + "/"
baseFolder     = instanceFolder + "EpiExplorer/"
configFolder   = baseFolder + "Config/"

#This is expected to be root directory of the EpiExplorer code e.g.
#baseFolder     = instanceFolder + "EpiExplorer/" 
#And is now used in place of relative paths to standard locations, 
#meaning the server processes can be started from anywhere, rather then the GDM dir.
#baseFolder is also used by performanceMultipleJoin.py

forwardServerHost="your_CGSServerHost""
forwardServerPort=56572
datasetServerHost="your_CGSDatasetServerHost"
datasetServerPort=51525
queryServerHost="your_CGSQueryServerHost
queryServerPort=51515

contact_email="epiexplorer@your.domain"
bcc_emails="you@your_domain.com,someone_else@their.domain"


#Now maintaining all data outside of code directory
#Datasets dir has been removed from hierarchy so all logs and output dirs
#are now in same directory

#Keep input data outside of the instanceFolder for use by other  EpiExplorer instances
#TODO Need write docs on how/what to move out of the Datasets dir here
inputDataFolder = instanceFolder + "../input_data/"
workingFolder  = instanceFolder + "output/"

genomesFolder   = inputDataFolder + "genomes/"
# The genomes fasta files can be created using GDM/utils/downloadGenome.py
logFile                    = workingFolder + "CGS_full.log"
exportBaseFolder           = workingFolder + "exported_data/"
userDB                     = workingFolder + "users.sqlite"
folderForTemporaryUserData = workingFolder + "temp_user_data/"
#Folder for user datasets settings files
folderForTemporaryDatasets = workingFolder + "user_datasets_descriptions/"

#Over-ride genomeData here if required, before genomeData loop
#genomeData = {"hg19":{}}

for genomeID in genomeData.keys():
  downloadDataFolder[genomeID] = inputDataFolder + genomeID + "_DownloadedDatasets/"
  rawDataFolder[genomeID]      = workingFolder + genomeID + "_RawDatasets/"
  indexDataFolder[genomeID]    = workingFolder + genomeID + "_CSFiles/"
  # The files to contain the links to all fully processed default datasets
  fullyProcessedDefaultDatasetsFile[genomeID] = workingFolder + genomeID + "_DefaultFullyProcessedDatasets.ini"
  # The files to contain the links to all fully processed user datasets
  fullyProcessedUserDatasetsFile[genomeID] = workingFolder + genomeID + "_UserFullyProcessedDatasets.ini"

  genomeData[genomeID].update(genomeDataNumbers[genomeID])
  genomeData[genomeID].update(genomeDataStr[genomeID])


### Other Software Config ###

# Bedtools config (move this to settings_default and comment out in here?)
#bedToolsFolder = "/Path/To/Your/bedtools/bin/" #Default is "" to use $PATH

# CompleteSearch config
startedServersFile    = workingFolder + "CSservers.txt"
#CS_CODE_DIR           = "/Path/To/Your/CompleteSearch/Binaries/" #Default is "" to use $PATH
startCompletionServer = CS_CODE_DIR + "startCompletionServer"
buildIndex            = CS_CODE_DIR + "buildIndex"
buildDocsDB           = CS_CODE_DIR + "buildDocsDB"


