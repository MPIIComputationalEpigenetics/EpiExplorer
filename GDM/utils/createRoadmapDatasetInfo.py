import os.path
import ftplib
import time
import gzip
import ThreadPool
import threading

def exportIniFileForExperiment(data):
    allData,baseOutputFolder,institute, experiment, mark, tissue = data 
    tissueSafeName = "".join(map(lambda x: x.capitalize(),tissue.replace("-"," ").split(" ")))
    fileName = baseOutputFolder+"hg19_NIHRE_BI_"+mark+"_"+tissueSafeName+".ini"
    if os.path.isfile(fileName):
        print "File already exists "+fileName
        return 
    print tissueSafeName,fileName
    lines = []
    lines.append("### http://www.ncbi.nlm.nih.gov/geo/roadmap/epigenomics/")
    lines.append("datasetSimpleName = nihre_bi_" + mark + "_" + tissueSafeName)
    lines.append("datasetWordName = nihrm")
    lines.append("")
    lines.append("genome = hg19")
    lines.append("hasGenomicRegions = False")
    lines.append("#regionsFiltering = combineOverlaps")
    lines.append("")
    lines.append("hasFeatures = True")
    lines.append("features = overlapBinary, overlapRatio, distanceToNearest ,neighborhood")
    lines.append("useNeighborhood = False")
    lines.append("")
    lines.append("computeRegionSizeRelative = False")
    lines.append("histoneMark = " + mark)
    lines.append("tissue = " + tissueSafeName)
    lines.append("")
    datasetFromLine = "#datasetFrom = "
    first = True
    for case in allData[institute][experiment][tissue]:
        if not first:
            datasetFromLine += ";"
        
        datasetFromLine += "ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/" + case[0][:6] + "nnn/" + case[0]
        first = False
    
    lines.append(datasetFromLine)
    lines.append("nullFrom = ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM428nnn/GSM428288/GSM428288_UCSF-UBC.H1.Input.TOTAL-H1EScd1.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM537nnn/GSM537620/GSM537620_BI.CD19_Primary_Cells.Input.CD19_8_1_08.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM537nnn/GSM537618/GSM537618_BI.CD3_Primary_Cells.Input.CD3_39661.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM486nnn/GSM486702/GSM486702_BI.CD34_Primary_Cells.Input.CD34_39661.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM537nnn/GSM537647/GSM537647_BI.ES-I3.Input.Solexa-10219.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM433nnn/GSM433179/GSM433179_BI.H1.Input.Solexa-10531.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM537nnn/GSM537682/GSM537682_BI.H1.Input.Solexa-12532.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM537nnn/GSM537701/GSM537701_BI.iPS-20b.Input.Solexa-10232.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM537nnn/GSM537662/GSM537662_BI.Mobilized_CD34_Primary_Cells.Input.Mobilized_CD34_5_28_09.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM537nnn/GSM537659/GSM537659_BI.Pancreatic_Islets.Input.pancreatic_islets_normal_3_27_09.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM521nnn/GSM521929/GSM521929_UCSD.IMR90.Input.SK-I2.wig.gz;ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM521nnn/GSM521926/GSM521926_UCSD.IMR90.Input.LL-I1.wig.gz")
    lines.append("")
    lines.append("datasetPythonClass = ../../../GDM/DatasetClasses/NIHEpigenomeWig.py")
    lines.append("")
    lines.append("datasetOfficialName  = NIH Roadmap " + experiment + " in " + tissue + " from " + institute)
    lines.append("#dataCategories = NIH Roadmap Epigenomics/ Broad Insititute/ Histone modifications")
    datasetDescription = "datasetDescription =  " + experiment + " experiment in " + tissue + " performed by the " + institute + "("
    first = True
    for case in allData[institute][experiment][tissue]:
        if not first:
            datasetDescription += " , "
        
        datasetDescription += "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=" + case[0]
        first = False
    
    datasetDescription += " )"
    lines.append(datasetDescription)
    lines.append("datasetMoreInfo = http://www.ncbi.nlm.nih.gov/geo/roadmap/epigenomics/")
