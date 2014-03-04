from utilities import *
import os.path
import sqlite3
import time

def collectFullRegions(datasets,cgsAS):
    fn = getRegionsCollectionName(cgsAS.datasetCollectionName,cgsAS.genome)
    fnBed = fn[:-8]+".bed"
    #what to do if the file is already computed
    if os.path.isfile(fn):
        #os.unlink(fn)
        log("General: The collection of all regions is already computed "+fn)
        log("...checking for any new datasets...")
        # we need to check if the regions are already processed
        connI = sqlite3.connect(fn)
        cI = connI.cursor()
        cI.execute('SELECT datasetName,datasetID FROM datasets')
        processedDatasets = {}
        for row in cI:
             processedDatasets[str(row[0])] = row[1]
        cI.close()
        connI.close()
        allOK = True
        #for datasetKey in datasets.keys():
        
        for datasetKey in cgsAS.regionDatasets.keys():
            dataset = datasets[datasetKey]        
            #if dataset.hasGenomicRegions:# The cgsAS.regionDatasets assures that this region is meant to be collected
            if processedDatasets.has_key(dataset.datasetSimpleName):
                log("..."+dataset.datasetSimpleName+" is present")
            else:
                allOK = False
                log("..."+dataset.datasetSimpleName+" is NOT present")
                log("... deleting combined regions file "+fn)
                os.unlink(fn)
                break
#        if not allOK:
#            for datasetKey in datasets.keys():
#                fnd = datasets[datasetKey].getDatasetBinaryName()
#                if os.path.isfile(fnd):
#                    log("... deleting the processed data for "+datasets[datasetKey].datasetSimpleName+ " stored in "+fnd)                 
#                    os.unlink(fnd)
        if allOK:
            log("...no new datasets. Skipping collection of regions")
            return
    
    connTemp = sqlite3.connect(fn+".temp")
    cTemp = connTemp.cursor()
    cTemp.execute('CREATE TABLE regions_temp (chrom INTEGER, start INTEGER, stop INTEGER, datasetID INTEGER, score INTEGER, strand INTEGER)')
    datasetsIndex = {}
    datasetID = 0
    id = 1
    try:
        #for datasetKey in datasets.keys():
        for datasetKey in cgsAS.regionDatasets.keys():        
            dataset = datasets[datasetKey]        
            #if dataset.hasGenomicRegions:# The cgsAS.regionDatasets assures that this region is meant to be collected
            datasetID += 1
            log(dataset.datasetSimpleName+": Collecting regions")
            regions = dataset.getRegions()
            
            datasetsIndex[datasetID] = dataset.datasetSimpleName
            i = 0
            if regions.shape[1] == 3:
                defScore = -1
                defStrand = 0
                # No strands and scores available fill them all with zeros
                for i in xrange(regions.shape[0]):
                    cTemp.execute("INSERT INTO regions_temp VALUES (?,?,?,?,?,?)",( int(regions[i,0]),
                                                                               int(regions[i,1]),
                                                                               int(regions[i,2]),
                                                                               datasetID,
                                                                               defScore,
                                                                               defStrand))                    
            else:
                # With strands or scores or both
                for i in xrange(regions.shape[0]): 
                    cTemp.execute("INSERT INTO regions_temp VALUES (?,?,?,?,?,?)",(int(regions[i,0]),
                                                                               int(regions[i,1]),
                                                                               int(regions[i,2]),
                                                                               datasetID,
                                                                               int(regions[i,3]),
                                                                               int(regions[i,4])))                    
                
            connTemp.commit()            
            log(dataset.datasetSimpleName+": "+str(len(regions))+" regions were committed to the database")
    except:
        os.unlink(fn+".temp")
        raise
    #sort the regions
    connI = sqlite3.connect(fn)
    cI = connI.cursor()
    cI.execute('CREATE TABLE datasets (datasetName TEXT, datasetID INTEGER)')
    
    for datasetID in datasetsIndex.keys():
        cI.execute("INSERT INTO datasets VALUES (?,?)",(datasetsIndex[datasetID],datasetID))
        #print "Inserted into the datasets database",datasetsIndex[datasetID],datasetID
        
    connI.commit()
    #cI.execute('CREATE TABLE regions (id INTEGER,chrom INTEGER, start INTEGER, stop INTEGER,length INTEGER,datasetID INTEGER)')
    cI.execute('CREATE TABLE regions (regionID INTEGER,chrom INTEGER, start INTEGER, stop INTEGER, datasetID INTEGER, score INTEGER, strand INTEGER)')
    
    cTemp.execute("SELECT COUNT(*) FROM regions_temp")
                        
    #cTemp.execute("SELECT DISTINCT chrom, start, stop, datasetID, score, strand  FROM regions_temp ORDER BY chrom,start,stop")
    cTemp.execute("SELECT chrom, start, stop, datasetID, score, strand  FROM regions_temp ORDER BY chrom,start,stop")
    i = 1
    fnBedF  = open(fnBed,"w")
    for row in cTemp:
        #print row
#        cI.execute("INSERT INTO regions VALUES (?,?,?,?,?,?)",(id,
        fnBedF.write("\t".join([convertIntToChrom(cgsAS.genome,row[0]),str(row[1]),str(row[2]),str(id),str(row[4]),convertIntToStrand(row[5])])+"\n")
        cI.execute("INSERT INTO regions VALUES (?,?,?,?,?,?,?)",(id,
                                                             row[0],
                                                             row[1],
                                                             row[2],                                                        
                                                             row[3],
                                                             row[4],
                                                             row[5]))
        id += 1
    connI.commit()        
    cTemp.close()
    connTemp.close()
    os.unlink(fn+".temp")    
    cI.close() 
    fnBedF.close()              
    log("General: All regions are collected")
    connI.close() 
#    listDatabaseInfo(fn)
             
            