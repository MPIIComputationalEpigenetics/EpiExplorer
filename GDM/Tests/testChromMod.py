import unittest
import numpy
import sys
import cx_Oracle
import random
import os
import os.path
 

if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
else:    
    mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep    
    sys.path.insert(0,mainFolder)     
import readDatasetDescriptions
import utilities

class testChromMod(unittest.TestCase):
    def setUp(self):
        pass
        
#    def test_100_CTCF_regions(self):
#        self.mainTest("CTCF",100)
#    def test_100_PolII_regions(self):
#        self.mainTest("PolII",100)
#    def test_100_H3K4me3_regions(self):
#        self.mainTest("H3K4me3",100)
#    def test_100_H3K27me2_regions(self):
#        self.mainTest("H3K27me2",100)
#    def test_100_H3K9me1_regions(self):
#        self.mainTest("H3K9me1",100)
        
    def test_Fixed_Region(self):        
        regionID = 42469
        chrommod = "H3K4me3"
        self.oneRegionTest(regionID,chrommod)
    def test_Fixed_Region_Full(self):
        self.fail()
        regionID = 42469         
        self.chmodName = "H3K4me3"
        self.chrommod = readDatasetDescriptions.readDataset(["chrommod_"+self.chmodName,
                                                        "hg18_Barski_chrommod_"+ self.chmodName +".ini",
                                                        "D:/Projects/Integrated_Genome_Profile_Search_Engine/Cosgen/Datasets/"])
        self.chrommod.datasetCollectionName = "main"   
        
        self.chrommod.openDBConnections()        
        self.chrommod.cR.execute("SELECT regionID,chrom,start,stop FROM regions WHERE regionID="+str(regionID))
        regionData = list(self.chrommod.cR.fetchone())
        chrom = regionData[1]
        start = regionData[2]
        stop = regionData[3]
        print chrom,start,stop        
        self.chrommod.initializeIntervalArray()
        overlapingRegionsInterval = self.chrommod.intervalArray.findTwoDimentionalWithAdditionalInfo(chrom, start, stop,0,1)
        print overlapingRegionsInterval
        reducedGR = utilities.gr_reduceRegionSet(list(overlapingRegionsInterval))
        print reducedGR
        overlap_ratio = utilities.gr_Coverage(reducedGR, start, stop) / float(stop - start)
        print overlap_ratio
        
    def oneRegionTest(self,regionID,chrommod):
        self.chmodName = chrommod
        self.chrommod = readDatasetDescriptions.readDataset(["chrommod_"+self.chmodName,
                                                        "hg18_Barski_chrommod_"+ self.chmodName +".ini",
                                                        "D:/Projects/Integrated_Genome_Profile_Search_Engine/Cosgen/Datasets/"])
        self.chrommod.datasetCollectionName = "main"        
        
        self.chrommod.openDBConnections()        
        self.chrommod.cR.execute("SELECT regionID,chrom,start,stop FROM regions WHERE regionID="+str(regionID))
        regionData = list(self.chrommod.cR.fetchone())
        start = regionData[2]
        stop = regionData[3]
        print regionID,regionData
        sqlQuery = "SELECT overlap_ratio, overlap_count FROM "+ self.chrommod.datasetSimpleName + "_data WHERE regionID = "+str(regionID)
        self.chrommod.cD.execute(sqlQuery)
        regionResult = list(self.chrommod.cD.fetchone())
        print regionID,regionResult
        dbcon = cx_Oracle.connect("epigraph_admin", "epigraph123", "bioinfo")
        dbcur = dbcon.cursor()
        oracleSQLQuery = "SELECT chromstart, chromend FROM hg18_EPIGRAPH_#romatin WHERE chrom = '"+str(utilities.convertIntToChrom(self.genome,regionData[1]))+"' AND chromstart <= "+str(stop)+" AND chromend > "+str(start)+" AND chrommod = '"+self.chmodName+"' ORDER BY chromstart"
        dbcur.execute(oracleSQLQuery)
        oracleD = map(list,list(dbcur.fetchall()))
        print regionID,oracleD
        reducedGR = utilities.gr_reduceRegionSet(list(oracleD))
        oracle_overlap_ratio = utilities.gr_Coverage(reducedGR, start, stop) / float(stop - start)
        self.assertEqual(len(oracleD),regionResult[1])
        self.assertEqual(regionResult[0],oracle_overlap_ratio)
        
                
    def mainTest(self,chrommod,n):
        self.chmodName = chrommod        
        self.chrommod = readDatasetDescriptions.readDataset(["chrommod_"+self.chmodName,
                                                        "hg18_Barski_chrommod_"+ self.chmodName +".ini",
                                                        "D:/Projects/Integrated_Genome_Profile_Search_Engine/Cosgen/Datasets/"])
        self.chrommod.datasetCollectionName = "main"
        
        # load n random regions
        self.chrommod.openDBConnections()
        self.chrommod.cR.execute("SELECT COUNT(*) FROM regions")
        nRows = self.chrommod.cR.fetchone()[0]
        print nRows
        self.chrommod.cR.execute("SELECT regionID,chrom,start,stop,datasetID FROM regions ORDER BY regionID")
        dR = self.chrommod.cR.fetchall()
        selectedRegionIDs = []
        selectedRegionsData = {}
        for i in range(n):
            id  = random.randint(0,nRows-1)
            selectedRegionIDs.append(id)
            if id != dR[id-1][0]:
                print id, dR[id-1]
                raise Exception                
            selectedRegionsData[id] = dR[id-1][1:]
            
        selectedRegionIDs = list(set(selectedRegionIDs))
        selectedRegionIDs.sort()
        print selectedRegionIDs
        dbcon = cx_Oracle.connect("epigraph_admin", "epigraph123", "bioinfo")
        dbcur = dbcon.cursor()
        count = 0
        for regionID in selectedRegionIDs:
            sqlQuery = "SELECT overlap_ratio, overlap_count FROM "+ self.chrommod.datasetSimpleName + "_data WHERE regionID = "+str(regionID)
            self.chrommod.cD.execute(sqlQuery)
            try:
                regionData = list(self.chrommod.cD.fetchone())
                overlap_ratio = regionData[0]  
                overlap_count = regionData[1]
            except TypeError,ex:
                overlap_ratio = 0
                overlap_count  = 0                
            start = selectedRegionsData[regionID][1]
            stop = selectedRegionsData[regionID][2]
            print regionID,overlap_ratio,overlap_count
            oracleSQLQuery = "SELECT chromstart, chromend FROM hg18_EPIGRAPH_#romatin WHERE chrom = '"+str(utilities.convertIntToChrom(self.genome,selectedRegionsData[regionID][0]))+"' AND chromstart <= "+str(stop)+" AND chromend > "+str(start)+" AND chrommod = '"+self.chmodName+"' ORDER BY chromstart"
            print oracleSQLQuery
            dbcur.execute(oracleSQLQuery)
            oracleD = map(list,list(dbcur.fetchall()))
            #print oracleD
            self.assertEqual(overlap_count,len(oracleD))
            reducedGR = utilities.gr_reduceRegionSet(list(oracleD))
            oracle_overlap_ratio = utilities.gr_Coverage(reducedGR, start, stop) / float(stop - start)
            self.assertEqual(overlap_ratio,oracle_overlap_ratio)        
#    def test_beforeFirst(self):
#        # search for element before the first        
#        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",1,2)
#        self.assertEquals(len(x),0)
#        self.assertEquals(self.ia.currentChrom,"chr1")
#        self.assertEquals(self.ia.currentStartIndex,0)
#        self.assertEquals(self.ia.currentEndIndex,0)
    

if __name__ == '__main__':
    unittest.main()
