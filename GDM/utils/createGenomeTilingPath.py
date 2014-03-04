#! /usr/bin/python
#
# Summary: generate a region set that covers the entire genome, excluding regions that are exclusively consisting of Ns
#
# example call:
# python createGenomeTilingPath.py --outputFile=. --genomeDir=genomes --genome=hg18 --chromosomes=chr21
# python createGenomeTilingPath.py --outputFile=regions_hg18/hg18.28.Tiling_regions_5kb.tilingRegions_size5000_step4500.region --genomeDir=genomes --genome=hg18 --windowSize=5000 --slidingOffset=4500 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_hg18/hg18.29.Tiling_regions_5kb_nonRepetitive.tilingRegions_size5000_step4500_maxRepeats25p.region --genomeDir=genomes --genome=hg18 --windowSize=5000 --slidingOffset=4500 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=0.25 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_hg18/hg18.30.Tiling_regions_5kb_repetitive.tilingRegions_size5000_step4500_minRepeats75p.region --genomeDir=genomes --genome=hg18 --windowSize=5000 --slidingOffset=4500 --minRatioNonN=0.25 --minRatioRepeats=0.75 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_hg18/hg18.31.Tiling_regions_2kb.tilingRegions_size2000_step1000.region --genomeDir=genomes --genome=hg18 --windowSize=2000 --slidingOffset=1000 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_mm9/mm9.28.Tiling_regions_5kb.tilingRegions_size5000_step4500.region --genomeDir=genomes --genome=mm9 --windowSize=5000 --slidingOffset=4500 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_mm9/mm9.29.Tiling_regions_5kb_nonRepetitive.tilingRegions_size5000_step4500_maxRepeats25p.region --genomeDir=genomes --genome=mm9 --windowSize=5000 --slidingOffset=4500 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=0.25 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_mm9/mm9.30.Tiling_regions_5kb_repetitive.tilingRegions_size5000_step4500_minRepeats75p.region --genomeDir=genomes --genome=mm9 --windowSize=5000 --slidingOffset=4500 --minRatioNonN=0.25 --minRatioRepeats=0.75 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_mm9/mm9.31.Tiling_regions_2kb.tilingRegions_size2000_step1000.region --genomeDir=genomes --genome=mm9 --windowSize=2000 --slidingOffset=1000 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_danRer6/danRer6.28.Tiling_regions_5kb.tilingRegions_size5000_step4500.region --genomeDir=genomes --genome=danRer6 --windowSize=5000 --slidingOffset=4500 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chr23,chr24,chr25
# python createGenomeTilingPath.py --outputFile=regions_danRer6/danRer6.29.Tiling_regions_5kb_nonRepetitive.tilingRegions_size5000_step4500_maxRepeats25p.region --genomeDir=genomes --genome=danRer6 --windowSize=5000 --slidingOffset=4500 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=0.25 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chr23,chr24,chr25
# python createGenomeTilingPath.py --outputFile=regions_danRer6/danRer6.30.Tiling_regions_5kb_repetitive.tilingRegions_size5000_step4500_minRepeats75p.region --genomeDir=genomes --genome=danRer6 --windowSize=5000 --slidingOffset=4500 --minRatioNonN=0.25 --minRatioRepeats=0.75 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chr23,chr24,chr25

# python createGenomeTilingPath.py --outputFile=regions_hg18/hg18.40.Tiling_regions_5kb.tilingRegions_size5000_step5000.region --genomeDir=genomes --genome=hg18 --windowSize=5000 --slidingOffset=5000 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_hg18/hg18.41.Tiling_regions_2kb.tilingRegions_size2000_step1000.region --genomeDir=genomes --genome=hg18 --windowSize=2000 --slidingOffset=1000 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_hg18/hg18.42.Tiling_regions_2kb.tilingRegions_size2000_step2000.region --genomeDir=genomes --genome=hg18 --windowSize=2000 --slidingOffset=2000 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_hg18/hg18.43.Tiling_regions_2kb.tilingRegions_size2000_step1500.region --genomeDir=genomes --genome=hg18 --windowSize=2000 --slidingOffset=1500 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_hg18/hg18.44.Tiling_regions_1kb.tilingRegions_size1000_step1000.region --genomeDir=genomes --genome=hg18 --windowSize=1000 --slidingOffset=1000 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY
# python createGenomeTilingPath.py --outputFile=regions_hg18/hg18.45.Tiling_regions_1kb.tilingRegions_size1000_step500.region --genomeDir=genomes --genome=hg18 --windowSize=1000 --slidingOffset=500 --minRatioNonN=0.25 --minRatioRepeats=0 --maxRatioRepeats=1 --chromosomes=chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY

import os
from downloadGenome import downloadGenome

# removes newline characters at the end of a string (similar to rstrip() but leaves tabs intact)
def removeLinefeed(s):
    while s[-1] in ["\n","\r"]: s = s[0:-1]
    return s