#    try:
    #print lines
    f = open(fileName, "w")
    f.write("\n".join(lines))
    f.close()
#    except:
#        os.unlink(fileName)
#        raise

def loadData():
    allData = {}
    f = open(baseFile)
    header = f.readline().strip()
    print header
    line = f.readline()
    while line:
        lineParts = map(lambda x: x.strip('"'), line.strip().split(","))
        datasetInstitute = lineParts[4]
        if not allData.has_key(datasetInstitute):
            allData[datasetInstitute] = {}
        
        datasetExperiment = lineParts[2]
        if not allData[datasetInstitute].has_key(datasetExperiment):
            allData[datasetInstitute][datasetExperiment] = {}
        
        datasetTissue = lineParts[1]
        if not allData[datasetInstitute][datasetExperiment].has_key(datasetTissue):
            allData[datasetInstitute][datasetExperiment][datasetTissue] = []
        
        allData[datasetInstitute][datasetExperiment][datasetTissue].append([lineParts[0], lineParts[6], lineParts[7]])
        #print lineParts
        line = f.readline()
    
    f.close()
    return allData
def downloadFile(url,localFile):
    import os.path
    if os.path.isfile(localFile):
        raise Exception, "Error: File already exists "+localFile
    from urllib import FancyURLopener

    # a special opener to simulate firefox queries
    class MyOpener(FancyURLopener):
        version = 'Mozilla/5.0'
    myopener = MyOpener()
    myopener.retrieve(url, localFile)
    
def downloadFileFromFTP(urlBed,localBed):
    if os.path.isfile(localBed):
        print time.strftime("%d.%m %H:%M:%S"),"File",localBed,"already exists"
        return
           
    print time.strftime("%d.%m %H:%M:%S"),"Downloading",urlBed
    #main method via urllib
    #downloadFile(urlBed,localBed)
    # Alternative version
    # wget
    wgetCommand = 'wget -nv -O "'+localBed+'" "'+urlBed+'"'
    os.system(wgetCommand)
    #print time.strftime("%d.%m %H:%M:%S"),wgetCommand
    print time.strftime("%d.%m %H:%M:%S"),"Downloaded",urlBed
def extractFileFromGzBed(localGzBed,outputFile):
    if os.path.isfile(outputFile):
        print time.strftime("%d.%m %H:%M:%S"),"File",outputFile,"already exists"
        return
    print time.strftime("%d.%m %H:%M:%S"),"Extracting",localGzBed
    f = gzip.open(localGzBed, 'rb')
    file_content = f.read()
    f.close()
    fw = open(outputFile,"w")
    fw.write(file_content)
    fw.close()
    print time.strftime("%d.%m %H:%M:%S"),"Extracted",localGzBed
    
def sortBed(bedFile,bedFileSorted):
    if os.path.isfile(bedFileSorted):
        print time.strftime("%d.%m %H:%M:%S"),"File",bedFileSorted,"already exists"
        return
    print time.strftime("%d.%m %H:%M:%S"),"Sorting",bedFile
    os.system(rsegBaseFolder+"bin/sortbed "+bedFile +" -o "+bedFileSorted)
    print time.strftime("%d.%m %H:%M:%S"),"Sorted",bedFile

def rsegBed(bedFileSorted,inputFile):    
    rsegOutput = baseOutputFolder+os.path.basename(bedFileSorted[:-7])+":"+os.path.basename(inputFile[:-7])+"-domains.bed"                
    if os.path.isfile(rsegOutput):
        print time.strftime("%d.%m %H:%M:%S"),"Rseg file ",rsegOutput,"already exists"
    else:
        command = rsegBaseFolder+"bin/rseg-diff -c "+rsegBaseFolder+"examples/human-hg19-size.bed -d "+rsegBaseFolder+"examples/deadzones-k36-hg19.bed -Hideaki -o "+baseOutputFolder+" -mode 2 "+bedFileSorted+" "+inputFile
        print command 
        os.system(command)
    enrichedOutput = rsegOutput.replace("-domains","-enriched") 
    if os.path.isfile(enrichedOutput): 
        print time.strftime("%d.%m %H:%M:%S"),"Enriched file ",enrichedOutput,"already exists"
    else:
        fr = open(rsegOutput)
        lines = filter(lambda x:x[3] != 'BACKGROUND',map(lambda x:x.strip().split("\t"),fr.readlines()))
        fr.close()
        fw = open(enrichedOutput,"w")
        fw.write("\n".join(map(lambda x:"\t".join(x),lines))+"\n    ")
        fw.close()
