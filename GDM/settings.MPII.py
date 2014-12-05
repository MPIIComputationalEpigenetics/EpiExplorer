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
queryServerHost   = "srv-13-13"
datasetServerHost = "srv-13-13"
xmlprcServerHost  = "wks-13-15" #?
#These hosts will likely all be the same
#ini file writing will only be for settings.php
#otherwise it maybe out of date for startCGSServers
#Although we do want to stop the previously running servers for this instance
#so startCGSServers will need to read both to get the old ports/host and the new
#ports hosts
datasetServerPort = 51525
queryServerPort   = 51515
xmplrpcServerPort = 56572

#This is likely to change from a dictionary to a simple scalar
#with instanceServer being used for differentiation of instance code/data/config paths
webservers     = {"production":"http://epiexplorer.mpi-inf.mpg.de/server.php",
                  "test":"http://moebius.ag3.mpi-sb.mpg.de/epiexplorer/server.php"}

#This is where all instance specific code/data dirs should go
#instanceFolder = "/Your/Base/Work/Directory/" + instanceServer + "/"

# baseFolder is platform independant base folder variable
if sys.platform == "win32":
  #for local testing
  baseFolder = "D:/Projects/Integrated_Genome_Profile_Search_Engine/Cosgen/"
else:     #assume unix
  baseFolder = "/TL/epigenetics2/work/completesearch/"

#This is expected to be root directory of the EpiExplorer code e.g.
#baseFolder     = instanceFolder + "EpiExplorer/" 
#And is now used in place of relative paths to standard locations, 
#meaning the server processes can be started from anywhere, rather then the GDM dir.

#baseFolder is also used by performanceMultipleJoin.py

#Now maintaining all data outside of code directory
#Datasets dir has been removed from hierachy so all logs and output dirs
#are now in same directory

#Keep input data outside of the instanceFolder for use by other  EpiExplorer instances
#TODO Need write docs on how/what to move out of the Datasets dir here
#inputDataFolder = instanceFolder + "../input_data/"
#workingFolder  = instanceFolder + "output/"
inputDataFolder = baseFolder + "Datasets/"
workingFolder   = baseFolder + "Datasets/"

bedToolsFolder = "/TL/epigenetics2/work/completesearch/dev_codebase/bedtools/bedtools-2.17.0/bin/"
#genomesFolder   = inputDataFolder + "genomes/"
genomesFolder = os.path.abspath(os.path.join(bedToolsFolder, os.path.pardir)) + "/genomes/"

# The genomes fasta files can be created using GDM/utils/downloadGenome.py
#logFile                    = baseFolder + "CGS_full.log"
logFile                    = "/TL/www/epiexplorer/CGS.log"
#exportBaseFolder           = workingFolder + "exported_data/"
exportBaseFolder = "/TL/www/epiexplorer/www/pub/Datasets/"
userDB                     = workingFolder + "users.sqlite"
folderForTemporaryUserData = workingFolder + "temp_user_data/"
#folderForTemporaryUserData = "/TL/epigenetics2/work/completesearch/Datasets/temp_user_data/"
#Folder for user datasets settings files
folderForTemporaryDatasets = workingFolder + "user_datasets_descriptions/"

#Over-ride genomeData here if required, before genomeData loop
#genomeData = {"hg19":{}}

for genomeID in genomeData.keys():
  downloadDataFolder[genomeID] = inputDataFolder + genomeID + "_DownloadedDatasets/"
  rawDataFolder[genomeID]      = workingFolder + genomeID + "_RawDatasets/"
  indexDataFolder[genomeID]    = workingFolder + genomeID + "_CSFiles/"
  # The files to contain the links to all fully processed default datasets
  fullyProcessedDefaultDatasetsFile[genomeID] = baseFolder + "Datasets/" + genomeID + "_DefaultFullyProcessedDatasets.ini"
  # The files to contain the links to all fully processed user datasets
  fullyProcessedUserDatasetsFile[genomeID] = workingFolder + genomeID + "_UserFullyProcessedDatasets.ini"

  genomeData[genomeID].update(genomeDataNumbers[genomeID])
  genomeData[genomeID].update(genomeDataStr[genomeID])


### Other Software Config ###

#bedToolsFolder = "/TL/epigenetics2/work/completesearch/dev_codebase/bedtools/bedtools-2.17.0/bin/"

# CompleteSearch config
#startedServersFile    = workingFolder + "CSservers.txt"
startedServersFile    = baseFolder+"Datasets/Servers/CSservers.txt"
CS_CODE_DIR           = "/TL/epigenetics2/work/completesearch/binaries/04.2012/"
startCompletionServer = CS_CODE_DIR + "startCompletionServer"
buildIndex            = CS_CODE_DIR + "buildIndex"
buildDocsDB           = CS_CODE_DIR + "buildDocsDB"


