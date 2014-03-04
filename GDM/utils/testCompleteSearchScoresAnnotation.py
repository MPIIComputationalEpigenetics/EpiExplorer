# This test is going to generate a complete search file and test which one is more efficient. 
# to have many words with similar prefixes or to have less words and search for ranges and completions

# the test is oging to be the anount of time it takes for the CS to answer all queries
import random
import os 
import sys
import subprocess 
import time
#time.sleep(5)
import urllib2
import numpy


if sys.platform  == "win32":
    baseFolder = "D:/Projects/Integrated_Genome_Profile_Search_Engine/Documentation/CompleteSearch/SearchEngine and preprocessing/Tests/"
else:
    baseFolder = "/TL/epigenetics/work/completesearch/databases/wordtest/"
    
def runQueryTests(baseName,nd,wd):
#    retcode = subprocess.call(["cd", baseFolder],shell=True)
#    os.chdir(baseFolder)
#    retcode = subprocess.call(["export", "DB="+baseName])    
#    baseQ = "http://infao3806:8989/?q=&h=10&c=3"
#    baseQ = "http://infao3806:8989/?q=&h=0&c=1000"
#    baseQ = "http://infao3806:8989/?q=&h=100&c=0"
    baseQ = "http://infao3806:8989/?q=&h=100&c=1000"
    for queryType in ["wordbase","wordfull","range"]:
#        L = ["make","--directory="+baseFolder,"-e","start"]
#        p = os.fork()
#        if p != 0:
#            os.environ.update({"DB":baseName})
#            pid = os.spawnvpe(os.P_NOWAIT, 'make', L,os.environ)
#            time.sleep(100)
#            os.system("kill -9 "+str(pid))
#        else:   
            #pid = subprocess.Popen(["make","--directory="+baseFolder,"-e","start","&"],env={"DB":baseName}).pid # Success!
        #print "Server is started",pid 
        #time.sleep(5)        
        querySourceFile = getQueryFileBaseName(nd,wd)+"."+queryType
        f = open(querySourceFile)
        query = f.readline().strip()
        times = []
        while query:
            exactQuery = baseQ.replace("q=&","q="+query+"*&")
            
            responseSocket = urllib2.urlopen(exactQuery)                                
            response = responseSocket.read()
            #print response
            fi = response.find("time")
            fi = response.find(">",fi)
            fs = response.find("<",fi)
            time = float(response[fi+1:fs])
            times.append(time) 
            query = f.readline().strip()
            print "AAAAAAA",response,time,exactQuery
            #raise Exception
        f.close()
        nt = numpy.array(times)
        queryResultFile = querySourceFile+".result"
        f = open(queryResultFile,"a")
        f.write(baseName+"\n")
        f.write("All = "+str(",".join(map(str,nt)))+"\n")
        f.write("mean = "+str(nt.mean())+"\n")
        f.write("std = "+str(nt.std())+"\n\n")
        f.write("max = "+str(max(nt))+"\n\n")
        f.close()
        #os.system("kill -9 "+str(pid))
        #time.sleep(5)
        
    

    
def generateIndexFiles(baseName):
    retcode = subprocess.call(["cd", baseFolder],shell=True)
#    os.chdir(baseFolder)
#    retcode = subprocess.call(["export", "DB="+baseName],shell=True)
    p = subprocess.call(["make","--directory="+baseFolder,"-e","-B","all"],env={"DB":baseName})    
        
    
    
def generateAllCSFiles():

    
    for nd in number_of_documents:
        for wd in wordsPerDocument:
            basewords = []
            for i in range(wd):        
                basewords.append(getRandomWord())
            mr = max(wordsCompletions)
            completions = []
            for j in range(mr):
                completions.append(getRandomExtension(mr))
            selections = []
            for wc in wordsCompletions:
                selections += random.sample(completions,wc-len(selections))  
                print nd,wd,wc      
                di = generateCSFiles(nd,basewords,selections)                
                if wc == min(wordsCompletions):
                    generateQueryFile(nd,basewords,selections,completions)
                #create the database files
                generateIndexFiles(di)   
#                runQueryTests(di,nd,wd)
#                raise Exception
                
def getQueryFileBaseName(nd,wd):
    return baseFolder+"nd"+str(nd)+"_bw"+str(wd)

def generateQueryFile(nd,basewords,selections,completions):
    wd = len(basewords)
    queryCount = 100
    f = open(getQueryFileBaseName(nd,wd)+".wordbase","w")
    q = ""
    for i in range(queryCount):
        q += random.choice(basewords)+"\n"
    f.write(q)
    f.close()
        
    f = open(getQueryFileBaseName(nd,wd)+".wordfull","w")
    q = ""
    for i in range(queryCount):        
        q += random.choice(basewords)+random.choice(selections)+"\n"
    f.write(q)
    f.close()
        
    f = open(getQueryFileBaseName(nd,wd)+".range","w")
    q = ""
    for i in range(queryCount):
        bw = random.choice(basewords)
        c1 = random.choice(completions)
        c2 = random.choice(completions)
        if int(c1) < int(c2):
            q += bw+c1+"--"+bw+c2+"\n"
        else:
            q += bw+c2+"--"+bw+c1+"\n"
    f.write(q)
    f.close()
    
def getRandomWord():
    alphabet = "qwertyuioplkjhgfdsazxcvbnm"
    la = len(alphabet)
    baseword = ""
    basewordLength = 4
    for j in range(basewordLength):
        baseword += alphabet[random.randint(0,la-1)]
    return baseword

def getRandomExtension(wordsCompletions):    
    r = int(random.gauss(wordsCompletions+wordsCompletions/2,wordsCompletions/6))
    return str(int(r))  
def getBaseName(nd,wd,wc):
    sep = "_"
    return "wordTest" +sep+"nd"+str(nd)+sep+"wd"+str(wd)+sep+"wc"+str(wc)                
def generateCSFiles(numberOfDocuments,basewords,selections):    
    
    #print basewords
    #raise Exception
    
    di = getBaseName(numberOfDocuments,len(basewords),len(selections))
    
    
    s = ""
    
    for i in range(1,numberOfDocuments+1):
        s += str(i)+"\t"+"u:\t"+"t:d"+str(i)+"\tH:\n"
    fd = open(baseFolder+di+".docs","w")
    fd.write(s)
    fd.close()
    # make all words stuff
    fw = open(baseFolder+di+".words-unsorted.ascii","w")
    s = ""
    for i in range(1,numberOfDocuments+1):
        for bw in basewords:
            w = bw + random.choice(selections)
            s += w + "\t"+str(i)+"\t0\t0\n"
            if len(s) > 1000000:
                fw.write(s)
                s = ""
    fw.write(s)
    fw.close()
#    raise Exception
    return di

# generate files
number_of_documents = [ 
                       10000000
                      ]
wordsPerDocument = [
#                    10, 
                    100
                   ]
wordsCompletions = [
                    10, 
#                    100, 
                    1000
                   ]            
#generateAllCSFiles()
#raise Exception
#run tests
print sys.argv

nd = int(sys.argv[1])
wd = int(sys.argv[2])
wc = int(sys.argv[3])
di = getBaseName(nd,wd,wc)
print di
runQueryTests(di,nd,wd)