def initInputFiles(institute,experiment,mark,tissue):
    try:
        inputLocalFiles[institute+"_"+tissue] = []
        print "Input is ",allData[institute][experiment.replace(mark,"input")][tissue]
        for nCase in range(len(allData[institute][experiment.replace(mark,"input")][tissue])):
            case = allData[institute][experiment.replace(mark,"input")][tissue][nCase]
            baseFTP = 'ftp.ncbi.nih.gov'
            index = case[1].find(baseFTP)
            if index < 0:
                raise Exception,str(case)                    
            ftpFolder = case[1][index+len(baseFTP):]
            ftpLock.acquire()
            try:
                ftp.cwd(ftpFolder)        
                fileList = ftp.nlst()
            finally:
                ftpLock.release()
            for fNameInput in fileList:
                if fNameInput.endswith("bed.gz"):
                    localInputGZBed = baseOutputFolder+fNameInput
                    localInputBed = localInputGZBed[:-3]
                    localInputBedSorted = localInputBed+".sorted"
                    if os.path.isfile(localInputBedSorted):
                        inputLocalFiles[institute+"_"+tissue].append(localInputBedSorted)
                    else:
                        raise Exception, "Input file "+str(localInputBedSorted)+" does not exist!"
    except:
        print "No valid input for ",institute, experiment, mark, tissue
        inputLocalFiles[institute+"_"+tissue] = []    

def threadProcessRseg(data):
    allData,baseOutputFolder,institute, experiment, mark, tissue,baseFTP,index,case,fName = data         
    localGZBed = baseOutputFolder+fName
    localBed = localGZBed[:-3]
    localBedSorted = localBed+".sorted"
    if not inputLocalFiles.has_key(institute+"_"+tissue):
        initInputFiles(institute, experiment, mark, tissue)
    #inputFiles = ["/TL/epigenetics/nobackup/completesearch/NIHRoadmap/Data/GSM433179_BI.H1.Input.Solexa-10531.bed.sorted","/TL/epigenetics/nobackup/completesearch/NIHRoadmap/Data/GSM537682_BI.H1.Input.Solexa-12532.bed.sorted"] 

    for inputFile in inputLocalFiles[institute+"_"+tissue]:
        rsegBed(localBedSorted,inputFile)
        
        
        
def threadDownload(data):
    allData,baseOutputFolder,institute, experiment, mark, tissue,baseFTP,index,case,fName = data         
    localGZBed = baseOutputFolder+fName
    localBed = localGZBed[:-3]
    localBedSorted = localBed+".sorted"
                
    if os.path.isfile(localBedSorted):        
        print time.strftime("%d.%m %H:%M:%S"),"File",localBedSorted,"was already fully processed"
        return                
    #download the file
    downloadFileFromFTP("ftp://"+baseFTP+case[1][index+len(baseFTP):]+fName,localGZBed)
    #extract if from the archive                
    extractFileFromGzBed(localGZBed,localBed)
    # sort the bed file                
    sortBed(localBed,localBedSorted)
    outputLock.acquire()
    try:
        f = open(baseOutputFolder+"allsorted.ini","a")
        f.write("\t".join(map(str,[institute,mark,tissue,nCase,localBedSorted]))+"\n")
        f.close()
    finally:
        outputLock.release()   
    #cleanup
    try:
        os.unlink(localGZBed)        
        os.unlink(localBed)
    except:
        pass
                
    
    
