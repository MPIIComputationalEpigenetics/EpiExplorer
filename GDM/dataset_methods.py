import random
import time
import numpy
import utilities
import settings

#===============================================================================
# @summary filterByLength: intersects two regions l1, l2
# every region is list of 3 elements chrom,chromstart, chromend
# @param l1: region1
# @param l2: region2
# @return: 0 means intersection, -1 is first region is before the second, 1is second region is before the first
#===============================================================================
def intersect(l1,l2):
    l1Chr = convertChromToSortableNumber(l1[0])
    l2Chr = convertChromToSortableNumber(l2[0])
    if l1Chr==l2Chr and (l1[1]<l2[2] and l2[1]<l1[2]):
        return 0
    if l1Chr < l2Chr or (l1Chr == l2Chr and l1[2] <= l2[1]):
        return -1
    if l1Chr > l2Chr or (l1Chr == l2Chr and l2[2] <= l1[1]):
        return 1  

#===============================================================================
# @summary filterByLength: Filter every region by length
# every region is list of 3 elements chrom,chromstart, chromend
# @param data: ?
# @param minLen: minimum length
#===============================================================================
def filterByLength(data,minLen):
    return filter(lambda x:(x[2]-x[1])>=minLen,data)

# 
#===============================================================================
# @summary mergeOverlapping: base method for merge overlapping
# @param data: ?
# @param method: either "first" or "max" see below
#===============================================================================
def mergeOverlapping(data,method):
    if method == "first":
        newdata = mergeOverlappingFirst(data)
    elif method == "max":
        newdata = mergeOverlappingMax(data)
    print "Merging removed",len(data)- len(newdata),"regions"
    return newdata

#===============================================================================
# @summary mergeOverlappingFirst: overlapping first is preserved and every following that overlaps with it is omitted,the next that does not overlap is again added
# @param data: ?
#===============================================================================
def mergeOverlappingFirst(data):
    newData = [data[0]]
    ld = len(data)    
    intersectID = 0    
    for i in range(1,ld):
        isect = False
        for j in range(len(newData)-1,intersectID-1,-1):
            if intersect(data[i],newData[j]) == 0:
                isect = True
                break
        if not isect:
           newData.append(data[i])
           intersectID = len(newData)-1
    return newData
# 
#===============================================================================
# @summary mergeOverlappingMax: unite all overlapping regions to the maximum region
# @param data: ?
# @param f: method that merges values of the score columns 
#===============================================================================
def mergeOverlappingMax(data,f=max):
    newData = []
    ld = len(data)
    le = len(data[0])
    ler = range(3,le)    
    intersectStart = 0    
    for i in range(ld):
        add = True 
        if i != ld -1:            
            for j in range(intersectStart,i+1):
                if intersect(data[j],data[i+1]) == 0:
                    add = False                    
        if add:
            d = [data[intersectStart][0],
                 data[intersectStart][1],
                 max(map(lambda x:data[x][2],range(intersectStart,i+1)))]
            for j in ler:
                d.append(f(map(lambda x:data[x][j],range(intersectStart,i+1)))) 
            newData.append(d)
            intersectStart = i+1
    utilities.log(str(ld - len(newData))+": after merging overlaping the dataset was reduced from "+str(ld)+" lines to "+ str(len(newData)))
    return newData

#===============================================================================
# @summary removeIntersection: remove the regions from dataset1 that overlap with the regions of dataset2
# the region sets are asuumed to be sorted by chrom and chromstart
# @param data1: dataset 1 
# @param data2: dataset 2
#=============================================================================== 
def divideIntersection(data1,data2,keepOrRemove):
    l2 = len(data2)    
    nonIntersectionData = []
    intersectingData = []    
    d2 = 0    
    for d1 in range(len(data1)):
        iv = intersect(data1[d1],data2[d2])
        if iv > 0:
            # regions in data1 is after next region in data2, move j, until one of the below cases
            while d2 < l2 and iv > 0:                
                d2 += 1
                if d2 < l2:
                    iv = intersect(data1[d1],data2[d2])                
            if d2 == l2:
                nonIntersectionData.extend(data1[d1:])
                break                
        if iv < 0:
            # regions in data1 is before next region in data2, add it
            nonIntersectionData.append(data1[d1])
        elif iv == 0:
            # regions in data1 intersects with next region in data2, skip it
            intersectingData.append(data1[d1])
    if len(data1) != len(nonIntersectionData) +len(intersectingData):
        raise Exception, str(len(data1))+","+str(len(nonIntersectionData))+","+str(len(intersectingData))+","
    if keepOrRemove == "remove":
        return nonIntersectionData
    elif keepOrRemove == "keep":
        return intersectingData
    else:
        raise Exception
    
