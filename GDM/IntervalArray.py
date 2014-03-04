import numpy
import settings
from utilities import *
import os.path
import zipfile  

class GenomeIntervalArray:
    """ Assume that the regions are not overlapping
    """
    def __init__(self,baseName,arrayType,arrayDimension):
        self.baseName = baseName
        self.zipFileName = self.baseName.replace("CHR","").replace(".data",".zip")
        #These are for storing and loading purposes
        self.arrayType = arrayType
        self.arrayDimension = arrayDimension
        self.chroms = {}        
                
    def store(self):
        try:        
            zpa = zipfile.ZipFile(self.zipFileName,"w",zipfile.ZIP_DEFLATED)            
            for chrom in self.chroms.keys():
                chromName = self.baseName.replace("CHR",str(chrom))                
                self.chroms[chrom].tofile(str(chromName))                            
                zpa.write(str(chromName),os.path.basename(chromName))            
                os.unlink(chromName)
            zpa.close()
        except:
            os.unlink(self.zipFileName)
            raise
        
    
    def exist(self,chrom):
        chromName = self.baseName.replace("CHR",str(chrom))
        #return os.path.isfile(chromName)
        try:
            exists = os.path.isfile(self.zipFileName) and zipfile.ZipFile(self.zipFileName).getinfo(os.path.basename(chromName))
        except KeyError:
            return False
        return bool(exists) 
        
            
    def load(self,chrom):        
        chromName = self.baseName.replace("CHR",str(chrom))        
        if not self.exist(str(chrom)):
            raise GDMException, "Error: the file "+chromName+" could not be found"
        buffer = zipfile.ZipFile(self.zipFileName).read(os.path.basename(chromName))
        tempArray = numpy.frombuffer(buffer,dtype=self.arrayType)
        self.chroms[chrom] = numpy.reshape(tempArray,(-1,self.arrayDimension))
        
    def cleanup(self):
        self.store()
        for chrom in self.chroms.keys():
            del self.chroms[chrom]        
            
    def loadFullDataSortedbyChrom(self,d,removeInclusions):
        if len(d) == 0:
            raise Exception, "No data"
        startChromIndex = 0
        currentChrom = d[startChromIndex][0]
        for i in xrange(len(d)):
            if currentChrom == d[i][0]:
                pass
            else:
                self.addChromosomeArray(currentChrom,map(lambda x:x[1:],d[startChromIndex:i]),removeInclusions)
                startChromIndex = i
                currentChrom = d[i][0]
        self.addChromosomeArray(currentChrom,map(lambda x:x[1:],d[startChromIndex:]),removeInclusions)
                
    def addChromosomeArray(self,chrom,data,removeInclusions,esIndex = 1):
        #print chrom,len(data)
        global maxEnd
        def filterNextMaxSmallerThanPrevMax(y):
            global maxEnd
            if y[1]<=maxEnd:
                return False    
            else:
                maxEnd = y[1]
                return True
#        print chrom, "is added", len(a)
        if self.chroms.has_key(chrom):
            raise Exception, "chrom "+str(chrom)+" is already in the database"
        if isinstance(data,list):
            if removeInclusions:
                maxEnd = 0 
                data = numpy.array(filter(filterNextMaxSmallerThanPrevMax,data),self.arrayType)
            self.chroms[chrom] = numpy.array(data,self.arrayType)
        else:
            if removeInclusions:
                raise GDMException, "removeInclusions only works for lists"                
            self.chroms[chrom] = data
        # check for regions within regions
        for i in xrange(1,self.chroms[chrom].shape[0]):
            if self.chroms[chrom][i-1,esIndex] >= self.chroms[chrom][i,esIndex]:
                raise RegionsInclusionException, "Intervals "+str(self.chroms[chrom][i-1])+" and "+str(self.chroms[chrom][i])+" are fully included on chromosome "+str(chrom)+". Consider using IntervalTree for this dataset"  
        
    def findOneDimentional(self, chrom, start, stop):
        if not self.chroms.has_key(chrom):
            raise Exception, "No data for chromosome "+str(chrom)+" this should be removed once the software is working"+str(self.chroms.keys())
        a = self.chroms[chrom][:,0]# sorted one dimentional array of the positions
        endIndex = a.searchsorted(stop,side="right")#gives the index of the first LARGER than the sought value
        startIndex = a.searchsorted(start,side="left")#gives the index of the first EQUAL OR LARGER than the sought value
        #if value is too large os small it will give the same index and hence no values will be retrived
        return self.chroms[chrom][startIndex:endIndex,:]
    
    def findTwoDimentional(self, chrom, start, stop,localData):
        if not self.chroms.has_key(chrom):
            if self.exist(chrom):
                self.load(chrom)
            else:
                localData['distanceDownstream'] = settings.MAX_DISTANCE
                localData['distanceUpstream'] = settings.MAX_DISTANCE                
                #log("Error: No data for chromosome "+str(chrom)+" this should be removed once the software is working"+str(self.chroms.keys()))
                return []
        #a = self.chroms[chrom][:,0]# sorted one dimentional array of the positions
        endIndex = self.chroms[chrom][:,0].searchsorted(stop,side="right")#gives the index of the first LARGER than the sought value
        startIndex = self.chroms[chrom][:,1].searchsorted(start,side="left")#gives the index of the first EQUAL OR LARGER than the sought value
        
        #if value is too large os small it will give the same index and hence no values will be retrived
        try:            
            if startIndex > 0:
                localData['distanceUpstream'] = start - self.chroms[chrom][startIndex-1,1]                
            else:
                localData['distanceUpstream'] = settings.MAX_DISTANCE
        except UnboundLocalError:
            localData['distanceUpstream'] = settings.MAX_DISTANCE
        try:
            
            localData['distanceDownstream'] = self.chroms[chrom][endIndex,0] - stop
            if localData['distanceDownstream'] < 0:                
                localData['distanceDownstream'] = settings.MAX_DISTANCE
        except UnboundLocalError:            
            localData['distanceDownstream'] = settings.MAX_DISTANCE
        except IndexError:            
            localData['distanceDownstream'] = settings.MAX_DISTANCE
             
        if startIndex > 0 and self.chroms[chrom].shape[0] > startIndex + 1 and self.chroms[chrom][startIndex,1] == start:
            startIndex += 1
        if endIndex > 0 and self.chroms[chrom].shape[0] > endIndex and self.chroms[chrom][endIndex,0] == stop:
            endIndex -=1
            
        return self.chroms[chrom][startIndex:endIndex,:].copy()
    
    def findTwoDimentionalWithAdditionalInfo(self, chrom, start, stop,localData, ssIndex = 0, esIndex = 1):
        """
        This method uses the additional info that the regions are provided sorted 
        hence we don't need to search in the whole array 
        """
        if not self.chroms.has_key(chrom):
            # The data for this chromosoem is not loaded
            if self.exist(chrom):
                #load it if it exists
                self.load(chrom)
            else:
                #return no overlaps found otherwise
                localData['distanceDownstream'] = settings.MAX_DISTANCE
                localData['distanceUpstream'] = settings.MAX_DISTANCE                
                
                return []
        if localData['currentChrom'] == chrom and localData['currentChromStart'] <= start:
            #gives the index of the first EQUAL OR SMALLER than the sought value
            startIndex = self.chroms[chrom].shape[0]            
            for i in xrange(localData['currentStartIndex'],self.chroms[chrom].shape[0]):
                if self.chroms[chrom][i,esIndex] > start:
                    startIndex = i
                    break
            
            #gives the index of the first LARGER than the sought value
            endIndex = self.chroms[chrom].shape[0]
            for i in xrange(localData['currentStartIndex'],self.chroms[chrom].shape[0]):
                if self.chroms[chrom][i,ssIndex] >= stop:
                    endIndex = i
                    break