def processAllRoadmapData(baseFile,baseOutputFolder,
                          intitutePositiveFilter,intituteNegativeFilter,
                          experimentNegativeFilter,experimentPositiveFilter,
                          tissuePositiveFilter,tissueNegativeFilter,
                          pool,methodToProcess):
    allData = loadData()

    print "Institutes",allData.keys()
    for institute in allData.keys():
        if intitutePositiveFilter and not intitutePositiveFilter in institute:
            continue 
        if intituteNegativeFilter and intituteNegativeFilter in institute:
            continue
        print "Experiments from ",institute,allData[institute].keys()
        for experiment in allData[institute].keys():
            if experimentPositiveFilter and not experimentPositiveFilter in experiment:
                continue 
            if experimentNegativeFilter and experimentNegativeFilter in experiment:
                continue        
            mark = experiment[10:]     
            print experiment,mark,allData[institute][experiment].keys()    
            
            for tissue in allData[institute][experiment].keys():
                if tissuePositiveFilter and not tissuePositiveFilter in tissue:
                    continue 
                if tissueNegativeFilter and tissueNegativeFilter in tissue:
                    continue
                print "TO PROCESS:",institute, experiment, mark, tissue
                for nCase in range(len(allData[institute][experiment][tissue])):
                    case = allData[institute][experiment][tissue][nCase]
                    baseFTP = 'ftp.ncbi.nih.gov'
                    index = case[1].find(baseFTP)
                    if index < 0:
                        raise Exception,str(case)
                    
                    ftpFolder = case[1][index+len(baseFTP):]
                    ftpLock.acquire()
                    try:
                        ftp.cwd(ftpFolder)        
                        fileList = ftp.nlst()
                    finally:
                        ftpLock.release()
                    for fName in fileList:
                        if fName.endswith("bed.gz"):
                            #localGZBed = baseOutputFolder+".".join(map(str,[institute,mark,tissue,nCase]))+".bed.gz"                            
                            pool.queueTask(methodToProcess, 
                                           (allData,baseOutputFolder,institute, experiment, mark, tissue,baseFTP,index,case,fName), 
                                           None)                                

rsegBaseFolder = "/TL/epigenetics/work/completesearch/dev_codebase/rseg/rseg/"
#baseFile = "D:/Projects/Integrated_Genome_Profile_Search_Engine/Datasets/Roadmap/11.02.16 samples.csv"
#baseOutputFolder = "D:/Projects/Integrated_Genome_Profile_Search_Engine/Cosgen/Datasets/Datasets_descriptions/NIHRoadmapEpigenomics/"
baseFile = "/TL/epigenetics/nobackup/completesearch/NIHRoadmap/11.03.16 samples.csv"
baseOutputFolder = "/TL/epigenetics/nobackup/completesearch/NIHRoadmap/Data/"

intitutePositiveFilter = "Broad"
intituteNegativeFilter = ""
experimentNegativeFilter = "input"
#experimentNegativeFilter = ""
experimentPositiveFilter = "ChIP-Seq:"
tissuePositiveFilter = "H1"
#tissuePositiveFilter = ""
tissueNegativeFilter = ""

inputLocalFiles = {}
ftp = ftplib.FTP('ftp.ncbi.nih.gov')        
ftp.login()
ftpLock = threading.Lock()
downloadPool = ThreadPool.ThreadPool(4)
outputLock = threading.Lock()
try:
    processAllRoadmapData(baseFile,baseOutputFolder,
                      intitutePositiveFilter,intituteNegativeFilter,
                      experimentNegativeFilter,experimentPositiveFilter,
                      tissuePositiveFilter,tissueNegativeFilter,
                      downloadPool,threadDownload)
finally:
    downloadPool.joinAll()

executePool = ThreadPool.ThreadPool(10)
try:
    processAllRoadmapData(baseFile,baseOutputFolder,
                      intitutePositiveFilter,intituteNegativeFilter,
                      experimentNegativeFilter,experimentPositiveFilter,
                      tissuePositiveFilter,tissueNegativeFilter,
                      executePool,threadProcessRseg)
finally:
    executePool.joinAll()    
    

           
            


        
     