#===============================================================================
# @summary addIDs: Method adding an ID column to an existing dataset
# @param name: Name of the dataset 
#===============================================================================  
def addIDs(name):
    ds = readDataset(defaultFolder+name+".txt")
#    id = 1
#    for d in ds:
#        d.insert(0,id)
#        id += 1
    saveDataset(ds, name, True)
    del ds
#===============================================================================
# @summary convertChromToSortableNumber: Utility method used for sorting of geneomic regions
# @param chromStr: A string chromsome name 
#===============================================================================        
def convertChromToSortableNumber(chromStr):
    result = chromStr[3:]
    try:
        result = int(result)
    except:
        if len(result) > 1:
            #print chromStr
            raise Exception, "Invalid chromosome"+chromStr
        else:
            pass        
    return result    
#===============================================================================
# @summary readDataset: Reads a dataset from a file
# @param datasetFileName: filename
# @param useStrand: Whether it should keep the column after the chrom, chromstart and chromend as a strand column 
#===============================================================================    
def readDataset(datasetFileName,useStrand = False):            
    f = open(datasetFileName)
    ds = readDatasetFromFileObject(f,genome,useStrand) 
    f.close()
    return ds
#===============================================================================
# @summary readDatasetFromFileObject: Reads a dataset from a file object
# @param datasetFileName: filename
# @param useStrand: Whether it should keep the column after the chrom, chromstart and chromend as a strand column 
#===============================================================================  
def readDatasetFromFileObjectIntoArray(f):
    lines = f.readlines()    
    index = 0    
    ds = numpy.zeros((len(lines),3),dtype=int)
    for i in xrange(len(lines)):
        try:
            d = lines[i].strip().split("\t")[:3]            
            d[1] = int(d[1])
            d[2] = int(d[2])
            #filter the chrom column
            if "random" in d[0+suffix] or d[1+suffix] < 0 or d[2+suffix] < 0:
                raise Exception
            #convert the chrom to a number or "X" and "Y" so that the sorting gives the correct order
            d[0] = convertChromToSortableNumber(d[0+suffix])            
            ds[index] = d
            index += 1
        except:
            pass
    
    ds = quicksort(ds)
    ds = ds[ds.argsort(axis=0)[:,0]]
    
    return ds  
def readDatasetFromFileObject(f,genome,chromIndex,chromStartIndex,chromEndIndex,otherScoreIndeces):
#    print chromIndex,chromStartIndex,chromEndIndex,otherScoreIndeces
    lines = f.readlines()    
    ds = []
    for i in xrange(len(lines)):
        try:
            d = lines[i].strip().split("\t")
            #convert the chrom to a number or "X" and "Y" so that the sorting gives the correct order
            nd = [utilities.convertChromToInt(genome,d[chromIndex]),int(d[chromStartIndex]),int(d[chromEndIndex])]
            #filter the chrom column
            if d[1] < 0 or d[2] < 0:
                raise Exception
            if otherScoreIndeces:
                nd.extend([d[e] for e in otherScoreIndeces])          
            ds.append(nd)
        except utilities.GDMException:
            if "_random" in d[chromIndex]:
                pass
            elif "chrM" in d[chromIndex]:
                pass
            elif "hap" in d[chromIndex]:
                pass
            elif d[chromIndex].startswith("chrUn"):
                pass
            elif i == 0:
                # potential title, allow it to pass
                pass
            else:
                raise

    #ds = qsort(ds)    
    ds = quicksort(ds)    
    #ds.sort()
    ds = map(lambda x:[utilities.convertIntToChrom(genome,x[0])]+x[1:],ds)
             
    return ds
#===============================================================================
# @summary saveDataset: Saves a dataset into a file
# @param dataset: dataset to be updated
# @param name: name under whichit should be saved
# @param hasID: Whether it has an ID 
#===============================================================================
#def saveDataset(dataset,name,hasID=False):
#    f = open(defaultFolder+name+".txt","w")
#    if hasID:
#        s = "ID\t"
#    else:
#        s = ""
#    s += "chrom\tchromstart\tchromend\n"+"\n".join(map(lambda x:"\t".join(map(str,x)),dataset))
#    f.write(s)
#    f.close()
    
