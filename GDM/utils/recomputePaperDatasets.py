import xmlrpclib
import socket
import time
import sys
import subprocess
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
#server = xmlrpclib.Server("http://srv-13-13:51925",encoding='ISO-8859-1',allow_none=True)

def getAdditionalFullsettings(genome,useHistones,useNeighborhood,
                              useDNAsequence,useDNaseI,
                              includeMethylation,includeChromHMMSeg):
    histoneProperties = {"hasFeatures":useHistones,                            
                        "useNeighborhood":useNeighborhood,
    #                   "neighborhoodBeforeStart":[100000,30000,10000,3000,1000,300,100,30,10],
    #                   "neighborhoodAfterEnd":[10,30,100,300,1000,3000,10000,30000,100000],
                        }  
    additionalSettings = {"hg18":{                                  
                                  "hg18_broad_histones_H4K20me1":histoneProperties,
                                  "hg18_broad_histones_H3K27ac":histoneProperties,
                                  "hg18_broad_histones_H3K27me3":histoneProperties,
                                  "hg18_broad_histones_H3K36me3":histoneProperties,
                                  "hg18_broad_histones_H3K4me1":histoneProperties,
                                  "hg18_broad_histones_H3K4me2":histoneProperties,
                                  "hg18_broad_histones_H3K4me3":histoneProperties,
                                  "hg18_broad_histones_H3K9ac":histoneProperties,
                                  "hg18_broad_histones_H3K9me1":histoneProperties,                                  
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
                                                  "includeGenesUpTo":10000}

                                  },
                          "hg19":{
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
                                    "hg19_chmm_rcnv15":{"hasFeatures":includeChromHMMSeg}
                                  },
    }
    return additionalSettings[genome]
p = getAdditionalFullsettings("hg18",False,False,False,False,False,False)
p["hg18_broad_histones_H3K4me1"] = {"hasFeatures":True,                            
                                    "useNeighborhood":False}

if sys.argv[1] == "compute":
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
    print server.processUserDataset("Szulwach5hmC20120717",
                               "/TL/epigenetics/work/completesearch/Datasets/hg18_DownloadedDatasets/d_5hmChotspotsSzulwach_777078.user",
                               "hg18",
                                p,
                                "halachev@mpi-inf.mpg.de",
                                False,
                                "",
                                "",
                                {"useScore":True})
elif sys.argv[1] == "start":
    datasetName = sys.argv[2]
    datasetName = "Szulwach5hmC20120717_449566"
    port = 47321
    serverArguments = [
                       "/TL/epigenetics/work/completesearch/binaries/04.2012/startCompletionServer",# standard start                           
                       "--locale=en_US.utf8",# the locale of the server and the text
#                           "--normalize-words", # not sure
                       "--log-file="+datasetName+".log",# the log file, this is the standard name
                       "--port="+str(port),#the port on which the server is going to be running
                       "-c "+str(1024*1024*1024),# cash size for the excerpt generator
                       "-h "+str(2*1024*1024*1024),# history size
                       "-q 10000",#number of queroes storedin the history(impl is quadratic)
#                            "-r",# automatically restart the server on crash
#                            "-m",#multithreading
#                            "-d 1",#documents should be ranked by document ID, hopefully this will save some
#                            "-w 1",#words should be sorted by documents count
                        "-T",#do not return document titles as links
                        "-P .completesearch_"+socket.gethostname()+"_"+str(port)+".pid",# name of file containing the process id,first %s will be replaced by host name, second %s will be replaced by port.
                        datasetName+".hybrid" # the file name of the main hybrid file
                       ]
#/TL/epigenetics/work/completesearch/codebase/server/startCompletionServer --locale=en_US.utf8 --normalize-words --log-file=test_user_dataset.log --port=8989 -c 1G -h 1G -q 10000 -r -m test_user_dataset.hybrid
        #print serverArguments
#tail -f test_user_dataset.log        
    p = subprocess.call(serverArguments,cwd="/TL/epigenetics/work/EpiExplorerTest/Datasets/hg18_CSFiles/")  


#for key in [            
#            "hg18_ucsc_cpg_islands",
#            "hg18_ensembl_gene_TSS",
#            "hg18_ensembl_gene_promoters",
#            "hg18_PutativeenhancersErnstetal"
#            ]:
###    if key == "hg18_ucsc_cpg_islands":
###            histoneNeighborhoodSettings.update({"hg18_ensembl_gene_genes":{"includeGO":True,
###                                              "includeGeneDescriptions": True,
###                                              "includeGeneTranscripts":True,
###                                              "includeGenesUpTo":50000}})
#    additionalSettings = getAdditionalFullsettings("hg18",True,True,True,True,True,True)
#    print key
#    server.processDefaultDataset(key,False,additionalSettings)
#for key in [            
#           "hg18_tiling_genome_wide_5000"            
#            ]:    
#    additionalSettings = getAdditionalFullsettings("hg18",True,False,True,True,True,True)
#    print key
#    server.processDefaultDataset(key,False,additionalSettings)
#for key in [            
##            "hg19_ucsc_cpg_islands",
##            "hg19_ensembl_gene_TSS",
##            "hg19_ensembl_gene_promoters",
##            "hg19_PutativeenhancersErnstetal"
#            ]:
#    print key
#    additionalSettings = getAdditionalFullsettings("hg19",True,True,True,True,True,True)
#    server.processDefaultDataset(key,False,additionalSettings)
#for key in [            
##            "hg19_tiling_genome_wide_5000"            
#            ]:    
#    additionalSettings = getAdditionalFullsettings("hg19",True,False,True,True,True,True)
#    print key
#    server.processDefaultDataset(key,False,additionalSettings)



    
    

