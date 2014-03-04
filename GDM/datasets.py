import dataset_methods as dm
import sys

#===============================================================================
# @summary: Execution part
#===============================================================================
# default folder included in dataset_methods
if "win32" in sys.platform:
    defaultFolder = "D:/Projects/Datasets/RawDatasets/"
else:
    defaultFolder = "/TL/epigenetics2/work/halachev/Datasets/"
dm.defaultFolder = defaultFolder
dm.regionDatasets = {} 
dm.regionDatasets = {
            "mm9_refseq_genes":defaultFolder+"BaseSources/"+"mm9.refseq_genes.txt",
            "hg18_refseq_genes":defaultFolder+"BaseSources/"+"hg18.refseq_genes.txt",
            "mm9_ensembl_genes":defaultFolder+"BaseSources/"+"mm9.ensembl_genes.txt",
            "hg18_ensembl_genes":defaultFolder+"BaseSources/"+"hg18.ensembl_genes.txt",
            "mm9_CGI_CGIHunter_GG":defaultFolder+"BaseSources/"+"mm9.GG_CGIHunter.txt",
            "hg18_CGI_CGIHunter_GG":defaultFolder+"BaseSources/"+"hg18.GG_CGIHunter.txt",
            "mm9_RefSeq_middleExons":defaultFolder+"BaseSources/"+"mm9.middleExons_UCSC_all.txt",
            "hg18_RefSeq_middleExons":defaultFolder+"BaseSources/"+"hg18.middleExons_UCSC_all.txt",
            "mm9_RefSeq_3UTR":defaultFolder+"BaseSources/"+"mm9.3UTR_UCSC_all.txt",
            "hg18_RefSeq_3UTR":defaultFolder+"BaseSources/"+"hg18.3UTR_UCSC_all.txt",
            "mm9_RefSeq_allCodingExons":defaultFolder+"BaseSources/"+"mm9_RefSeq_allCodingExons.txt",
            "hg18_RefSeq_allCodingExons":defaultFolder+"BaseSources/"+"hg18_RefSeq_allCodingExons.txt",
            "mm9_mostConserved_all":defaultFolder+"BaseSources/"+"mm9.mostConserved_UCSC_all.txt",
            "hg18_mostConserved_all":defaultFolder+"BaseSources/"+"hg18.mostConserved_UCSC_all.txt",
            "mm9_enhancers_Visel_all":defaultFolder+"BaseSources/"+"mm9.enhancers_Visel_p300Sites_all.txt",
            "hg18_enhancers_Heintzman2009":defaultFolder+"BaseSources/"+"hg18_enhancers_Heintzman2009_h3k4me2Sites_nonPromoter.txt",
            "mm9_enhancers_meissner_all":defaultFolder+"BaseSources/"+"mm9.enhancers_Meissner2008_h3k4me2SitesWithin1kbTo100kbOfNearestPromoter_all.txt",
            "hg18_alleleSpecificDMR":defaultFolder+"BaseSources/"+"hg18.alleleSpecificDMR.txt",
            "mm9_alleleSpecificDMR":defaultFolder+"BaseSources/"+"mm9.alleleSpecificDMR.txt",
            "mm9_imprintedGenes":defaultFolder+"BaseSources/"+"mm9.imprinted_Refseq_Genes.txt",
            "hg18_imprintedGenes":defaultFolder+"BaseSources/"+"hg18.imprinted_Refseq_Genes.txt",
            "hg18_support.12.DNaseI_HS_site.hg18_tCell_DNaseI_hypersensitive_sites_Boyle2008":defaultFolder+"BaseSources/"+"hg18_support.12.DNaseI_HS_site.hg18_tCell_DNaseI_hypersensitive_sites_Boyle2008.txt",
            "hg18_CancerGene_Promoters":defaultFolder+"BaseSources/"+"hg18.CancerGene_Promoter.hg18_corePromoters_ensemblGenesMinus1000ToPlus1000AroundTSS_cancerGeneCensus.region",
            "mm9_CancerGene_Promoters":defaultFolder+"BaseSources/"+"mm9.CancerGene_Promoter.mm9_corePromoters_ensemblGenesMinus1000ToPlus1000AroundTSS_cancerGeneCensus.region",
            "hg18_CandidatePromoters":defaultFolder+"BaseSources/"+"hg18.Candidate_Promoter.hg18_corePromoters_ensemblGenesMinus1000ToPlus1000AroundTSS_manuallyCuratedList.region",
            "mm9_CandidatePromoters":defaultFolder+"BaseSources/"+"mm9.Candidate_Promoter.mm9_corePromoters_ensemblGenesMinus1000ToPlus1000AroundTSS_manuallyCuratedList.region",
            }
regionDatasetsRepeatsHG18 = {
           "hg18_tandemRepeat":defaultFolder+"BaseSources/Repeats/"+"hg18.simpleRepeat.txt",
           "hg18_Repeat_DNA":defaultFolder+"BaseSources/Repeats/"+"hg18.Repeat_DNA.txt",            
           "hg18_Repeat_LINE":defaultFolder+"BaseSources/Repeats/"+"hg18.Repeat_LINE.txt",
           "hg18_Repeat_LowComplex":defaultFolder+"BaseSources/Repeats/"+"hg18.Repeat_LowComplex.txt",
           "hg18_Repeat_LTR":defaultFolder+"BaseSources/Repeats/"+"hg18.Repeat_LTR.txt",
           "hg18_Repeat_Simple":defaultFolder+"BaseSources/Repeats/"+"hg18.Repeat_Simple.txt",
           "hg18_Repeat_SINE":defaultFolder+"BaseSources/Repeats/"+"hg18.Repeat_SINE.txt"
           }
