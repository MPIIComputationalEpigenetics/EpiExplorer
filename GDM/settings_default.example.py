# This file contains the main default settings
# It is unlikely any of these will need changing
# Copy this file to setting_dafult.py
# If any chages are required, over-ride the settings
# here by adding them to settings.py 

import string
import threading

from file_utilities import *


def read_CGSServer_ini(file_path):
    host_ports = read_ini_file(file_path)
    return (host_ports['datasetServerHost'], int(host_ports['datasetServerPort']),
            host_ports['queryServerHost'],   int(host_ports['queryServerPort']),
            host_ports['forwardServerHost'], int(host_ports['forwardServerPort']))


# classes for the datasets that were accepted until now
datasetClasses = ["DatasetRegions", "DatasetRegionsWithTissues", "DNASequence", "RRBSmethylation", "Genes",
                  "ChromatinModifications", "RepeatMasker", "Conservation", "BroadHistones",  "TilingRegions",
                  "IIDataset", "Infinium", "ChromosomeBand", "BroadHistonesSingle", "NIHEpigenomeWig"]

# max disatnce parameter
MAX_DISTANCE = 1000000000

# How long a CS server will live
CS_TIME_LIFE = 3 * 24 * 60 * 60     # 3 days
CS_TIME_CHECK_TIME = 60 * 60        # 1 hour
CS_TIME_REPORT_TIME = 24 * 60 * 60  # daily

# Allowed characters in words
allowed_chars = string.ascii_letters + string.digits + '_:'
trans_table = string.maketrans('', '')

wordPrefixes = {
    # ===============================================================
    # The ones used for warming up the server are added also to completeSearch to the
    # list of special queries in Globals.h
    # If these constants are changed here then they need to be changed there also
    # ===============================================================
    "region": "Eregion",
    "regionBin": "EregBin",
    "regionScore": "Ersc",
    "hypermethylation": "Ehyper",
    "hypomethylation": "Ehypo",
    "regionRank": "Erank",
    "regionStrand": "Erst",
    "overlap": "Eoverlaps",
    "overlap10p": "Eoverlaps10p",
    "overlap50p": "Eoverlaps50p",
    "overlapRatio": "Eor",
    # "overlapCount":"Eoc",
    "minimumDistance": "Emmd",
    "minimumDistanceUpstream": "Emud",
    "minimumDistanceDownstream": "Emdd",
    "gene": "gene",
    "geneName": "Egn",
    "geneStrand": "Egs",
    "geneOverlap": "Egoverlaps",
    "geneOverlapRatio": "Egor",
    "geneDistanceDownstream": "Egdd",
    "geneDistanceUpstream": "Egud",
    "geneDistance": "Egmd",
    "goTerm": " GOterm",
    "geneGOterm": "gGO",
    "geneGOtermParent": "gGOp",
    "goTermNumberGenes": "gGONG",
    "omimTermNumberGenes": "gOMIMNG",
    "GOdescription": "gGOd",
    "omimTerm": "omim",
    "omimTermDescription": "omimD",
    "omimTermID": "omimID",
    "geneSymbol": "gS",
    "geneDescriptionWord": "gD",
    "geneTranscript": "gT",
    "strand": "Estrand",
    "methSummary": "Emeth",
    "methSummaryMeth": "meth",
    "methSummaryUnmeth": "unmeth",
    "methCpGcount": "EmethCpG",
    "methRatio": "EmethR",
    "methRatioMin": "EmethRmin",
    "methRatioMax": "EmethRmax",
    "methRatioStd": "EmethRstd",
    "regionType": "Eregion",
    "regionLength": "Elength_magnitude",
    "chrom": "Echr",
    "chromStart": "Esrmchromstart",
    "chromEnd": "Esrmchromend",
    "id": "ID",
    "dnasequence": "Ednaseq",
    "chrband": "Echrband",
    "significanceValue": "EsigValue",
    "pValue": "EpValue",
    "neighborhood": "Enbh",
    "settings": "settings",
    "features": "features",
    "junkWords": "junkWords",
    "coverage": "coverage"
}