def saveDataset(dataset,name,addID):
    if addID:
        id = 1
        for d in dataset:
            d.insert(3,id)
            id += 1
    f = open(defaultFolder+name+".txt","w")    
    if not addID:
        s = "#chrom\tchromstart\tchromend\n"
    else:
        s = "#chrom\tchromstart\tchromend\tname\n"
    maxNodes = 100000
    while len(dataset) > maxNodes:
        s += "\n".join(map(lambda x:"\t".join(map(str,x)),dataset[:maxNodes]))
        dataset[:maxNodes] = []
        f.write(s)
        s = "\n"
        
    s += "\n".join(map(lambda x:"\t".join(map(str,x)),dataset))
    f.write(s)
        
    f.close()
    del s

#================================================================================
# @summary: quicksort: implements a quicksort in place, because the standard list sorting is slow
# @param L: list of elements comparable with < and >
# @return: sorted list
#================================================================================
def _doquicksort(values, left, right):
    """Quick sort"""
    def partition(values, left, right, pivotidx):
        """In place paritioning from left to right using the element at
        pivotidx as the pivot. Returns the new pivot position."""
 
        pivot = values[pivotidx]
        # swap pivot and the last element
        values[right], values[pivotidx] = values[pivotidx], values[right]
 
        storeidx = left
        for idx in range(left, right):
            if values[idx] < pivot:
                values[idx], values[storeidx] = values[storeidx], values[idx]
                storeidx += 1
 
        # move pivot to the proper place
        values[storeidx], values[right] = values[right], values[storeidx]
        return storeidx
 
    if right > left:
        # random pivot
        pivotidx = int(random.uniform(left, right))
        pivotidx = partition(values, left, right, pivotidx)
        _doquicksort(values, left, pivotidx)
        _doquicksort(values, pivotidx + 1, right)
 
    return values
 
def quicksort(mylist):
    return _doquicksort(mylist, 0, len(mylist) - 1)

#================================================================================
# @summary: qSort: implements a quicksort, because the standard list sorting is slow
# @param L: list of elements comparable with < and >
# @return: sorted list
#================================================================================    
def qsort(L):
    if len(L) <= 1: return L
    return qsort( [ lt for lt in L[1:] if lt < L[0] ] )  +  [ L[0] ]  +  qsort( [ ge for ge in L[1:] if ge >= L[0] ] )

#================================================================================
# @summary: downsampleDataset: Downsamples a dataset to a specified maximum number of regions
# @param ds: the initial dataset
# @param data: The maximum number of cases
# @return: the downsampled dataset
#================================================================================
def downsampleDataset(ds,downsample):    
    if downsample == 0 or downsample >= len(ds):
        return ds
    downsampledIndeces = qsort(random.sample(range(len(ds)),downsample))    
    #downsampledIndeces.sort()
    newDS = []
    for index in downsampledIndeces:
        newDS.append(ds[index])
    return newDS
        
#================================================================================
# @summary: removeDuplicatesFromDS: Removes any duplicate lines
# @param data: the data
# @return: the filtered data without duplicates
#================================================================================
    
def removeDuplicatesFromDS(data):
    indecesRemoved = []
    newData = []
    newData.append(data[0])
    for i in range(1,len(data)):
        if data[i] != data[i-1]:
            newData.append(data[i])
        else:
            indecesRemoved.append(i)
    #print ",".join(map(str,indecesRemoved))
    return newData
    
