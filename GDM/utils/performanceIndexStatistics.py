#import testCountPrefixes
#import testPerformanceIndex

baseName = "hg18_ucsc_cpg_islands"
baseFolder = "D:/Projects/Integrated_Genome_Profile_Search_Engine/Documentation/CompleteSearch/testData/"

stats = {"totalTime":0,
         "count":0,
         "maxtime":0}

#for indexLog in indexLogs:
f = open(baseFolder+baseName+".log")
lines = f.readlines()
f.close()

timelines = filter(lambda x:"* remaining part of query is " in x,lines)
allQueries = {}
for timeline in timelines:
    timelineParts = filter(lambda x:x,timeline.strip().split("\""))    
    #print timelineParts[1]
    #timelineParts[1].split(" ")    
    if not allQueries.has_key(timelineParts[1]):
        allQueries[timelineParts[1]] = 0
    allQueries[timelineParts[1]] += 1
queries = []
for k in allQueries:
    queries.append([allQueries[k],k])
queries.sort()
queries.reverse()
print queries[:10]
    