# the base url for the UCSC genome database
# ucscDatabaseBase = "http://hgdownload.cse.ucsc.edu/goldenPath/hg18/database/"
# the base url for the UCSC genome track descriptions
# ucscDescriptionBase = "http://genome.ucsc.edu/cgi-bin/hgTrackUi?g="
# the length of the different chromosomes
# usually obtained from http://hgdownload.cse.ucsc.edu/goldenPath/mm9/database/chromInfo.txt.gz

# Remove half of this and generate it dynamically

genomeChromToInt = {
    "hg18": {"chr1": 1, "chr2": 2, "chr3": 3, "chr4": 4, "chr5": 5, "chr6": 6, "chr7": 7, "chr8": 8,
             "chr9": 9, "chr10": 10, "chr11": 11, "chr12": 12, "chr13": 13, "chr14": 14,
             "chr15": 15, "chr16": 16, "chr17": 17, "chr18": 18, "chr19": 19, "chr20": 20,
             "chr21": 21, "chr22": 22, "chrX": 23, "chrY": 24, "X": 23, "Y": 24},
    "hg19": {"chr1": 1, "chr2": 2, "chr3": 3, "chr4": 4, "chr5": 5, "chr6": 6, "chr7": 7, "chr8": 8,
             "chr9": 9, "chr10": 10, "chr11": 11, "chr12": 12, "chr13": 13, "chr14": 14,
             "chr15": 15, "chr16": 16, "chr17": 17, "chr18": 18, "chr19": 19, "chr20": 20,
             "chr21": 21, "chr22": 22, "chrX": 23, "chrY": 24, "X": 23, "Y": 24},
    "mm9": {"chr1": 1, "chr2": 2, "chr3": 3, "chr4": 4, "chr5": 5, "chr6": 6, "chr7": 7, "chr8": 8,
            "chr9": 9, "chr10": 10, "chr11": 11, "chr12": 12, "chr13": 13, "chr14": 14,
            "chr15": 15, "chr16": 16, "chr17": 17, "chr18": 18, "chr19": 19,
            "chrX": 20, "chrY": 21, "X": 20, "Y": 21}}
# Why is chrX and X, and chrY and Y required above?

genomeIntToChrom = {
    "hg18": {1: "chr1", 2: "chr2", 3: "chr3", 4: "chr4", 5: "chr5", 6: "chr6", 7: "chr7", 8: "chr8",
             9: "chr9", 10: "chr10", 11: "chr11", 12: "chr12", 13: "chr13", 14: "chr14",
             15: "chr15", 16: "chr16", 17: "chr17", 18: "chr18", 19: "chr19", 20: "chr20",
             21: "chr21", 22: "chr22", 23: "chrX", 24: "chrY"},
    "hg19": {1: "chr1", 2: "chr2", 3: "chr3", 4: "chr4", 5: "chr5", 6: "chr6", 7: "chr7", 8: "chr8",
             9: "chr9", 10: "chr10", 11: "chr11", 12: "chr12", 13: "chr13", 14: "chr14",
             15: "chr15", 16: "chr16", 17: "chr17", 18: "chr18", 19: "chr19", 20: "chr20",
             21: "chr21", 22: "chr22", 23: "chrX", 24: "chrY"},
    "mm9": {1: "chr1", 2: "chr2", 3: "chr3", 4: "chr4", 5: "chr5", 6: "chr6", 7: "chr7", 8: "chr8",
            9: "chr9", 10: "chr10", 11: "chr11", 12: "chr12", 13: "chr13", 14: "chr14",
            15: "chr15", 16: "chr16", 17: "chr17", 18: "chr18", 19: "chr19", 20: "chrX", 21: "chrY"}}

