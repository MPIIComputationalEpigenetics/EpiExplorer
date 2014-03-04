from threading import BoundedSemaphore
from threading import RLock
from utilities import log

class DatasetProcessorManager:
    def __init__(self):
        self.setFastQueueThreshold(40 * 1000)
        self.__fast_queue = CGSBoundedSemaphore(value=1)
        self.__slow_queue = CGSBoundedSemaphore(value=1)   
        self.datasetComputationsInProgress = {}
        self.datasetQueue = {}

	#--- Schedule a computation for execution ()
    def acquire(self, datasetID, size=0):
        if size <= self.__threshold:
            log("DatasetProcessorManager.acquire(dataset="+str(datasetID)+",size=" + repr(size) + "): put in the __fast_queue")
            self.datasetQueue[datasetID] = self.__fast_queue
            self.__fast_queue.acquire(datasetID)
            log("DatasetProcessorManager dataset="+str(datasetID)+"running from the from the __fast_queue")
        else:
            log("DatasetProcessorManager.acquire(dataset="+str(datasetID)+",size=" + repr(size) + "): put in the __slow_queue")
            self.datasetQueue[datasetID] = self.__slow_queue
            self.__slow_queue.acquire(datasetID)
            log("DatasetProcessorManager dataset="+str(datasetID)+" running from the __slow_queue")

    def release(self, datasetID, size=0):
		if size <= self.__threshold:
			self.__fast_queue.release(datasetID)
 			log("DatasetProcessorManager.release(dataset="+str(datasetID)+",size=" + repr(size) + ") from the __fast_queue")
		else:
			self.__slow_queue.release(datasetID)
			log("DatasetProcessorManager.release(dataset="+str(datasetID)+",size=" + repr(size) + ") from the __slow_queue")
			
    def getComputationStatus(self, datasetID):
        if self.datasetComputationsInProgress.has_key(datasetID):
			#waiting or computing
            if self.datasetComputationsInProgress[datasetID][0] == 2:
                #waiting, update waiting status
                self.indicateComputationWaiting(datasetID) 
            return self.datasetComputationsInProgress[datasetID]
        else:
			#not available
			return [-1]

    def indicateComputationError(self, datasetName, errorMessage):
            self.datasetComputationsInProgress[datasetName] = [3, errorMessage]
    
    def indicateComputationProgress(self, datasetName, progressMessage):
            self.datasetComputationsInProgress[datasetName] = [1, progressMessage]
    
    def indicateComputationWaiting(self, datasetName):
        if self.datasetQueue.has_key(datasetName):
            self.datasetComputationsInProgress[datasetName] = [2,self.datasetQueue[datasetName].getIndexDatasetId(datasetName)]
        else:
            self.datasetComputationsInProgress[datasetName] = [2,"Not scheduled yet"]
            
    def removeComputation(self, datasetID):
        if self.datasetComputationsInProgress.has_key(datasetID):
            del self.datasetComputationsInProgress[datasetID]	
        if self.datasetQueue.has_key(datasetID):
            del self.datasetQueue[datasetID]
	
    def setFastQueueThreshold(self,newThreshold):
        self.__threshold = newThreshold
    
    def getFastQueueThreshold(self):
        return self.__threshold
        	  
    def stopWaitingComputation(self, datasetName):
		if self.datasetComputationsInProgress.has_key(datasetName):
			#waiting or computing            
			if self.getComputationStatus(datasetName)[0] == 2:
				#waiting
				self.removeComputation(datasetName)
				return "Success"
			else:
				return "Dataset is not in waiting mode"
		else:
			#not available 
			return "Dataset is not available"
#	def bockProcessing(self, datasetName):
#		pass
#
#	def killProcessing(self, datasetName):
#		pass
#
#	def setThreshold(self, thresholds):
#		pass
#
#	def removePriority(self, datasetName):
#		pass
#
#	def increasePriority(self, threshold):
#		pass
#
#	def startWaitingProcessing(self, datasetName):
#		pass
#
#	def cancelWaitingProcessing(self, datasetName):
#		pass
#    def saveQueuedDatasets():
    def status(self):
        return [self.__fast_queue.status(),self.__slow_queue.status()]
        
class CGSBoundedSemaphore:
    def __init__(self,value):
        self.boundedSemaphore = BoundedSemaphore(value)
        self.datasetQueueLock = RLock()
        self.datasetQueue = []
    
    def acquire(self,datasetId):
        try:
            self.datasetQueueLock.acquire()
            self.datasetQueue.append(datasetId)
        finally:
            self.datasetQueueLock.release()
        self.boundedSemaphore.acquire()
        
    def release(self,datasetId):
        try:
            self.datasetQueueLock.acquire()
            self.datasetQueue.remove(datasetId)
        except:
            pass
        finally:
            self.datasetQueueLock.release()
        self.boundedSemaphore.release()
    
    def getIndexDatasetId(self,datasetId):
        try:
            self.datasetQueueLock.acquire()
            return self.datasetQueue.index(datasetId)
        except:            
            return -1
        finally:
            self.datasetQueueLock.release()
    
    def status(self):
        return list(self.datasetQueue)
        
        
if __name__ == "__main__":
    import threading
    import time
    import random
    dpm = DatasetProcessorManager()
    computations = []
    class TThread(threading.Thread):
        def __init__(self, dpm, datasetID, size):
            threading.Thread.__init__(self)
            self.datasetId = datasetID
            self.size = size
            self.dpm = dpm
            
        def run(self):
            print "Starting " + self.datasetId
            try:                
                dpm.indicateComputationWaiting(self.datasetId)
                dpm.acquire(self.datasetId, self.size)
                self.dpm.indicateComputationProgress(self.datasetId,"progress")# computing
                print "Running " + self.datasetId
                time.sleep(random.randint(5,15))
            except Exception,ex:
                print ex           
            finally:
                dpm.release(self.datasetId, self.size)
            self.dpm.removeComputation(self.datasetId)
            print "Exiting " + self.datasetId
    
    def printStatus():
        print "DPM status:",dpm.status()
        if len(computations) > 0:
            did = computations[random.randint(0,len(computations)-1)]
            print "Computation status:",did,dpm.getComputationStatus(did)
        t = threading.Timer(5, printStatus) # run each 5 secs        
        t.start()
    printStatus()
    
    fast = 10
    slow = 20
    for i in range(1,slow+1):        
        did = "d"+str(i)+"-slow"
        computations.append(did)
        t = TThread(dpm,did,50000+i*10000)
        t.start()
    for i in range(1,fast+1):
        did = "d"+str(i)+"-fast"
        computations.append(did)
        t = TThread(dpm,did,10000+i*1000)
        t.start()
        
    
    
        
