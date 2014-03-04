import cx_Oracle
import time
import sys

print sys.argv
dsName = "hg18_ucsc_cpg_islands"
dsName = sys.argv[2]
mode = sys.argv[3]
if mode != "t" and mode != "n":
    raise Exception, "Mode is only allowed to be text or numeric"
mode = sys.argv[3]

tableName = "E"+mode+dsName
#tableName = "testEpiexplorer"

def createTable():
#    statement = "CREATE TABLE "+tableName+"""(
#    docID INTEGER,
#    datasetGroup INTEGER,
#    datasetName INTEGER,
#    tissueName INTEGER,
#    datasetFullName NVARCHAR2(100))"""
    if mode == "n":
        statement = "CREATE TABLE "+tableName+"""(
    docID INTEGER,    
    datasetFullName INTEGER)"""
    elif mode == "t":
        statement = "CREATE TABLE "+tableName+"""(
    docID INTEGER,
    datasetFullName NVARCHAR2(100))"""
    result = dbcur.execute(statement)
def initTable():
    try:
        #fillInTable()
        fillInTableMany()
        createIndeces()
    except Exception,ex:
        print ex
def fillInTable():
    fn = "/TL/epigenetics/work/EpiExplorerTest/Datasets/hg18_CSFiles/"+dsName+".words-sorted.ascii"
    f = open(fn)
    numberOfLines = 0    
    for line in f:
        if line.startswith("Eoverlaps:"):
            lineParts = line.strip().split("\t")             
            statement = "INSERT INTO "+tableName+" (docID, datasetFullName) VALUES ("+lineParts[1]+", '"+lineParts[0]+"')"
            #statement = "INSERT INTO "+tableName+" (docID, datasetFullName) VALUES (1, 'test')"
            result = dbcur.execute(statement)
            numberOfLines += 1
            #print lineParts
            #raise Exception
            if numberOfLines %1000 == 0:
                print numberOfLines        
        
    f.close()
    print numberOfLines
    
def fillInTableMany():
    fn = "/TL/epigenetics/work/EpiExplorerTest/Datasets/hg18_CSFiles/"+dsName+".words-sorted.ascii"
    f = open(fn)
    d = {"counter":0}
    numberOfLines = 0
    statement = "INSERT INTO "+tableName+" (docID, datasetFullName) VALUES (:1, :2)"    
    statementParams = []
    for line in f:
        if line.startswith("Eoverlaps:"):
            lineParts = line.strip().split("\t")
            if not d.has_key(lineParts[0]):
                d[lineParts[0]] = d["counter"]
                d["counter"] += 1
            if mode == "n":
                statementParams.append({"1":lineParts[1],"2":d[lineParts[0]]})
            elif mode == "t":
                statementParams.append({"1":lineParts[1],"2":lineParts[0]})
            
            numberOfLines += 1
            #print lineParts
            #raise Exception
            if numberOfLines % 100000 == 0:                
                result = dbcur.executemany(statement,statementParams)
                statementParams = []
                print numberOfLines
                #raise Exception
    if statementParams:        
        result = dbcur.executemany(statement,statementParams)
        statementParams = []
    f.close()
    dbcon.commit()
    print numberOfLines
    
def createIndeces():    
    statement = "CREATE INDEX i"+mode+dsName+" ON "+tableName+" (docID)"
    result = dbcur.execute(statement)
    print "Index di ready"
#    statement = "CREATE INDEX dgi ON "+tableName+" (datasetGroup)"
#    result = dbcur.execute(statement)
#    print "Index dgi ready"
#    statement = "CREATE INDEX dni ON "+tableName+" (datasetName)"
#    result = dbcur.execute(statement)
#    print "Index dni ready"
#    statement = "CREATE INDEX tni ON "+tableName+" (tissueName)"
#    result = dbcur.execute(statement)
#    print "Index tni ready"
    statement = "CREATE INDEX f"+mode+dsName+" ON "+tableName+" (datasetFullName)"
    result = dbcur.execute(statement)
    print "Index df ready"
    
def testCall(totalTime,numberOfCalls):    
    
    statement = "SELECT datasetFullName,COUNT(*) FROM "+tableName+" GROUP BY datasetFullName"
    for i in xrange(numberOfCalls):
        t0 = time.time()
        result = dbcur.execute(statement)
        t = time.time() - t0        
        totalTime[0] += t
        r = list(dbcur.fetchall())
        totalTime[1] += 1 
        totalTime[2].append(t)
    totalTime[2].sort() 
    print r
    percentile = 0.95
    print int(percentile*100),"% of the calls in under time",totalTime[2][int(len(totalTime[2])*percentile)]
    timecutoff = 2
    print "Percent of queries executed in less than",timecutoff,"seconds",round((100*len(filter(lambda x:x<=2,totalTime[2])))/float(totalTime[1]),2),"%"
def dropTable():
    statement = "DROP TABLE "+tableName+""
    result = dbcur.execute(statement)


if __name__ == "__main__":
    dbcon = cx_Oracle.connect("epigraph_admin", "epigraph123", "bioinfo")
    dbcur = dbcon.cursor()
    if sys.argv[1] == "init":
        createTable()
        initTable()
    elif sys.argv[1] == "test":
        numberOfCalls = int(sys.argv[4])
        totalTime = [0,0,[]]     
        testCall(totalTime,numberOfCalls)
        print totalTime,totalTime[0]/totalTime[1]
    elif sys.argv[1] == "drop":               
        dropTable()    
    
    dbcur.close()
    dbcon.commit()
    dbcon.close()
