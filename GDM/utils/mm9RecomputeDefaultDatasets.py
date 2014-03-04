import xmlrpclib
import socket
import time
#===============================================================================
# Testing the triple serverama
#===============================================================================
# public server
#server = xmlrpclib.Server("http://infao3700:56563",encoding='ISO-8859-1',allow_none=True)
##private server
#server = xmlrpclib.Server("http://infao3806:51515",encoding='ISO-8859-1',allow_none=True)
#server = xmlrpclib.Server("http://localhost:8099",encoding='ISO-8859-1',allow_none=True)
##print server.add(5,7)
#print server.pow(5,7)
#===============================================================================
# Computing all default region sets
#===============================================================================
server = xmlrpclib.Server("http://srv-13-13:59525",encoding='ISO-8859-1',allow_none=True)
#time.sleep(60*60*3)
serverActive = False
while not serverActive:
    try:
        server.echo("aa")
        serverActive = True
    except:
        print "Fail",time.strftime("%d.%m %H:%M:%S")
        time.sleep(600)
def getAdditionalFullsettings(genome,useHistones,useNeighborhood,
                              useDNAsequence,useDNaseI,
                              includeMethylation,includeChromHMMSeg):

    histoneProperties = {"hasFeatures":useHistones,                            
                        "useNeighborhood":useNeighborhood,
    #                   "neighborhoodBeforeStart":[100000,30000,10000,3000,1000,300,100,30,10],
    #                   "neighborhoodAfterEnd":[10,30,100,300,1000,3000,10000,30000,100000],
                        }          
    additionalSettings = {"hg18":{
                                  "hg18_broad_histones_CTCF":histoneProperties,
                                  "hg18_broad_histones_H4K20me1":histoneProperties,
                                  "hg18_broad_histones_H3K27ac":histoneProperties,
                                  "hg18_broad_histones_H3K27me3":histoneProperties,
                                  "hg18_broad_histones_H3K36me3":histoneProperties,
                                  "hg18_broad_histones_H3K4me1":histoneProperties,
                                  "hg18_broad_histones_H3K4me2":histoneProperties,
                                  "hg18_broad_histones_H3K4me3":histoneProperties,
                                  "hg18_broad_histones_H3K9ac":histoneProperties,
                                  "hg18_broad_histones_H3K9me1":histoneProperties,
                                  "hg18_broad_histones_Pol2b":histoneProperties,
                                  "hg18_dna_sequence":{"hasFeatures":useDNAsequence},
                                  "hg18_uw_DNaseI":{"hasFeatures":useDNaseI},
                                  "hg18_rrbsmeth_hES_H1_p38":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_hES_H9_p58":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_fetal_brain":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_fetal_heart":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_fetal_kidney":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_fetal_lung":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_hEB16d_H1_p38":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_hFib_11_p8":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_Human_blood_CD34_mobilized_REMC":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_Neuron_H9_derived":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_NPC_H9_derived":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_Skeletal_muscle":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_Smooth_muscle":{"hasFeatures":includeMethylation},
                                  "hg18_rrbsmeth_Stomach_mucosa":{"hasFeatures":includeMethylation},
                                  "hg18_chmm_activeprom":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_weakprom":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_poisedprom":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_strenh4":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_strenh5":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_wenh6":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_wenh7":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_ins":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_trtrans":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_trelon":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_wtrx":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_prepr":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_hetr":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_rcnv14":{"hasFeatures":includeChromHMMSeg},
                                    "hg18_chmm_rcnv15":{"hasFeatures":includeChromHMMSeg},
                                  "hg18_ensembl_gene_genes":{"includeGO":True,
                                                  "includeGeneDescriptions": True,
                                                  "includeOMIM": True,
#                                                  "includeGeneTranscripts":False,
                                                  "includeGenesUpTo":5000}
                                  },
                          "hg19":{
                                  "hg19_broad_histones_CTCF":histoneProperties,
                                  "hg19_broad_histones_H2AZ":histoneProperties,
                                  "hg19_broad_histones_H3K4me1":histoneProperties,
                                  "hg19_broad_histones_H3K4me2":histoneProperties,
                                  "hg19_broad_histones_H3K4me3":histoneProperties,
                                  "hg19_broad_histones_H3K9ac":histoneProperties,
                                  "hg19_broad_histones_H3K9me1":histoneProperties,
                                  "hg19_broad_histones_H3K9me3":histoneProperties,
                                  "hg19_broad_histones_H3K27ac":histoneProperties,
                                  "hg19_broad_histones_H3K27me3":histoneProperties,
                                  "hg19_broad_histones_H3K36me3":histoneProperties,
                                  "hg19_broad_histones_H3K79me2":histoneProperties,
                                  "hg19_broad_histones_H4K20me1":histoneProperties,
                                  "hg19_broad_histones_Pol2b":histoneProperties,
                                  "hg19_dna_sequence":{"hasFeatures":useDNAsequence},
                                  "hg19_uw_DNaseI":{"hasFeatures":useDNaseI},
                                  "hg19_rrbsmeth_GM12878":{"hasFeatures":includeMethylation},
                                  "hg19_rrbsmeth_H1hESC":{"hasFeatures":includeMethylation},
                                  "hg19_rrbsmeth_HeLaS3":{"hasFeatures":includeMethylation},
                                  "hg19_rrbsmeth_HepG2":{"hasFeatures":includeMethylation},
                                  "hg19_rrbsmeth_HMEC":{"hasFeatures":includeMethylation},
                                  "hg19_rrbsmeth_HSMM":{"hasFeatures":includeMethylation},
                                  "hg19_rrbsmeth_K562":{"hasFeatures":includeMethylation},                                  
                                  "hg19_chmm_activeprom":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_weakprom":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_poisedprom":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_strenh4":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_strenh5":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_wenh6":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_wenh7":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_ins":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_trtrans":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_trelon":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_wtrx":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_prepr":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_hetr":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_rcnv14":{"hasFeatures":includeChromHMMSeg},
                                    "hg19_chmm_rcnv15":{"hasFeatures":includeChromHMMSeg},
                                  "hg19_ensembl_gene_genes":{"includeGO":True,
                                                  "includeGeneDescriptions": True,
                                                  "includeOMIM": True,
#                                                  "includeGeneTranscripts":False,
                                                  "includeGenesUpTo":5000}
                                  },
    }
    return additionalSettings[genome]

