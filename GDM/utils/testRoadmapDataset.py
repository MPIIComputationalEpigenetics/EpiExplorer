import sys



def checkReadsSorted(fn):
    f = open(fn)
    line = f.readline()
    prevLine = [None]
    while line:
        line = line.strip().split("\t")
        line[1] = int(line[1])
        line[2] = int(line[2])
        if line[0] == prevLine[0]:
            if prevLine[1] >= line[1]:
                raise Exception, str(line)+str(prevLine)
        else:
            print line
        prevLine = line
        line = f.readline()
    f.close()        
                
        
if len(sys.argv) > 1:
    fn = sys.argv[1]
#fn = "D:/Projects/Integrated_Genome_Profile_Search_Engine/temp/GSM537698_BI.Adult_Liver.H3K27me3.3.bed"
#checkReadsSorted(fn)
#print "Done"   

#==============================================================================
# Decoding the MACS test on 
# http://liulab.dfci.harvard.edu/MACS/Download.html 
#==============================================================================

def convert(string):
    return "".join([chr((ord(c)- 96 +13)%26 +96) for c in string])

string = "puvcfrd"
string = "znpf"
print convert(string) 
