## 
##
## The goal is to test the performance of the index files 
## based on the already executed queries in the log
##
##

import sys
#indexLog = sys.argv[1]
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ucsc_cpg_islands.log"
#new log
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/Szulwach5hmCpeaks_923127.log"
#old log
#indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/Szulwach5hmCpeaks_857580.log"
#reference
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/Szulwach5hmCpeaks_ref_857580.log"
# Stroud

#H3K4me1 ES cells 
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/H3K4me1H1EScellpeaks_886108.log"
# Gene rpomoters
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ensembl_gene_promoters.log"
# CpG islands
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ucsc_cpg_islands.log"
# Szulwach 1
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/Szulwach5hmCpeaks_923127.log"
#Stroud
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/Stroud5hmCpeaks_589616.log"
# DNaseI hypersensitive sites
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/DNaseIhypersensitivesites_880638.log"
# Genome wide
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_tiling_genome_wide_2000.log"

# Genome wide
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_PutativeenhancersErnstetal.log"
# Genome wide
indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/d_5hmChotspotsSzulwach_777078.log"
# Genome wide
#indexLogs = ["D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ucsc_cpg_islands.log"]
# Genome wide
#indexLogs = ["D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_tiling_genome_wide_5000.log"]
# Genome wide
#indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ensembl_gene_promoters.log"
# Genome wide
#indexLog = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ensembl_gene_TSS.log"


indexLogs = ["D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/d_5hmChotspotsSzulwach_777078.log",
#             "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/Szulwach5hmCpeaks_923127.log",
#             "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/Szulwach5hmCpeaks_857580.log",
             "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/d_5hmChotspotsSzulwachetal_330832.log"]
             
#indexLogs = [
#             "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ucsc_cpg_islands_old.log",
#             "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ucsc_cpg_islands.log"]

#indexLogs = ["D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_PutativeenhancersErnstetal.log"]

indexLogs = ["D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ensembl_gene_promoters.log",]
             #"D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ensembl_gene_promoters_old.log"]
#indexLogs = ["D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ensembl_gene_TSS.log",]
             #"D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_ensembl_gene_TSS_old.log"]
#indexLogs = [             "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_tiling_genome_wide_5000.log",]
             #"D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/hg18_tiling_genome_wide_5000_old.log"
#             ]
def oldStyle():
    selectPhrase = "remaining part of query is "
    selectPhrase = 'remaining part of query is "Eregion Eoverlaps:*"'
    selectPhrase = '[1mEregion Eoverlaps:*'
    
    stats = {"totalTime":0,
             "count":0,
             "maxtime":[0,None]}
    alltimes = []
    for indexLog in indexLogs:
        f = open(indexLog)
        lines = f.readlines()
        f.close()
        addNext = False
        timelines = filter(lambda x:"[1mtotal time" in x or selectPhrase in x,lines)
        for i in xrange(len(timelines)):
            timeline = timelines[i]
            if "remaining part of query is " in timeline:
                addNext = True
                continue
            if addNext:
                addNext = False
                timelineParts = filter(lambda x:x,timeline.strip().split(" "))
                
                if timelineParts[5] == 'millisecs':
                    factor = 0.001
                elif timelineParts[5] == 'secs':
                    factor = 1
                elif timelineParts[5] == 'microsecs':
                    factor = 0.000001
                time = float(timelineParts[4])*factor
                alltimes.append(time)
                stats["count"] += 1
                stats["totalTime"] += time
                if stats["maxtime"][0] < time:
                   stats["maxtime"][0] = time 
                   stats["maxtime"][1] = timelines[i-1]
                print time, timelineParts
    alltimes.sort()
def newStyle(selectPhrase,removePhrases,lastN=0):
    global alltimes    
    for indexLog in indexLogs:
        f = open(indexLog)
        lines = f.readlines()
        f.close()        
        timelines = filter(lambda x:selectPhrase in x,lines)
        for i in xrange(len(timelines)):            
            timeline = timelines[i]  
            toRemove = False
            for rp in removePhrases:
                if rp in timeline:
                    toRemove = True
                    break
            if toRemove:
                continue 
            else:            
                timelineParts = filter(lambda x:x,timeline.strip().split(" "))
                correctI = -1
                for i in range(len(timelineParts)):
                    if "secs" in timelineParts[i]:
                        correctI = i
                        break 
                if correctI == -1:
                    print timelineParts
                    raise Exception
                
                if timelineParts[correctI] == 'millisecs':
                    factor = 0.001
                elif timelineParts[correctI] == 'secs':
                    factor = 1
                elif timelineParts[correctI] == 'microsecs':
                    factor = 0.000001            
                try:    
                    time = float(timelineParts[correctI-1])*factor
                    alltimes.append(time)
                    stats["count"] += 1
                    stats["totalTime"] += time
                    if stats["maxtime"][0] < time:
                       stats["maxtime"][0] = time 
                       stats["maxtime"][1] = timeline
                    print time, timelineParts
                except Exception,ex:
                    print "EXCEPTION:",ex
    
    alltimes = alltimes[-1*lastN:]    
    alltimes.sort()
alltimes = []
stats = {"totalTime":0,
         "count":0,
         "maxtime":[0,None]}
selectPhrase = '2] \x1b[1mEregion Eoverlaps:*'        
selectPhrase = '] \x1b[1m'
removePhrases = ["1]","2]","3]","4]"]
removePhrases = []
newStyle(selectPhrase,removePhrases)
print "Total number of queries",stats["count"]
print "Average query time",round(stats["totalTime"]/stats["count"],3),round(sum(alltimes)/float(len(alltimes)),3)
print "Maximum query time",stats["maxtime"]
percentile = 0.95
print int(percentile*100),"% of the queries in under time",alltimes[int(len(alltimes)*percentile)]
timecutoff = 2
print "Percent of queries executed in less than",timecutoff,"seconds",round((100*len(filter(lambda x:x<=2,alltimes)))/float(len(alltimes)),2),"%"
 