for key in [            
#            "hg18_ucsc_cpg_islands",
#            "hg18_ensembl_gene_TSS",
#            "hg18_ensembl_gene_promoters",
#            "hg18_PutativeenhancersErnstetal"
            ]:
##    if key == "hg18_ucsc_cpg_islands":
##            histoneNeighborhoodSettings.update({"hg18_ensembl_gene_genes":{"includeGO":True,
##                                              "includeGeneDescriptions": True,
##                                              "includeGeneTranscripts":True,
##                                              "includeGenesUpTo":50000}})
    additionalSettings = getAdditionalFullsettings("hg18",True,True,True,True,True,True)
    print key
    #server.processDefaultDataset(key,False,additionalSettings)
for key in [            
           #"hg18_tiling_genome_wide_5000"            
            ]:    
    additionalSettings = getAdditionalFullsettings("hg18",True,False,True,True,True,True)
    print key
    #server.processDefaultDataset(key,False,additionalSettings)
#for key in [            
#            "hg19_ucsc_cpg_islands",
#            "hg19_ensembl_gene_TSS",
#            "hg19_ensembl_gene_promoters"
#                         "hg19_PutativeenhancersErnstetal"
#            ]:
#    print key
#    additionalSettings = getAdditionalFullsettings("hg19",True,True,True,True,True,True)
#    server.processDefaultDataset(key,False,additionalSettings)
#for key in [            
#            "hg19_tiling_genome_wide_5000"            
#            ]:    
#    additionalSettings = getAdditionalFullsettings("hg19",True,False,True,True,True,True)
#    print key
#    server.processDefaultDataset(key,False,additionalSettings)


#print server.processUserDataset("Szulwach5hmC20120110",
 #                               "/TL/epigenetics/work/completesearch/Datasets/hg18_DownloadedDatasets/d_5hmChotspotsSzulwach_777078.user",
 #                               "hg18",
#                                                                getAdditionalFullsettings("hg18",True,True,True,True,True,True),
#                                "halachev@mpi-inf.mpg.de",
 #                               False,"","",{"useScore":True})


for key in [            
            "mm9_ucsc_cpg_islands",
            "mm9_ensembl_gene_TSS",
            "mm9_ensembl_gene_promoters"
            ]:
    print key
    #additionalSettings = getAdditionalFullsettings("hg19",True,True,True,True,True,True)
    server.processDefaultDataset(key,False)
    
for key in [            
            "mm9_tiling_genome_wide_5000"            
            ]:    
    #additionalSettings = getAdditionalFullsettings("hg18",True,False,True,True,True,True)
    print key
    server.processDefaultDataset(key,False)




