regionDatasetsRepeatsMM9 = {
           "mm9_tandemRepeat":defaultFolder+"BaseSources/Repeats/"+"mm9.simpleRepeat.txt",
           "mm9_Repeat_DNA":defaultFolder+"BaseSources/Repeats/"+"mm9.Repeat_DNA.txt",            
           "mm9_Repeat_LINE":defaultFolder+"BaseSources/Repeats/"+"mm9.Repeat_LINE.txt",
           "mm9_Repeat_LowComplex":defaultFolder+"BaseSources/Repeats/"+"mm9.Repeat_LowComplex.txt",
           "mm9_Repeat_LTR":defaultFolder+"BaseSources/Repeats/"+"mm9.Repeat_LTR.txt",
           "mm9_Repeat_Simple":defaultFolder+"BaseSources/Repeats/"+"mm9.Repeat_Simple.txt",
           "mm9_Repeat_SINE":defaultFolder+"BaseSources/Repeats/"+"mm9.Repeat_SINE.txt"
           }
regionDatasets_DNaseI_Washington = {
           "BJ-DS10018":defaultFolder+"BaseSources/New_DNase_Peaks/"+"BJ-DS10018.peaks.fdr.005.hg17.bed",
           "BJ-DS10081":defaultFolder+"BaseSources/New_DNase_Peaks/"+"BJ-DS10081.peaks.fdr.005.hg17.bed",
           "CACO2-DS8235":defaultFolder+"BaseSources/New_DNase_Peaks/"+"CACO2-DS8235.peaks.fdr.005.hg17.bed",
           "CACO2-DS8416":defaultFolder+"BaseSources/New_DNase_Peaks/"+"CACO2-DS8416.peaks.fdr.005.hg17.bed",
           "GM12878-DS10671":defaultFolder+"BaseSources/New_DNase_Peaks/"+"GM12878-DS10671.peaks.fdr.005.hg17.bed",
           "GM12878-DS9432":defaultFolder+"BaseSources/New_DNase_Peaks/"+"GM12878-DS9432.peaks.fdr.005.hg17.bed",
           "Hela-DS10011":defaultFolder+"BaseSources/New_DNase_Peaks/"+"Hela-DS10011.peaks.fdr.005.hg17.bed",
           "Hela-DS8200":defaultFolder+"BaseSources/New_DNase_Peaks/"+"Hela-DS8200.peaks.fdr.005.hg17.bed",
           "HL60-DS7830":defaultFolder+"BaseSources/New_DNase_Peaks/"+"HL60-DS7830.peaks.fdr.005.hg17.bed",
           "HRCE-DS10662":defaultFolder+"BaseSources/New_DNase_Peaks/"+"HRCE-DS10662.peaks.fdr.005.hg17.bed",
           "HRCE-DS10666":defaultFolder+"BaseSources/New_DNase_Peaks/"+"HRCE-DS10666.peaks.fdr.005.hg17.bed",
           "HRE-DS10631":defaultFolder+"BaseSources/New_DNase_Peaks/"+"HRE-DS10631.peaks.fdr.005.hg17.bed",
           "HRE-DS10641":defaultFolder+"BaseSources/New_DNase_Peaks/"+"HRE-DS10641.peaks.fdr.005.hg17.bed",
           "hTH2-DS7842":defaultFolder+"BaseSources/New_DNase_Peaks/"+"hTH2-DS7842.peaks.fdr.005.hg17.bed",
           "HUVEC-DS10060":defaultFolder+"BaseSources/New_DNase_Peaks/"+"HUVEC-DS10060.peaks.fdr.005.hg17.bed",
           "K562-DS9764-4L":defaultFolder+"BaseSources/New_DNase_Peaks/"+"K562-DS9764-4L.peaks.fdr.005.hg17.bed",
           "K562-DS9767-4L":defaultFolder+"BaseSources/New_DNase_Peaks/"+"K562-DS9767-4L.peaks.fdr.005.hg17.bed",
           "SKMC-DS7911":defaultFolder+"BaseSources/New_DNase_Peaks/"+"SKMC-DS7911.peaks.fdr.005.hg17.bed",
           "SKNSH-DS10153":defaultFolder+"BaseSources/New_DNase_Peaks/"+"SKNSH-DS10153.peaks.fdr.005.hg17.bed",
           "Gm06990-Rep1":defaultFolder+"BaseSources/New_DNase_Peaks/"+"wgEncodeUwDnaseSeqPeaksRep1Gm06990.narrowPeak",
           "Hepg2-Rep1":defaultFolder+"BaseSources/New_DNase_Peaks/"+"wgEncodeUwDnaseSeqPeaksRep1Hepg2.narrowPeak",
           "Sknshra-Rep1":defaultFolder+"BaseSources/New_DNase_Peaks/"+"wgEncodeUwDnaseSeqPeaksRep1Sknshra.narrowPeak",
           "Th1-Rep1":defaultFolder+"BaseSources/New_DNase_Peaks/"+"wgEncodeUwDnaseSeqPeaksRep1Th1.narrowPeak",
           "Gm06990-Rep2":defaultFolder+"BaseSources/New_DNase_Peaks/"+"wgEncodeUwDnaseSeqPeaksRep2Gm06990.narrowPeak",
           "Hepg2-Rep2":defaultFolder+"BaseSources/New_DNase_Peaks/"+"wgEncodeUwDnaseSeqPeaksRep2Hepg2.narrowPeak",           
           }
regionDatasets_DNaseI_Duke = { 
           "hg18.28.GM12878_DukeDNaseSeq.pk":defaultFolder+"BaseSources/DNase_Faire_peaks/"+"GM12878_DukeDNaseSeq.pk",
           "hg18.28.GM12878_UncFAIREseq.pk":defaultFolder+"BaseSources/DNase_Faire_peaks/"+"GM12878_UncFAIREseq.pk",
           "hg18.28.HelaS3_DukeDNaseSeq.pk":defaultFolder+"BaseSources/DNase_Faire_peaks/"+"HelaS3_DukeDNaseSeq.pk",
           "hg18.28.HelaS3_UncFAIREseq.pk":defaultFolder+"BaseSources/DNase_Faire_peaks/"+"HelaS3_UncFAIREseq.pk",
           "hg18.28.HepG2_DukeDNaseSeq.pk":defaultFolder+"BaseSources/DNase_Faire_peaks/"+"HepG2_DukeDNaseSeq.pk",
           "hg18.28.HepG2_UncFAIREseq.pk":defaultFolder+"BaseSources/DNase_Faire_peaks/"+"HepG2_UncFAIREseq.pk",
           "hg18.28.K562_DukeDNaseSeq.pk":defaultFolder+"BaseSources/DNase_Faire_peaks/"+"K562_DukeDNaseSeq.pk",
           "hg18.28.K562_UncFAIREseq.pk":defaultFolder+"BaseSources/DNase_Faire_peaks/"+"K562_UncFAIREseq.pk",                                   
           }


