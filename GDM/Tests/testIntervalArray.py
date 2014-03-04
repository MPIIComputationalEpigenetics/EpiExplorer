import unittest
import numpy
import sys
import os
import os.path

if sys.platform == "win32":
    sys.path.insert(0,"D:\\Projects\\Integrated_Genome_Profile_Search_Engine\\Cosgen\\GDM")
else:    
    mainFolder = os.path.abspath(os.path.dirname(__file__)+"/..")+os.sep    
    sys.path.insert(0,mainFolder)    
import IntervalArray

class testIntervalArray(unittest.TestCase):
    def setUp(self):
        self.ia = IntervalArray.GenomeIntervalArray()
        chr1Data = numpy.array([[3,5],
                                [6,8],
                                [10,13],
                                [20,21],
                                [22,25],
                                [30,40],
                                [42,43],
                                [100,110],
                                [200,201],                                
                                ])
        self.ia.addChromosomeArray("chr1",chr1Data,False)
        chr2Data = numpy.array([[7,15],
                                [150,155],                                                                
                                ])
        self.ia.addChromosomeArray("chr2",chr2Data,False)
        
        

    def test_notExistingChromosome(self):
        # make sure the shuffled sequence does not lose any elements
        failed= False
        try:
            self.ia.findTwoDimentionalWithAdditionalInfo("chr3",5,15)
        except:
            failed = True
        if failed == False:
            self.fail("No Exception was raised")
    def test_beforeFirst(self):
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",1,2)
        self.assertEquals(len(x),0)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,0)
        self.assertEquals(self.ia.currentEndIndex,0)
    def test_overlapsWithFirst(self):
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",2,4)
        self.assertEquals(len(x),1)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,0)
        self.assertEquals(self.ia.currentEndIndex,1)
        
    def test_overlapsWithFirstThree(self):
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",2,15)
        self.assertEquals(len(x),3)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,0)
        self.assertEquals(self.ia.currentEndIndex,3)
    
    def test_overlapsWithMiddle2(self):
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",18,26)
        self.assertEquals(len(x),2)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,3)
        self.assertEquals(self.ia.currentEndIndex,5)
        
    def test_inMiddle(self):
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",27,28)
        self.assertEquals(len(x),0)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,5)
        self.assertEquals(self.ia.currentEndIndex,5)
        
    def test_overlapsLast(self):
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",195,203)
        self.assertEquals(len(x),1)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,8)
        self.assertEquals(self.ia.currentEndIndex,9)
    def test_afterLast(self):
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",203,250)
        self.assertEquals(len(x),0)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,9)
        self.assertEquals(self.ia.currentEndIndex,9)
        
    def test_alltogether(self):            
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",1,2)
        self.assertEquals(len(x),0)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,0)
        self.assertEquals(self.ia.currentEndIndex,0)
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",1,4)
        self.assertEquals(len(x),1)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,0)
        self.assertEquals(self.ia.currentEndIndex,1)
        
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",1,15)
        self.assertEquals(len(x),3)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,0)
        self.assertEquals(self.ia.currentEndIndex,3)
    
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",18,26)
        self.assertEquals(len(x),2)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,3)
        self.assertEquals(self.ia.currentEndIndex,5)
        
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",27,28)
        self.assertEquals(len(x),0)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,5)
        self.assertEquals(self.ia.currentEndIndex,5)
        
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",195,203)
        self.assertEquals(len(x),1)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,8)
        self.assertEquals(self.ia.currentEndIndex,9)
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",203,250)
        self.assertEquals(len(x),0)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,9)
        self.assertEquals(self.ia.currentEndIndex,9)
        
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr1",300,310)
        self.assertEquals(len(x),0)
        self.assertEquals(self.ia.currentChrom,"chr1")
        self.assertEquals(self.ia.currentStartIndex,9)
        self.assertEquals(self.ia.currentEndIndex,9)
        
        # search for element before the first        
        x = self.ia.findTwoDimentionalWithAdditionalInfo("chr2",1,2)
        self.assertEquals(len(x),0)
        self.assertEquals(self.ia.currentChrom,"chr2")
        self.assertEquals(self.ia.currentStartIndex,0)
        self.assertEquals(self.ia.currentEndIndex,0)
        
        


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(testIntervalArray)
    unittest.TextTestRunner(verbosity=2).run(suite)

    #unittest.main()