additionalSettings = {        
                              "hg18_dna_sequence":{"hasFeatures":True},
                              "hg18_ensembl_gene_genes":{"includeGO":True,
                                              "includeGeneDescriptions": True,
                                              "includeOMIM": True,
                                              "includeGeneTranscripts":False,
                                              "includeGenesUpTo":0}
                    } 

   
for key in [##            "ucsc_cpg_islands",
###            "ensembl_gene_TSS",
###            "ensembl_gene_genes",
#            "hg18_ensembl_gene_promoters_region",
###            "ensembl_gene_promoters_centered",
###            "ensembl_gene_promoters",
###            "ensembl_gene_introns",
###            "ensembl_gene_exons",
#            "hg18_cgihunter_CpG_Islands",
###            "conservation",
###            "uw_DNaseI",

#            "hg18_tiling_genome_wide_2000",
###            "tiling_around_genes_2000",
###            "tiling_around_genes_1000",            
####            #"broad_histones",            
####            #"repeat_masker"
####### MOUSE DATASETS
#            "mm9_ucsc_cpg_islands",
#######mm9repeat_masker",
#######mm9conservation",
#####            "mm9chromosome_band",            
#            "mm9_cgihunter_CpG_Islands",
#            "mm9_ensembl_gene_promoters",
##            "mm9ensembl_gene_promoters_centered",
##            "mm9ensembl_gene_promoters_region",
#            "mm9_ensembl_gene_TSS",
##            "mm9ensembl_gene_exons",
#####            "mm9ensembl_gene_introns",
##            "mm9ensembl_gene_genes",
#            "mm9_tiling_genome_wide_2000",
#            "hg18_tiling_genome_wide_2000",
#            "hg19_ucsc_cpg_islands"
            ]:
    print time.strftime("%d.%m %H:%M:%S"),"Processing ",key
    server.processDefaultDataset(key,False,additionalSettings)
#===========================================================================
#    Computing a user dataset
#===========================================================================
# test old format
#server.processUserDataset("hg18test_user_dataset","/TL/epigenetics/work/completesearch/Datasets/hg18_DownloadedDatasets/basictest_482894.user","hg18")
# test new fromat with empty settings
#print server.processUserDataset("hg18test_user_dataset","/TL/epigenetics/work/completesearch/Datasets/hg18_DownloadedDatasets/test_882315.user","hg18",{})
# test new format with one hisotme mod switched off
#print server.processUserDataset("hg18test_user_dataset",
#                                "/TL/epigenetics/work/completesearch/Datasets/hg18_DownloadedDatasets/test_882315.user",
#                                "hg18",
#                                {"hg18_broad_histones_H4K20me1":{"hasFeatures":False},
#                                 "hg18_broad_histones_H3K9ac":{"hasFeatures":False},
#                                "hg18_broad_histones_CTCF":{"hasFeatures":False},
#                                "hg18_broad_histones_H3K4me3":{"hasFeatures":True,
#                                                              "useNeighborhood":True,
#                                                              "neighborhoodBeforeStart":[500,1000],
#                                                              "neighborhoodAfterEnd":[300,600],
#                                                              },
#                                "hg18_dna_sequence":{"hasFeatures":True,
#                                                     "patterns":["A","CGCG","CCCC","AAAAA"]}})
# test new format with more patterns
#print server.processUserDataset("hg18test_user_dataset",
#                                "/TL/epigenetics/work/completesearch/Datasets/hg18_DownloadedDatasets/test_882315.user",
#                                "hg18",
#                                {"notExistingDataset":{"hasFeatures":True}})
#print server.processUserDataset("hg18test_user_dataset",
#                                "/TL/epigenetics/work/completesearch/Datasets/hg18_DownloadedDatasets/test_882315.user",
#                                "hg18",
#                                {"hg18_broad_histones_H3K4me3":{"notAllowed":True}})

datasetUpdatedProperties = {"hasFeatures":True,                            
                            "useNeighborhood":True,
                            "neighborhoodBeforeStart":[100000,30000,10000,3000,1000,300,100,30,10],
                            "neighborhoodAfterEnd":[10,30,100,300,1000,3000,10000,30000,100000],
                            }          