##===============================================================================
#dm.regionDatasets = {
##           "randomRegions_all":defaultFolder+"mm9_randomRegions.txt",
#           "mm9.randomRegions_no":defaultFolder+"mm9.randomRegions_no.txt",
#            }    


#
## 9.19 mm9.19.Random_Region.mm9_randomRegions_no
#dm.deriveNewDataset("mm9.19.Random_Region.mm9_randomRegions_no",
#                 "mm9.randomRegions_no",
#                 [],
#                 None,
#                 None,
#                 True)



#===============================================================================

#===============================================================================
#dm.regionDatasets = {
#           "hg18.randomRegions_no":defaultFolder+"hg18.randomRegions_no.txt",
#            }  



## 19 hg18.19.Random_Region.hg18_randomRegions_no
#dm.deriveNewDataset("hg18.19.Random_Region.hg18_randomRegions_no",
#                 "hg18.randomRegions_no",
#                 [],
#                 None,
#                 None,
#                 True)
#===============================================================================
#### 1
def hg18_1():
    dm.extractFlanks("hg18_ensembl_genes",
                     "hg18_support.1.Promoter_ensembl.ensemblGenes_minus_5000_to_1000_around_TSS_flancks",
                     True,"start",5000,1000)
    dm.deriveNewDataset("hg18.1.Promoter_ensembl.ensemblGenes_minus_5000_to_1000_around_TSS.region",
                     "hg18_support.1.Promoter_ensembl.ensemblGenes_minus_5000_to_1000_around_TSS_flancks",
                     [],
                     [],
                     None,
                     None,
                     True,
                     True)
    
def mm9_1():
    dm.extractFlanks("mm9_ensembl_genes",
                     "mm9_support.1.Promoter_ensembl.ensemblGenes_minus_5000_to_1000_around_TSS_flancks",
                     True,"start",5000,1000)
    dm.deriveNewDataset("mm9.1.Promoter_ensembl.ensemblGenes_minus_5000_to_1000_around_TSS.region",
                     "mm9_support.1.Promoter_ensembl.ensemblGenes_minus_5000_to_1000_around_TSS_flancks",
                     [],
                     [],
                     None,
                     None,
                     True,
                     True)
    