#===============================================================================
# @summary deriveNewDataset: Derives new dataset from a given datase based on a number of constraints
# @param name: name for the new dataset
# @param baseAttribute: name of base dataset
# @param notOverlapWith: A list of dataset names, for each of any of the regions of the resulting dataset should not overlap with 
# @param onlyOverlapsWith: A list of dataset names, for each of any of the regions of the resulting dataset overlap with
# @param intersectionMergeRule: Whether overlapping regions should be merged into a single region. Possibilities are either "first" or "max". Max 
# @param filterLength: Filter by minimum length
# @param addID: Whether to add an ID as first column
# @param removeDuplicates: Wheather to remove duplicates or not
# @param downsample: downsample the attribute to a certain number. Default is 0(no downsampling)
#===============================================================================    
def deriveNewDataset(name,baseAttribute,notOverlapWith,onlyOverlapsWith,
                     intersectionMergeRule,filterLength,
                     addID=False,removeDuplicates=True,downsample=0):
    global regionDatasets
    print time.strftime("%d.%m %H:%M:%S"),"Processing",name
    ds = readDataset(regionDatasets[baseAttribute])
    print "Dataset read"
    if filterLength:
        print time.strftime("%d.%m %H:%M:%S"),"Dataset filter by length, starts length is ",len(ds)
        ds = filterByLength(ds,filterLength)
        print time.strftime("%d.%m %H:%M:%S"),"Dataset filter by length, new length is ",len(ds)
    if onlyOverlapsWith:    
        for otherDataset in onlyOverlapsWith:            
            nods = readDataset(regionDatasets[otherDataset])
            print time.strftime("%d.%m %H:%M:%S"),"Dataset keep only overlaps with",otherDataset,len(nods),"length is",len(ds)
            ds = divideIntersection(ds,nods,"keep")
            print time.strftime("%d.%m %H:%M:%S"),"Dataset non-overlaps with",otherDataset,"removed, new length is",len(ds)
    if notOverlapWith:
        for otherDataset in notOverlapWith:            
            nods = readDataset(regionDatasets[otherDataset])
            print time.strftime("%d.%m %H:%M:%S"),"Dataset remove overlaps with",otherDataset,len(nods),"length is",len(ds)
            ds = divideIntersection(ds,nods,"remove")
            print time.strftime("%d.%m %H:%M:%S"),"Dataset overlaps with",otherDataset,"removed, new length is",len(ds)
    if intersectionMergeRule:
        print time.strftime("%d.%m %H:%M:%S"),"Dataset merge, before:",len(ds)
        ds = mergeOverlapping(ds,intersectionMergeRule)
        print time.strftime("%d.%m %H:%M:%S"),"Dataset merge, after:",len(ds)
    if removeDuplicates:        
        print time.strftime("%d.%m %H:%M:%S"),"Dataset remove duplicates","length is",len(ds)
        ds = removeDuplicatesFromDS(ds)
        print time.strftime("%d.%m %H:%M:%S"),"Dataset remove duplicates","new length is",len(ds)
    if downsample:
        ds = downsampleDataset(ds,downsample)
        
        
#    saveDataset(ds,name)
    saveDataset(ds,name,addID) 
    regionDatasets[name] =    defaultFolder+name+".txt"
#    if addID:
#        addIDs(name)
    del ds
#===============================================================================
# @summary: Extracts Flanks for a given dataset:
# @param dataset: name of the dataset
# @param newName: the name of the new dataset
# @param useStrand: whether to use strand data. If True, it assumes the given dataset has 4 columns with the 4th one the strand data
# @param whichSide: from which side the flanks should be computed. 'start' indicates upstream, 'end' is downstream and 'whole_region' is just that
# @param leftFlank: how much to substract from the upstream side 
# @param leftFlank: how much to add to the downstream side
#===============================================================================

def extractFlanks(dataset,newName,useStrand,whichSide,leftFlank,rightFlank):
    print time.strftime("%d.%m %H:%M:%S"),"Extract flanks "+dataset+" "+whichSide+" "+str(leftFlank)+" "+str(rightFlank)
    leftFlank = str(leftFlank)
    rightFlank = str(rightFlank)
    ds = readDataset(regionDatasets[dataset],useStrand)
    flankRegions = []
    for i in range(len(ds)):
        region = ds[i]
        newRegion = [region[0]]
        chromstart = region[1]
        chromend = region[2]
        sides = []
        if (whichSide == "start" and not useStrand):
           newRegion.append(region[1]-eval(leftFlank))
           newRegion.append(region[1]+eval(rightFlank))
        elif (whichSide == "start" and useStrand and region[3]=="+"):
            newRegion.append(region[1]-eval(leftFlank))
            newRegion.append(region[1]+eval(rightFlank))
        elif (whichSide == "end" and useStrand and region[3]=="-"):            
            newRegion.append(region[1]-eval(rightFlank))
            newRegion.append(region[1]+eval(leftFlank))
        elif whichSide == "end":
           newRegion.append(region[2]-eval(leftFlank))
           newRegion.append(region[2]+eval(rightFlank))
        elif (whichSide == "end" and useStrand and region[3]=="+"):
            newRegion.append(region[2]-eval(leftFlank))
            newRegion.append(region[2]+eval(rightFlank))
        elif (whichSide == "start" and useStrand and region[3]=="-"):            
            newRegion.append(region[2]-eval(rightFlank))
            newRegion.append(region[2]+eval(leftFlank))        
        elif whichSide == "whole_region":
           newRegion.append(region[1]-eval(leftFlank))
           newRegion.append(region[2]+eval(rightFlank))
        elif (whichSide == "whole_region" and useStrand and region[3]=="+"):
            newRegion.append(region[1]-eval(leftFlank))
            newRegion.append(region[2]+eval(rightFlank))
        elif (whichSide == "whole_region" and useStrand and region[3]=="-"):            
            newRegion.append(region[1]-eval(rightFlank))
            newRegion.append(region[2]+eval(leftFlank))
        if useStrand:
            newRegion.append(region[3])
        # if the start is before 1
        if newRegion[1] < 1:
            if newRegion[2] < 1:
                # if end is before the start also skip the region
                continue
            else:
                #otherwise move it to 1
                newRegion[1] = 1                        
        flankRegions.append(newRegion)    
