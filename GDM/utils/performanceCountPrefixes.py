#===============================================================================
# Count prefixes
#===============================================================================
def getWordsSummary(fn,type):
    f = open(fn)
    prefixesCounts = {}
    line = f.readline()
    while line:
        lineParts = line.strip().split("\t")
        lineParts = lineParts[0].split(":")
        if int(type) == 1:
            word = lineParts[0]
        else:
            if len(lineParts) > 1:
                word = ":".join(lineParts[:-1])
            else:
                word = lineParts[0]
        try:
            prefixesCounts[word] += 1
        except:
            prefixesCounts[word] = 1
        line = f.readline()
        
    f.close()
    total = 0
    for prefix in prefixesCounts.keys():
        print prefix,prefixesCounts[prefix]
        total += prefixesCounts[prefix]
    
    prefixArray = [[prefixesCounts[el],prefixesCounts[el]/float(total),el] for el in prefixesCounts.keys()]
    prefixArray.sort()
    for el in prefixArray:
        print el
    
    dict((v,k) for k, v in prefixesCounts.iteritems())
#fn = "/TL/epigenetics/work/completesearch/Datasets/hg18_CSFiles/hg18_ucsc_cpg_islands_test.words-sorted.ascii-old"
#fn = "/TL/epigenetics/work/completesearch/Datasets/hg18_CSFiles/hg18_ucsc_cpg_islands_test.words-sorted.ascii"
import sys
#getWordsSummary(sys.argv[1],sys.argv[2])
fn = "d:/Projects/Integrated_Genome_Profile_Search_Engine/Documentation/CompleteSearch/testData/hg18_ucsc_cpg_islands.words-sorted.ascii"
type = 1
getWordsSummary(fn,1)