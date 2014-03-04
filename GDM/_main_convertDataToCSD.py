## @package convert genomic data To CompleteSearch formats
#
# Author : Konstantin Halachev halachev@mpi-inf.mpg.de
#
# Converts genome datasets into CompleteSearch preindex format.
#
# Needs to scan:
# which datasets are available
# extract the regions from them 
# for every region, compute the properties of all datasets with it
# export all those dataset properties to a ascii text with format 
# word <tab> documentID <tab> ranking_score <tab> position_in_document
# http://docs.python.org/library/sqlite3.html
# http://www.scipy.org/Numpy_Example_List
from utilities import *
import settings
#import psyco; psyco.full()
import sys
import subprocess
import os.path
import CGSAnnotationsSettings
#os.chdir(settings.baseFolder)

#===============================================================================
# #Step 0 Read the settings
#===============================================================================
genome = sys.argv[1]
directParam = "computeAll"
if len(sys.argv) > 2:
    directParam = sys.argv[2] 
print "Genome:",genome
datasetCollectionName = genome+"_ucsc_cpg_islands_test"
cgsAS = CGSAnnotationsSettings.CGSAnnotationsSettings(datasetCollectionName,genome,{},{})

if directParam == "computeAll":
    datasetsIndexFile = getMainDatasetIndexFileName(cgsAS.genome+"_test")
    #===============================================================================
    # #Step 1 Read all datasets
    #===============================================================================
    import readDatasetDescriptions
    datasets = readDatasetDescriptions.readDatasets(datasetsIndexFile)
    
    #===============================================================================
    # #Step 2 Download and process datasets
    #===============================================================================
    #datasets = {"broad_histones_CTCF":datasets["broad_histones_CTCF"],
    #            datasetCollectionName:datasets[datasetCollectionName]}
    for dataset in datasets:
        datasets[dataset].init()
        cgsAS.addFeatureDataset({dataset:datasets[dataset].getDefaultAnnotationSettings()})
        if dataset == "hg18_ensembl_gene_genes":
            cgsAS.addFeatureDataset({"hg18_ensembl_gene_genes":{"includeGO":True,
                                              "includeGeneDescriptions": True,
                                              "includeOMIM": True,
                                              "includeGeneTranscripts":False,
                                              "includeGenesUpTo":10000}})
        if dataset.startswith("hg18_broad"):
            cgsAS.addFeatureDataset({dataset:{"useNeighborhood":True}})        
            #print cgsAS.featuresDatasets[dataset]
        if dataset.startswith("nihre_"):
            cgsAS.addFeatureDataset({dataset:{"includeGO":True,
                                              "includeGeneDescriptions": True,
                                              "includeGeneTranscripts":True,
                                              "includeGenesUpTo":50000}})
            
    for dataset in datasets:    
        datasets[dataset].downloadDataset()    
        datasets[dataset].preprocessDownloadedDataset()    
    
    ##===============================================================================
    ## #Step 3 Collect all regions
    ##===============================================================================
    
        
    # I gave up the idea for a 
    import collectRegions
    dn = genome+"_ucsc_cpg_islands"
    cgsAS.addRegionDataset({dn:datasets[dn].getDefaultAnnotationSettings()})
    collectRegions.collectFullRegions(datasets,cgsAS)
    
    
    ##===============================================================================
    ## #Step 4 Compute properties of the regions
    ##===============================================================================
    for datasetName in datasets.keys():        
        datasets[datasetName].computeRegionsProperties(cgsAS)
    
    ##===============================================================================
    ## #Step 5 export all the data to the input format of the CompleteSearch
    ##===============================================================================
    
    import exportRegionData
    exportRegionData.exportAllData(datasets,cgsAS)    
    ##===============================================================================
    ## #Step 6 print detailed description of all words that are available
    ##===============================================================================
    #import exportRegionData
    #exportRegionData.exportWordDescription(datasets,cgsAS)
    
    ##===============================================================================
    ## #Step 7 preprocess the CS server
    ##===============================================================================
    import subprocess
    
    #p = subprocess.call(["make", "--directory=" + settings.indexDataFolder[cgsAS.genome], "-e", "-B", "all"], env={"DB": cgsAS.datasetCollectionName})
    p = subprocess.Popen(["make", "--directory=" + settings.indexDataFolder[cgsAS.genome], "-e", "-B", "all.withprefixes"], env={"DB": cgsAS.datasetCollectionName}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()        
    print "makeOutput: ",str(stdout)

if directParam == "startServer":
    import subprocess
    if cgsAS.genome == "hg18":
        port = "8890"
    elif cgsAS.genome == "hg19":
        port = "8891"
    else:
        port = "8892"
    p = subprocess.call(["make", "--directory=" + settings.indexDataFolder[cgsAS.genome], "-e", "start"], env={"DB": cgsAS.datasetCollectionName,"PORT":port})

#print doc