additionalSettings = {
                              "hg18_broad_histones_CTCF":datasetUpdatedProperties,
                              "hg18_broad_histones_H4K20me1":datasetUpdatedProperties,
                              "hg18_broad_histones_H3K27ac":datasetUpdatedProperties,
                              "hg18_broad_histones_H3K27me3":datasetUpdatedProperties,
                              "hg18_broad_histones_H3K36me3":datasetUpdatedProperties,
                              "hg18_broad_histones_H3K4me1":datasetUpdatedProperties,
                              "hg18_broad_histones_H3K4me2":datasetUpdatedProperties,
                              "hg18_broad_histones_H3K4me3":datasetUpdatedProperties,
                              "hg18_broad_histones_H3K9ac":datasetUpdatedProperties,
                              "hg18_broad_histones_H3K9me1":datasetUpdatedProperties,
                              "hg18_broad_histones_Pol2b":datasetUpdatedProperties,
                              "hg18_dna_sequence":{"hasFeatures":True},
                              "hg18_ensembl_gene_genes":{"includeGO":True,
                                              "includeGeneDescriptions": True,
                                              "includeOMIM": True,
                                              "includeGeneTranscripts":False,
                                              "includeGenesUpTo":0}}
#print server.processUserDataset("DNaseI hypersensitive sites",
#                                "/TL/epigenetics/work/completesearch/Datasets/hg18_RawDatasets/hg18_uw_DNaseI_any.bed",
#                                "hg18",
#                                additionalSettings,
#                                "halachev@mpi-inf.mpg.de")

#print server.processUserDataset("RFGFC4vs4s",
#                                "/TL/epigenetics/work/completesearch/Datasets/hg18_DownloadedDatasets/RFGFC4vs4sfiltered2_434390.user",
#                                "hg18",
#                                {"hg18_ensembl_gene_genes":{"includeGO":True,
#                                              "includeGeneDescriptions": True,
#                                              #"includeOMIM": True,
#                                              #"includeGeneTranscripts":False,
#                                              "includeGenesUpTo":10000},
#                                 "hg18_dna_sequence":{"hasFeatures":True}},
#                                 "halachev@mpi-inf.mpg.de")
#time.sleep(60*5)
#print server.processUserDataset("RFSFC4vs4s",
#                                "/TL/epigenetics/work/completesearch/Datasets/hg18_DownloadedDatasets/RFSFC4vs4sfiltered2_490978.user",
#                                "hg18",
#                                {"hg18_ensembl_gene_genes":{"includeGO":True,
#                                              "includeGeneDescriptions": True,
#                                              #"includeOMIM": True,
#                                              #"includeGeneTranscripts":False,
#                                              "includeGenesUpTo":10000},
#                                 "hg18_dna_sequence":{"hasFeatures":True}},
#                                 "halachev@mpi-inf.mpg.de")

#print server.processUserDataset("RFFC4vs4s",
#                                "/TL/epigenetics/work/completesearch/Datasets/hg18_DownloadedDatasets/RFFC4vs4sfiltered_993988.user",
#                                "hg18",
#                                {"hg18_ensembl_gene_genes":{"includeGO":True,
#                                              "includeGeneDescriptions": True,
#                                              #"includeOMIM": True,
#                                              #"includeGeneTranscripts":False,
#                                              "includeGenesUpTo":10000},
#                                 "hg18_dna_sequence":{"hasFeatures":True}},
#                                 "halachev@mpi-inf.mpg.de")

#===============================================================================
# Computing all properties for custom region 
#===============================================================================
#print server.getGenomicRegionProperties("hg18",["chr1",2965603,2977603])
#print server.getGenomicRegionProperties("mm9",["chr1",2965603,2977603])

#===============================================================================
# Precomputing all Illumina datasets
#===============================================================================
#print server.echo("aaa")
#
#tempFolder = "/TL/epigenetics/work/completesearch/Datasets/hg18_temp_datasets/"
#
#IIDatasets = ['II_Bork', 'II_Chari', 'II_Chung', 'II_Encode', 'II_Gibbs', 'II_Groenninger', 'II_Hagemann', 'II_Kerkel', 'II_Kim', 'II_Lui', 'II_Rakyan_SB', 'II_Rakyan_WB', 'II_Terschendorff_Cervical', 'II_Terschendorff_WB', 'II_Terschendorff_WB_diabetes', 'II_Uddin', 'II_vdAuwera_normal', 'II_Walker', 'II_Zhang','II_All']
#for IIdatasetName in IIDatasets:
#    print IIdatasetName
#    status = server.processUserDatasetCore(IIdatasetName,tempFolder+IIdatasetName+".ini","",IIdatasetName)
#    print status
#    if status[0] != 0:
#        raise Exception, "Wrong status"     
#server.reloadProcessedUserDatasets()
    
    

