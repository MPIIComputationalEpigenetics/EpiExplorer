# the purpose of this file is to sumulate queries 
# such as those for the infinium datasets
# the complete search is going to have 3 types of documents:
## - The location documents containing location information with additional annotations 
## - The sample information, containing information about the sameble, tissue and other clinical info
## - score docuement containign a location and sample Id and a score
import random 
import subprocess

def createTestMultipleCpGScoreSingle():
    f = open(docsFile,"w")
    f.close()
    f = open(wordsFile,"w")
    f.close()
    did = 1
    scores = {}
    #makign the words slection for the locations
    for lid in range(1, locNumber + 1): 
        scores[lid] = {}  
        if len(wordList) > 1000:
            appendWordsFile()
        
        if len(docList) > 1000:
            appendDocsFile()     
        lids = str(lid)
        dids = str(did)        
        wordList.append("locID:%s\t%s\t%i\t0" % (lids, dids,random.randint(0, 100)))
        #wordsStr +="locTestF:"+str(random.randint(0,1))+"\t"+dids+"\t0\t0\n"
        wordList.append("locTestF1:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF2:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF3:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        for sampleid in range(1, sampleNumber + 1):
            sids = str(sampleid)
            scores[lid][sampleid] = int(100 * random.random())
            wordList.append("L%s:S%s:score:%i\t%s\t0\t0" % (lids,sids,scores[lid][sampleid], dids))
        
        docList.append("\t".join([dids, "u:", "t:", "H:"]))
        did += 1
        #makign the words slection for the samples
    
    for sampleid in range(1, sampleNumber + 1):
        sids = str(sampleid)
        dids = str(did)
        if len(wordList) > 1000:
            appendWordsFile()
        
        if len(docList) > 1000:
            appendDocsFile()
        
        wordList.append("sampleID:%s\t%s\t0\t0" % (sids, dids))
        if sampleid % 10 == 0:
            print sids, "out of", sampleNumber
        for sn in range(1,11):
            wordList.append("sampleTestF%i:%i\t%s\t0\t0" % (sn,random.randint(0, 1), dids))
        for lid in range(1, locNumber + 1):
            lids = str(lid)
            wordList.append("L%s:S%s:score:%i\t%s\t0\t0" % (lids,sids,scores[lid][sampleid], dids))
        docList.append("\t".join([dids, "u:", "t:", "H:"]))
        did += 1   
    
    appendDocsFile()
    appendWordsFile()
    
    retcode = subprocess.call(["cd", baseFolder],shell=True)
    p = subprocess.call(["make","--directory="+baseFolder,"-e","-B","all"],env={"DB":baseName})
    # 0. few samples and loci raw
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 L*#locTestF1:1 locTestF2:1 L*\]&c=10&h=0"
    # 1. few loci 
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 L*&c=10&h=0"
    # 2. few samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 L*&c=10&h=0"
    # 3. few samples and loci after 1 and 2
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 L*#locTestF1:1 locTestF2:1 L*\]&c=10&h=0"
    # 4. increment loci
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locTestF3:1 L*&c=10&h=0"
    # 5. increment samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 L*&c=10&h=0"
    # 6. few samples and loci after 1 and 2 3,4,5
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 L*#locTestF1:1 locTestF2:1 locTestF3:1 L*\]&c=10&h=0"
    
def createTestMultipleCpGScoreSingleWithScores():
    f = open(docsFile,"w")
    f.close()
    f = open(wordsFile,"w")
    f.close()
    did = 1    
    #makign the words slection for the locations
    for lid in range(1, locNumber + 1):
        if len(wordList) > 1000:
            appendWordsFile()
        
        if len(docList) > 1000:
            appendDocsFile()     
        lids = str(lid)
        dids = str(did)        
        wordList.append("locID:%s\t%s\t0\t0" % (lids, dids))
        #wordsStr +="locTestF:"+str(random.randint(0,1))+"\t"+dids+"\t0\t0\n"
        wordList.append("locTestF1:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF2:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF3:%i\t%s\t0\t0" % (random.randint(0, 1), dids))        
        
        docList.append("\t".join([dids, "u:", "t:", "H:"]))
        did += 1
        #makign the words slection for the samples
    
    for sampleid in range(1, sampleNumber + 1):
        sids = str(sampleid)
        dids = str(did)
        if len(wordList) > 1000:
            appendWordsFile()
        
        if len(docList) > 1000:
            appendDocsFile()
        
        wordList.append("sampleID:%s\t%s\t0\t0" % (sids, dids))
        if sampleid % 10 == 0:
            print sids, "out of", sampleNumber
        for sn in range(1,11):
            wordList.append("sampleTestF%i:%i\t%s\t0\t0" % (sn,random.randint(0, 1), dids))
        for lid in range(1, locNumber + 1):
            lids = str(lid)
            wordList.append("locID:%s\t%s\t%i\t0" % (lids,dids,random.randint(0, 100)))
        docList.append("\t".join([dids, "u:", "t:", "H:"]))
        did += 1   
    
    appendDocsFile()
    appendWordsFile()
    
    retcode = subprocess.call(["cd", baseFolder],shell=True)
    p = subprocess.call(["make","--directory="+baseFolder,"-e","-B","all"],env={"DB":baseName})
    # 0. few samples and loci raw
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 locID:*#locTestF1:1 locTestF2:1 locID:*\]&c=10&h=0"
    # 1. few loci 
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locID:*&c=10&h=0"
    # 2. few samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 sampleID:*&c=10&h=0"
    # 3. few samples and loci after 1 and 2
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 locID:*#locTestF1:1 locTestF2:1 locID:*\]&c=10&h=0"
    # 4. increment loci
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locTestF3:1 locID*&c=10&h=0"
    # 5. increment samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 locID*&c=10&h=0"
    # 6. few samples and loci after 1 and 2 3,4,5
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 locID:*#locTestF1:1 locTestF2:1 locTestF3:1 locID:*\]&c=10&h=0"

def createTestMultipleCpGScoreDouble():
    f = open(docsFile,"w")
    f.close()
    f = open(wordsFile,"w")
    f.close()
    did = 1
    #makign the words slection for the locations
    for lid in range(1, locNumber + 1):
        lids = str(lid)
        dids = str(did)
        #allwords[did]  = makeLocationDocument(lid)
        #appendDoc(did,"","lid:"+str(lid),"")
        #wordsStr +="loc\t"+dids+"\t0\t0\n"
        #wordList.append("loc\t%s\t0\t0" % (dids,))
        #wordsStr +="locID:"+lids+"\t"+dids+"\t0\t0\n"
        wordList.append("locID:%s\t%s\t0\t0" % (lids, dids))
        #wordsStr +="locTestF:"+str(random.randint(0,1))+"\t"+dids+"\t0\t0\n"
        wordList.append("locTestF1:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF2:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF3:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        #docStr += dids+"\tu:\tt:lid:"+lids+"\tH:\n"
        docList.append("\t".join([dids, "u:", "t:", "H:"]))
        did += 1
        #makign the words slection for the samples
    
    for sampleid in range(1, sampleNumber + 1):
        sids = str(sampleid)
        if len(wordList) > 1000:
            appendWordsFile()
        
        if len(docList) > 1000:
            appendDocsFile()
        
        if sampleid % 10 == 0:
            print sids, "out of", sampleNumber        
        
        for lid in range(1, locNumber + 1):
            lids = str(lid)
            dids = str(did)
            for sn in range(1,11):
                wordList.append("sampleTestF%i:%i\t%s\t0\t0" % (sn,random.randint(0, 1), dids))            
            #wordsStr +="locID:"+lids+"\t"+dids+"\t0\t0\n"
            wordList.append("locID:%s\t%s\t0\t0" % (lids, dids))
            #wordsStr +="score:"+str(int(100*random.random()))+"\t"+dids+"\t0\t0\n"
            wordList.append("score:%i\t%s\t0\t0" % (int(10 * random.random()), dids))
            #docStr += dids+"\tu:\tt:samplelocid:"+str(sampleid)+":"+str(lid)+"\tH:\n"
            docList.append("\t".join([dids, "u:", "t:", "H:"]))
            did += 1
        
    
    appendDocsFile()
    appendWordsFile()
    
    retcode = subprocess.call(["cd", baseFolder],shell=True)
    p = subprocess.call(["make","--directory="+baseFolder,"-e","-B","all"],env={"DB":baseName})
    # 0. few samples and loci raw
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 locID:*#locTestF1:1 locTestF2:1 locID:*\] score:*&c=10&h=0"
    # 1. few loci 
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locID:*&c=10&h=0"
    # 2. few samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 locID:*&c=10&h=0"
    # 3. few samples and loci after 1 and 2
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 locID:*#locTestF1:1 locTestF2:1 locID:*\] score:*&c=10&h=0"
    # 4. increment loci
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locTestF3:1 locID:*&c=10&h=0"
    # 5. increment samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 locID:*&c=10&h=0"
    # 6. few samples and loci after 1 and 2 3,4,5
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 locID:*#locTestF1:1 locTestF2:1 locTestF3:1 locID:*\] score:*&c=10&h=0"
    
def createTestMultipleCpGScoreDoubleWithScores():
    f = open(docsFile,"w")
    f.close()
    f = open(wordsFile,"w")
    f.close()
    did = 1
    #makign the words slection for the locations
    for lid in range(1, locNumber + 1):
        lids = str(lid)
        dids = str(did)
        #allwords[did]  = makeLocationDocument(lid)
        #appendDoc(did,"","lid:"+str(lid),"")
        #wordsStr +="loc\t"+dids+"\t0\t0\n"
        #wordList.append("loc\t%s\t0\t0" % (dids,))
        #wordsStr +="locID:"+lids+"\t"+dids+"\t0\t0\n"
        wordList.append("locID:%s\t%s\t0\t0" % (lids, dids))
        #wordsStr +="locTestF:"+str(random.randint(0,1))+"\t"+dids+"\t0\t0\n"
        wordList.append("locTestF1:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF2:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF3:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        #docStr += dids+"\tu:\tt:lid:"+lids+"\tH:\n"
        docList.append("\t".join([dids, "u:", "t:", "H:"]))
        did += 1
        #makign the words slection for the samples
    
    for sampleid in range(1, sampleNumber + 1):
        sids = str(sampleid)
        if len(wordList) > 1000:
            appendWordsFile()
        
        if len(docList) > 1000:
            appendDocsFile()
        
        if sampleid % 10 == 0:
            print sids, "out of", sampleNumber        
        
        for lid in range(1, locNumber + 1):
            lids = str(lid)
            dids = str(did)
            for sn in range(1,11):
                wordList.append("sampleTestF%i:%i\t%s\t0\t0" % (sn,random.randint(0, 1), dids))            
            #wordsStr +="locID:"+lids+"\t"+dids+"\t0\t0\n"
            wordList.append("locID:%s\t%s\t%i\t0" % (lids, dids,int(100 * random.random())))
            #wordsStr +="score:"+str(int(100*random.random()))+"\t"+dids+"\t0\t0\n"
            #wordList.append("score:%i\t%s\t0\t0" % (int(100 * random.random()), dids))
            #docStr += dids+"\tu:\tt:samplelocid:"+str(sampleid)+":"+str(lid)+"\tH:\n"
            docList.append("\t".join([dids, "u:", "t:", "H:"]))
            did += 1
        
    
    appendDocsFile()
    appendWordsFile()
    
    retcode = subprocess.call(["cd", baseFolder],shell=True)
    p = subprocess.call(["make","--directory="+baseFolder,"-e","-B","all"],env={"DB":baseName})
    # 0. few samples and loci raw
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 locID:*#locTestF1:1 locTestF2:1 locID:*\]&c=10&h=0"
    # 1. few loci 
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locID:*&c=10&h=0"
    # 2. few samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 locID:*&c=10&h=0"
    # 3. few samples and loci after 1 and 2
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 locID:*#locTestF1:1 locTestF2:1 locID:*\]&c=10&h=0"
    # 4. increment loci
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locTestF3:1 locID:*&c=10&h=0"
    # 5. increment samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 locID:*&c=10&h=0"
    # 6. few samples and loci after 1 and 2 3,4,5
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 locID:*#locTestF1:1 locTestF2:1 locTestF3:1 locID:*\] score:*&c=10&h=0"

def createTestMultipleCpGScoreTriple():
    f = open(docsFile,"w")
    f.close()
    f = open(wordsFile,"w")
    f.close()
    
    did = 1
    #makign the words slection for the locations
    for lid in range(1, locNumber + 1):
        lids = str(lid)
        dids = str(did)
        #allwords[did]  = makeLocationDocument(lid)
        #appendDoc(did,"","lid:"+str(lid),"")
        #wordsStr +="loc\t"+dids+"\t0\t0\n"
        #wordList.append("loc\t%s\t0\t0" % (dids,))
        #wordsStr +="locID:"+lids+"\t"+dids+"\t0\t0\n"
        wordList.append("locID:%s\t%s\t0\t0" % (lids, dids))
        #wordsStr +="locTestF:"+str(random.randint(0,1))+"\t"+dids+"\t0\t0\n"
        wordList.append("locTestF1:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF2:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF3:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        #docStr += dids+"\tu:\tt:lid:"+lids+"\tH:\n"
        docList.append("\t".join([dids, "u:", "t:", "H:"]))
        did += 1
        #makign the words slection for the samples
    
    for sampleid in range(1, sampleNumber + 1):
        sids = str(sampleid)
        dids = str(did)
        #allwords[did] = makeSampleDocument(sampleid)
        #appendDoc(did,"","sampleid:"+str(sampleid),"")
        #wordsStr += "sample\t"+dids+"\t0\t0\n"
        #wordList.append("sample\t%s\t0\t0" % (dids,))
        #wordsStr += "sampleID:"+str(sids)+"\t"+dids+"\t0\t0\n"
        wordList.append("sampleID:%s\t%s\t0\t0" % (sids, dids))
        #wordsStr += "sampleTestF1:"+str(random.randint(0,1))+"\t"+dids+"\t0\t0\n"
        #wordsStr += "sampleTestF2:"+str(random.randint(0,1))+"\t"+dids+"\t0\t0\n"
        for sn in range(1,11):
            wordList.append("sampleTestF%i:%i\t%s\t0\t0" % (sn,random.randint(0, 1), dids))    
        #docStr += dids+"\tu:\tt:sampleid:"+str(sampleid)+"\tH:\n"
        docList.append("\t".join([dids, "u:", "t:", "H:"]))
        did += 1
        #makign the words slection for the samples
    
    for sampleid in range(1, sampleNumber + 1):
        sids = str(sampleid)
        if len(wordList) > 1000:
            appendWordsFile()
        
        if len(docList) > 1000:
            appendDocsFile()
        
        if sampleid % 10 == 0:
            print sids, "out of", sampleNumber
        
        for lid in range(1, locNumber + 1):
            lids = str(lid)
            dids = str(did)
            #allwords[did] =  makeSampleLocDocument(lid,sampleid)
            #appendDoc(did,"","samplelocid:"+str(sampleid)+":"+str(lid),"")
            #wordsStr += "sampleloc\t"+dids+"\t0\t0\n"
            #wordList.append("sampleloc\t%s\t0\t0" % (dids,))
            #wordsStr += "sampleID:"+str(sids)+"\t"+dids+"\t0\t0\n"
            wordList.append("sampleID:%s\t%s\t0\t0" % (sids, dids))
            #wordsStr +="locID:"+lids+"\t"+dids+"\t0\t0\n"
            wordList.append("locID:%s\t%s\t0\t0" % (lids, dids))
            #wordsStr +="score:"+str(int(100*random.random()))+"\t"+dids+"\t0\t0\n"
            wordList.append("score:%i\t%s\t0\t0" % (int(10 * random.random()), dids))
            #docStr += dids+"\tu:\tt:samplelocid:"+str(sampleid)+":"+str(lid)+"\tH:\n"
            docList.append("\t".join([dids, "u:", "t:", "H:"]))
            did += 1
        
    
    appendDocsFile()
    appendWordsFile()
    
    retcode = subprocess.call(["cd", baseFolder],shell=True)
    p = subprocess.call(["make","--directory="+baseFolder,"-e","-B","all"],env={"DB":baseName})    
    # 0. few samples and loci raw
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 sampleID:*#sampleID:*\] \[locID:*#locTestF1:1 locTestF2:1 locID:*\] score:*&c=10&h=0"
    # 1. few loci 
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locID:*&c=10&h=0"
    # 2. few samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 sampleID:*&c=10&h=0"
    # 3. few samples and loci after 1 and 2
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 sampleID:*#sampleID:*\] \[locID:*#locTestF1:1 locTestF2:1 locID:*\] score:*&c=10&h=0"
    # 4. increment loci
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locTestF3:1 locID:*&c=10&h=0"
    # 5. increment samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 sampleID:*&c=10&h=0"
    # 6. few samples and loci after 1 and 2 3,4,5
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 sampleID:*#sampleID:*\] \[locID:*#locTestF1:1 locTestF2:1 locTestF3:1 locID:*\] score:*&c=10&h=0"

def createTestMultipleCpGScoreTripleWithScores():
    f = open(docsFile,"w")
    f.close()
    f = open(wordsFile,"w")
    f.close()
    
    did = 1
    #makign the words slection for the locations
    for lid in range(1, locNumber + 1):
        lids = str(lid)
        dids = str(did)
        #allwords[did]  = makeLocationDocument(lid)
        #appendDoc(did,"","lid:"+str(lid),"")
        #wordsStr +="loc\t"+dids+"\t0\t0\n"
        #wordList.append("loc\t%s\t0\t0" % (dids,))
        #wordsStr +="locID:"+lids+"\t"+dids+"\t0\t0\n"
        wordList.append("locID:%s\t%s\t0\t0" % (lids, dids))
        #wordsStr +="locTestF:"+str(random.randint(0,1))+"\t"+dids+"\t0\t0\n"
        wordList.append("locTestF1:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF2:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        wordList.append("locTestF3:%i\t%s\t0\t0" % (random.randint(0, 1), dids))
        #docStr += dids+"\tu:\tt:lid:"+lids+"\tH:\n"
        docList.append("\t".join([dids, "u:", "t:", "H:"]))
        did += 1
        #makign the words slection for the samples
    
    for sampleid in range(1, sampleNumber + 1):
        sids = str(sampleid)
        dids = str(did)
        #allwords[did] = makeSampleDocument(sampleid)
        #appendDoc(did,"","sampleid:"+str(sampleid),"")
        #wordsStr += "sample\t"+dids+"\t0\t0\n"
        #wordList.append("sample\t%s\t0\t0" % (dids,))
        #wordsStr += "sampleID:"+str(sids)+"\t"+dids+"\t0\t0\n"
        wordList.append("sampleID:%s\t%s\t0\t0" % (sids, dids))
        #wordsStr += "sampleTestF1:"+str(random.randint(0,1))+"\t"+dids+"\t0\t0\n"
        #wordsStr += "sampleTestF2:"+str(random.randint(0,1))+"\t"+dids+"\t0\t0\n"
        for sn in range(1,11):
            wordList.append("sampleTestF%i:%i\t%s\t0\t0" % (sn,random.randint(0, 1), dids))    
        #docStr += dids+"\tu:\tt:sampleid:"+str(sampleid)+"\tH:\n"
        docList.append("\t".join([dids, "u:", "t:", "H:"]))
        did += 1
        #makign the words slection for the samples
    
    for sampleid in range(1, sampleNumber + 1):
        sids = str(sampleid)
        if len(wordList) > 1000:
            appendWordsFile()
        
        if len(docList) > 1000:
            appendDocsFile()
        
        if sampleid % 10 == 0:
            print sids, "out of", sampleNumber
        
        for lid in range(1, locNumber + 1):
            lids = str(lid)
            dids = str(did)
            #allwords[did] =  makeSampleLocDocument(lid,sampleid)
            #appendDoc(did,"","samplelocid:"+str(sampleid)+":"+str(lid),"")
            #wordsStr += "sampleloc\t"+dids+"\t0\t0\n"
            #wordList.append("sampleloc\t%s\t0\t0" % (dids,))
            #wordsStr += "sampleID:"+str(sids)+"\t"+dids+"\t0\t0\n"
            wordList.append("sampleID:%s\t%s\t0\t0" % (sids, dids))
            #wordsStr +="locID:"+lids+"\t"+dids+"\t0\t0\n"
            wordList.append("locID:%s\t%s\t%i\t0" % (lids, dids,int(100 * random.random())))
            #wordsStr +="score:"+str(int(100*random.random()))+"\t"+dids+"\t0\t0\n"
            #wordList.append("score:%i\t%s\t0\t0" % (, dids))
            #docStr += dids+"\tu:\tt:samplelocid:"+str(sampleid)+":"+str(lid)+"\tH:\n"
            docList.append("\t".join([dids, "u:", "t:", "H:"]))
            did += 1
        
    
    appendDocsFile()
    appendWordsFile()
    
    retcode = subprocess.call(["cd", baseFolder],shell=True)
    p = subprocess.call(["make","--directory="+baseFolder,"-e","-B","all"],env={"DB":baseName})    
    # 0. few samples and loci raw
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 sampleID:*#sampleID:*\] \[locID:*#locTestF1:1 locTestF2:1 locID:*\]&c=10&h=0"
    # 1. few loci 
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locID:*&c=10&h=0"
    # 2. few samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 sampleID:*&c=10&h=0"
    # 3. few samples and loci after 1 and 2
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 sampleID:*#sampleID:*\] \[locID:*#locTestF1:1 locTestF2:1 locID:*\]&c=10&h=0"
    # 4. increment loci
    # curl "http://infao3806:8912/?q=locTestF1:1 locTestF2:1 locTestF3:1 locID:*&c=10&h=0"
    # 5. increment samples
    # curl "http://infao3806:8912/?q=sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 sampleID:*&c=10&h=0"
    # 6. few samples and loci after 1 and 2 3,4,5
    # curl "http://infao3806:8912/?q=\[sampleTestF1:1 sampleTestF2:1 sampleTestF3:1 sampleID:*#sampleID:*\] \[locID:*#locTestF1:1 locTestF2:1 locTestF3:1 locID:*\] score:*&c=10&h=0"

def makeLocationDocument(locID):
    words = []
    words.append("loc")
    words.append("locID:"+str(locID))
    words.append("locTestF:"+str(random.randint(0,1)))
    return words

def makeSampleDocument(sampleID):
    words = []
    words.append("sample")
    words.append("sampleID:"+str(sampleID))
    words.append("sampleTestF1:"+str(random.randint(0,1)))
    words.append("sampleTestF2:"+str(random.randint(0,1)))
    return words

def makeSampleLocDocument(locID,sampleID):
    words = []
    words.append("sampleloc")
    words.append("sampleID:"+str(sampleID))
    words.append("locID:"+str(locID))    
    words.append("score:"+str(round(random.random(),2)))
    return words
    
def appendDoc(id,u,t,h):
    global docStr
    sep="\t"    
    docStr += str(id)+sep+"u:"+u+sep+"t:"+t+sep+"H:"+h+"\n"

def writeDocsFile():    
    f = open(docsFile,"w")
    f.write(docStr)
    f.close()
    
def appendDocsFile():
    global docStr,docList
    if not len(docList):
        return
    f = open(docsFile,"a")
    f.write("\n".join(docList)+"\n")
    docList = []
    #f.write(docStr)
    #docStr = ""
    f.close()
    
def appendWordsFile():
    global wordsStr,wordList
    if not len(wordList):
        return
    f = open(wordsFile,"a")
    f.write("\n".join(wordList)+"\n")
    wordList = []
    #f.write(wordsStr)
    #wordsStr = ""
    f.close()
def writeWordsFile():
    f = open(wordsFile,"w")
    sep="\t"
    for docID in allwords.keys():
        for word in allwords[docID]:
            f.write(word+sep+str(docID)+sep+"0"+sep+"0\n")
    f.close()
        

#selecting the file names for the docs and the words file
#baseName = "D:/Projects/Integrated_Genome_Profile_Search_Engine/Documentation/CompleteSearch/SearchEngine and preprocessing/multipleJoin"
#baseName = "/TL/epigenetics/work/completesearch/databases/wordtest/multipleJoin"
baseFolder = "/TL/epigenetics/work/completesearch/databases/wordtest/"
locNumber = 1000
sampleNumber = 100
docList = []    
wordList = []
allwords = {}
##single
#baseName = "multipleJoinSingle"+str(sampleNumber)
#docsFile = baseFolder + baseName + ".docs"
#wordsFile = baseFolder + baseName + ".words-unsorted.ascii"
#createTestMultipleCpGScoreSingle()
baseName = "multipleJoinSingleWS"+str(sampleNumber)
docsFile = baseFolder + baseName + ".docs-sorted"
wordsFile = baseFolder + baseName + ".words-unsorted.ascii"
#wordsFile = baseFolder + baseName + ".words-unsorted.binary"
createTestMultipleCpGScoreSingleWithScores()

##triple
#baseName = "multipleJoinTriple"+str(sampleNumber)
#docsFile = baseFolder + baseName + ".docs"
#wordsFile = baseFolder + baseName + ".words-unsorted.ascii"
#createTestMultipleCpGScoreTriple()
#baseName = "multipleJoinTripleWS"+str(sampleNumber)
#docsFile = baseFolder + baseName + ".docs"
#wordsFile = baseFolder + baseName + ".words-unsorted.ascii"
#createTestMultipleCpGScoreTripleWithScores()

##double
#baseName = "multipleJoinDouble"+str(sampleNumber)
#docsFile = baseFolder + baseName + ".docs"
#wordsFile = baseFolder + baseName + ".words-unsorted.ascii"
#createTestMultipleCpGScoreDouble()
#baseName = "multipleJoinDoubleWS"+str(sampleNumber)
#docsFile = baseFolder + baseName + ".docs"
#wordsFile = baseFolder + baseName + ".words-unsorted.ascii"
#createTestMultipleCpGScoreDoubleWithScores()