#### 2
def mm9_2():
    dm.extractFlanks("mm9_refseq_genes",
                     "mm9_support.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS_flancks",
                     True,"start",1000,1000)
    dm.deriveNewDataset("mm9.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                        "mm9_support.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS_flancks",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
def hg18_2():
    dm.extractFlanks("hg18_refseq_genes",
                     "hg18_support.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS_flancks",
                     True,"start",1000,1000)
    dm.deriveNewDataset("hg18.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                        "hg18_support.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS_flancks",
                        [],                        
                        [],
                        None,
                        None,
                        True,
                        True)
##### 3
def mm9_3():
    dm.extractFlanks("mm9_refseq_genes",
                     "mm9_support.3.Promoter_region.refSeqGenes_minus_10000_to_2000_around_TSS_flancks",
                     True,"start",10000,2000)
    dm.deriveNewDataset("mm9.3.Promoter_region.refSeqGenes_minus_10000_to_2000_around_TSS.region",
                        "mm9_support.3.Promoter_region.refSeqGenes_minus_10000_to_2000_around_TSS_flancks",
                        [],
                        [],
                        "max",
                        None,
                        True,
                        True)

def hg18_3():
    dm.extractFlanks("hg18_refseq_genes",
                     "hg18_support.3.Promoter_region.refSeqGenes_minus_10000_to_2000_around_TSS_flancks",
                     True,"start",10000,2000)
    dm.deriveNewDataset("hg18.3.Promoter_region.refSeqGenes_minus_10000_to_2000_around_TSS.region",
                        "hg18_support.3.Promoter_region.refSeqGenes_minus_10000_to_2000_around_TSS_flancks",
                        [],
                        [],
                        "max",
                        None,
                        True,
                        True)
    
#### 4
def hg18_4():
    dm.deriveNewDataset("hg18.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region",
                        "hg18_CGI_CGIHunter_GG",
                        [],
                        [],
                        None,
                        200,
                        True)
def mm9_4():
    dm.deriveNewDataset("mm9.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region",
                        "mm9_CGI_CGIHunter_GG",
                        [],
                        [],
                        None,
                        200,
                        True)
##### 5
def hg18_5():
    dm.deriveNewDataset("hg18.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region",
                        "hg18_CGI_CGIHunter_GG",
                        [],
                        [],
                        None,
                        700,
                        True)
def mm9_5():
    dm.deriveNewDataset("mm9.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region",
                        "mm9_CGI_CGIHunter_GG",
                        [],
                        [],
                        None,
                        700,
                        True)
###### 6
def hg18_6():
#    dm.deriveNewDataset("hg18.6.CGI_Promoter.Promoter_centered_overlapping_with_BonaFide_CGI.region",
#                        "hg18.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
#                        ["hg18.7.NonCGI_Promoter.Promoter_centered_nonOverlapping_with_BonaFide_CGI.region"],
#                        [],
#                        None,
#                        None,
#                        True)
    dm.deriveNewDataset("hg18.6.CGI_Promoter.Promoter_centered_overlapping_with_BonaFide_CGI.region",
                        "hg18.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                        [],
                        ["hg18.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region"],
                        None,
                        None,
                        True)
def mm9_6():
    dm.deriveNewDataset("mm9.6.CGI_Promoter.Promoter_centered_overlapping_with_BonaFide_CGI.region",
                        "mm9.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
#                        ["mm9.7.NonCGI_Promoter.Promoter_centered_nonOverlapping_with_BonaFide_CGI.region"],
                        [],
                        ["mm9.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region"],
                        None,
                        None,
                        True)
    
###### 7
def hg18_7():
    dm.deriveNewDataset("hg18.7.NonCGI_Promoter.Promoter_centered_nonOverlapping_with_BonaFide_CGI.region",
                        "hg18.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                        ["hg18.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region"],
                        [],
                        None,
                        None,
                        True)
def mm9_7():
    dm.deriveNewDataset("mm9.7.NonCGI_Promoter.Promoter_centered_nonOverlapping_with_BonaFide_CGI.region",
                        "mm9.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                        ["mm9.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region"],
                        [],
                        None,
                        None,
                        True)

##### 8
def hg18_8():
    dm.extractFlanks("hg18_refseq_genes",
                     "hg18_refseq_genes_plus10k",
                     False,"whole_region",10000,10000)
    dm.deriveNewDataset("hg18.8.NonGenic_CGI.cgiHunter_oe0.6_gc50_len200_geneDistance10000.region",
                        "hg18.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region",
                        ["hg18_refseq_genes_plus10k"],
                        [],
                        None,
                        None,
                        True)
def mm9_8():
    dm.extractFlanks("mm9_refseq_genes",
                     "mm9_support.8.refseq_genes_plus10k",
                     False,"whole_region",10000,10000)
    dm.deriveNewDataset("mm9.8.NonGenic_CGI.cgiHunter_oe0.6_gc50_len200_geneDistance10000.region",
                        "mm9.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region",
                        ["mm9_support.8.refseq_genes_plus10k"],
                        [],
                        None,
                        None,
                        True)
    
###### 9
def hg18_9(): 
    dm.deriveNewDataset("hg18.9.Middle_Exon.refSeqGenes_exon_noPromoter_noUTR.region",
                    "hg18_RefSeq_middleExons",
                    ["hg18.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                     "hg18_RefSeq_3UTR"],
                     [],
                    "max",
                    None,
                    True,
                    True)

def mm9_9(): 
    dm.deriveNewDataset("mm9.9.Middle_Exon.refSeqGenes_exon_noPromoter_noUTR.region",
                    "mm9_RefSeq_middleExons",
                    ["mm9.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                     "mm9_RefSeq_3UTR"],
                     [],
                    "max",
                    None,
                    True,
                    True)
###### 10
def hg18_10():
    dm.deriveNewDataset(
                "hg18.10.3prim_UTR.refSeqGenes_3prim_UTR_noPromoter_noExon.region",
                "hg18_RefSeq_3UTR",
                 ["hg18.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                  "hg18_RefSeq_allCodingExons"],
                  [],
                 "max",
                 None,
                 True,
                 True)

def mm9_10():
    dm.deriveNewDataset(
                "mm9.10.3prim_UTR.refSeqGenes_3prim_UTR_noPromoter_noExon.region",
                "mm9_RefSeq_3UTR",
                 ["mm9.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                  "mm9_RefSeq_allCodingExons"],
                  [],
                 "max",
                 None,
                 True,
                 True)
###### 11
def hg18_11():
    dm.deriveNewDataset("hg18.11.Conserved_Region.UCSC_mostConserved_minLength100_noPromoter_noCGI_noExon_noUTR.region",
                        "hg18_mostConserved_all",
                 ["hg18.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                  "hg18.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region",
                  "hg18_RefSeq_allCodingExons","hg18_RefSeq_3UTR"],
                  [],
                 "max",
                 100,
                 True)
def mm9_11():
    dm.deriveNewDataset("mm9.11.Conserved_Region.UCSC_mostConserved_minLength100_noPromoter_noCGI_noExon_noUTR.region",
                        "mm9_mostConserved_all",
                 ["mm9.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region",
                  "mm9.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region",
                  "mm9_RefSeq_allCodingExons","mm9_RefSeq_3UTR"],
                  [],
                 "max",
                 100,
                 True)
###### 12
def hg18_12():    
    dm.deriveNewDataset("hg18_support.12.DNaseI_HS_site.hg18_tCell_DNaseI_hypersensitive_sites_Boyle2008",
                        "hg18_DNAseCD4Sites",
                        [],
                        [],
                        None,
                        None,
                        True)

    
    dm.regionDatasets.update(regionDatasets_DNaseI_Duke)
    dm.mergeDatasets("hg18_support.12.Duke_GM12878_HelaS3_K562_hepg2_SortedNotMerged",regionDatasets_DNaseI_Duke.keys())
    dm.deriveNewDataset("hg18_support.12.Duke_GM12878_HelaS3_K562_hepg2",
                        "hg18_support.12.Duke_GM12878_HelaS3_K562_hepg2_SortedNotMerged",
                        [],
                        [],
                        "max",
                        None,
                        True,
                        True)
#

    dm.regionDatasets.update(regionDatasets_DNaseI_Washington)

    dm.mergeDatasets("hg18_support.12.Open_Chromatin.ENCODE_DNaseI_hypersensitive_sites_SortedNotMerged",
                     regionDatasets_DNaseI_Washington.keys())

    dm.deriveNewDataset("hg18_support.12.Open_Chromatin.ENCODE_DNaseI_hypersensitive_sites",
                 "hg18_support.12.Open_Chromatin.ENCODE_DNaseI_hypersensitive_sites_SortedNotMerged",
                 [],
                 [],
                 "max",
                 None,
                 True,
                 True)
    dm.mergeDatasets("hg18_support.12.All_DNaseI_datasets_merged",
                     ["hg18_support.12.Open_Chromatin.ENCODE_DNaseI_hypersensitive_sites",
                      "hg18_support.12.Duke_GM12878_HelaS3_K562_hepg2",
                      "hg18_support.12.DNaseI_HS_site.hg18_tCell_DNaseI_hypersensitive_sites_Boyle2008"
                      ])
    
    dm.deriveNewDataset("hg18.12.Open_Chromatin.DNase_FAIRE_peaks_ENCODE_noPromoter.region",
                        "hg18_support.12.All_DNaseI_datasets_merged",
                        ["hg18.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region"],
                        [],
                        "max",
                        None,
                        True,
                        True)
    dm.deriveNewDataset("hg18.12.Open_Chromatin.DNase_FAIRE_peaks_ENCODE_noPromoter_downsampledTo500k.region",
                 "hg18.12.Open_Chromatin.DNase_FAIRE_peaks_ENCODE_noPromoter.region",
                 [],
                 [],
                 None,
                 None,
                 True,
                 True,
                 500000)
    
def hg18_12_new():
    dm.extractFlanks("hg18_support.12.DNaseI_HS_site.hg18_tCell_DNaseI_hypersensitive_sites_Boyle2008",
                     "hg18_support.12.DNaseI_HS_site.hg18_tCell_DNaseI_hypersensitive_sites_Boyle2008_1kb",
                     False,"whole_region",
                     "max(0,int(500-(chromend-chromstart)/2))","max(0,int(500-(chromend-chromstart)/2))")
    
    dm.regionDatasets.update(regionDatasets_DNaseI_Duke)
    dm.mergeDatasets("hg18_support.12.Duke_GM12878_HelaS3_K562_hepg2_SortedNotMerged",regionDatasets_DNaseI_Duke.keys())
    dm.extractFlanks("hg18_support.12.Duke_GM12878_HelaS3_K562_hepg2_SortedNotMerged",
                     "hg18_support.12.Duke_GM12878_HelaS3_K562_hepg2_SortedNotMerged_1kb",
                     False,"whole_region",
                     "max(0,int(500-(chromend-chromstart)/2))","max(0,int(500-(chromend-chromstart)/2))")
    dm.regionDatasets.update(regionDatasets_DNaseI_Washington)
    dm.mergeDatasets("hg18_support.12.Open_Chromatin.ENCODE_DNaseI_hypersensitive_sites_SortedNotMerged",
                     regionDatasets_DNaseI_Washington.keys())
    dm.extractFlanks("hg18_support.12.Open_Chromatin.ENCODE_DNaseI_hypersensitive_sites_SortedNotMerged",
                     "hg18_support.12.Open_Chromatin.ENCODE_DNaseI_hypersensitive_sites_SortedNotMerged_1kb",
                     False,"whole_region",
                     "max(0,int(500-(chromend-chromstart)/2))","max(0,int(500-(chromend-chromstart)/2))")
#    datasetCurrent = {"hg18_support.12.DNaseI_HS_site.hg18_tCell_DNaseI_hypersensitive_sites_Boyle2008_1kb":defaultFolder+"hg18_support.12.DNaseI_HS_site.hg18_tCell_DNaseI_hypersensitive_sites_Boyle2008_1kb"+".txt",
#                      "hg18_support.12.Duke_GM12878_HelaS3_K562_hepg2_SortedNotMerged_1kb":defaultFolder+"hg18_support.12.Duke_GM12878_HelaS3_K562_hepg2_SortedNotMerged_1kb"+".txt",
#                      "hg18_support.12.Open_Chromatin.ENCODE_DNaseI_hypersensitive_sites_SortedNotMerged_1kb":defaultFolder+"hg18_support.12.Open_Chromatin.ENCODE_DNaseI_hypersensitive_sites_SortedNotMerged_1kb"+".txt",
#                      }
#    dm.regionDatasets.update(datasetCurrent)
    dm.mergeDatasets("hg18_support.12.All_DNaseI_datasets_merged",
                     ["hg18_support.12.DNaseI_HS_site.hg18_tCell_DNaseI_hypersensitive_sites_Boyle2008_1kb",
                      "hg18_support.12.Duke_GM12878_HelaS3_K562_hepg2_SortedNotMerged_1kb",
                      "hg18_support.12.Open_Chromatin.ENCODE_DNaseI_hypersensitive_sites_SortedNotMerged_1kb"                      
                      ])
    
    dm.deriveNewDataset("hg18.12_new.Open_Chromatin.DNase_FAIRE_peaks_ENCODE_noPromoter.region",
                        "hg18_support.12.All_DNaseI_datasets_merged",
                        ["hg18.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region"],
                        [],
                        "max",
                        None,
                        True,
                        True)
def mm9_12():    
    dm.deriveNewDataset("mm9.12.Enhancer_p300.ChIPseq_p300_binding_sites_Visel2009_noPromoter.region",
                        "mm9_enhancers_Visel_all",
                        ["mm9.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region"],
                        [],
                        "max",
                        None,
                        True)
    
####### 13
def hg18_13():    
    dm.deriveNewDataset("hg18.13.Enhancer_H3K4me2.ChIPseq_H3K4me2_sites_Heintzman2009_noPromoter.region",
                        "hg18_enhancers_Heintzman2009",
                        ["hg18.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region"],
                        [],
                        None,
                        None,
                        True)
         
def mm9_13():
    dm.deriveNewDataset(
                        "mm9.13.Enhancer_H3K4me2.ChIPseq_H3K4me2_sitesWithin1kbTo100kbOfPromoter_Meissner2008_noPromoter.region",
                        "mm9_enhancers_meissner_all",
                        ["mm9.2.Promoter_centered.refSeqGenes_minus_1000_to_1000_around_TSS.region"],
                        [],
                        "max",
                        None,
                        True)
    
####### 14
def hg18_14():
    dm.extractFlanks("hg18.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region",
                     "hg18_support.14.CGI200_downstream",
                     False,"start",2000,0)
    dm.extractFlanks("hg18.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region",
                     "hg18_support.14.CGI200_upstream",
                     False,"end",0,2000)
    dm.mergeDatasets("hg18_support.14.CpG_Island_Shore.cgiHunter_oe0.6_gc50_len200_2kb_outsideCgi",
                     ["hg18_support.14.CGI200_upstream",
                      "hg18_support.14.CGI200_downstream"])
    dm.deriveNewDataset("hg18.14.CpG_Island_Shore.cgiHunter_oe0.6_gc50_len200_2kb_outsideCgi.region",
                        "hg18_support.14.CpG_Island_Shore.cgiHunter_oe0.6_gc50_len200_2kb_outsideCgi",
                        [],
                        [],
                        "max",
                        None,
                        True)
def mm9_14():
    dm.extractFlanks("mm9.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region",
                     "mm9_support.14.CGI200_downstream",
                     False,"start",2000,0)
    dm.extractFlanks("mm9.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region",
                     "mm9_support.14.CGI200_upstream",
                     False,"end",0,2000)
    dm.mergeDatasets("mm9_support.14.CpG_Island_Shore.cgiHunter_oe0.6_gc50_len200_2kb_outsideCgi",
                     ["mm9_support.14.CGI200_upstream",
                      "mm9_support.14.CGI200_downstream"])
    dm.deriveNewDataset("mm9.14.CpG_Island_Shore.cgiHunter_oe0.6_gc50_len200_2kb_outsideCgi.region",
                        "mm9_support.14.CpG_Island_Shore.cgiHunter_oe0.6_gc50_len200_2kb_outsideCgi",
                        [],
                        [],
                        "max",
                        None,
                        True)    
#### 15
def hg18_15():
    dm.extractFlanks("hg18.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region",
                     "hg18_support.15.CGI700_downstream",
                     False,"start",2000,0)
    dm.extractFlanks("hg18.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region",
                     "hg18_support.15.CGI700_upstream",
                     False,"end",0,2000)
    dm.mergeDatasets("hg18_support.15.BonaFide_CGI_Shore.cgiHunter_oe0.6_gc50_len700_2kb_outsideCgi",
                     ["hg18_support.15.CGI700_downstream",
                      "hg18_support.15.CGI700_upstream"])
    dm.deriveNewDataset("hg18.15.BonaFide_CGI_Shore.cgiHunter_oe0.6_gc50_len700_2kb_outsideCgi.region",
                        "hg18_support.15.BonaFide_CGI_Shore.cgiHunter_oe0.6_gc50_len700_2kb_outsideCgi",
                        [],
                        [],
                        None,
                        None,
                        True)
def mm9_15():
    dm.extractFlanks("mm9.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region",
                     "mm9_support.15.CGI700_downstream",
                     False,"start",2000,0)
    dm.extractFlanks("mm9.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region",
                     "mm9_support.15.CGI700_upstream",
                     False,"end",0,2000)
    dm.mergeDatasets("mm9_support.15.BonaFide_CGI_Shore.cgiHunter_oe0.6_gc50_len700_2kb_outsideCgi",
                     ["mm9_support.15.CGI700_downstream",
                      "mm9_support.15.CGI700_upstream"])
    dm.deriveNewDataset("mm9.15.BonaFide_CGI_Shore.cgiHunter_oe0.6_gc50_len700_2kb_outsideCgi.region",
                        "mm9_support.15.BonaFide_CGI_Shore.cgiHunter_oe0.6_gc50_len700_2kb_outsideCgi",
                        [],
                        [],
                        None,
                        None,
                        True)
#### 16
def hg18_16():
    dm.extractFlanks("hg18.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region",
                     "hg18_support.16.500bp_centered_downstream",
                     False,"start",
#                     250,"int(min(250,(chromend-chromstart)*0.25))")
                     250,250)
    dm.extractFlanks("hg18.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region",
                     "hg18_support.16.500bp_centered_upstream",
                     False,"end",
#                     "int(min(250,(chromend-chromstart)*0.25))",250)
                     250,250)
    dm.mergeDatasets("hg18_support.16.BonaFide_CGI_Border.cgiHunter_oe0.6_gc50_len700_500bp_centeredOnBorders",
                     ["hg18_support.16.500bp_centered_downstream",
                      "hg18_support.16.500bp_centered_upstream"])
    dm.deriveNewDataset("hg18.16.BonaFide_CGI_Border.cgiHunter_oe0.6_gc50_len700_500bp_centeredOnBorders.region",
                        "hg18_support.16.BonaFide_CGI_Border.cgiHunter_oe0.6_gc50_len700_500bp_centeredOnBorders",
                        [],
                        [],
                        "max",
                        None,
                        True)
    
def mm9_16():
    dm.extractFlanks("mm9.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region",
                     "mm9_support.16.500bp_centered_downstream",
                     False,"start",
#                     250,"int(min(250,(chromend-chromstart)*0.25))")
                     250,250)
    dm.extractFlanks("mm9.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region",
                     "mm9_support.16.500bp_centered_upstream",
                     False,"end",
#                     "int(min(250,(chromend-chromstart)*0.25))",250)
                     250,250)
    dm.mergeDatasets("mm9_support.16.BonaFide_CGI_Border.cgiHunter_oe0.6_gc50_len700_500bp_centeredOnBorders",
                     ["mm9_support.16.500bp_centered_downstream",
                      "mm9_support.16.500bp_centered_upstream"])
    dm.deriveNewDataset("mm9.16.BonaFide_CGI_Border.cgiHunter_oe0.6_gc50_len700_500bp_centeredOnBorders.region",
                        "mm9_support.16.BonaFide_CGI_Border.cgiHunter_oe0.6_gc50_len700_500bp_centeredOnBorders",
                        [],
                        [],
                        "max",
                        None,
                        True)
###### 17
def hg18_17():
    dm.deriveNewDataset("hg18.17.Imprinted_DMR.alleleSpecific_differentiallyMethylatedRegions_manuallyCurated.region",
                        "hg18_alleleSpecificDMR",
                        [],
                        [],
                        None,
                        None,
                        True)
def mm9_17():
    dm.deriveNewDataset("mm9.17.Imprinted_DMR.alleleSpecific_differentiallyMethylatedRegions_manuallyCurated.region",
                        "mm9_alleleSpecificDMR",
                        [],
                        [],
                        None,
                        None,
                        True)
    
###### 18
def hg18_18():
    dm.extractFlanks("hg18_imprintedGenes",
                     "hg18.18.Imprinted_Promoter.Promoter_region_refSeqGenesMinus10000ToPlus2000AroundTSS_otagoList.region",
                     True,"start",10000,2000)
#    dm.addIDs("hg18.18.Imprinted_Promoter.Promoter_region_refSeqGenesMinus10000ToPlus2000AroundTSS_otagoList.region")

def mm9_18():
    dm.extractFlanks("mm9_imprintedGenes",
                     "mm9.18.Imprinted_Promoter.Promoter_region_refSeqGenesMinus10000ToPlus2000AroundTSS_otagoList.region",
                     True,"start",10000,2000)
#    dm.addIDs("mm9.18.Imprinted_Promoter.Promoter_region_refSeqGenesMinus10000ToPlus2000AroundTSS_otagoList.region")
###### 19
def hg18_19():    
    dm.deriveNewDataset("hg18.19.CancerGene_Promoter.Promoter_region_ensemblGenesMinus10000ToPlus2000AroundTSS_cancerGeneCensus.region",
                        "hg18_CancerGene_Promoters",
                        [],
                        [],
                        None,
                        None,
                        True)
def mm9_19():
    dm.deriveNewDataset("mm9.19.CancerGene_Promoter.Promoter_region_ensemblGenesMinus10000ToPlus2000AroundTSS_cancerGeneCensus.region",
                        "mm9_CancerGene_Promoters",
                        [],
                        [],
                        None,
                        None,
                        True)
###### 20
def hg18_20():
    dm.deriveNewDataset("hg18.20.CellStateGene_Promoter.Promoter_region_ensemblGenesMinus10000ToPlus2000AroundTSS_manuallyCurated.region",
                        "hg18_CandidatePromoters",
                        [],
                        [],
                        None,
                        None,
                        True)
def mm9_20():
    dm.deriveNewDataset("mm9.20.CellStateGene_Promoter.Promoter_region_ensemblGenesMinus10000ToPlus2000AroundTSS_manuallyCurated.region",
                        "mm9_CandidatePromoters",
                        [],
                        [],
                        None,
                        None,
                        True)
###### 21
def hg18_21():
    dm.regionDatasets.update(regionDatasetsRepeatsHG18)
    dm.deriveNewDataset("hg18.21.Tandem_Repeat.tandemRepeatFinder_annotation.region",
                 "hg18_tandemRepeat",
                 [],
                 [],
                 None,
                 None,
                 True)
    dm.deriveNewDataset("hg18.21.Tandem_Repeat.tandemRepeatFinder_annotation_downsampledTo500k.region",
                 "hg18_tandemRepeat",
                 [],
                 [],
                 None,
                 None,
                 True,
                 True,
                 500000)
def mm9_21():
    dm.regionDatasets.update(regionDatasetsRepeatsMM9)
    dm.deriveNewDataset("mm9.21.Tandem_Repeat.tandemRepeatFinder_annotation.region",
                 "mm9_tandemRepeat",
                 [],
                 [],
                 "max",
                 None,
                 True)
    dm.deriveNewDataset("mm9.21.Tandem_Repeat.tandemRepeatFinder_annotation_downsampledTo500k.region",
                 "mm9_tandemRepeat",
                 [],
                 [],
                 "max",
                 None,
                 True,
                 True,
                 500000)
###### 22
def hg18_22():
    dm.regionDatasets.update(regionDatasetsRepeatsHG18)
    dm.deriveNewDataset("hg18.22.Repeat_DNA.repeatMasker_annotation_DNA_repeats.region",
                        "hg18_Repeat_DNA",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
#    dm.deriveNewDataset("hg18.22.Repeat_DNA.repeatMasker_annotation_DNA_repeats_downsampledTo500k.region",
#                        "hg18_Repeat_DNA",
#                        [],
#                        None,
#                        None,
#                        True,
#                        True,
#                        500000)
def mm9_22():
    dm.regionDatasets.update(regionDatasetsRepeatsMM9)
    dm.deriveNewDataset("mm9.22.Repeat_DNA.repeatMasker_annotation_DNA_repeats.region",
                        "mm9_Repeat_DNA",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
#    dm.deriveNewDataset("mm9.22.Repeat_DNA.repeatMasker_annotation_DNA_repeats_downsampledTo500k.region",
#                        "mm9_Repeat_DNA",
#                        [],
#                        None,
#                        None,
#                        True,
#                        True,
#                        500000)
######## 23
def hg18_23():
    dm.regionDatasets.update(regionDatasetsRepeatsHG18)
    dm.deriveNewDataset("hg18.23.Repeat_LINE.repeatMasker_annotation_long_interspersed_nucleotide_elements.region",
                        "hg18_Repeat_LINE",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
    dm.deriveNewDataset("hg18.23.Repeat_LINE.repeatMasker_annotation_long_interspersed_nucleotide_elements_downsampledTo500k.region",
                        "hg18_Repeat_LINE",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True,
                        500000)

def mm9_23():
    dm.regionDatasets.update(regionDatasetsRepeatsMM9)
    dm.deriveNewDataset("mm9.23.Repeat_LINE.repeatMasker_annotation_long_interspersed_nucleotide_elements.region",
                        "mm9_Repeat_LINE",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
    dm.deriveNewDataset("mm9.23.Repeat_LINE.repeatMasker_annotation_long_interspersed_nucleotide_elements_downsampledTo500k.region",
                        "mm9_Repeat_LINE",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True,
                        500000)
    
    
######## 24
def hg18_24():
    dm.regionDatasets.update(regionDatasetsRepeatsHG18)
    dm.deriveNewDataset("hg18.24.Repeat_LowComplex.repeatMasker_annotation_low_complexity_repeats.region",
                        "hg18_Repeat_LowComplex",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
#    dm.deriveNewDataset("hg18.24.Repeat_LowComplex.repeatMasker_annotation_low_complexity_repeats_downsampledTo500k.region",
#                        "hg18_Repeat_LowComplex",
#                        [],
#                        None,
#                        None,
#                        True,
#                        True,
#                        500000)
def mm9_24():
    dm.regionDatasets.update(regionDatasetsRepeatsMM9)
    dm.deriveNewDataset("mm9.24.Repeat_LowComplex.repeatMasker_annotation_low_complexity_repeats.region",
                        "mm9_Repeat_LowComplex",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
#    dm.deriveNewDataset("mm9.24.Repeat_LowComplex.repeatMasker_annotation_low_complexity_repeats_downsampledTo500k.region",
#                        "mm9_Repeat_LowComplex",
#                        [],
#                        None,
#                        None,
#                        True,
#                        True,
#                        500000)
######## 25
def hg18_25():
    dm.regionDatasets.update(regionDatasetsRepeatsHG18)
    dm.deriveNewDataset("hg18.25.Repeat_LTR.repeatMasker_annotation_long_terminal_repeats.region",
                        "hg18_Repeat_LTR",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
    dm.deriveNewDataset("hg18.25.Repeat_LTR.repeatMasker_annotation_long_terminal_repeats_downsampledTo500k.region",
                        "hg18_Repeat_LTR",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True,
                        500000)
def mm9_25():
    dm.regionDatasets.update(regionDatasetsRepeatsMM9)
    dm.deriveNewDataset("mm9.25.Repeat_LTR.repeatMasker_annotation_long_terminal_repeats.region",
                        "mm9_Repeat_LTR",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
    dm.deriveNewDataset("mm9.25.Repeat_LTR.repeatMasker_annotation_long_terminal_repeats_downsampledTo500k.region",
                        "mm9_Repeat_LTR",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True,
                        500000)
    
######## 26
def hg18_26():
    dm.regionDatasets.update(regionDatasetsRepeatsHG18)
    dm.deriveNewDataset("hg18.26.Repeat_Simple.repeatMasker_annotation_simple_repeats.region",
                        "hg18_Repeat_Simple",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
#    dm.deriveNewDataset("hg18.26.Repeat_Simple.repeatMasker_annotation_simple_repeats_downsampledTo500k.region",
#                        "hg18_Repeat_Simple",
#                        [],
#                        None,
#                        None,
#                        True,
#                        True,
#                        500000)
def mm9_26():
    dm.regionDatasets.update(regionDatasetsRepeatsMM9)
    dm.deriveNewDataset("mm9.26.Repeat_Simple.repeatMasker_annotation_simple_repeats.region",
                        "mm9_Repeat_Simple",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
    dm.deriveNewDataset("mm9.26.Repeat_Simple.repeatMasker_annotation_simple_repeats_downsampledTo500k.region",
                        "mm9_Repeat_Simple",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True,
                        500000)
    
######## 27
def hg18_27():
    dm.regionDatasets.update(regionDatasetsRepeatsHG18)
    dm.deriveNewDataset("hg18.27.Repeat_SINE.repeatMasker_annotation_short_interspersed_nucleotide_elements.region",
                        "hg18_Repeat_SINE",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
    dm.deriveNewDataset("hg18.27.Repeat_SINE.repeatMasker_annotation_short_interspersed_nucleotide_elements_downsampledTo500k.region",
                        "hg18_Repeat_SINE",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True,
                        500000)
def mm9_27():
    dm.regionDatasets.update(regionDatasetsRepeatsMM9)
    dm.deriveNewDataset("mm9.27.Repeat_SINE.repeatMasker_annotation_short_interspersed_nucleotide_elements.region",
                        "mm9_Repeat_SINE",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True)
    dm.deriveNewDataset("mm9.27.Repeat_SINE.repeatMasker_annotation_short_interspersed_nucleotide_elements_downsampledTo500k.region",
                        "mm9_Repeat_SINE",
                        [],
                        [],
                        None,
                        None,
                        True,
                        True,
                        500000)
#===============================================================================
# Other datasets
#===============================================================================
def CancerGenePromoterSufficientMethylationOverlappingWithBFCGI():
    cancerDataset = {
            "cancerPromoters_withMethylation":defaultFolder+"mm9.19.CancerGene_Promoter.Promoter_region_ensemblGenesMinus10000ToPlus2000AroundTSS_cancerGeneCensus.region_withMathylation.txt",
            }
    dm.regionDatasets.update(cancerDataset)
    #mm9_4()
    mm9_5()
    dm.deriveNewDataset("mm9.cancerPRomoters_BFCGI",
                        "cancerPromoters_withMethylation",
                        [],
                        #["mm9_CGI_CGIHunter_GG"],
                        ["mm9.5.BonaFide_CGI.cgiHunter_oe0.6_gc50_len700.region"],
                        None,
                        None,
                        True,
                        True)
def CancerGenePromoterSufficientMethylationOverlappingWithCGI():
    cancerDataset = {
            "cancerPromoters_withMethylation":defaultFolder+"mm9.19.CancerGene_Promoter.Promoter_region_ensemblGenesMinus10000ToPlus2000AroundTSS_cancerGeneCensus.region_withMathylation.txt",
            }
    dm.regionDatasets.update(cancerDataset)
    mm9_4()
    
    dm.deriveNewDataset("mm9.cancerPRomoters_CGI",
                        "cancerPromoters_withMethylation",
                        [],                        
                        ["mm9.4.CpG_Island.cgiHunter_oe0.6_gc50_len200.region"],
                        None,
                        None,
                        True,
                        True)
    
    
#===============================================================================
# mm9 datasets
#===============================================================================
#mm9Methods = [
#              "mm9_1()","mm9_2()","mm9_3()","mm9_4()","mm9_5()","mm9_7()","mm9_6()",
#              "mm9_8()","mm9_9()","mm9_10()","mm9_11()",
#              "mm9_12()","mm9_13()",
#              "mm9_14()","mm9_15()","mm9_16()","mm9_17()","mm9_18()",
#              "mm9_19()","mm9_20()",
#              "mm9_21()","mm9_22()","mm9_23()","mm9_24()","mm9_25()","mm9_26()","mm9_27()"
#              ]
#for method in mm9Methods:
#    eval(method) 
#
#
##===============================================================================
## hg18 datasets
##===============================================================================
#hg18Methods = [
#              "hg18_1()","hg18_2()","hg18_3()","hg18_4()","hg18_5()","hg18_7()","hg18_6()",
#              "hg18_8()","hg18_9()","hg18_10()","hg18_11()",
##              "hg18_12()",
#              "hg18_13()","hg18_14()","hg18_15()","hg18_16()","hg18_17()","hg18_18()",
#              "hg18_19()","hg18_20()",
#              "hg18_21()","hg18_22()","hg18_23()","hg18_24()","hg18_25()","hg18_26()","hg18_27()"
#              ]
#for method in hg18Methods:
#    eval(method) 

#testMethods = ["hg18_2()","hg18_5()","hg18_7()","hg18_6()",]
#for method in testMethods:
#    eval(method) 

#hg18_2()
#hg18_12_new()

CancerGenePromoterSufficientMethylationOverlappingWithBFCGI()
CancerGenePromoterSufficientMethylationOverlappingWithCGI()