#            endIndexCheck = self.chroms[chrom][:,ssIndex].searchsorted(stop,side="right")
#            startIndexCheck = self.chroms[chrom][:,esIndex].searchsorted(start,side="left")
#            if startIndexCheck != startIndex:
#                print "StartIndex",startIndexCheck, startIndex,chrom, start, stop
#                print self.chroms[chrom][startIndexCheck,:],self.chroms[chrom][startIndex,:]
#                if self.chroms[chrom][startIndexCheck,1] != start:
#                    raise Exception            
#            if endIndexCheck != endIndex:
#                print "EndIndex",endIndexCheck, endIndex,chrom, start, stop
#                print self.chroms[chrom][endIndexCheck,:],self.chroms[chrom][endIndex,:]
#                if self.chroms[chrom][endIndex,0] > stop: 
#                    raise Exception
            #print "start rel",startIndex,endIndex,(chrom, start, stop)
        else:
            #gives the index of the first LARGER than the sought value
            endIndex = self.chroms[chrom][:,ssIndex].searchsorted(stop,side="right")
            #gives the index of the first EQUAL OR LARGER than the sought value
            startIndex = self.chroms[chrom][:,esIndex].searchsorted(start,side="left")
            #print "start abs",startIndex,endIndex,(chrom, start, stop) 
            #if value is too large os small it will give the same index and hence no values will be retrived           
        try:
            localData['currentStartIndex'] = startIndex
            if localData['currentStartIndex'] > 0:
                localData['distanceUpstream'] = start - self.chroms[chrom][localData['currentStartIndex']-1,1]                
            else:
                localData['distanceUpstream'] = settings.MAX_DISTANCE
        except UnboundLocalError:
            startIndex = self.chroms[chrom].shape[0]
            localData['currentStartIndex'] = startIndex
            localData['distanceUpstream'] = settings.MAX_DISTANCE
        try:
            localData['currentEndIndex'] = endIndex
            localData['distanceDownstream'] = self.chroms[chrom][localData['currentEndIndex'],0] - stop
            if localData['distanceDownstream'] < 0:
                endIndex = self.chroms[chrom].shape[0]
                localData['currentEndIndex'] = endIndex
                localData['distanceDownstream'] = settings.MAX_DISTANCE
        except UnboundLocalError:
            endIndex = self.chroms[chrom].shape[0]
            localData['currentEndIndex'] = endIndex
            localData['distanceDownstream'] = settings.MAX_DISTANCE
        except IndexError:
            endIndex = self.chroms[chrom].shape[0]
            localData['currentEndIndex'] = endIndex
            localData['distanceDownstream'] = settings.MAX_DISTANCE 
        localData['currentChrom'] = chrom
        localData['currentChromStart'] = start
        #print "end",localData['currentStartIndex'],localData['currentEndIndex']
        return self.chroms[localData['currentChrom']][localData['currentStartIndex']:localData['currentEndIndex'],:].copy()
    
    def findTwoDimentionalNeighborhood(self,chrom,positions):
        if not self.chroms.has_key(chrom):            
            if self.exist(chrom):
                self.load(chrom)
            else:
                return "0"*len(positions)
        overlapData = ""
        indeces = self.chroms[chrom][:,1].searchsorted(positions)
#        for i in range(indeces[0]-1,indeces[1]+1):
#            if i > 0:
#                print list(self.chroms[chrom][i,:])
        for i in xrange(len(indeces)):
            try:
                if self.chroms[chrom][indeces[i],0] <= positions[i]:
                    overlapData += "1"
                else:
                    overlapData += "0"
            except:
                overlapData += "0"
#        print overlapData
        return overlapData
        
        
        
        
        
        
     
