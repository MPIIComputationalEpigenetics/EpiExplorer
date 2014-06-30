import urllib2
import gzip
import os.path

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


for i in range(1,23)+["X","Y"]:	
  chrom = "chr"+str(i)
  print chrom
  url = "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/chromosomes/"+chrom+".fa.gz"
  localFile = "/TL/epigenetics/nobackup/epigraph/AttributeDatabase_test/upload_workdir/hg19_genome/"+chrom+".fa.gz"
  
  if not os.path.isfile(localFile):
  	downloadFile(url,localFile)
  print "download complete"
  localFileNolines = "/TL/epigenetics/nobackup/epigraph/AttributeDatabase_test/upload_workdir/hg19_genome/hg19_"+chrom+"_noLinebreaks.fa"  
  if not os.path.isfile(localFileNolines):
  	f = gzip.GzipFile(localFile,"rb")  
  	f.readline()
  	chromSeq = f.read()
  	f.close()
  	fw = open(localFileNolines,"w")
  	chromSeqUp = chromSeq.replace("\r","").replace("\n","")
  	fw.write(chromSeqUp)
  	fw.close()