# obtain the DNA sequence for a given genomic region   
def lookupSequence(genomePath, chrom, chromstart, chromend):
    global chromFiles
    global offset
    try:
        chromFile = chromFiles[chrom]
    except KeyError:
        chromFilename = genomePath + os.sep + chrom + ".fa"
        chromFile = open(chromFilename,'r')        
        # determine offset
        firstByte = chromFile.read(1)
        offset = 0
        if firstByte == ">": offset = len(chromFile.readline()) + 1 # +1 for first byte
        # make sure that the row length is 50 bp and the line separator is "\n"
        chromFile.seek(offset+49,0)
        seq = chromFile.read(3)
        validLetters = ["A","C","G","T","N"]
        if not seq[0].upper() in validLetters or not seq[1] == "\n" or not seq[2].upper() in validLetters:
            print "Incorrect file format detected for "+chrom+". Sequence around position 50: "+seq
            raise SystemExit
        chromFiles[chrom] = chromFile
    # retrieve genomic sequence
    pos = chromstart / 50 * 51 + chromstart % 50
    length = (chromend - chromstart + 50) / 50 * 51
    chromFile.seek(offset+pos,0)
    seq = chromFile.read(length)
    seq = seq.replace("\n","")
    seq = seq[0:(chromend-chromstart)]
    if debug: print "Sequence of %s:%i-%i (%s) is: %s" % (chrom, chromstart, chromend, genome, seq)    
    return seq
    
    
# main analysis procedure
def performAnalysis(options):
    # prepare output file
    outfile = open(options.outputFile,'w')
    header = "#chrom\tchromstart\tchromend\tname\n"
    outfile.write(header)    

    # obtain genome sequence (if necessary)
    genomePath = options.genomeDir+os.sep+options.genome
    if not os.path.exists(genomePath):
        print "Genome assembly not found for '"+options.genome+"', trying to obtain genome from UCSC Genome Browser"        
        downloadGenome(options.genome, options.genomeDir)    
    if not os.path.exists(genomePath):
        print "Could not obtain required genome assembly for '"+options.genome+"'"
        raise SystemExit    

    # perform region annotation
    chromosomes = options.chromosomes.split(",")
    count = 0
    global chromFiles
    chromFiles = {} # will be initialized on the first call to lookupSequence()
    for chrom in chromosomes:        
        chromstart = 0
        chromend = 0
        while True:            
            if chromstart % 10000000 <= options.slidingOffset: print "Processing: %s %i %i" % (chrom, chromstart, chromstart + options.windowSize)
            try:
                seq = lookupSequence(genomePath, chrom, chromstart, chromstart + options.windowSize)
            except Exception, ex:
                print 'Could not retrieve sequence for current position: ("'+chrom+":"+str(chromstart)+"-"+str(chromstart+options.windowSize)+'") due to the following exception: '+str(type(ex))+": "+str(ex)    
                break
            else:
                length = len(seq)                
                if length == 0: 
                    print "End of chromosome "+chrom+" reached: "+str(chromend)
                    break
                chromend = chromstart + length
                if 1 - float(seq.count("N"))/length >= options.minRatioNonN:
                    nonRepeatLetter = ['A','C','G','T']
                    repeatCount = length
                    for letter in nonRepeatLetter: repeatCount -= seq.count(letter) # substract any occurance of non repeat letter
                    if options.minRatioRepeats <= float(repeatCount)/length <= options.maxRatioRepeats:
                        count += 1
                        outfile.write("%s\t%s\t%s\t%s\n" % (chrom,chromstart,chromend,count))
            chromstart = chromstart + options.slidingOffset
        
    # cleaning up
    for chrom in chromFiles.keys():
        chromFiles[chrom].close()
    outfile.close()
    


if __name__ == '__main__':
    print "Starting program..." 
    # constructing command line parser
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('--outputFile',action='store',type='string',dest='outputFile',help='Specify the prefix of the output file',default="tilingRegions")
    parser.add_option('--genome',action='store',type='string',dest='genome',help='Specify the genome for which the DNA sequence should be retrieved (default: hg18)', default="hg18")    
    parser.add_option('--genomeDir',action='store',type='string',dest='genomeDir',help='Specify the name of the directory containing the genome sequence data (will be downloaded from USCS Genome Browser if not available locally)',default="genomes")
    parser.add_option('--windowSize',action='store',type='int',dest='windowSize',help='Specify the window size for the sliding window (default: 5000)', default=5000)
    parser.add_option('--slidingOffset',action='store',type='int',dest='slidingOffset',help='Specify the offset for the sliding window (default: 2500)', default=2500)
    parser.add_option('--minRatioNonN',action='store',type='float',dest='minRatioNonN',help='Specify the minimum ratio of non-N characters for a window to be accepted (default: 0.25)', default=0.25)
    parser.add_option('--minRatioRepeats',action='store',type='float',dest='minRatioRepeats',help='Specify the minimum ratio of repeat characters for a window to be accepted (default: 0)', default=0)    
    parser.add_option('--maxRatioRepeats',action='store',type='float',dest='maxRatioRepeats',help='Specify the maximum ratio of repeat characters for a window to be accepted (default: 1)', default=1)    
    parser.add_option('--chromosomes',action='store',type='string',dest='chromosomes',help='Specify the chromosomes and their order in the form of a comma-separated string (default: chr1 to chr22, chrX, chrY)', default="chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY")    
    parser.add_option('-v','--verbose',action='store_true',dest='verbose',help='Print debugging information [default=False]',default=False)
    (options,args) = parser.parse_args()
    global debug
    debug = options.verbose

    performAnalysis(options)
                         
    print "Program successfully terminating...."     