genomeDataStr = {
    "hg18": {"chr1": 247249719, "chr2": 242951149, "chr3": 199501827, "chr4": 191273063,
             "chr5": 180857866, "chr6": 170899992, "chr7": 158821424, "chr8": 146274826,
             "chr9": 140273252, "chr10": 135374737, "chr11": 134452384, "chr12": 132349534,
             "chr13": 114142980, "chr14": 106368585, "chr15": 100338915, "chr16": 88827254,
             "chr17": 78774742, "chr18": 76117153, "chr19": 63811651, "chr20": 62435964,
             "chr21": 46944323, "chr22": 49691432, "chrX": 154913754, "chrY": 57772954},
    "hg19": {"chr1": 249250621, "chr2": 243199373, "chr3": 198022430, "chr4": 191154276,
             "chr5": 180915260, "chr6": 171115067, "chr7": 159138663, "chr8": 146364022,
             "chr9": 141213431, "chr10": 135534747, "chr11": 135006516, "chr12": 133851895,
             "chr13": 115169878, "chr14": 107349540, "chr15": 102531392, "chr16": 90354753,
             "chr17": 81195210, "chr18": 78077248, "chr19": 59128983, "chr20": 63025520,
             "chr21": 48129895, "chr22": 51304566, "chrX": 155270560, "chrY": 59373566},
    "mm9": {"chr1": 197195432, "chr2": 181748087, "chr3": 159599783, "chr4": 155630120, "chr5": 152537259,
            "chr6": 149517037, "chr7": 152524553, "chr8": 131738871, "chr9": 124076172, "chr10": 129993255,
            "chr11": 121843856, "chr12": 121257530, "chr13": 120284312, "chr14": 125194864, "chr15": 103494974,
            "chr16": 98319150, "chr17": 95272651, "chr18": 90772031, "chr19": 61342430, "chrX": 166650296,
            "chrY": 15902555}}

genomeDataNumbers = {
    "hg18": {1: 247249719, 2: 242951149, 3: 199501827, 4: 191273063,
             5: 180857866, 6: 170899992, 7: 158821424, 8: 146274826,
             9: 140273252, 10: 135374737, 11: 134452384, 12: 132349534,
             13: 114142980, 14: 106368585, 15: 100338915, 16: 88827254,
             17: 78774742, 18: 76117153, 19: 63811651, 20: 62435964,
             21: 46944323, 22: 49691432, 23: 154913754, 24: 57772954},
    "hg19": {1: 249250621, 2: 243199373, 3: 198022430, 4: 191154276,
             5: 180915260, 6: 171115067, 7: 159138663, 8: 146364022,
             9: 141213431, 10: 135534747, 11: 135006516, 12: 133851895,
             13: 115169878, 14: 107349540, 15: 102531392, 16: 90354753,
             17: 81195210, 18: 78077248, 19: 59128983, 20: 63025520,
             21: 48129895, 22: 51304566, 23: 155270560, 24: 59373566},
    "mm9": {1: 197195432, 2: 181748087, 3: 159599783, 4: 155630120, 5: 152537259,
            6: 149517037, 7: 152524553, 8: 131738871, 9: 124076172, 10: 129993255,
            11: 121843856, 12: 121257530, 13: 120284312, 14: 125194864, 15: 103494974,
            16: 98319150, 17: 95272651, 18: 90772031, 19: 61342430, 20: 166650296, 21: 15902555}}

genomeData = {
    "hg18": {},
    "mm9": {},
    "hg19": {}}

# This will be populated in setting.py based on genomeData
downloadDataFolder = {}
rawDataFolder      = {}
indexDataFolder    = {}
fullyProcessedDefaultDatasetsFile = {}
fullyProcessedUserDatasetsFile    = {}

# Semaphore to make the access to the log synchronized
logSemaphore = threading.Semaphore()

# Fast memory-based folder
fastTmpFolder = "/tmp/"

# should the system send mails
doSendMails = True

# should the system keep the raw words and docs files (for debug purposes)
# Shouldn't this be handled by deleteIntermediary? 
keepWordsFiles = False

csPortsStart = 45000
csPortsMaxNumber = 1000 

logTimeFormat = "%d.%m %H:%M:%S"

# These will be correct if they are in the $PATH
bedToolsFolder = ""
CS_CODE_DIR    = ""