#    saveDataset(flankRegions,newName,False)
#    addIDs(newName)
    saveDataset(flankRegions,newName,True)

    regionDatasets[newName] = defaultFolder+newName+".txt"
    del flankRegions
#===============================================================================
# @summary: Merges two datasets:
# @param newDatasetName: name for the merged dataset
# @param dsNames: list of dataset names
#===============================================================================
def mergeDatasets(newDatasetName,dsNames):
    print time.strftime("%d.%m %H:%M:%S"),"Merging datasets "+", ".join(dsNames)
    ds1 = []
    for dsName in dsNames:
        ds2 = readDataset(regionDatasets[dsName])    
        ds1.extend(ds2)
    ds = map(lambda x:[convertChromToSortableNumber(x[0])]+x[1:],ds1)
    #ds = qsort(ds)
    #ds = quicksort(ds)
    ds.sort()
    ds = map(lambda x:["chr"+str(x[0])]+x[1:],ds)
    saveDataset(ds,newDatasetName,True)
    regionDatasets[newDatasetName] = defaultFolder+newDatasetName+".txt"
    del ds
    
regionDatasets = {}

def filterMinNNContent(ds,genome,maxNNContent):
    import readDatasetDescriptions
    import CGSAnnotationsSettings
    seqDataset = readDatasetDescriptions.readDataset(["dnasequence",settings.baseFolder+"/Datasets/Datasets_descriptions/"+genome+"_unix_dnasequence.ini","./"])
    seqDataset.init()    
    cgsAS = CGSAnnotationsSettings.CGSAnnotationsSettings("dnasequence",genome,{},{})
    cgsAS.addFeatureDataset({seqDataset.datasetSimpleName:seqDataset.getDefaultAnnotationSettings()}) 
    print seqDataset.chromFiles    
    newDS = []
    for region in ds:
        if cgsAS.featuresDatasets[seqDataset.datasetSimpleName]["currentLoadedChromosome"] != utilities.convertChromToInt(genome,region[0]):
            print "New chromosome",region[0]
            seqDataset.loadChromosome(utilities.convertChromToInt(genome,region[0]),cgsAS)
        o = cgsAS.featuresDatasets[seqDataset.datasetSimpleName]["currentLoadedChromosomeSeq"][region[1]:region[2]].count("N")/float(region[2]-region[1])
        if o <= maxNNContent:
            newDS.append(region)
    return newDS
            
    
def getTilingRegions(ds,genome,windowSize,windowStep):
    #assuming that ds does not have overlapping regions
   # ds = mergeOverlappingMax(ds)
    tilingRegions = []
    for region in ds:
        tilingRegions.extend(getTilingRegionsForRegion(region,genome,windowSize,windowStep))
    return tilingRegions

def getTilingRegionsForRegion(region,genome,windowSize,windowStep):        
    newRegions = []
    try:
        chrom = region[0]
        start = region[1]
        stop = region[2]
        chrLength = settings.genomeData[genome][chrom] 
        while stop - start > windowSize:
            if chrLength > start+windowSize:        
                newRegions.append([chrom,start,start+windowSize])
            else:
                newRegions.append([chrom,start,chrLength])
                return newRegions
            start = start + windowStep
        if chrLength > start+windowSize:
            newRegions.append([chrom,start,start+windowSize])
        else:
            newRegions.append([chrom,start,chrLength])
    except:
        print region
        raise
    return newRegions


        
        
    


    

        
    


