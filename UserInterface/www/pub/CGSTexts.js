
function readableOverlaps(regionDescription,overlapType){
	return "The region overlaps with "+regionDescription+overlapType;
}
function readableMethRatio(scoreDescription,tissue,scoreIndex,feature){
	var featureParts = feature.split("--");
	if (featureParts.length == 2){
		var featurePartsParts1 = featureParts[0].split(":");
		var featurePartsParts2 = featureParts[1].split(":");
		return "The "+scoreDescription+" methylation ratio in "+tissue+" is between "+(parseInt(featurePartsParts1[scoreIndex],10)+1)/100+" and "+(parseInt(featurePartsParts2[scoreIndex],10)+1)/100;
	}else if (featureParts.length == 1){
		var featurePartsParts = featureParts[0].split(":");
		return "The "+scoreDescription+" methylation ratio in "+tissue+" is "+(parseInt(featurePartsParts[scoreIndex],10)+1)/100;
	}
}

function readableOverlapRatio(regionDescription,scoreIndex,feature){
	var featureParts = feature.split("--");
	if (featureParts.length == 2){
		var featurePartsParts1 = featureParts[0].split(":");
		var featurePartsParts2 = featureParts[1].split(":");
		return "Between "+(parseInt(featurePartsParts1[scoreIndex],10)+1)+"% and "+(parseInt(featurePartsParts2[scoreIndex],10)+1)+"% of the region overlap with "+regionDescription;
	}else if (featureParts.length == 1){
		var featurePartsParts = featureParts[0].split(":");
		return (parseInt(featurePartsParts[scoreIndex],10)+1)+"% of the region overlap with "+regionDescription;
	}
}
function readableNOTOverlaps(regionDescription,overlapType){
	return "The region DOES NOT overlap with "+regionDescription+overlapType;
}
function readableDistanceTo(regionDescription,direction,indexOfD,feature,numberOfDigits,base){
	var featureParts = feature.split("--");
	if (featureParts.length == 2){
		var featurePartsParts1 = featureParts[0].split(":");
		var featurePartsParts2 = featureParts[1].split(":");
		return "The minimum distance to "+regionDescription+" "+direction+" is between "+convertRangeToNumber((parseInt(featurePartsParts1[indexOfD],10)),numberOfDigits,base)+" and "+convertRangeToNumber((parseInt(featurePartsParts2[indexOfD],10)+1),numberOfDigits,base)+" bp";
	}else if (featureParts.length == 1){
		var featurePartsParts = featureParts[0].split(":");
		return "The minimum distance to "+regionDescription+" "+direction+" is between "+convertRangeToNumber((parseInt(featurePartsParts[indexOfD],10)),numberOfDigits,base)+" and "+convertRangeToNumber((parseInt(featurePartsParts[indexOfD],10)+1),numberOfDigits,base)+" bp";
	}
}

var featureGroupDescription= {
		"chmm": "Chromatin state segmentation.",
		"location": "Regions localization.",
		"hg19tfbs": "Transcription Factor Binding Sites.",
		"hg19summary": "Summary of the selected data.",
		"hg19methylation": "DNA methylation (ENCODE).",
		"hg19histones": "Histone modifications."
}

var featureGroupNames = {
		  "hg18_dna_sequence":"DNA sequence",
		  "hg19_dna_sequence":"DNA sequence",
		  "mm9_dna_sequence":"DNA sequence",
		  "eC":"C + G",
		  "eA":"A + T",
		  "eTG":"TG + CA",
		  "repeats":"Repeat elements",
		  "hg18_repeat_masker":"Repeat elements",
		  "hg19_repeat_masker":"Repeat elements",
		  "hg18_ucsc_cpg_islands":"CpG islands (specific)",
		  "hg19_ucsc_cpg_islands":"CpG islands (specific)",
		  "DNaseI":"DNaseI hypersensitive sites (ENCODE)",
		  "hg18_PutativeenhancersErnstetal":"Strong enhancer candidates",
		  "hg19_PutativeenhancersErnstetal":"Strong enhancer candidates",
		  "mm9DNaseI":"DNaseI hypersensitive sites (ENCODE)",
		  "hg18_uw_DNaseI":"DNaseI hypersensitive sites (ENCODE)",
		  "hg19_uw_DNaseI":"DNaseI hypersensitive sites (ENCODE)",
		  "hg18_ensembl_gene_exons":"Gene exons",
		  "hg19_ensembl_gene_exons":"Gene exons",
		  "hg18_ensembl_gene_genes":"Genes",
		  "hg19_ensembl_gene_genes":"Genes",
		  "hg18_ensembl_gene_introns":"Gene introns",
		  "hg19_ensembl_gene_introns":"Gene introns",
		  "hg18_conservation":"Conservation",
		  "hg19_conservation":"Conservation",
		  "hg18_cgihunter_CpG_Islands":"CpG islands (sensitive)",
		  "hg19_cgihunter_CpG_Islands":"CpG islands (sensitive)",
		  "hg18_ensembl_gene_promoters_centered":"Gene promoters (-1kb to 1kb)",
		  "hg19_ensembl_gene_promoters_centered":"Gene promoters (-1kb to 1kb)",
		  "hg18_ensembl_gene_promoters_region":" Gene promoters (-10kb to 2kb)",
		  "hg19_ensembl_gene_promoters_region":" Gene promoters (-10kb to 2kb)",
		  "hg18_ensembl_gene_promoters":" Gene promoters (-5kb to 1kb)",
		  "hg19_ensembl_gene_promoters":" Gene promoters (-5kb to 1kb)",
		  "hg18_ensembl_gene_TSS":" Gene transcription start sites",
		  "hg19_ensembl_gene_TSS":" Gene transcription start sites",
		  "location":"Region location",
		  "mm9summary":"Summary",
		  "hg18summary":"Summary",
		  "hg19summary":"Summary",
		  "mm9tfbs":"Transcription factor binding sites (ENCODE)",
		  "hg18tfbs":"Transcription factor binding sites (ENCODE)",
		  "hg19tfbs":"Transcription factor binding sites (ENCODE)",
		  "generelated":"Genes and annotations",
		  "promoters":"Gene promoters",
		  "histones":"Histone modifications (ENCODE)",
		  "mm9histones":"Histone modifications (ENCODE)",
		  "hg19histones":"Histone modifications (ENCODE)",
		  "distanceTo":"Distance to nearest",
		  "methylation":"DNA methylation (ROADMAP)",
		  "mm9methylation":"DNA methylation (ROADMAP)",
		  "hg19methylation":"DNA methylation (ENCODE)",
		  "chmm":"Chromatin state segmentation",
		  "chmm01aprom":"Active promoters (1)",
		  "chmm02wprom":"Weak promoters (2)",
		  "chmm03pprom":"Poised promoters (3)",
		  "chmm04strenh":"Strong enhancers (4)",
		  "chmm05strenh":"Strong enhancers (5)",
		  "chmm06wenh":"Weak enhancers (6)",
		  "chmm07wenh":"Weak enhancers (7)",
		  "chmm08ins":"Insulators (8)",
		  "chmm09trtr":"Transcriptional transition (9)",
		  "chmm10trel":"Transcriptional elongation (10)",
		  "chmm11wtrx":"Weak transcribed (11)",
		  "chmm12prepr":"Polycomb repressed (12)",
		  "chmm13hetr":"Heterochromatin (low signal) (13)",
		  "chmm14rcnv":"Repetitive/CNV (14)",
		  "chmm15rcnv":"Repetitive/CNV (15)",
		  "User":"User annotations"
};

var overlapLabels = {"Eoverlaps:repeats:any":"Any repeats","Eoverlaps:repeats:DNA":"DNA","Eoverlaps:repeats:snRNA":"snRNA","Eoverlaps:repeats:Low_complexity":"Low complexity","Eoverlaps:repeats:LINE":"LINE","Eoverlaps:repeats:SINE":"SINE","Eoverlaps:repeats:Simple_repeat":"Simple repeats","Eoverlaps:repeats:srpRNA":"srpRNA","Eoverlaps:repeats:scRNA":"scRNA","Eoverlaps:repeats:LTR":"LTR","Eoverlaps:repeats:RC":"RC","Eoverlaps:repeats:rRNA":"rRNA","Eoverlaps:repeats:RNA":"RNA","Eoverlaps:repeats:tRNA":"tRNA","Eoverlaps:repeats:Satellite":"Satellite","Eoverlaps:repeats:Other":"Other","Eoverlaps:repeats:Unknown":"Unknown",
					"Eoverlaps:cons":"Conserved regions",
				    "Eoverlaps:genes":"Genes",
					  "Eoverlaps:exons":"Exons",
					  "Eoverlaps:introns":"Introns",
					  "Eoverlaps:promoters_def":"Gene promoters (-5kb to 1kb)",
					  "Eoverlaps:promoters_cen":"Gene promoters (-1kb to 1kb)",
					  "Eoverlaps:promoters_reg":"Gene promoters (-10kb to 2kb)",
					  "Eoverlaps:promoters_TSS":"Gene transcription start sites",
					  "Eoverlaps:ucscCGI":"CpG islands (specific)",
					  "Eoverlaps:DNaseI:any":"DNaseI sites (any)",
					  "Eoverlaps:DNaseI:GM12878":"DNaseI sites (GM12878)",
					  "Eoverlaps:DNaseI:H1hESC":"DNaseI sites (H1-hESC)",
					  "Eoverlaps:DNaseI:HepG2":"DNaseI sites (HepG2)",
					  "Eoverlaps:DNaseI:NHLF":"DNaseI sites (NHLF)",
					  "Eoverlaps:DNaseI:HUVEC":"DNaseI sites (HUVEC)",
					  "Eoverlaps:DNaseI:NHEK":"DNaseI sites (NHEK)",
					  "Eoverlaps:DNaseI:K562":"DNaseI sites (K562)",
					  "Eoverlaps:DNaseI:HeLaS3":"DNaseI sites (Helas3)",
					  "Eoverlaps:DNaseI:HMEC":"DNaseI sites (HMEC)",
					  //"Eoverlaps:tfbs:CTCF:any":"CTCF binding sites (any)",
					  //"Eoverlaps:tfbs:Pol2:any":"Pol2 binding sites (any)",
					  "Eoverlaps:DNaseIa:any":"DNaseI sites (any)",
					  "Eoverlaps:LaminaB1:any":"Lamina sites (any)",
					  "Eoverlaps:LaminaB1:Astrocytes":"Lamina sites (astrocytes)",
					  "Eoverlaps:LaminaB1:MEF":"Lamina sites (embryonic fibroblasts)",
					  "Eoverlaps:LaminaB1:ESC":"Lamina sites (embryonic stem cells)",
					  "Eoverlaps:LaminaB1:NPC":"Lamina sites (neural progenitor cells)",
					  "Eoverlaps:hg18LaminaB1":"Lamina sites (any)",
					  "Eoverlaps:hg19LaminaB1":"Lamina sites (any)",
					  "Eoverlaps:cgihunterCGI":"CGIHunter CpG islands",
					  "Eoverlaps:enhancers":"Enhancers"
		};


var featureGroupCategories = { }
var overlapMarks = {}

function processHistMark(mark) {
	s = mark.split("_", 2);
	if (s.length > 1) {
		if (s[1] == "emb") {
			s[1] = "embryonic";
		}
		if (s[1] == "24wks") {
			s[1] = "24 weeks";
		}
		return s[0] + " - " + s[1];
	} else {
		return mark;
	}
}

var bhist = {
	"H3K4me1":['GM12878', 'H1hESC', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','HSMMtube','Osteobl','NHA','Bmarrow','Cbellum','Cortex','Heart','Kidney','Liver','Lung','Mef','Spleen','Bmdm', 'Olfact', 'Plac', 'Smint',  'Testis', 'Thymus', 'Wbrain', 'Bat_24wks', 'Esb4_emb', 'Heart_emb', 'Limb_emb', 'Liver_emb', 'Mel_immortal', 'any'],
	"H3K4me2":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','HSMMtube','Osteobl','NHDFAd','HelaS3','any'],
	"H3K4me3":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','HSMMtube', 'NHA','NHDFAd','HelaS3','Bmarrow','Cbellum','Ch12','Cortex','Heart','Kidney','Liver','Lung','Mef','Mel','Spleen', 'Bmdm', 'Olfact', 'Plac', 'Smint', 'Spleen', 'Testis', 'Thymus', 'Bat_24wks', 'Esb4_emb', 'Heart_emb', 'Limb_emb', 'Liver_emb', 'WBrain_emb', 'mel_immortal', 'any'],
	"H3K9ac": ['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','HSMMtube','NHDFAd','HelaS3', 'Heart', 'Liver', 'Mel_immortal', 'any'],
	"H3K9me1":['HUVEC', 'K562', 'HMEC', 'NHEK','any'],
	"H3K27ac":['GM12878', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','H1hESC','HSMMtube','NHDFAd','HelaS3','NHA','Osteobl','Bmdm', 'Bmarrow', 'Cbellum', 'Cortex', 'Heart', 'Kidney', 'Liver', 'Mef', 'Olfact', 'Plac', 'Smint', 'Spleen', 'Testis', 'Thymus','Bat_24wks', 'Esb4_emb', 'Heart_emb', 'Limb_emb', 'Liver_emb', 'Wbrain_emb', 'Mel_immortal', 'any'],
	"H3K27me3":['GM12878', 'H1hESC', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','HelaS3','HepG2','NHA','NHDFAd','Heart', 'Liver', 'any'],
	"H4K20me1":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','HSMMtube','HelaS3','any'],
	"H3K36me3":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','HSMMtube','HelaS3','NHA','Osteobl','NHDFAd','Heart', 'Liver', 'Mel_immortal', 'any'],
	"H2AZ":['GM12878', 'HSMM', 'HMEC', 'HSMMtube', 'HepG2', 'K562', 'Osteobl', 'any'],
	"H3K9me3":['GM12878', 'HSMM', 'K562', 'Osteobl','HMEC', 'any'],
	"H3K79me2":['GM12878', 'HSMM', 'HSMMtube', 'HelaS3',  'HepG2', 'K562','HMEC', 'Heart', 'Liver', 'Mel_immortal', 'any']};

$.each(bhist,function(b,tissues){
	$.each(tissues,function(index,t){
		if (t == "any"){
			overlapLabels["Eoverlaps:bhist:"+b+":"+t] = b+" (any tissue)";
		}else{
			overlapLabels["Eoverlaps:bhist:"+b+":"+t] = b+" ("+processHistMark(t)+")";
		}
	})
})
var tfbs = {"SMC3":["CH12", "MEL","any"],
//"Rad21":["CH12", "MEL","any"],
//"Pol2":["CH12", "MEL","any"],
"JunD":["CH12", "MEL","any"],
//"E2F4":["CH12", "MEL","any"],
"USF2":["CH12", "MEL","any"],
"TBP":["CH12", "MEL","any"],
"P300":["MEL","GM12878","H1hESC","HepG2","any"],
//"NELFe":["CH12", "MEL","any"],
"Mxi1":["CH12", "MEL","any"],
//"Max":["CH12", "MEL","any"],
"MafK":["CH12", "MEL","any"],
//"GATA1":["MEL","any"],
"CTCF":["CH12", "MEL", 'C2C12', 'GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','HSMMtube','HelaS3','NHA','NHDFAd','Osteobl', "any"],
"c_Myc":["CH12", "MEL","any"],
"c_Myb":["MEL","any"],
"c_Jun":["CH12","any"],
"CHD2":["CH12", "MEL","any"],
"Bhlhe40nb100":["CH12","any"],
"AP2alpha":["HeLaS3","any"],
"AP2gamma":["HeLaS3","any"],
"ATF3":["GM12878","K562","H1hESC","HepG2","any"],
"BDP1":["K562","HeLaS3","any"],
"BRF1":["K562","HeLaS3","any"],
"BRF2":["K562","HeLaS3","any"],
"cFos":["GM12878","K562","HeLaS3","any"],
"cJun":["GM12878","K562","HUVEC","any"],
"c_Jun":["CH12","any"],
"cMyc":["GM12878","K562","HeLaS3","any"],
"E2F1":["HeLaS3","any"],
"E2F4":["K562","HeLaS3","CH12", "MEL", "C2C12", "any"],
"E2F6":["K562","HeLaS3","any"],
"GATA1":["K562", "MEL", "any",],
"GATA2":["K562","any"],
"GTF2B":["K562","any"],
"junD":["GM12878","K562","H1hESC","HepG2","any"],
"Max":["GM12878", "K562", "HeLaS3", "HUVEC","CH12", "MEL","any"],
"NELFe":["K562", "CH12", "MEL","any"],
"NFE2":["K562","any"],
"NFKB":["GM12878","any"],
"Pol2":["GM12878", "K562", "HeLaS3", "HUVEC","CH12", "MEL","HepG2","H1hESC","C2C12", "any"],
"Pol2b":['HUVEC', 'K562', 'NHEK','HMEC','HelaS3','any'],
"Pol3":["GM12878","K562","any"],
"Rad21":["K562","CH12", "MEL","GM12878","H1hESC","HepG2","any"],
"RPC155":["K562","HeLaS3","any"],
"SETDB1":["K562","any"],
"SIRT6":["K562","any"],
"TFIIIC110":["K562","HeLaS3","any"],
"TR4":["GM12878", "K562", "HeLaS3", "HepG2","any"],
"XRCC4":["K562","any"],
"YY1":["GM12878","K562","any"],
"ZNF263":["K562","any"],
"ZNF274":["K562","any"],
"ZZZ3":["GM12878","any"],
"PU1":["GM12878","K562","any"],
"SP1":["GM12878","K562","H1hESC","HepG2","any"],
"SRF":["GM12878","K562","H1hESC","HepG2","C2C12", "any"],
"BATF":["GM12878","any"],
"BCL3":["GM12878","any"],
"EGR1":["GM12878","K562","H1hESC","any"],
"ETS1":["GM12878","K562","any"],
"GABP":["GM12878","K562","H1hESC","HeLaS3","any"],
"NRSF":["GM12878","K562","H1hESC","HeLaS3","HepG2", "C2C12", "any"],
"RXRA":["GM12878","H1hESC","HepG2","any"],
"SIX5":["GM12878","K562","H1hESC","any"],
"TAF1":["GM12878","K562","H1hESC","HeLaS3","HepG2","any"],
"USF1":["GM12878","K562","H1hESC","HepG2","C2C12", "any"],
"FOSL2":["HepG2","any"],
"MEF2A":["GM12878","K562","any"],
"TCF12":["GM12878","H1hESC","C2C12", "any"],
"BCL11A":["GM12878","H1hESC","any"],
"BCLAF1":["GM12878","K562","any"],
"POU2F2":["GM12878","any"],
"ZBTB33":["GM12878","K562","HepG2","any"],
"BHLHE40":["HepG2","any"],
"PAX5C19":["GM12878","any"],
"PAX5C20":["GM12878","any"],
"PBX3":["GM12878","any"],
"SIN3AK20":["K562","H1hESC","HepG2","any"],
"Bhlhe40nb100":["CH12", "any"],
"CEBPB": ["CH12", "any"],
"FOSL1": ["C2C12", "any"],
"MyoD": ["C2C12", "any"],
"Myogenin": ["C2C12", "any"],
"TCF3" : ["C2C12", "any"],
};
$.each(tfbs,function(b,tissues){
	$.each(tissues,function(index,t){
		if (t == "any"){
			overlapLabels["Eoverlaps:tfbs:"+b+":"+t] = b+" (any tissue)";
		}else{
			overlapLabels["Eoverlaps:tfbs:"+b+":"+t] = b+" ("+t+")";
		}
	})
})
var chmm = {"chmm01aprom":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm02wprom":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm03pprom":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm04strenh":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm05strenh":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm06wenh":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm07wenh":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm08ins":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm09trtr":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm10trel":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm11wtrx":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm12prepr":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm13hetr":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm14rcnv":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"chmm15rcnv":['GM12878', 'H1hESC', 'HepG2', 'HMEC', 'HSMM', 'HUVEC', 'K562', 'NHEK', 'NHLF','any'],
"DNaseIa":['Bcellcd19p', 'Bcellcd43n', 'Cerebellum', 'Cerebrum', 'Fat', 'Fibroblast', 'Kidney', 'Liver', 'Lung','Tnaive', 'Wholebrain', 'A20','any'],
"DNaseIi":['3134Riii', 'PatskiSpbl6','any'],
"DNaseIme0":['Escj7S129', 'Zhbtc4129ola','any'],
"DNaseIme14":['Brain', 'any']
		   };
$.each(chmm,function(b,tissues){
	$.each(tissues,function(index,t){
		var bText = getTextForFeatureGroup(b);
		if (t == "any"){
			overlapLabels["Eoverlaps:"+b+":"+t] = bText+" (any tissue)";
			//overlapLabels["Eoverlaps:"+b+":"+t] = "any tissue";
		}else{
			overlapLabels["Eoverlaps:"+b+":"+t] = bText+" ("+t+")";
			//overlapLabels["Eoverlaps:"+b+":"+t] = t;
		}
	})
})
var rrbsMethTissues = ["hES_H1_p38","hES_H9_p58","hFib_11_p8","hEB16d_H1_p38","fetal_heart","Fetal_kidney","Fetal_lung","Fetal_brain","Smooth_muscle","Skeletal_muscle","Stomach_mucosa","Neuron_H9_derived","NPC_H9_derived","Human_blood_CD34_mobilized_REMC","HMEC","HSMM","K562","HepG2","H1hESC","HeLaS3","GM12878","heart","brain","liver"];

for (var rrbsMethTissueIndex =0;rrbsMethTissueIndex< rrbsMethTissues.length;rrbsMethTissueIndex++){
	if (rrbsMethTissues[rrbsMethTissueIndex] != undefined){
		var rrbsMethTissue = rrbsMethTissues[rrbsMethTissueIndex];
		var newk = "Eoverlaps:rrbs:"+rrbsMethTissue+":unmeth";
		overlapLabels[newk] = "Unmethylated in "+rrbsMethTissue.replace(/_/g," ");
		newk = "Eoverlaps:rrbs:"+rrbsMethTissue+":meth";
		overlapLabels[newk] = "Methylated in "+rrbsMethTissue.replace(/_/g," ");
	}
}

for (var overlapLabel in overlapLabels){
	var newOverlapLabel = overlapLabel.replace("Eoverlaps:","Eoverlaps10p:");
	overlapLabels[newOverlapLabel] = overlapLabels[overlapLabel];
	newOverlapLabel = overlapLabel.replace("Eoverlaps:","Eoverlaps50p:");
	overlapLabels[newOverlapLabel] = overlapLabels[overlapLabel];
}


function getReadableFeatureText(feature){
	//alert("getReadableFeatureText "+ feature);
	if (feature.split("|").length > 1){
		var featureTexts = [];
		var featureParts = feature.split("|");
		for (var i = 0; i < featureParts.length;i++){
			featureTexts.push(getReadableFeatureText(featureParts[i]))
		}
		return featureTexts.join(" OR ");
	}else if (feature.startsWith("Echr:chr")){
		return "Chromosome "+feature.substr(8);
	}else if (feature.startsWith("Elength_magnitude:")){
		var featureParts = feature.split("--");
		if (featureParts.length == 2){
			return "Length of the region is between "+convertRangeToNumber(parseInt(featureParts[0].substr("Elength_magnitude:".length), 10),3,0)+" and "+convertRangeToNumber(1+parseInt(featureParts[1].substr("Elength_magnitude:".length), 10),3,0);
		}else if (featureParts.length == 1){
			return "Length of the region is between "+convertRangeToNumber(parseInt(featureParts[0].substr("Elength_magnitude:".length), 10),3,0)+" and "+convertRangeToNumber(1+parseInt(featureParts[0].substr("Elength_magnitude:".length), 10),3,0);
		}
	}else if (feature.startsWith("Ednaseq:")){
		//Ednaseq:AA:freq:0--Ednaseq:AA:freq:87
		// will need a separate case for the counts
		var featureParts = feature.split("--");
		if (featureParts.length == 2){
			var featurePartsParts1 = featureParts[0].split(":");
			var featurePartsParts2 = featureParts[1].split(":");
			return "The frequency of the "+getDNAsequencePatternText(featurePartsParts1[1])+" pattern is between "+(featurePartsParts1[3])/1000+" and "+featurePartsParts2[3]/1000;
		}else if (featureParts.length == 1){
			var featurePartsParts = featureParts[0].split(":");
			return "The frequency of the "+getDNAsequencePatternText(featurePartsParts[1])+" pattern is "+featurePartsParts[3]/1000;
		}
	}else if (feature.startsWith("Eoverlaps:repeats:")){
		return readableOverlaps(feature.substr("Eoverlaps:repeats:".length)+" repeats"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:repeats:")){
		return readableOverlaps(feature.substr("Eoverlaps10p:repeats:".length)+" repeats"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:repeats:")){
		return readableOverlaps(feature.substr("Eoverlaps50p:repeats:".length)+" repeats"," (50%)");
	}else if (feature.startsWith("-Eoverlaps:repeats:")){
		return readableNOTOverlaps(feature.substr("-Eoverlaps:repeats:".length)+" repeats"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:repeats:")){
		return readableNOTOverlaps(feature.substr("-Eoverlaps10p:repeats:".length)+" repeats"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:repeats:")){
		return readableNOTOverlaps(feature.substr("-Eoverlaps50p:repeats:".length)+" repeats"," (50%)");
	}else if (feature.startsWith("Eor:repeats:")){
		return readableOverlapRatio(feature.split("--")[0].split(":")[2]+" repeats",3,feature)
	}else if (feature.startsWith("Eoverlaps:DNaseI")){
		//feature.split(":")[2];
		return readableOverlaps("DNaseI hypersensitive sites in "+ feature.split(":")[2] +" tissue"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:DNaseI")){
		return readableOverlaps("DNaseI hypersensitive sites in "+ feature.split(":")[2] +" tissue"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:DNaseI")){
		return readableOverlaps("DNaseI hypersensitive sites in "+ feature.split(":")[2] +" tissue"," (50%)");
	}else if (feature.startsWith("Eor:DNaseI")){
		//or:DNaseI:Hepg2:42
		return readableOverlapRatio("DNaseI hypersensitive sites in "+feature.split("--")[0].split(":")[2]+" tissue",3,feature)
	}else if (feature.startsWith("-Eoverlaps:DNaseI")){
		return readableNOTOverlaps("DNaseI hypersensitive sites in "+ feature.split(":")[2] +" tissue"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:DNaseI")){
		return readableNOTOverlaps("DNaseI hypersensitive sites in "+ feature.split(":")[2] +" tissue"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:DNaseI")){
		return readableNOTOverlaps("DNaseI hypersensitive sites in "+ feature.split(":")[2] +" tissue"," (50%)");
		return readableNOTOverlaps("DNaseI hypersensitive sites in "+ feature.split(":")[2] +" tissue","(50%)");
	}else if (feature.startsWith("Emdd:DNaseI")){
		//mdd:DNaseI:17
		return readableDistanceTo("a DNaseI hypersensitive site","downstream",3,feature,2,0);
	}else if (feature.startsWith("Emud:DNaseI")){
		//mud:DNaseI:71
		return readableDistanceTo("a DNaseI hypersensitive site","upstream",3,feature,2,0);
	}else if (feature.startsWith("Emmd:DNaseI")){
		//mmd:DNaseI:71
		var featureParts = feature.split("--")[0].split(":");
		return readableDistanceTo("a "+featureParts[2]+" DNaseI hypersensitive site","",3,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:LaminaB1")){
		return readableOverlaps("Lamina associated domains in "+ feature.split(":")[2] +" tissue"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:LaminaB1")){
		return readableOverlaps("Lamina associated domains in "+ feature.split(":")[2] +" tissue"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:LaminaB1")){
		return readableOverlaps("Lamina associated domains in "+ feature.split(":")[2] +" tissue"," (50%)");
	}else if (feature.startsWith("Eor:LaminaB1")){
		//or:DNaseI:Hepg2:42
		return readableOverlapRatio("Lamina associated domains in "+feature.split("--")[0].split(":")[2]+" tissue",3,feature)
	}else if (feature.startsWith("-Eoverlaps:LaminaB1")){
		return readableNOTOverlaps("Lamina associated domains in "+ feature.split(":")[2] +" tissue"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:LaminaB1")){
		return readableNOTOverlaps("Lamina associated domains in "+ feature.split(":")[2] +" tissue"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:LaminaB1")){
		return readableNOTOverlaps("Lamina associated domains in "+ feature.split(":")[2] +" tissue"," (50%)");
	}else if (feature.startsWith("Emdd:LaminaB1")){
		//mdd:DNaseI:17
		return readableDistanceTo("a lamina associated domain","downstream",3,feature,2,0);
	}else if (feature.startsWith("Emud:LaminaB1")){
		//mud:DNaseI:71
		return readableDistanceTo("a lamina associated domain","upstream",3,feature,2,0);
	}else if (feature.startsWith("Emmd:LaminaB1")){
		//mmd:DNaseI:71
		var featureParts = feature.split("--")[0].split(":");
		return readableDistanceTo("a "+featureParts[2]+" lamina associated domain","",3,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:chmm")){
		var featureParts = feature.split("--")[0].split(":");
		return readableOverlaps(getTextForFeatureGroup(featureParts[1])+" in "+ featureParts[2] +" tissue"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:chmm")){
		var featureParts = feature.split("--")[0].split(":");
		return readableOverlaps(getTextForFeatureGroup(featureParts[1])+" in "+ featureParts[2] +" tissue"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:chmm")){
		var featureParts = feature.split("--")[0].split(":");
		return readableOverlaps(getTextForFeatureGroup(featureParts[1])+" in "+ featureParts[2] +" tissue"," (50%)");
	}else if (feature.startsWith("Eor:chmm")){
		var featureParts = feature.split("--")[0].split(":");
		return readableOverlapRatio(getTextForFeatureGroup(featureParts[1])+" in "+featureParts[2]+" tissue",3,feature)
	}else if (feature.startsWith("-Eoverlaps:chmm")){
		var featureParts = feature.split("--")[0].split(":");
		return readableNOTOverlaps(getTextForFeatureGroup(featureParts[1])+" in "+featureParts[2] +" tissue"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:chmm")){
		var featureParts = feature.split("--")[0].split(":");
		return readableNOTOverlaps(getTextForFeatureGroup(featureParts[1])+" in "+featureParts[2] +" tissue"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:chmm")){
		var featureParts = feature.split("--")[0].split(":");
		return readableNOTOverlaps(getTextForFeatureGroup(featureParts[1])+" in "+featureParts[2]+" tissue"," (50%)");
		return readableNOTOverlaps(getTextForFeatureGroup(featureParts[1])+" in "+featureParts[2]+" tissue","(50%)");
	}else if (feature.startsWith("Emmd:chmm")){
		//mmd:DNaseI:71
		var featureParts = feature.split("--")[0].split(":");
		return readableDistanceTo("a "+featureParts[2]+" "+getTextForFeatureGroup(featureParts[1])+" site","",3,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:cgihunterCGI")){
		return readableOverlaps("CGIHunter CpG islands"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:cgihunterCGI"," (10%)")){
		return readableOverlaps("CGIHunter CpG islands");
	}else if (feature.startsWith("Eoverlaps50p:cgihunterCGI")){
		return readableOverlaps("CGIHunter CpG islands"," (50%)");
	}else if (feature.startsWith("Eor:cgihunterCGI:")){
		//or:cgihunter_CpG_Islands:42
		return readableOverlapRatio("CGIHunter CpG islands",2,feature)
	}else if (feature.startsWith("-Eoverlaps:cgihunterCGI")){
		return readableNOTOverlaps("CGIHunter CpG islands"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:cgihunterCGI")){
		return readableNOTOverlaps("CGIHunter CpG islands"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:cgihunterCGI")){
		return readableNOTOverlaps("CGIHunter CpG islands"," (50%)");
	}else if (feature.startsWith("Emdd:cgihunterCGI:")){
		//ddm:cgihunter_CpG_Islands::17
		//alert("Readable distance mdd")
		return readableDistanceTo("a CGIHunter CGI","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:cgihunterCGI:")){
		//dum:cgihunter_CpG_Islands:71
		//alert("Readable distance mud")
		return readableDistanceTo("a CGIHunter CGI","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:cgihunterCGI:")){
		//alert("Readable distance mmd")
		return readableDistanceTo("a CGIHunter CGI","",2,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:hg18LaminaB1") || feature.startsWith("Eoverlaps:hg19LaminaB1")){
		return readableOverlaps("lamina-associated domains"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:hg18LaminaB1")  || feature.startsWith("Eoverlaps10p:hg19LaminaB1")){
		return readableOverlaps("lamina-associated domains"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:hg18LaminaB1") || feature.startsWith("Eoverlaps50p:hg19LaminaB1")){
		return readableOverlaps("lamina-associated domains"," (50%)");
	}else if (feature.startsWith("Eor:hg18LaminaB1:") || feature.startsWith("Eor:hg19LaminaB1:")){
		//or:cgihunter_CpG_Islands:42
		return readableOverlapRatio("lamina-associated domains",2,feature)
	}else if (feature.startsWith("-Eoverlaps:hg18LaminaB1") || feature.startsWith("-Eoverlaps:hg19LaminaB1")){
		return readableNOTOverlaps("lamina-associated domains"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:hg18LaminaB1") || feature.startsWith("-Eoverlaps10p:hg19LaminaB1")){
		return readableNOTOverlaps("lamina-associated domains "," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:hg18LaminaB1")  || feature.startsWith("-Eoverlaps50p:hg19LaminaB1")){
		return readableNOTOverlaps("lamina-associated domains"," (50%)");
	}else if (feature.startsWith("Emdd:hg18LaminaB1:") || feature.startsWith("Emdd:hg19LaminaB1:")){
		//ddm:cgihunter_CpG_Islands::17
		//alert("Readable distance mdd")
		return readableDistanceTo("a lamina-associated domain","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:hg18LaminaB1:") || feature.startsWith("Emud:hg19LaminaB1:")){
		//dum:cgihunter_CpG_Islands:71
		//alert("Readable distance mud")
		return readableDistanceTo("a lamina-associated domain","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:hg18LaminaB1:") || feature.startsWith("Emmd:hg19LaminaB1:")){
		//alert("Readable distance mmd")
		return readableDistanceTo("a lamina-associated domain","",2,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:ucscCGI")){
		return readableOverlaps("CpG islands"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:ucscCGI")){
		return readableOverlaps("CpG islands"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:ucscCGI")){
		return readableOverlaps("CpG islands"," (50%)");
	}else if (feature.startsWith("Eor:ucscCGI:")){
		return readableOverlapRatio("CpG islands",2,feature)
	}else if (feature.startsWith("-Eoverlaps:ucscCGI")){
		return readableNOTOverlaps("CpG islands"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:ucscCGI")){
		return readableNOTOverlaps("CpG islands"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:ucscCGI")){
		return readableNOTOverlaps("CpG islands"," (50%)");
	}else if (feature.startsWith("Emdd:ucscCGI:")){
		return readableDistanceTo("a UCSC CGI","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:ucscCGI:")){
		return readableDistanceTo("a UCSC CGI","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:ucscCGI:")){
		return readableDistanceTo("a UCSC CGI","",2,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:cons")){
		return readableOverlaps("conserved regions"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:cons")){
		return readableOverlaps("conserved regions"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:cons")){
		return readableOverlaps("conserved regions"," (50%)");
	}else if (feature.startsWith("Eor:cons:")){
		return readableOverlapRatio("conserved regions",2,feature)
	}else if (feature.startsWith("-Eoverlaps:cons")){
		return readableNOTOverlaps("conserved regions"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:cons")){
		return readableNOTOverlaps("conserved regions"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:cons")){
		return readableNOTOverlaps("conserved regions"," (50%)");
	}else if (feature.startsWith("Emdd:cons:")){
		return readableDistanceTo("conserved regions","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:cons:")){
		return readableDistanceTo("conserved regions","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:cons:")){
		return readableDistanceTo("conserved regions","",2,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:genes")){
		return readableOverlaps("genes"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:genes")){
		return readableOverlaps("genes"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:genes")){
		return readableOverlaps("genes"," (50%)");
	}else if (feature.startsWith("Eor:genes:")){
		return readableOverlapRatio("genes",2,feature)
	}else if (feature.startsWith("-Eoverlaps:genes")){
		return readableNOTOverlaps("genes"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:genes")){
		return readableNOTOverlaps("genes"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:genes")){
		return readableNOTOverlaps("genes"," (50%)");
	}else if (feature.startsWith("Emdd:genes:")){
		return readableDistanceTo("genes","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:genes:")){
		return readableDistanceTo("genes","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:genes:")){
		return readableDistanceTo("genes","",2,feature,2,0);
	}else if (feature == "Eoverlaps:promoters_def"){
		return readableOverlaps("gene promoters (-5kb->1kb)"," (1bp)");
	}else if (feature == "Eoverlaps10p:promoters_def"){
		return readableOverlaps("gene promoters (-5kb->1kb)"," (10%)");
	}else if (feature == "Eoverlaps50p:promoters_def"){
		return readableOverlaps("gene promoters (-5kb->1kb)"," (50%)");
	}else if (feature.startsWith("Eor:promoters_def:")){
		return readableOverlapRatio("gene promoters (-5kb->1kb)",2,feature)
	}else if (feature.startsWith("-Eoverlaps:promoters_def")){
		return readableNOTOverlaps("gene promoters (-5kb->1kb)"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:promoters_def")){
		return readableNOTOverlaps("gene promoters (-5kb->1kb)"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:promoters_def")){
		return readableNOTOverlaps("gene promoters (-5kb->1kb)"," (50%)");
	}else if (feature.startsWith("Emdd:promoters_def:")){
		return readableDistanceTo("gene promoters (-5kb->1kb)","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:promoters_def:")){
		return readableDistanceTo("gene promoters (-5kb->1kb)","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:promoters_def:")){
		return readableDistanceTo("gene promoters (-5kb->1kb)","",2,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:promoters_cen")){
		return readableOverlaps("gene promoters (-1kb->1kb)"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:promoters_cen")){
		return readableOverlaps("gene promoters (-1kb->1kb)"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:promoters_cen")){
		return readableOverlaps("gene promoters (-1kb->1kb)"," (50%)");
	}else if (feature.startsWith("Eor:promoters_cen:")){
		return readableOverlapRatio("gene promoters (-1kb->1kb)",2,feature)
	}else if (feature.startsWith("-Eoverlaps:promoters_cen")){
		return readableNOTOverlaps("gene promoters (-1kb->1kb)"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:promoters_cen")){
		return readableNOTOverlaps("gene promoters (-1kb->1kb)"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:promoters_cen")){
		return readableNOTOverlaps("gene promoters (-1kb->1kb)"," (50%)");
	}else if (feature.startsWith("Emdd:promoters_cen:")){
		return readableDistanceTo("gene promoters (-1kb->1kb)","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:promoters_cen:")){
		return readableDistanceTo("gene promoters (-1kb->1kb)","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:promoters_cen:")){
		return readableDistanceTo("gene promoters (-1kb->1kb)","",2,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:promoters_reg")){
		return readableOverlaps("gene promoters (-10kb->2kb)"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:promoters_reg")){
		return readableOverlaps("gene promoters (-10kb->2kb)"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:promoters_reg")){
		return readableOverlaps("gene promoters (-10kb->2kb)"," (50%)");
	}else if (feature.startsWith("Eor:promoters_reg:")){
		return readableOverlapRatio("gene promoters (-10kb->2kb)",2,feature)
	}else if (feature.startsWith("-Eoverlaps:promoters_reg")){
		return readableNOTOverlaps("gene promoters (-10kb->2kb)"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:promoters_reg")){
		return readableNOTOverlaps("gene promoters (-10kb->2kb)"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:promoters_reg")){
		return readableNOTOverlaps("gene promoters (-10kb->2kb)"," (50%)");
	}else if (feature.startsWith("Emdd:promoters_reg:")){
		return readableDistanceTo("gene promoters (-10kb->2kb)","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:promoters_reg:")){
		return readableDistanceTo("gene promoters (-10kb->2kb)","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:promoters_reg:")){
		return readableDistanceTo("gene promoters (-10kb->2kb)","",2,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:exons")){
		return readableOverlaps("gene exons"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:exons")){
		return readableOverlaps("gene exons"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:exons")){
		return readableOverlaps("gene exons"," (50%)");
	}else if (feature.startsWith("Eor:exons:")){
		return readableOverlapRatio("gene exons",2,feature)
	}else if (feature.startsWith("-Eoverlaps:exons")){
		return readableNOTOverlaps("gene exons"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:exons")){
		return readableNOTOverlaps("gene exons"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:exons")){
		return readableNOTOverlaps("gene exons"," (50%)");
	}else if (feature.startsWith("Emdd:exons:")){
		return readableDistanceTo("gene exons","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:exons:")){
		return readableDistanceTo("gene exons","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:exons:")){
		return readableDistanceTo("gene exons","",2,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:introns")){
		return readableOverlaps("gene introns"," (1bp)");
	}else if (feature.startsWith("Eor:introns:")){
		return readableOverlapRatio("gene introns",2,feature)
	}else if (feature.startsWith("-Eoverlaps:introns")){
		return readableNOTOverlaps("gene introns"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:introns")){
		return readableNOTOverlaps("gene introns"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:introns")){
		return readableNOTOverlaps("gene introns"," (50%)");
	}else if (feature.startsWith("Emdd:introns:")){
		return readableDistanceTo("gene introns","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:introns:")){
		return readableDistanceTo("gene introns","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:introns:")){
		return readableDistanceTo("gene introns","",2,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:promoters_TSS")){
		return readableOverlaps("gene TSS"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:promoters_TSS")){
		return readableOverlaps("gene TSS"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:promoters_TSS")){
		return readableOverlaps("gene TSS"," (50%)");
	}else if (feature.startsWith("Eor:promoters_TSS:")){
		return readableOverlapRatio("gene TSS",2,feature)
	}else if (feature.startsWith("-Eoverlaps:promoters_TSS")){
		return readableNOTOverlaps("gene TSS"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:promoters_TSS")){
		return readableNOTOverlaps("gene TSS"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:promoters_TSS")){
		return readableNOTOverlaps("gene TSS"," (50%)");
	}else if (feature.startsWith("Emdd:promoters_TSS:")){
		return readableDistanceTo("gene TSS","downstream",2,feature,2,0);
	}else if (feature.startsWith("Emud:promoters_TSS:")){
		return readableDistanceTo("gene TSS","upstream",2,feature,2,0);
	}else if (feature.startsWith("Emmd:promoters_TSS:")){
		return readableDistanceTo("gene TSS","",2,feature,2,0);
	}else if (feature.startsWith("Eoverlaps:bhist:")||feature.startsWith("Eoverlaps:tfbs:")){
		var featureParts = feature.split(":");
		return readableOverlaps(featureParts[2]+" sites in "+featureParts[3]+" tissue"," (1bp)");
	}else if (feature.startsWith("Eoverlaps10p:bhist:")||feature.startsWith("Eoverlaps10p:tfbs:")){
		var featureParts = feature.split(":");
		return readableOverlaps(featureParts[2]+" sites in "+featureParts[3]+" tissue"," (10%)"," (10%)");
	}else if (feature.startsWith("Eoverlaps50p:bhist:")||feature.startsWith("Eoverlaps50p:tfbs:")){
		var featureParts = feature.split(":");
		return readableOverlaps(featureParts[2]+" sites in "+featureParts[3]+" tissue"," (50%)");
	}else if (feature.startsWith("Eor:bhist:")||feature.startsWith("Eor:tfbs:")){
		var featureParts = feature.split("--")[0].split(":");
		return readableOverlapRatio(featureParts[2]+" sites in "+featureParts[3]+" tissue",4,feature)
	}else if (feature.startsWith("-Eoverlaps:bhist:")||feature.startsWith("-Eoverlaps:tfbs:")){
		var featureParts = feature.split(":");
		return readableNOTOverlaps(featureParts[2]+" sites in "+featureParts[3]+" tissue"," (1bp)");
	}else if (feature.startsWith("-Eoverlaps10p:bhist:")||feature.startsWith("-Eoverlaps10p:tfbs:")){
		var featureParts = feature.split(":");
		return readableNOTOverlaps(featureParts[2]+" sites in "+featureParts[3]+" tissue"," (10%)");
	}else if (feature.startsWith("-Eoverlaps50p:bhist:")||feature.startsWith("-Eoverlaps50p:tfbs:")){
		var featureParts = feature.split(":");
		return readableNOTOverlaps(featureParts[2]+" sites in "+featureParts[3]+" tissue"," (50%)");
	}else if (feature.startsWith("Emdd:bhist:")||feature.startsWith("Emdd:tfbs:")){
		var featureParts = feature.split("--")[0].split(":");
		return readableDistanceTo(featureParts[2]+" sites","downstream",3,feature,2,0);
	}else if (feature.startsWith("Emud:bhist:")||feature.startsWith("Emud:tfbs:")){
		var featureParts = feature.split("--")[0].split(":");
		return readableDistanceTo(featureParts[2]+" sites","upstream",3,feature,2,0);
	}else if (feature.startsWith("Emmd:bhist:")||feature.startsWith("Emmd:tfbs:")){
		var featureParts = feature.split("--")[0].split(":");
		return readableDistanceTo(featureParts[2]+" sites","",3,feature,2,0);
	}else if (feature.startsWith("nihrm:")){
		var featureParts = feature.split("--")[0].split(":");
		var featureType = "";
		var indexOfD = 4;
		var numberOfDigits = 3;
		var base;
		if (featureParts[3] == "oddsratio"){
			featureType = "odds ratio";
			base = 5;
		}else if (featureParts[3] == "oddsdif"){
			featureType = "odds difference";
			base = 9;
		}else{
			return feature
		}
		var featureParts = feature.split("--");
		if (featureParts.length == 2){
			var featurePartsParts1 = featureParts[0].split(":");
			var featurePartsParts2 = featureParts[1].split(":");
			return "The odds ratio is between "+convertRangeToNumber((parseInt(featurePartsParts1[indexOfD],10)),numberOfDigits,base)+" and "+convertRangeToNumber((parseInt(featurePartsParts2[indexOfD],10)+1),numberOfDigits,base)+"";
		}else if (featureParts.length == 1){
			var featurePartsParts = featureParts[0].split(":");
			return "The odds ratio is between"+convertRangeToNumber((parseInt(featurePartsParts[indexOfD],10)),numberOfDigits,base)+" and "+convertRangeToNumber((parseInt(featurePartsParts[indexOfD],10)+1),numberOfDigits,base)+" bp";
		}

	}else if (feature.startsWith("Eoverlaps:")){
		//The general overlaps
		var featureParts = feature.split(":")
		var dname = featureParts[featureParts.length-1];
		if (hasDatasetInfo(dname,"officialName")){
			dname = currentState["datasetInfo"][dname]["officialName"];
		}
		return "Overlapping with "+dname+" (1bp)";
	}else if (feature.startsWith("Eoverlaps10p:")){
		//The general overlaps
		var featureParts = feature.split(":")
		var dname = featureParts[featureParts.length-1];
		if (hasDatasetInfo(dname,"officialName")){
			dname = currentState["datasetInfo"][dname]["officialName"];
		}
		return "Overlapping with "+dname+" (10%)";
	}else if (feature.startsWith("Eoverlaps50p:")){
		//The general overlaps
		var featureParts = feature.split(":")
		var dname = featureParts[featureParts.length-1];
		if (hasDatasetInfo(dname,"officialName")){
			dname = currentState["datasetInfo"][dname]["officialName"];
		}
		return "Overlapping with "+dname+" (50%)";
	}else if (feature.startsWith("-Eoverlaps:")){
		//The general overlaps
		var featureParts = feature.split(":")
		var dname = featureParts[featureParts.length-1];
		if (hasDatasetInfo(dname,"officialName")){
			dname = currentState["datasetInfo"][dname]["officialName"];
		}
		return "Not overlapping with "+dname+" (1bp)";
	}else if (feature.startsWith("-Eoverlaps10p:")){
		//The general overlaps
		var featureParts = feature.split(":")
		var dname = featureParts[featureParts.length-1];
		if (hasDatasetInfo(dname,"officialName")){
			dname = currentState["datasetInfo"][dname]["officialName"];
		}
		return "Not overlapping with "+dname+" (10%)";
	}else if (feature.startsWith("-Eoverlaps50p:")){
		//The general overlaps
		var featureParts = feature.split(":")
		var dname = featureParts[featureParts.length-1];
		if (hasDatasetInfo(dname,"officialName")){
			dname = currentState["datasetInfo"][dname]["officialName"];
		}
		return "Not overlapping with "+dname+" (50%)";
	}else if (feature.startsWith("Emdd:")){
		var featureParts = feature.split(":")
		var dname = featureParts[1];
		if (hasDatasetInfo(dname,"officialName")){
			dname = currentState["datasetInfo"][dname]["officialName"];
		}
		return readableDistanceTo("a "+dname+" site","downstream",2,feature,2,0);

	}else if (feature.startsWith("Emud:")){
		var featureParts = feature.split(":")
		var dname = featureParts[1];
		if (hasDatasetInfo(dname,"officialName")){
			dname = currentState["datasetInfo"][dname]["officialName"];
		}
		return readableDistanceTo("a "+dname+" site","upstream",2,feature,2,0);

	}else if (feature.startsWith("Emmd:")){
		var featureParts = feature.split(":")
		var dname = featureParts[1];
		if (hasDatasetInfo(dname,"officialName")){
			dname = currentState["datasetInfo"][dname]["officialName"];
		}
		return readableDistanceTo("a "+dname+" site","",2,feature,2,0);

	}else if (feature.startsWith("Egn:")){
		return "Overlapping with gene " + feature.substring(4)
	}else if (feature.slice(0,12) == "[Egn:*%23gS:"){
		return "Overlapping with genes described by the symbol '" + feature.substring(12, feature.indexOf('%20')) + "'"
	}else if (feature.startsWith("gGO:")){
		return "Overlapping with genes annotated with " + feature.substring(4)
	}else if (feature.slice(0,14) == "[gGO:*%23gGOd:"){
		return "Overlapping with genes annotated with GO term containing the word '" + feature.substring(14, feature.indexOf('%20')) + "'"
	}else if (feature.startsWith("omimID:")){
		return "Overlapping with genes annotated with OMIM:" + feature.substring(7)
	}else if (feature.slice(0,18) == "[omimID:*%23omimD:"){
		return "Overlapping with genes annotated with OMIM containing the word '" + feature.substring(18, feature.indexOf('%20')) + "'"
	}else if (feature.startsWith("EmethR:rrbs:")){
		return readableMethRatio("average",feature.split("--")[0].split(":")[2],3,feature)
	}else if (feature.startsWith("EmethRmin:rrbs:")){
		return readableMethRatio("minimum",feature.split("--")[0].split(":")[2],3,feature)
	}else if (feature.startsWith("EmethRmax:rrbs:")){
		return readableMethRatio("maximum",feature.split("--")[0].split(":")[2],3,feature)
	}else if (feature.startsWith("EmethRstd:rrbs:")){
		return readableMethRatio("standard deviation of",feature.split("--")[0].split(":")[2],3,feature)
	}else if (feature.startsWith("Ersc:")){
		var featureParts = feature.split("--");
		if (featureParts.length == 2){
			return "The region score is between "+parseInt(featureParts[0].substr(5),10)+" and "+parseInt(featureParts[1].substr(5),10);
		}else if (featureParts.length == 1){
			return "The region score is "+parseInt(featureParts[0].substr(5),10);
		}
	}else if (feature.startsWith("Erst:")){
		return "Strand "+feature.substr(5)
	}else if (feature.startsWith("EmethCpG:rrbs:")){
		var featureParts = feature.split("--");
		var featurePartsParts0 = featureParts[0].split(":");
		if (featureParts.length == 2){
			var featurePartsParts1 = featureParts[1].split(":");
			return "The number of measured CpGs in "+featurePartsParts0[2]+" is between "+convertRatioToNumber(parseInt(featurePartsParts0[3], 10),0)+" and "+convertRatioToNumber(1+parseInt(featurePartsParts1[3], 10),0);
		}else if (featureParts.length == 1){
			return "The number of measured CpGs in "+featurePartsParts0[2]+" is between "+convertRatioToNumber(parseInt(featurePartsParts0[3], 10),0)+" and "+convertRatioToNumber(1+parseInt(featurePartsParts0[3], 10),0);
		}

	}else if (feature.startsWith("gGONG:")){
		var featureParts = feature.split("--");
		var featurePartsParts0 = featureParts[0].split(":");
		if (featureParts.length == 2){
			var featurePartsParts1 = featureParts[1].split(":");
			return "GO terms associated with between "+convertRangeToNumber(parseInt(featurePartsParts0[1], 10),3,0)+" and "+convertRangeToNumber(parseInt(featurePartsParts1[1], 10)+1,3,0)+" genes";
		}else if (featureParts.length == 1){
			return "GO terms associated with between "+convertRangeToNumber(parseInt(featurePartsParts0[1], 10),3,0)+" and "+convertRangeToNumber(parseInt(featurePartsParts0[1], 10)+1,3,0)+" genes";
		}
	}else{

		return feature;
	}
}
function getGroupOrderElem(groupName){
	var groupNamesOrder = {
					  "mm9summary":10,
					  "hg18summary":10,
					  "hg19summary":10,
					  "featureBox":15,
					  "mm9_dna_sequence":30,
					  "hg18_dna_sequence":30,
					  "hg19_dna_sequence":30,
					  "location":30,
					  "histones":40,
					  "mm9histones":40,
					  "hg19histones":40,
					    "H2AZ":110,
					  	"H3K4me1":111,
					  	"H3K4me2":112,
					  	"H3K4me3":113,
					  	"H3K9ac":120,
					  	"H3K9me1":121,
					  	"H3K9me3":122,
					  	"H3K27ac":130,
					  	"H3K27me3":133,
					  	"H3K36me3":143,
					  	"H3K79me2":150,
					  	"H4K20me1":160,
					  	"CTCF":180,
					  	"Pol2b":190,
					  "DNaseI":45,
					  "mm9DNaseI":45,
					  "hg18_uw_DNaseI":45,
					  "hg19_uw_DNaseI":45,
					  "methylation":50,
					  "mm9methylation":50,
					  "hg19methylation":50,

					  "chmm":58,
					  	  "chmm01aprom":101,
						  "chmm02wprom":102,
						  "chmm03pprom":103,
						  "chmm04strenh":104,
						  "chmm05strenh":105,
						  "chmm06wenh":106,
						  "chmm07wenh":107,
						  "chmm08ins":108,
						  "chmm09trtr":109,
						  "chmm10trel":110,
						  "chmm11wtrx":111,
						  "chmm12prepr":112,
						  "chmm13hetr":113,
						  "chmm14rcnv":114,
						  "chmm15rcnv":115,
					  "tfbs":59,
					  "mm9tfbs":59,
					  "hg18tfbs":59,
					  "hg19tfbs":59,
					  "mm9_ucsc_cpg_islands":60,
					  "hg18_ucsc_cpg_islands":60,
					  "hg19_ucsc_cpg_islands":60,
					  "mm9_cgihunter_CpG_Islands":65,
					  "hg18_cgihunter_CpG_Islands":65,
					  "hg19_cgihunter_CpG_Islands":65,
					  "mm9_lamin_b1":67,
					  "hg18_lamin_b1":67,
					  "hg19_lamin_b1":67,
					  "LaminaB1":67,
					  "mm9_conservation":68,
					  "hg18_conservation":68,
					  "hg19_conservation":68,
					  "hg18_PutativeenhancersErnstetal":69,
					  "hg19_PutativeenhancersErnstetal":69,
					  "mm9_repeat_masker":70,
					  "hg18_repeat_masker":70,
					  "hg19_repeat_masker":70,
					  "repeats":70,
					  "generelated":80,
					  	  "mm9_ensembl_gene_genes":45,
						  "hg18_ensembl_gene_genes":45,
						  "hg19_ensembl_gene_genes":45,
						  "promoters":50,
						  		"mm9_ensembl_gene_promoters":10,
						  		"hg18_ensembl_gene_promoters":10,
						  		"hg19_ensembl_gene_promoters":10,
						  		"mm9_ensembl_gene_promoters_centered":20,
						  		"hg18_ensembl_gene_promoters_centered":20,
						  		"hg19_ensembl_gene_promoters_centered":20,
						  		"mm9_ensembl_gene_promoters_region":30,
						  		"hg18_ensembl_gene_promoters_region":30,
						  		"hg19_ensembl_gene_promoters_region":30,
						  "mm9_ensembl_gene_TSS":60,
						  "hg18_ensembl_gene_TSS":60,
						  "hg19_ensembl_gene_TSS":60,
						  "mm9_ensembl_gene_exons":70,
						  "hg18_ensembl_gene_exons":70,
						  "hg19_ensembl_gene_exons":70,
						  "mm9_ensembl_gene_introns":98,
						  "hg18_ensembl_gene_introns":98,
						  "hg19_ensembl_gene_introns":98,
					  	  "OMIM:TERMS:":"090",
					  "User":99,
					  "distanceTo":98
	};
	var groupOrder;
	if (groupNamesOrder[groupName] !== undefined){
		groupOrder = groupNamesOrder[groupName];
	}else{
		if (groupName.startsWith("Emmd:")){
			groupOrder = "088";
		}else{
			groupOrder = "0"+groupName.length;
		}
	}
	return groupOrder;
}
function getForwardVisualizationID(currentVisualization,currentItem){
	//alert("getForwardingID")
	if (currentVisualization == ""){
		currentVisualization = settings["genome"]+"summary"
	}
	//alert("getForwardingID 1")
	if (getOverlapSummaryForGroup(currentVisualization) == ""){
		//There is no such visualization do nothing
		return ""
	}
	//alert("getForwardingID 2")
	if (currentVisualization == settings["genome"]+"summary"){
		//alert(currentItem)
		if (currentItem.startsWith("OVERLAP:bhist")){
			return "histones";
		}else if (currentItem.startsWith("OVERLAP:chmm")){
			return "chmm";
		}else if (currentItem.startsWith("OVERLAP:promoters_def") || currentItem.startsWith("OVERLAP:genes")){
			return "generelated";
		}else if (currentItem.startsWith("OVERLAP:repeats")){
			return "OVERLAP:repeats";
		}else if (currentItem.startsWith("OVERLAP:DNaseI")){
			return "OVERLAP:DNaseI";
		}else if (currentItem.startsWith("OVERLAP:ucscCGI")){
			return "OVERLAP:ucscCGI";
		}else if (currentItem.startsWith("OVERLAP:cons")){
			return "OVERLAP:cons";
		}
	}else if (currentVisualization == "histones"){
		var he = currentItem.split(":");
		he.pop()
		return he.join(":")
		//return currentItem;//.split(":")[2]
	}else if (currentVisualization == "chmm"){
		var he = currentItem.split(":");
		he.pop()
		return he.join(":")
		//return currentItem;//.split(":")[1]
	}else if (currentVisualization == "methylation"){
		return currentItem.split(":")[2]
	}else if (currentVisualization == "generelated"){
		return currentItem;
	}
	//alert("getForwardingID 3")

}
function getOverlapSummaryForGroup(groupName){

	var groupsummaryValues = {
		"hg18":{
			"hg18summary":"OVERLAP:bhist:H3K4me1:TISSUE,OVERLAP:bhist:H3K4me3:TISSUE,OVERLAP:bhist:H3K27me3:TISSUE,OVERLAP:bhist:H3K36me3:TISSUE,OVERLAP:DNaseI:TISSUE,OVERLAP:chmm04strenh:TISSUE,OVERLAP:chmm08ins:TISSUE,OVERLAP:ucscCGI,OVERLAP:cons,OVERLAP:repeats:any,OVERLAP:promoters_def,OVERLAP:genes",
			"repeats":"OVERLAP:repeats:any,OVERLAP:repeats:DNA,OVERLAP:repeats:snRNA,OVERLAP:repeats:Low_complexity,OVERLAP:repeats:LINE,OVERLAP:repeats:SINE,OVERLAP:repeats:Simple_repeat,OVERLAP:repeats:srpRNA,OVERLAP:repeats:scRNA,OVERLAP:repeats:LTR,OVERLAP:repeats:RC,OVERLAP:repeats:rRNA,OVERLAP:repeats:RNA,OVERLAP:repeats:tRNA,OVERLAP:repeats:Satellite,OVERLAP:repeats:Other,OVERLAP:repeats:Unknown",
			"hg18_repeat_masker":"OVERLAP:repeats:any,OVERLAP:repeats:DNA,OVERLAP:repeats:snRNA,OVERLAP:repeats:Low_complexity,OVERLAP:repeats:LINE,OVERLAP:repeats:SINE,OVERLAP:repeats:Simple_repeat,OVERLAP:repeats:srpRNA,OVERLAP:repeats:scRNA,OVERLAP:repeats:LTR,OVERLAP:repeats:RC,OVERLAP:repeats:rRNA,OVERLAP:repeats:RNA,OVERLAP:repeats:tRNA,OVERLAP:repeats:Satellite,OVERLAP:repeats:Other,OVERLAP:repeats:Unknown",
			"hg18_uw_DNaseI":"OVERLAP:DNaseI:any,OVERLAP:DNaseI:GM12878,OVERLAP:DNaseI:H1hESC,OVERLAP:DNaseI:HepG2,OVERLAP:DNaseI:NHLF,OVERLAP:DNaseI:HUVEC,OVERLAP:DNaseI:NHEK,OVERLAP:DNaseI:K562,OVERLAP:DNaseI:HeLaS3,OVERLAP:DNaseI:HMEC",
			"DNaseI":"OVERLAP:DNaseI:any,OVERLAP:DNaseI:GM12878,OVERLAP:DNaseI:H1hESC,OVERLAP:DNaseI:HepG2,OVERLAP:DNaseI:NHLF,OVERLAP:DNaseI:HUVEC,OVERLAP:DNaseI:NHEK,OVERLAP:DNaseI:K562,OVERLAP:DNaseI:HeLaS3,OVERLAP:DNaseI:HMEC",
			"generelated":	"OVERLAP:genes,OVERLAP:promoters_def,OVERLAP:promoters_cen,OVERLAP:promoters_reg,OVERLAP:exons,OVERLAP:promoters_TSS",
			"histones": "OVERLAP:bhist:CTCF:TISSUE,OVERLAP:bhist:H3K4me1:TISSUE,OVERLAP:bhist:H3K4me2:TISSUE,OVERLAP:bhist:H3K4me3:TISSUE,OVERLAP:bhist:H3K9ac:TISSUE,OVERLAP:bhist:H3K9me1:TISSUE,OVERLAP:bhist:H3K27ac:TISSUE,OVERLAP:bhist:H3K27me3:TISSUE,OVERLAP:bhist:H4K20me1:TISSUE,OVERLAP:bhist:H3K36me3:TISSUE,OVERLAP:bhist:Pol2b:TISSUE",
				"Pol2b":"OVERLAP:bhist:Pol2b:any,OVERLAP:bhist:Pol2b:HUVEC,OVERLAP:bhist:Pol2b:K562,OVERLAP:bhist:Pol2b:NHEK",
				"H4K20me1":	"OVERLAP:bhist:H4K20me1:any,OVERLAP:bhist:H4K20me1:GM12878,OVERLAP:bhist:H4K20me1:H1hESC,OVERLAP:bhist:H4K20me1:HepG2,OVERLAP:bhist:H4K20me1:HMEC,OVERLAP:bhist:H4K20me1:HSMM,OVERLAP:bhist:H4K20me1:HUVEC,OVERLAP:bhist:H4K20me1:K562,OVERLAP:bhist:H4K20me1:NHEK,OVERLAP:bhist:H4K20me1:NHLF",
				"H3K36me3":	"OVERLAP:bhist:H3K36me3:any,OVERLAP:bhist:H3K36me3:GM12878,OVERLAP:bhist:H3K36me3:H1hESC,OVERLAP:bhist:H3K36me3:HepG2,OVERLAP:bhist:H3K36me3:HMEC,OVERLAP:bhist:H3K36me3:HSMM,OVERLAP:bhist:H3K36me3:HUVEC,OVERLAP:bhist:H3K36me3:K562,OVERLAP:bhist:H3K36me3:NHEK,OVERLAP:bhist:H3K36me3:NHLF",
				"H3K27me3":	"OVERLAP:bhist:H3K27me3:any,OVERLAP:bhist:H3K27me3:GM12878,OVERLAP:bhist:H3K27me3:H1hESC,OVERLAP:bhist:H3K27me3:HMEC,OVERLAP:bhist:H3K27me3:HSMM,OVERLAP:bhist:H3K27me3:HUVEC,OVERLAP:bhist:H3K27me3:K562,OVERLAP:bhist:H3K27me3:NHEK,OVERLAP:bhist:H3K27me3:NHLF",
				"H3K27ac":	"OVERLAP:bhist:H3K27ac:any,OVERLAP:bhist:H3K27ac:GM12878,OVERLAP:bhist:H3K27ac:HepG2,OVERLAP:bhist:H3K27ac:HMEC,OVERLAP:bhist:H3K27ac:HSMM,OVERLAP:bhist:H3K27ac:HUVEC,OVERLAP:bhist:H3K27ac:K562,OVERLAP:bhist:H3K27ac:NHEK,OVERLAP:bhist:H3K27ac:NHLF",
				"H3K9me1":	"OVERLAP:bhist:H3K9me1:any,OVERLAP:bhist:H3K9me1:HUVEC,OVERLAP:bhist:H3K9me1:K562,OVERLAP:bhist:H3K9me1:NHEK",
				"H3K9ac":	"OVERLAP:bhist:H3K9ac:any,OVERLAP:bhist:H3K9ac:GM12878,OVERLAP:bhist:H3K9ac:H1hESC,OVERLAP:bhist:H3K9ac:HepG2,OVERLAP:bhist:H3K9ac:HMEC,OVERLAP:bhist:H3K9ac:HSMM,OVERLAP:bhist:H3K9ac:HUVEC,OVERLAP:bhist:H3K9ac:K562,OVERLAP:bhist:H3K9ac:NHEK,OVERLAP:bhist:H3K9ac:NHLF",
				"H3K4me3":	"OVERLAP:bhist:H3K4me3:any,OVERLAP:bhist:H3K4me3:GM12878,OVERLAP:bhist:H3K4me3:H1hESC,OVERLAP:bhist:H3K4me3:HepG2,OVERLAP:bhist:H3K4me3:HMEC,OVERLAP:bhist:H3K4me3:HSMM,OVERLAP:bhist:H3K4me3:HUVEC,OVERLAP:bhist:H3K4me3:K562,OVERLAP:bhist:H3K4me3:NHEK,OVERLAP:bhist:H3K4me3:NHLF",
				"H3K4me2":	"OVERLAP:bhist:H3K4me2:any,OVERLAP:bhist:H3K4me2:GM12878,OVERLAP:bhist:H3K4me2:H1hESC,OVERLAP:bhist:H3K4me2:HepG2,OVERLAP:bhist:H3K4me2:HMEC,OVERLAP:bhist:H3K4me2:HSMM,OVERLAP:bhist:H3K4me2:HUVEC,OVERLAP:bhist:H3K4me2:K562,OVERLAP:bhist:H3K4me2:NHEK,OVERLAP:bhist:H3K4me2:NHLF",
				"H3K4me1":	"OVERLAP:bhist:H3K4me1:any,OVERLAP:bhist:H3K4me1:GM12878,OVERLAP:bhist:H3K4me1:H1hESC,OVERLAP:bhist:H3K4me1:HMEC,OVERLAP:bhist:H3K4me1:HSMM,OVERLAP:bhist:H3K4me1:HUVEC,OVERLAP:bhist:H3K4me1:K562,OVERLAP:bhist:H3K4me1:NHEK,OVERLAP:bhist:H3K4me1:NHLF",
				"CTCF":	"OVERLAP:bhist:CTCF:any,OVERLAP:bhist:CTCF:GM12878,OVERLAP:bhist:CTCF:H1hESC,OVERLAP:bhist:CTCF:HepG2,OVERLAP:bhist:CTCF:HMEC,OVERLAP:bhist:CTCF:HSMM,OVERLAP:bhist:CTCF:HUVEC,OVERLAP:bhist:CTCF:K562,OVERLAP:bhist:CTCF:NHEK,OVERLAP:bhist:CTCF:NHLF",
				"H2AZ":"OVERLAP:bhist:H2AZ:any,OVERLAP:bhist:H2AZ:HSMM,OVERLAP:bhist:H2AZ:HSMMtube,OVERLAP:bhist:H2AZ:HepG2,OVERLAP:bhist:H2AZ:K562,OVERLAP:bhist:H2AZ:Osteobl,OVERLAP:bhist:H2AZ:GM12878",
				"H3K9me3":"OVERLAP:bhist:H3K9me3:any,OVERLAP:bhist:H3K9me3:HSMM,OVERLAP:bhist:H3K9me3:K562,OVERLAP:bhist:H3K9me3:Osteobl,OVERLAP:bhist:H3K9me3:GM12878",
				"H3K79me2":"OVERLAP:bhist:H3K79me2:any,OVERLAP:bhist:H3K79me2:HSMM,OVERLAP:bhist:H3K79me2:HSMMtube,OVERLAP:bhist:H3K79me2:HelaS3,OVERLAP:bhist:H3K79me2:HepG2,OVERLAP:bhist:H3K79me2:K562,OVERLAP:bhist:H3K79me2:GM12878",
				"hg18_broad_histones_Pol2b":"OVERLAP:bhist:Pol2b:any,OVERLAP:bhist:Pol2b:HUVEC,OVERLAP:bhist:Pol2b:K562,OVERLAP:bhist:Pol2b:NHEK",
				"hg18_broad_histones_H4K20me1":	"OVERLAP:bhist:H4K20me1:any,OVERLAP:bhist:H4K20me1:GM12878,OVERLAP:bhist:H4K20me1:H1hESC,OVERLAP:bhist:H4K20me1:HepG2,OVERLAP:bhist:H4K20me1:HMEC,OVERLAP:bhist:H4K20me1:HSMM,OVERLAP:bhist:H4K20me1:HUVEC,OVERLAP:bhist:H4K20me1:K562,OVERLAP:bhist:H4K20me1:NHEK,OVERLAP:bhist:H4K20me1:NHLF",
				"hg18_broad_histones_H3K36me3":	"OVERLAP:bhist:H3K36me3:any,OVERLAP:bhist:H3K36me3:GM12878,OVERLAP:bhist:H3K36me3:H1hESC,OVERLAP:bhist:H3K36me3:HepG2,OVERLAP:bhist:H3K36me3:HMEC,OVERLAP:bhist:H3K36me3:HSMM,OVERLAP:bhist:H3K36me3:HUVEC,OVERLAP:bhist:H3K36me3:K562,OVERLAP:bhist:H3K36me3:NHEK,OVERLAP:bhist:H3K36me3:NHLF",
				"hg18_broad_histones_H3K27me3":	"OVERLAP:bhist:H3K27me3:any,OVERLAP:bhist:H3K27me3:GM12878,OVERLAP:bhist:H3K27me3:H1hESC,OVERLAP:bhist:H3K27me3:HMEC,OVERLAP:bhist:H3K27me3:HSMM,OVERLAP:bhist:H3K27me3:HUVEC,OVERLAP:bhist:H3K27me3:K562,OVERLAP:bhist:H3K27me3:NHEK,OVERLAP:bhist:H3K27me3:NHLF",
				"hg18_broad_histones_H3K27ac":	"OVERLAP:bhist:H3K27ac:any,OVERLAP:bhist:H3K27ac:GM12878,OVERLAP:bhist:H3K27ac:HepG2,OVERLAP:bhist:H3K27ac:HMEC,OVERLAP:bhist:H3K27ac:HSMM,OVERLAP:bhist:H3K27ac:HUVEC,OVERLAP:bhist:H3K27ac:K562,OVERLAP:bhist:H3K27ac:NHEK,OVERLAP:bhist:H3K27ac:NHLF",
				"hg18_broad_histones_H3K9me1":	"OVERLAP:bhist:H3K9me1:any,OVERLAP:bhist:H3K9me1:HUVEC,OVERLAP:bhist:H3K9me1:K562,OVERLAP:bhist:H3K9me1:NHEK",
				"hg18_broad_histones_H3K9ac":	"OVERLAP:bhist:H3K9ac:any,OVERLAP:bhist:H3K9ac:GM12878,OVERLAP:bhist:H3K9ac:H1hESC,OVERLAP:bhist:H3K9ac:HepG2,OVERLAP:bhist:H3K9ac:HMEC,OVERLAP:bhist:H3K9ac:HSMM,OVERLAP:bhist:H3K9ac:HUVEC,OVERLAP:bhist:H3K9ac:K562,OVERLAP:bhist:H3K9ac:NHEK,OVERLAP:bhist:H3K9ac:NHLF",
				"hg18_broad_histones_H3K4me3":	"OVERLAP:bhist:H3K4me3:any,OVERLAP:bhist:H3K4me3:GM12878,OVERLAP:bhist:H3K4me3:H1hESC,OVERLAP:bhist:H3K4me3:HepG2,OVERLAP:bhist:H3K4me3:HMEC,OVERLAP:bhist:H3K4me3:HSMM,OVERLAP:bhist:H3K4me3:HUVEC,OVERLAP:bhist:H3K4me3:K562,OVERLAP:bhist:H3K4me3:NHEK,OVERLAP:bhist:H3K4me3:NHLF",
				"hg18_broad_histones_H3K4me2":	"OVERLAP:bhist:H3K4me2:any,OVERLAP:bhist:H3K4me2:GM12878,OVERLAP:bhist:H3K4me2:H1hESC,OVERLAP:bhist:H3K4me2:HepG2,OVERLAP:bhist:H3K4me2:HMEC,OVERLAP:bhist:H3K4me2:HSMM,OVERLAP:bhist:H3K4me2:HUVEC,OVERLAP:bhist:H3K4me2:K562,OVERLAP:bhist:H3K4me2:NHEK,OVERLAP:bhist:H3K4me2:NHLF",
				"hg18_broad_histones_H3K4me1":	"OVERLAP:bhist:H3K4me1:any,OVERLAP:bhist:H3K4me1:GM12878,OVERLAP:bhist:H3K4me1:H1hESC,OVERLAP:bhist:H3K4me1:HMEC,OVERLAP:bhist:H3K4me1:HSMM,OVERLAP:bhist:H3K4me1:HUVEC,OVERLAP:bhist:H3K4me1:K562,OVERLAP:bhist:H3K4me1:NHEK,OVERLAP:bhist:H3K4me1:NHLF",
				"hg18_broad_histones_CTCF":	"OVERLAP:bhist:CTCF:any,OVERLAP:bhist:CTCF:GM12878,OVERLAP:bhist:CTCF:H1hESC,OVERLAP:bhist:CTCF:HepG2,OVERLAP:bhist:CTCF:HMEC,OVERLAP:bhist:CTCF:HSMM,OVERLAP:bhist:CTCF:HUVEC,OVERLAP:bhist:CTCF:K562,OVERLAP:bhist:CTCF:NHEK,OVERLAP:bhist:CTCF:NHLF",
				"hg18_broad_histones_H2AZ":"OVERLAP:bhist:H2AZ:any,OVERLAP:bhist:H2AZ:HSMM,OVERLAP:bhist:H2AZ:HSMMtube,OVERLAP:bhist:H2AZ:HepG2,OVERLAP:bhist:H2AZ:K562,OVERLAP:bhist:H2AZ:Osteobl,OVERLAP:bhist:H2AZ:GM12878",
				"hg18_broad_histones_H3K9me3":"OVERLAP:bhist:H3K9me3:any,OVERLAP:bhist:H3K9me3:HSMM,OVERLAP:bhist:H3K9me3:K562,OVERLAP:bhist:H3K9me3:Osteobl,OVERLAP:bhist:H3K9me3:GM12878",
				"hg18_broad_histones_H3K79me2":"OVERLAP:bhist:H3K79me2:any,OVERLAP:bhist:H3K79me2:HSMM,OVERLAP:bhist:H3K79me2:HSMMtube,OVERLAP:bhist:H3K79me2:HelaS3,OVERLAP:bhist:H3K79me2:HepG2,OVERLAP:bhist:H3K79me2:K562,OVERLAP:bhist:H3K79me2:GM12878",
			"chmm":"OVERLAP:chmm01aprom:TISSUE,OVERLAP:chmm02wprom:TISSUE,OVERLAP:chmm03pprom:TISSUE,OVERLAP:chmm04strenh:TISSUE,OVERLAP:chmm05strenh:TISSUE,OVERLAP:chmm06wenh:TISSUE,OVERLAP:chmm07wenh:TISSUE,OVERLAP:chmm08ins:TISSUE,OVERLAP:chmm09trtr:TISSUE,OVERLAP:chmm10trel:TISSUE,OVERLAP:chmm11wtrx:TISSUE,OVERLAP:chmm12prepr:TISSUE,OVERLAP:chmm13hetr:TISSUE,OVERLAP:chmm14rcnv:TISSUE,OVERLAP:chmm15rcnv:TISSUE",
				"chmm01aprom":"OVERLAP:chmm01aprom:GM12878,OVERLAP:chmm01aprom:H1hESC,OVERLAP:chmm01aprom:HepG2,OVERLAP:chmm01aprom:HMEC,OVERLAP:chmm01aprom:HSMM,OVERLAP:chmm01aprom:HUVEC,OVERLAP:chmm01aprom:K562,OVERLAP:chmm01aprom:NHEK,OVERLAP:chmm01aprom:NHLF,OVERLAP:chmm01aprom:any",
				"chmm02wprom":"OVERLAP:chmm02wprom:GM12878,OVERLAP:chmm02wprom:H1hESC,OVERLAP:chmm02wprom:HepG2,OVERLAP:chmm02wprom:HMEC,OVERLAP:chmm02wprom:HSMM,OVERLAP:chmm02wprom:HUVEC,OVERLAP:chmm02wprom:K562,OVERLAP:chmm02wprom:NHEK,OVERLAP:chmm02wprom:NHLF,OVERLAP:chmm02wprom:any",
				"chmm03pprom":"OVERLAP:chmm03pprom:GM12878,OVERLAP:chmm03pprom:H1hESC,OVERLAP:chmm03pprom:HepG2,OVERLAP:chmm03pprom:HMEC,OVERLAP:chmm03pprom:HSMM,OVERLAP:chmm03pprom:HUVEC,OVERLAP:chmm03pprom:K562,OVERLAP:chmm03pprom:NHEK,OVERLAP:chmm03pprom:NHLF,OVERLAP:chmm03pprom:any",
				"chmm04strenh":"OVERLAP:chmm04strenh:GM12878,OVERLAP:chmm04strenh:H1hESC,OVERLAP:chmm04strenh:HepG2,OVERLAP:chmm04strenh:HMEC,OVERLAP:chmm04strenh:HSMM,OVERLAP:chmm04strenh:HUVEC,OVERLAP:chmm04strenh:K562,OVERLAP:chmm04strenh:NHEK,OVERLAP:chmm04strenh:NHLF,OVERLAP:chmm04strenh:any",
				"chmm05strenh":"OVERLAP:chmm05strenh:GM12878,OVERLAP:chmm05strenh:H1hESC,OVERLAP:chmm05strenh:HepG2,OVERLAP:chmm05strenh:HMEC,OVERLAP:chmm05strenh:HSMM,OVERLAP:chmm05strenh:HUVEC,OVERLAP:chmm05strenh:K562,OVERLAP:chmm05strenh:NHEK,OVERLAP:chmm05strenh:NHLF,OVERLAP:chmm05strenh:any",
				"chmm06wenh":"OVERLAP:chmm06wenh:GM12878,OVERLAP:chmm06wenh:H1hESC,OVERLAP:chmm06wenh:HepG2,OVERLAP:chmm06wenh:HMEC,OVERLAP:chmm06wenh:HSMM,OVERLAP:chmm06wenh:HUVEC,OVERLAP:chmm06wenh:K562,OVERLAP:chmm06wenh:NHEK,OVERLAP:chmm06wenh:NHLF,OVERLAP:chmm06wenh:any",
				"chmm07wenh":"OVERLAP:chmm07wenh:GM12878,OVERLAP:chmm07wenh:H1hESC,OVERLAP:chmm07wenh:HepG2,OVERLAP:chmm07wenh:HMEC,OVERLAP:chmm07wenh:HSMM,OVERLAP:chmm07wenh:HUVEC,OVERLAP:chmm07wenh:K562,OVERLAP:chmm07wenh:NHEK,OVERLAP:chmm07wenh:NHLF,OVERLAP:chmm07wenh:any",
				"chmm08ins":"OVERLAP:chmm08ins:GM12878,OVERLAP:chmm08ins:H1hESC,OVERLAP:chmm08ins:HepG2,OVERLAP:chmm08ins:HMEC,OVERLAP:chmm08ins:HSMM,OVERLAP:chmm08ins:HUVEC,OVERLAP:chmm08ins:K562,OVERLAP:chmm08ins:NHEK,OVERLAP:chmm08ins:NHLF,OVERLAP:chmm08ins:any",
				"chmm09trtr":"OVERLAP:chmm09trtr:GM12878,OVERLAP:chmm09trtr:H1hESC,OVERLAP:chmm09trtr:HepG2,OVERLAP:chmm09trtr:HMEC,OVERLAP:chmm09trtr:HSMM,OVERLAP:chmm09trtr:HUVEC,OVERLAP:chmm09trtr:K562,OVERLAP:chmm09trtr:NHEK,OVERLAP:chmm09trtr:NHLF,OVERLAP:chmm09trtr:any",
				"chmm10trel":"OVERLAP:chmm10trel:GM12878,OVERLAP:chmm10trel:H1hESC,OVERLAP:chmm10trel:HepG2,OVERLAP:chmm10trel:HMEC,OVERLAP:chmm10trel:HSMM,OVERLAP:chmm10trel:HUVEC,OVERLAP:chmm10trel:K562,OVERLAP:chmm10trel:NHEK,OVERLAP:chmm10trel:NHLF,OVERLAP:chmm10trel:any",
				"chmm11wtrx":"OVERLAP:chmm11wtrx:GM12878,OVERLAP:chmm11wtrx:H1hESC,OVERLAP:chmm11wtrx:HepG2,OVERLAP:chmm11wtrx:HMEC,OVERLAP:chmm11wtrx:HSMM,OVERLAP:chmm11wtrx:HUVEC,OVERLAP:chmm11wtrx:K562,OVERLAP:chmm11wtrx:NHEK,OVERLAP:chmm11wtrx:NHLF,OVERLAP:chmm11wtrx:any",
				"chmm12prepr":"OVERLAP:chmm12prepr:GM12878,OVERLAP:chmm12prepr:H1hESC,OVERLAP:chmm12prepr:HepG2,OVERLAP:chmm12prepr:HMEC,OVERLAP:chmm12prepr:HSMM,OVERLAP:chmm12prepr:HUVEC,OVERLAP:chmm12prepr:K562,OVERLAP:chmm12prepr:NHEK,OVERLAP:chmm12prepr:NHLF,OVERLAP:chmm12prepr:any",
				"chmm13hetr":"OVERLAP:chmm13hetr:GM12878,OVERLAP:chmm13hetr:H1hESC,OVERLAP:chmm13hetr:HepG2,OVERLAP:chmm13hetr:HMEC,OVERLAP:chmm13hetr:HSMM,OVERLAP:chmm13hetr:HUVEC,OVERLAP:chmm13hetr:K562,OVERLAP:chmm13hetr:NHEK,OVERLAP:chmm13hetr:NHLF,OVERLAP:chmm13hetr:any",
				"chmm14rcnv":"OVERLAP:chmm14rcnv:GM12878,OVERLAP:chmm14rcnv:H1hESC,OVERLAP:chmm14rcnv:HepG2,OVERLAP:chmm14rcnv:HMEC,OVERLAP:chmm14rcnv:HSMM,OVERLAP:chmm14rcnv:HUVEC,OVERLAP:chmm14rcnv:K562,OVERLAP:chmm14rcnv:NHEK,OVERLAP:chmm14rcnv:NHLF,OVERLAP:chmm14rcnv:any",
				"chmm15rcnv":"OVERLAP:chmm15rcnv:GM12878,OVERLAP:chmm15rcnv:H1hESC,OVERLAP:chmm15rcnv:HepG2,OVERLAP:chmm15rcnv:HMEC,OVERLAP:chmm15rcnv:HSMM,OVERLAP:chmm15rcnv:HUVEC,OVERLAP:chmm15rcnv:K562,OVERLAP:chmm15rcnv:NHEK,OVERLAP:chmm15rcnv:NHLF,OVERLAP:chmm15rcnv:any",
				"hg18_chmm_activeprom":"OVERLAP:chmm01aprom:GM12878,OVERLAP:chmm01aprom:H1hESC,OVERLAP:chmm01aprom:HepG2,OVERLAP:chmm01aprom:HMEC,OVERLAP:chmm01aprom:HSMM,OVERLAP:chmm01aprom:HUVEC,OVERLAP:chmm01aprom:K562,OVERLAP:chmm01aprom:NHEK,OVERLAP:chmm01aprom:NHLF,OVERLAP:chmm01aprom:any",
				"hg18_chmm_weakprom":"OVERLAP:chmm02wprom:GM12878,OVERLAP:chmm02wprom:H1hESC,OVERLAP:chmm02wprom:HepG2,OVERLAP:chmm02wprom:HMEC,OVERLAP:chmm02wprom:HSMM,OVERLAP:chmm02wprom:HUVEC,OVERLAP:chmm02wprom:K562,OVERLAP:chmm02wprom:NHEK,OVERLAP:chmm02wprom:NHLF,OVERLAP:chmm02wprom:any",
				"hg18_chmm_poisedprom":"OVERLAP:chmm03pprom:GM12878,OVERLAP:chmm03pprom:H1hESC,OVERLAP:chmm03pprom:HepG2,OVERLAP:chmm03pprom:HMEC,OVERLAP:chmm03pprom:HSMM,OVERLAP:chmm03pprom:HUVEC,OVERLAP:chmm03pprom:K562,OVERLAP:chmm03pprom:NHEK,OVERLAP:chmm03pprom:NHLF,OVERLAP:chmm03pprom:any",
				"hg18_chmm_strenh4":"OVERLAP:chmm04strenh:GM12878,OVERLAP:chmm04strenh:H1hESC,OVERLAP:chmm04strenh:HepG2,OVERLAP:chmm04strenh:HMEC,OVERLAP:chmm04strenh:HSMM,OVERLAP:chmm04strenh:HUVEC,OVERLAP:chmm04strenh:K562,OVERLAP:chmm04strenh:NHEK,OVERLAP:chmm04strenh:NHLF,OVERLAP:chmm04strenh:any",
				"hg18_chmm_strenh5":"OVERLAP:chmm05strenh:GM12878,OVERLAP:chmm05strenh:H1hESC,OVERLAP:chmm05strenh:HepG2,OVERLAP:chmm05strenh:HMEC,OVERLAP:chmm05strenh:HSMM,OVERLAP:chmm05strenh:HUVEC,OVERLAP:chmm05strenh:K562,OVERLAP:chmm05strenh:NHEK,OVERLAP:chmm05strenh:NHLF,OVERLAP:chmm05strenh:any",
				"hg18_chmm_wenh6":"OVERLAP:chmm06wenh:GM12878,OVERLAP:chmm06wenh:H1hESC,OVERLAP:chmm06wenh:HepG2,OVERLAP:chmm06wenh:HMEC,OVERLAP:chmm06wenh:HSMM,OVERLAP:chmm06wenh:HUVEC,OVERLAP:chmm06wenh:K562,OVERLAP:chmm06wenh:NHEK,OVERLAP:chmm06wenh:NHLF,OVERLAP:chmm06wenh:any",
				"hg18_chmm_wenh7":"OVERLAP:chmm07wenh:GM12878,OVERLAP:chmm07wenh:H1hESC,OVERLAP:chmm07wenh:HepG2,OVERLAP:chmm07wenh:HMEC,OVERLAP:chmm07wenh:HSMM,OVERLAP:chmm07wenh:HUVEC,OVERLAP:chmm07wenh:K562,OVERLAP:chmm07wenh:NHEK,OVERLAP:chmm07wenh:NHLF,OVERLAP:chmm07wenh:any",
				"hg18_chmm_ins":"OVERLAP:chmm08ins:GM12878,OVERLAP:chmm08ins:H1hESC,OVERLAP:chmm08ins:HepG2,OVERLAP:chmm08ins:HMEC,OVERLAP:chmm08ins:HSMM,OVERLAP:chmm08ins:HUVEC,OVERLAP:chmm08ins:K562,OVERLAP:chmm08ins:NHEK,OVERLAP:chmm08ins:NHLF,OVERLAP:chmm08ins:any",
				"hg18_chmm_trtrans":"OVERLAP:chmm09trtr:GM12878,OVERLAP:chmm09trtr:H1hESC,OVERLAP:chmm09trtr:HepG2,OVERLAP:chmm09trtr:HMEC,OVERLAP:chmm09trtr:HSMM,OVERLAP:chmm09trtr:HUVEC,OVERLAP:chmm09trtr:K562,OVERLAP:chmm09trtr:NHEK,OVERLAP:chmm09trtr:NHLF,OVERLAP:chmm09trtr:any",
				"hg18_chmm_trelon":"OVERLAP:chmm10trel:GM12878,OVERLAP:chmm10trel:H1hESC,OVERLAP:chmm10trel:HepG2,OVERLAP:chmm10trel:HMEC,OVERLAP:chmm10trel:HSMM,OVERLAP:chmm10trel:HUVEC,OVERLAP:chmm10trel:K562,OVERLAP:chmm10trel:NHEK,OVERLAP:chmm10trel:NHLF,OVERLAP:chmm10trel:any",
				"hg18_chmm_wtrx":"OVERLAP:chmm11wtrx:GM12878,OVERLAP:chmm11wtrx:H1hESC,OVERLAP:chmm11wtrx:HepG2,OVERLAP:chmm11wtrx:HMEC,OVERLAP:chmm11wtrx:HSMM,OVERLAP:chmm11wtrx:HUVEC,OVERLAP:chmm11wtrx:K562,OVERLAP:chmm11wtrx:NHEK,OVERLAP:chmm11wtrx:NHLF,OVERLAP:chmm11wtrx:any",
				"hg18_chmm_prepr":"OVERLAP:chmm12prepr:GM12878,OVERLAP:chmm12prepr:H1hESC,OVERLAP:chmm12prepr:HepG2,OVERLAP:chmm12prepr:HMEC,OVERLAP:chmm12prepr:HSMM,OVERLAP:chmm12prepr:HUVEC,OVERLAP:chmm12prepr:K562,OVERLAP:chmm12prepr:NHEK,OVERLAP:chmm12prepr:NHLF,OVERLAP:chmm12prepr:any",
				"hg18_chmm_hetr":"OVERLAP:chmm13hetr:GM12878,OVERLAP:chmm13hetr:H1hESC,OVERLAP:chmm13hetr:HepG2,OVERLAP:chmm13hetr:HMEC,OVERLAP:chmm13hetr:HSMM,OVERLAP:chmm13hetr:HUVEC,OVERLAP:chmm13hetr:K562,OVERLAP:chmm13hetr:NHEK,OVERLAP:chmm13hetr:NHLF,OVERLAP:chmm13hetr:any",
				"hg18_chmm_rcnv14":"OVERLAP:chmm14rcnv:GM12878,OVERLAP:chmm14rcnv:H1hESC,OVERLAP:chmm14rcnv:HepG2,OVERLAP:chmm14rcnv:HMEC,OVERLAP:chmm14rcnv:HSMM,OVERLAP:chmm14rcnv:HUVEC,OVERLAP:chmm14rcnv:K562,OVERLAP:chmm14rcnv:NHEK,OVERLAP:chmm14rcnv:NHLF,OVERLAP:chmm14rcnv:any",
				"hg18_chmm_rcnv15":"OVERLAP:chmm15rcnv:GM12878,OVERLAP:chmm15rcnv:H1hESC,OVERLAP:chmm15rcnv:HepG2,OVERLAP:chmm15rcnv:HMEC,OVERLAP:chmm15rcnv:HSMM,OVERLAP:chmm15rcnv:HUVEC,OVERLAP:chmm15rcnv:K562,OVERLAP:chmm15rcnv:NHEK,OVERLAP:chmm15rcnv:NHLF,OVERLAP:chmm15rcnv:any",
			"methylation":"OVERLAP:rrbs:hES_H1_p38:unmeth,OVERLAP:rrbs:hES_H9_p58:unmeth,OVERLAP:rrbs:hFib_11_p8:unmeth,OVERLAP:rrbs:Fetal_kidney:unmeth,OVERLAP:rrbs:Fetal_lung:unmeth,OVERLAP:rrbs:Fetal_brain:unmeth,OVERLAP:rrbs:Smooth_muscle:unmeth,OVERLAP:rrbs:Stomach_mucosa:unmeth,OVERLAP:rrbs:Neuron_H9_derived:unmeth,OVERLAP:rrbs:NPC_H9_derived:unmeth",
				"hES_H1_p38":"OVERLAP:rrbs:hES_H1_p38:unmeth,OVERLAP:rrbs:hES_H1_p38:meth",
				"hES_H9_p58":"OVERLAP:rrbs:hES_H9_p58:unmeth,OVERLAP:rrbs:hES_H9_p58:meth",
				"hFib_11_p8":"OVERLAP:rrbs:hFib_11_p8:unmeth,OVERLAP:rrbs:hFib_11_p8:meth",
				"hEB16d_H1_p38":"OVERLAP:rrbs:hEB16d_H1_p38:unmeth,OVERLAP:rrbs:hEB16d_H1_p38:meth",
				"fetal_heart":"OVERLAP:rrbs:fetal_heart:unmeth,OVERLAP:rrbs:fetal_heart:meth",
				"Fetal_kidney":"OVERLAP:rrbs:Fetal_kidney:unmeth,OVERLAP:rrbs:Fetal_kidney:meth",
				"Fetal_lung":"OVERLAP:rrbs:Fetal_lung:unmeth,OVERLAP:rrbs:Fetal_lung:meth",
				"Fetal_brain":"OVERLAP:rrbs:Fetal_brain:unmeth,OVERLAP:rrbs:Fetal_brain:meth",
				"Smooth_muscle":"OVERLAP:rrbs:Smooth_muscle:unmeth,OVERLAP:rrbs:Smooth_muscle:meth",
				"Skeletal_muscle":"OVERLAP:rrbs:Skeletal_muscle:unmeth,OVERLAP:rrbs:Skeletal_muscle:meth",
				"Stomach_mucosa":"OVERLAP:rrbs:Stomach_mucosa:unmeth,OVERLAP:rrbs:Stomach_mucosa:meth",
				"Neuron_H9_derived":"OVERLAP:rrbs:Neuron_H9_derived:unmeth,OVERLAP:rrbs:Neuron_H9_derived:meth",
				"NPC_H9_derived":"OVERLAP:rrbs:NPC_H9_derived:unmeth,OVERLAP:rrbs:NPC_H9_derived:meth",
				"Human_blood_CD34_mobilized_REMC":"OVERLAP:rrbs:Human_blood_CD34_mobilized_REMC:unmeth,OVERLAP:rrbs:Human_blood_CD34_mobilized_REMC:meth"
		},
		"hg19":{
			"hg19summary":"OVERLAP:bhist:H3K4me1:TISSUE,OVERLAP:bhist:H3K4me3:TISSUE,OVERLAP:bhist:H3K27me3:TISSUE,OVERLAP:bhist:H3K36me3:TISSUE,OVERLAP:DNaseI:TISSUE,OVERLAP:chmm04strenh:TISSUE,OVERLAP:chmm08ins:TISSUE,OVERLAP:ucscCGI,OVERLAP:cons,OVERLAP:repeats:any,OVERLAP:promoters_def,OVERLAP:genes",
			"repeats":"OVERLAP:repeats:any,OVERLAP:repeats:DNA,OVERLAP:repeats:snRNA,OVERLAP:repeats:Low_complexity,OVERLAP:repeats:LINE,OVERLAP:repeats:SINE,OVERLAP:repeats:Simple_repeat,OVERLAP:repeats:srpRNA,OVERLAP:repeats:scRNA,OVERLAP:repeats:LTR,OVERLAP:repeats:RC,OVERLAP:repeats:rRNA,OVERLAP:repeats:RNA,OVERLAP:repeats:tRNA,OVERLAP:repeats:Satellite,OVERLAP:repeats:Other,OVERLAP:repeats:Unknown",
			"hg19_repeat_masker":"OVERLAP:repeats:any,OVERLAP:repeats:DNA,OVERLAP:repeats:snRNA,OVERLAP:repeats:Low_complexity,OVERLAP:repeats:LINE,OVERLAP:repeats:SINE,OVERLAP:repeats:Simple_repeat,OVERLAP:repeats:srpRNA,OVERLAP:repeats:scRNA,OVERLAP:repeats:LTR,OVERLAP:repeats:RC,OVERLAP:repeats:rRNA,OVERLAP:repeats:RNA,OVERLAP:repeats:tRNA,OVERLAP:repeats:Satellite,OVERLAP:repeats:Other,OVERLAP:repeats:Unknown",
			"hg19_uw_DNaseI":"OVERLAP:DNaseI:any,OVERLAP:DNaseI:GM12878,OVERLAP:DNaseI:H1hESC,OVERLAP:DNaseI:HepG2,OVERLAP:DNaseI:NHLF,OVERLAP:DNaseI:HUVEC,OVERLAP:DNaseI:NHEK,OVERLAP:DNaseI:K562,OVERLAP:DNaseI:HeLaS3,OVERLAP:DNaseI:HMEC",
			"DNaseI":"OVERLAP:DNaseI:any,OVERLAP:DNaseI:GM12878,OVERLAP:DNaseI:H1hESC,OVERLAP:DNaseI:HepG2,OVERLAP:DNaseI:NHLF,OVERLAP:DNaseI:HUVEC,OVERLAP:DNaseI:NHEK,OVERLAP:DNaseI:K562,OVERLAP:DNaseI:HeLaS3,OVERLAP:DNaseI:HMEC",
			"generelated":	"OVERLAP:genes,OVERLAP:promoters_def,OVERLAP:promoters_cen,OVERLAP:promoters_reg,OVERLAP:exons,OVERLAP:promoters_TSS",
			"hg19histones": "OVERLAP:bhist:CTCF:TISSUE,OVERLAP:bhist:H2AZ:TISSUE,OVERLAP:bhist:H3K4me1:TISSUE,OVERLAP:bhist:H3K4me2:TISSUE,OVERLAP:bhist:H3K4me3:TISSUE,OVERLAP:bhist:H3K9ac:TISSUE,OVERLAP:bhist:H3K9me1:TISSUE,OVERLAP:bhist:H3K9me3:TISSUE,OVERLAP:bhist:H3K27ac:TISSUE,OVERLAP:bhist:H3K27me3:TISSUE,OVERLAP:bhist:H3K79me2:TISSUE,OVERLAP:bhist:H4K20me1:TISSUE,OVERLAP:bhist:H3K36me3:TISSUE,OVERLAP:bhist:Pol2b:TISSUE",
				"Pol2b":"OVERLAP:bhist:Pol2b:any,OVERLAP:bhist:Pol2b:HUVEC,OVERLAP:bhist:Pol2b:K562,OVERLAP:bhist:Pol2b:NHEK",
				"H4K20me1":	"OVERLAP:bhist:H4K20me1:any,OVERLAP:bhist:H4K20me1:GM12878,OVERLAP:bhist:H4K20me1:H1hESC,OVERLAP:bhist:H4K20me1:HepG2,OVERLAP:bhist:H4K20me1:HMEC,OVERLAP:bhist:H4K20me1:HSMM,OVERLAP:bhist:H4K20me1:HUVEC,OVERLAP:bhist:H4K20me1:K562,OVERLAP:bhist:H4K20me1:NHEK,OVERLAP:bhist:H4K20me1:NHLF",
				"H3K36me3":	"OVERLAP:bhist:H3K36me3:any,OVERLAP:bhist:H3K36me3:GM12878,OVERLAP:bhist:H3K36me3:H1hESC,OVERLAP:bhist:H3K36me3:HepG2,OVERLAP:bhist:H3K36me3:HMEC,OVERLAP:bhist:H3K36me3:HSMM,OVERLAP:bhist:H3K36me3:HUVEC,OVERLAP:bhist:H3K36me3:K562,OVERLAP:bhist:H3K36me3:NHEK,OVERLAP:bhist:H3K36me3:NHLF",
				"H3K27me3":	"OVERLAP:bhist:H3K27me3:any,OVERLAP:bhist:H3K27me3:GM12878,OVERLAP:bhist:H3K27me3:H1hESC,OVERLAP:bhist:H3K27me3:HMEC,OVERLAP:bhist:H3K27me3:HSMM,OVERLAP:bhist:H3K27me3:HUVEC,OVERLAP:bhist:H3K27me3:K562,OVERLAP:bhist:H3K27me3:NHEK,OVERLAP:bhist:H3K27me3:NHLF",
				"H3K27ac":	"OVERLAP:bhist:H3K27ac:any,OVERLAP:bhist:H3K27ac:GM12878,OVERLAP:bhist:H3K27ac:HepG2,OVERLAP:bhist:H3K27ac:HMEC,OVERLAP:bhist:H3K27ac:HSMM,OVERLAP:bhist:H3K27ac:HUVEC,OVERLAP:bhist:H3K27ac:K562,OVERLAP:bhist:H3K27ac:NHEK,OVERLAP:bhist:H3K27ac:NHLF",
				"H3K9me1":	"OVERLAP:bhist:H3K9me1:any,OVERLAP:bhist:H3K9me1:HUVEC,OVERLAP:bhist:H3K9me1:K562,OVERLAP:bhist:H3K9me1:NHEK",
				"H3K9ac":	"OVERLAP:bhist:H3K9ac:any,OVERLAP:bhist:H3K9ac:GM12878,OVERLAP:bhist:H3K9ac:H1hESC,OVERLAP:bhist:H3K9ac:HepG2,OVERLAP:bhist:H3K9ac:HMEC,OVERLAP:bhist:H3K9ac:HSMM,OVERLAP:bhist:H3K9ac:HUVEC,OVERLAP:bhist:H3K9ac:K562,OVERLAP:bhist:H3K9ac:NHEK,OVERLAP:bhist:H3K9ac:NHLF",
				"H3K4me3":	"OVERLAP:bhist:H3K4me3:any,OVERLAP:bhist:H3K4me3:GM12878,OVERLAP:bhist:H3K4me3:H1hESC,OVERLAP:bhist:H3K4me3:HepG2,OVERLAP:bhist:H3K4me3:HMEC,OVERLAP:bhist:H3K4me3:HSMM,OVERLAP:bhist:H3K4me3:HUVEC,OVERLAP:bhist:H3K4me3:K562,OVERLAP:bhist:H3K4me3:NHEK,OVERLAP:bhist:H3K4me3:NHLF",
				"H3K4me2":	"OVERLAP:bhist:H3K4me2:any,OVERLAP:bhist:H3K4me2:GM12878,OVERLAP:bhist:H3K4me2:H1hESC,OVERLAP:bhist:H3K4me2:HepG2,OVERLAP:bhist:H3K4me2:HMEC,OVERLAP:bhist:H3K4me2:HSMM,OVERLAP:bhist:H3K4me2:HUVEC,OVERLAP:bhist:H3K4me2:K562,OVERLAP:bhist:H3K4me2:NHEK,OVERLAP:bhist:H3K4me2:NHLF",
				"H3K4me1":	"OVERLAP:bhist:H3K4me1:any,OVERLAP:bhist:H3K4me1:GM12878,OVERLAP:bhist:H3K4me1:H1hESC,OVERLAP:bhist:H3K4me1:HMEC,OVERLAP:bhist:H3K4me1:HSMM,OVERLAP:bhist:H3K4me1:HUVEC,OVERLAP:bhist:H3K4me1:K562,OVERLAP:bhist:H3K4me1:NHEK,OVERLAP:bhist:H3K4me1:NHLF",
				"CTCF":	"OVERLAP:bhist:CTCF:any,OVERLAP:bhist:CTCF:GM12878,OVERLAP:bhist:CTCF:H1hESC,OVERLAP:bhist:CTCF:HepG2,OVERLAP:bhist:CTCF:HMEC,OVERLAP:bhist:CTCF:HSMM,OVERLAP:bhist:CTCF:HUVEC,OVERLAP:bhist:CTCF:K562,OVERLAP:bhist:CTCF:NHEK,OVERLAP:bhist:CTCF:NHLF",
				"H2AZ":"OVERLAP:bhist:H2AZ:any,OVERLAP:bhist:H2AZ:HSMM,OVERLAP:bhist:H2AZ:HSMMtube,OVERLAP:bhist:H2AZ:HepG2,OVERLAP:bhist:H2AZ:K562,OVERLAP:bhist:H2AZ:Osteobl,OVERLAP:bhist:H2AZ:GM12878",
				"H3K9me3":"OVERLAP:bhist:H3K9me3:any,OVERLAP:bhist:H3K9me3:HSMM,OVERLAP:bhist:H3K9me3:K562,OVERLAP:bhist:H3K9me3:Osteobl,OVERLAP:bhist:H3K9me3:GM12878",
				"H3K79me2":"OVERLAP:bhist:H3K79me2:any,OVERLAP:bhist:H3K79me2:HSMM,OVERLAP:bhist:H3K79me2:HSMMtube,OVERLAP:bhist:H3K79me2:HelaS3,OVERLAP:bhist:H3K79me2:HepG2,OVERLAP:bhist:H3K79me2:K562,OVERLAP:bhist:H3K79me2:GM12878",
				"hg19_broad_histones_Pol2b":"OVERLAP:bhist:Pol2b:any,OVERLAP:bhist:Pol2b:HUVEC,OVERLAP:bhist:Pol2b:K562,OVERLAP:bhist:Pol2b:NHEK",
				"hg19_broad_histones_H4K20me1":	"OVERLAP:bhist:H4K20me1:any,OVERLAP:bhist:H4K20me1:GM12878,OVERLAP:bhist:H4K20me1:H1hESC,OVERLAP:bhist:H4K20me1:HepG2,OVERLAP:bhist:H4K20me1:HMEC,OVERLAP:bhist:H4K20me1:HSMM,OVERLAP:bhist:H4K20me1:HUVEC,OVERLAP:bhist:H4K20me1:K562,OVERLAP:bhist:H4K20me1:NHEK,OVERLAP:bhist:H4K20me1:NHLF",
				"hg19_broad_histones_H3K36me3":	"OVERLAP:bhist:H3K36me3:any,OVERLAP:bhist:H3K36me3:GM12878,OVERLAP:bhist:H3K36me3:H1hESC,OVERLAP:bhist:H3K36me3:HepG2,OVERLAP:bhist:H3K36me3:HMEC,OVERLAP:bhist:H3K36me3:HSMM,OVERLAP:bhist:H3K36me3:HUVEC,OVERLAP:bhist:H3K36me3:K562,OVERLAP:bhist:H3K36me3:NHEK,OVERLAP:bhist:H3K36me3:NHLF",
				"hg19_broad_histones_H3K27me3":	"OVERLAP:bhist:H3K27me3:any,OVERLAP:bhist:H3K27me3:GM12878,OVERLAP:bhist:H3K27me3:H1hESC,OVERLAP:bhist:H3K27me3:HMEC,OVERLAP:bhist:H3K27me3:HSMM,OVERLAP:bhist:H3K27me3:HUVEC,OVERLAP:bhist:H3K27me3:K562,OVERLAP:bhist:H3K27me3:NHEK,OVERLAP:bhist:H3K27me3:NHLF",
				"hg19_broad_histones_H3K27ac":	"OVERLAP:bhist:H3K27ac:any,OVERLAP:bhist:H3K27ac:GM12878,OVERLAP:bhist:H3K27ac:HepG2,OVERLAP:bhist:H3K27ac:HMEC,OVERLAP:bhist:H3K27ac:HSMM,OVERLAP:bhist:H3K27ac:HUVEC,OVERLAP:bhist:H3K27ac:K562,OVERLAP:bhist:H3K27ac:NHEK,OVERLAP:bhist:H3K27ac:NHLF",
				"hg19_broad_histones_H3K9me1":	"OVERLAP:bhist:H3K9me1:any,OVERLAP:bhist:H3K9me1:HUVEC,OVERLAP:bhist:H3K9me1:K562,OVERLAP:bhist:H3K9me1:NHEK",
				"hg19_broad_histones_H3K9ac":	"OVERLAP:bhist:H3K9ac:any,OVERLAP:bhist:H3K9ac:GM12878,OVERLAP:bhist:H3K9ac:H1hESC,OVERLAP:bhist:H3K9ac:HepG2,OVERLAP:bhist:H3K9ac:HMEC,OVERLAP:bhist:H3K9ac:HSMM,OVERLAP:bhist:H3K9ac:HUVEC,OVERLAP:bhist:H3K9ac:K562,OVERLAP:bhist:H3K9ac:NHEK,OVERLAP:bhist:H3K9ac:NHLF",
				"hg19_broad_histones_H3K4me3":	"OVERLAP:bhist:H3K4me3:any,OVERLAP:bhist:H3K4me3:GM12878,OVERLAP:bhist:H3K4me3:H1hESC,OVERLAP:bhist:H3K4me3:HepG2,OVERLAP:bhist:H3K4me3:HMEC,OVERLAP:bhist:H3K4me3:HSMM,OVERLAP:bhist:H3K4me3:HUVEC,OVERLAP:bhist:H3K4me3:K562,OVERLAP:bhist:H3K4me3:NHEK,OVERLAP:bhist:H3K4me3:NHLF",
				"hg19_broad_histones_H3K4me2":	"OVERLAP:bhist:H3K4me2:any,OVERLAP:bhist:H3K4me2:GM12878,OVERLAP:bhist:H3K4me2:H1hESC,OVERLAP:bhist:H3K4me2:HepG2,OVERLAP:bhist:H3K4me2:HMEC,OVERLAP:bhist:H3K4me2:HSMM,OVERLAP:bhist:H3K4me2:HUVEC,OVERLAP:bhist:H3K4me2:K562,OVERLAP:bhist:H3K4me2:NHEK,OVERLAP:bhist:H3K4me2:NHLF",
				"hg19_broad_histones_H3K4me1":	"OVERLAP:bhist:H3K4me1:any,OVERLAP:bhist:H3K4me1:GM12878,OVERLAP:bhist:H3K4me1:H1hESC,OVERLAP:bhist:H3K4me1:HMEC,OVERLAP:bhist:H3K4me1:HSMM,OVERLAP:bhist:H3K4me1:HUVEC,OVERLAP:bhist:H3K4me1:K562,OVERLAP:bhist:H3K4me1:NHEK,OVERLAP:bhist:H3K4me1:NHLF",
				"hg19_broad_histones_CTCF":	"OVERLAP:bhist:CTCF:any,OVERLAP:bhist:CTCF:GM12878,OVERLAP:bhist:CTCF:H1hESC,OVERLAP:bhist:CTCF:HepG2,OVERLAP:bhist:CTCF:HMEC,OVERLAP:bhist:CTCF:HSMM,OVERLAP:bhist:CTCF:HUVEC,OVERLAP:bhist:CTCF:K562,OVERLAP:bhist:CTCF:NHEK,OVERLAP:bhist:CTCF:NHLF",
				"hg19_broad_histones_H2AZ":"OVERLAP:bhist:H2AZ:any,OVERLAP:bhist:H2AZ:HSMM,OVERLAP:bhist:H2AZ:HSMMtube,OVERLAP:bhist:H2AZ:HepG2,OVERLAP:bhist:H2AZ:K562,OVERLAP:bhist:H2AZ:Osteobl,OVERLAP:bhist:H2AZ:GM12878",
				"hg19_broad_histones_H3K9me3":"OVERLAP:bhist:H3K9me3:any,OVERLAP:bhist:H3K9me3:HSMM,OVERLAP:bhist:H3K9me3:K562,OVERLAP:bhist:H3K9me3:Osteobl,OVERLAP:bhist:H3K9me3:GM12878",
				"hg19_broad_histones_H3K79me2":"OVERLAP:bhist:H3K79me2:any,OVERLAP:bhist:H3K79me2:HSMM,OVERLAP:bhist:H3K79me2:HSMMtube,OVERLAP:bhist:H3K79me2:HelaS3,OVERLAP:bhist:H3K79me2:HepG2,OVERLAP:bhist:H3K79me2:K562,OVERLAP:bhist:H3K79me2:GM12878",
			"chmm":"OVERLAP:chmm01aprom:TISSUE,OVERLAP:chmm02wprom:TISSUE,OVERLAP:chmm03pprom:TISSUE,OVERLAP:chmm04strenh:TISSUE,OVERLAP:chmm05strenh:TISSUE,OVERLAP:chmm06wenh:TISSUE,OVERLAP:chmm07wenh:TISSUE,OVERLAP:chmm08ins:TISSUE,OVERLAP:chmm09trtr:TISSUE,OVERLAP:chmm10trel:TISSUE,OVERLAP:chmm11wtrx:TISSUE,OVERLAP:chmm12prepr:TISSUE,OVERLAP:chmm13hetr:TISSUE,OVERLAP:chmm14rcnv:TISSUE,OVERLAP:chmm15rcnv:TISSUE",
				"chmm01aprom":"OVERLAP:chmm01aprom:GM12878,OVERLAP:chmm01aprom:H1hESC,OVERLAP:chmm01aprom:HepG2,OVERLAP:chmm01aprom:HMEC,OVERLAP:chmm01aprom:HSMM,OVERLAP:chmm01aprom:HUVEC,OVERLAP:chmm01aprom:K562,OVERLAP:chmm01aprom:NHEK,OVERLAP:chmm01aprom:NHLF,OVERLAP:chmm01aprom:any",
				"chmm02wprom":"OVERLAP:chmm02wprom:GM12878,OVERLAP:chmm02wprom:H1hESC,OVERLAP:chmm02wprom:HepG2,OVERLAP:chmm02wprom:HMEC,OVERLAP:chmm02wprom:HSMM,OVERLAP:chmm02wprom:HUVEC,OVERLAP:chmm02wprom:K562,OVERLAP:chmm02wprom:NHEK,OVERLAP:chmm02wprom:NHLF,OVERLAP:chmm02wprom:any",
				"chmm03pprom":"OVERLAP:chmm03pprom:GM12878,OVERLAP:chmm03pprom:H1hESC,OVERLAP:chmm03pprom:HepG2,OVERLAP:chmm03pprom:HMEC,OVERLAP:chmm03pprom:HSMM,OVERLAP:chmm03pprom:HUVEC,OVERLAP:chmm03pprom:K562,OVERLAP:chmm03pprom:NHEK,OVERLAP:chmm03pprom:NHLF,OVERLAP:chmm03pprom:any",
				"chmm04strenh":"OVERLAP:chmm04strenh:GM12878,OVERLAP:chmm04strenh:H1hESC,OVERLAP:chmm04strenh:HepG2,OVERLAP:chmm04strenh:HMEC,OVERLAP:chmm04strenh:HSMM,OVERLAP:chmm04strenh:HUVEC,OVERLAP:chmm04strenh:K562,OVERLAP:chmm04strenh:NHEK,OVERLAP:chmm04strenh:NHLF,OVERLAP:chmm04strenh:any",
				"chmm05strenh":"OVERLAP:chmm05strenh:GM12878,OVERLAP:chmm05strenh:H1hESC,OVERLAP:chmm05strenh:HepG2,OVERLAP:chmm05strenh:HMEC,OVERLAP:chmm05strenh:HSMM,OVERLAP:chmm05strenh:HUVEC,OVERLAP:chmm05strenh:K562,OVERLAP:chmm05strenh:NHEK,OVERLAP:chmm05strenh:NHLF,OVERLAP:chmm05strenh:any",
				"chmm06wenh":"OVERLAP:chmm06wenh:GM12878,OVERLAP:chmm06wenh:H1hESC,OVERLAP:chmm06wenh:HepG2,OVERLAP:chmm06wenh:HMEC,OVERLAP:chmm06wenh:HSMM,OVERLAP:chmm06wenh:HUVEC,OVERLAP:chmm06wenh:K562,OVERLAP:chmm06wenh:NHEK,OVERLAP:chmm06wenh:NHLF,OVERLAP:chmm06wenh:any",
				"chmm07wenh":"OVERLAP:chmm07wenh:GM12878,OVERLAP:chmm07wenh:H1hESC,OVERLAP:chmm07wenh:HepG2,OVERLAP:chmm07wenh:HMEC,OVERLAP:chmm07wenh:HSMM,OVERLAP:chmm07wenh:HUVEC,OVERLAP:chmm07wenh:K562,OVERLAP:chmm07wenh:NHEK,OVERLAP:chmm07wenh:NHLF,OVERLAP:chmm07wenh:any",
				"chmm08ins":"OVERLAP:chmm08ins:GM12878,OVERLAP:chmm08ins:H1hESC,OVERLAP:chmm08ins:HepG2,OVERLAP:chmm08ins:HMEC,OVERLAP:chmm08ins:HSMM,OVERLAP:chmm08ins:HUVEC,OVERLAP:chmm08ins:K562,OVERLAP:chmm08ins:NHEK,OVERLAP:chmm08ins:NHLF,OVERLAP:chmm08ins:any",
				"chmm09trtr":"OVERLAP:chmm09trtr:GM12878,OVERLAP:chmm09trtr:H1hESC,OVERLAP:chmm09trtr:HepG2,OVERLAP:chmm09trtr:HMEC,OVERLAP:chmm09trtr:HSMM,OVERLAP:chmm09trtr:HUVEC,OVERLAP:chmm09trtr:K562,OVERLAP:chmm09trtr:NHEK,OVERLAP:chmm09trtr:NHLF,OVERLAP:chmm09trtr:any",
				"chmm10trel":"OVERLAP:chmm10trel:GM12878,OVERLAP:chmm10trel:H1hESC,OVERLAP:chmm10trel:HepG2,OVERLAP:chmm10trel:HMEC,OVERLAP:chmm10trel:HSMM,OVERLAP:chmm10trel:HUVEC,OVERLAP:chmm10trel:K562,OVERLAP:chmm10trel:NHEK,OVERLAP:chmm10trel:NHLF,OVERLAP:chmm10trel:any",
				"chmm11wtrx":"OVERLAP:chmm11wtrx:GM12878,OVERLAP:chmm11wtrx:H1hESC,OVERLAP:chmm11wtrx:HepG2,OVERLAP:chmm11wtrx:HMEC,OVERLAP:chmm11wtrx:HSMM,OVERLAP:chmm11wtrx:HUVEC,OVERLAP:chmm11wtrx:K562,OVERLAP:chmm11wtrx:NHEK,OVERLAP:chmm11wtrx:NHLF,OVERLAP:chmm11wtrx:any",
				"chmm12prepr":"OVERLAP:chmm12prepr:GM12878,OVERLAP:chmm12prepr:H1hESC,OVERLAP:chmm12prepr:HepG2,OVERLAP:chmm12prepr:HMEC,OVERLAP:chmm12prepr:HSMM,OVERLAP:chmm12prepr:HUVEC,OVERLAP:chmm12prepr:K562,OVERLAP:chmm12prepr:NHEK,OVERLAP:chmm12prepr:NHLF,OVERLAP:chmm12prepr:any",
				"chmm13hetr":"OVERLAP:chmm13hetr:GM12878,OVERLAP:chmm13hetr:H1hESC,OVERLAP:chmm13hetr:HepG2,OVERLAP:chmm13hetr:HMEC,OVERLAP:chmm13hetr:HSMM,OVERLAP:chmm13hetr:HUVEC,OVERLAP:chmm13hetr:K562,OVERLAP:chmm13hetr:NHEK,OVERLAP:chmm13hetr:NHLF,OVERLAP:chmm13hetr:any",
				"chmm14rcnv":"OVERLAP:chmm14rcnv:GM12878,OVERLAP:chmm14rcnv:H1hESC,OVERLAP:chmm14rcnv:HepG2,OVERLAP:chmm14rcnv:HMEC,OVERLAP:chmm14rcnv:HSMM,OVERLAP:chmm14rcnv:HUVEC,OVERLAP:chmm14rcnv:K562,OVERLAP:chmm14rcnv:NHEK,OVERLAP:chmm14rcnv:NHLF,OVERLAP:chmm14rcnv:any",
				"chmm15rcnv":"OVERLAP:chmm15rcnv:GM12878,OVERLAP:chmm15rcnv:H1hESC,OVERLAP:chmm15rcnv:HepG2,OVERLAP:chmm15rcnv:HMEC,OVERLAP:chmm15rcnv:HSMM,OVERLAP:chmm15rcnv:HUVEC,OVERLAP:chmm15rcnv:K562,OVERLAP:chmm15rcnv:NHEK,OVERLAP:chmm15rcnv:NHLF,OVERLAP:chmm15rcnv:any",
				"hg19_chmm_activeprom":"OVERLAP:chmm01aprom:GM12878,OVERLAP:chmm01aprom:H1hESC,OVERLAP:chmm01aprom:HepG2,OVERLAP:chmm01aprom:HMEC,OVERLAP:chmm01aprom:HSMM,OVERLAP:chmm01aprom:HUVEC,OVERLAP:chmm01aprom:K562,OVERLAP:chmm01aprom:NHEK,OVERLAP:chmm01aprom:NHLF,OVERLAP:chmm01aprom:any",
				"hg19_chmm_weakprom":"OVERLAP:chmm02wprom:GM12878,OVERLAP:chmm02wprom:H1hESC,OVERLAP:chmm02wprom:HepG2,OVERLAP:chmm02wprom:HMEC,OVERLAP:chmm02wprom:HSMM,OVERLAP:chmm02wprom:HUVEC,OVERLAP:chmm02wprom:K562,OVERLAP:chmm02wprom:NHEK,OVERLAP:chmm02wprom:NHLF,OVERLAP:chmm02wprom:any",
				"hg19_chmm_poisedprom":"OVERLAP:chmm03pprom:GM12878,OVERLAP:chmm03pprom:H1hESC,OVERLAP:chmm03pprom:HepG2,OVERLAP:chmm03pprom:HMEC,OVERLAP:chmm03pprom:HSMM,OVERLAP:chmm03pprom:HUVEC,OVERLAP:chmm03pprom:K562,OVERLAP:chmm03pprom:NHEK,OVERLAP:chmm03pprom:NHLF,OVERLAP:chmm03pprom:any",
				"hg19_chmm_strenh4":"OVERLAP:chmm04strenh:GM12878,OVERLAP:chmm04strenh:H1hESC,OVERLAP:chmm04strenh:HepG2,OVERLAP:chmm04strenh:HMEC,OVERLAP:chmm04strenh:HSMM,OVERLAP:chmm04strenh:HUVEC,OVERLAP:chmm04strenh:K562,OVERLAP:chmm04strenh:NHEK,OVERLAP:chmm04strenh:NHLF,OVERLAP:chmm04strenh:any",
				"hg19_chmm_strenh5":"OVERLAP:chmm05strenh:GM12878,OVERLAP:chmm05strenh:H1hESC,OVERLAP:chmm05strenh:HepG2,OVERLAP:chmm05strenh:HMEC,OVERLAP:chmm05strenh:HSMM,OVERLAP:chmm05strenh:HUVEC,OVERLAP:chmm05strenh:K562,OVERLAP:chmm05strenh:NHEK,OVERLAP:chmm05strenh:NHLF,OVERLAP:chmm05strenh:any",
				"hg19_chmm_wenh6":"OVERLAP:chmm06wenh:GM12878,OVERLAP:chmm06wenh:H1hESC,OVERLAP:chmm06wenh:HepG2,OVERLAP:chmm06wenh:HMEC,OVERLAP:chmm06wenh:HSMM,OVERLAP:chmm06wenh:HUVEC,OVERLAP:chmm06wenh:K562,OVERLAP:chmm06wenh:NHEK,OVERLAP:chmm06wenh:NHLF,OVERLAP:chmm06wenh:any",
				"hg19_chmm_wenh7":"OVERLAP:chmm07wenh:GM12878,OVERLAP:chmm07wenh:H1hESC,OVERLAP:chmm07wenh:HepG2,OVERLAP:chmm07wenh:HMEC,OVERLAP:chmm07wenh:HSMM,OVERLAP:chmm07wenh:HUVEC,OVERLAP:chmm07wenh:K562,OVERLAP:chmm07wenh:NHEK,OVERLAP:chmm07wenh:NHLF,OVERLAP:chmm07wenh:any",
				"hg19_chmm_ins":"OVERLAP:chmm08ins:GM12878,OVERLAP:chmm08ins:H1hESC,OVERLAP:chmm08ins:HepG2,OVERLAP:chmm08ins:HMEC,OVERLAP:chmm08ins:HSMM,OVERLAP:chmm08ins:HUVEC,OVERLAP:chmm08ins:K562,OVERLAP:chmm08ins:NHEK,OVERLAP:chmm08ins:NHLF,OVERLAP:chmm08ins:any",
				"hg19_chmm_trtrans":"OVERLAP:chmm09trtr:GM12878,OVERLAP:chmm09trtr:H1hESC,OVERLAP:chmm09trtr:HepG2,OVERLAP:chmm09trtr:HMEC,OVERLAP:chmm09trtr:HSMM,OVERLAP:chmm09trtr:HUVEC,OVERLAP:chmm09trtr:K562,OVERLAP:chmm09trtr:NHEK,OVERLAP:chmm09trtr:NHLF,OVERLAP:chmm09trtr:any",
				"hg19_chmm_trelon":"OVERLAP:chmm10trel:GM12878,OVERLAP:chmm10trel:H1hESC,OVERLAP:chmm10trel:HepG2,OVERLAP:chmm10trel:HMEC,OVERLAP:chmm10trel:HSMM,OVERLAP:chmm10trel:HUVEC,OVERLAP:chmm10trel:K562,OVERLAP:chmm10trel:NHEK,OVERLAP:chmm10trel:NHLF,OVERLAP:chmm10trel:any",
				"hg19_chmm_wtrx":"OVERLAP:chmm11wtrx:GM12878,OVERLAP:chmm11wtrx:H1hESC,OVERLAP:chmm11wtrx:HepG2,OVERLAP:chmm11wtrx:HMEC,OVERLAP:chmm11wtrx:HSMM,OVERLAP:chmm11wtrx:HUVEC,OVERLAP:chmm11wtrx:K562,OVERLAP:chmm11wtrx:NHEK,OVERLAP:chmm11wtrx:NHLF,OVERLAP:chmm11wtrx:any",
				"hg19_chmm_prepr":"OVERLAP:chmm12prepr:GM12878,OVERLAP:chmm12prepr:H1hESC,OVERLAP:chmm12prepr:HepG2,OVERLAP:chmm12prepr:HMEC,OVERLAP:chmm12prepr:HSMM,OVERLAP:chmm12prepr:HUVEC,OVERLAP:chmm12prepr:K562,OVERLAP:chmm12prepr:NHEK,OVERLAP:chmm12prepr:NHLF,OVERLAP:chmm12prepr:any",
				"hg19_chmm_hetr":"OVERLAP:chmm13hetr:GM12878,OVERLAP:chmm13hetr:H1hESC,OVERLAP:chmm13hetr:HepG2,OVERLAP:chmm13hetr:HMEC,OVERLAP:chmm13hetr:HSMM,OVERLAP:chmm13hetr:HUVEC,OVERLAP:chmm13hetr:K562,OVERLAP:chmm13hetr:NHEK,OVERLAP:chmm13hetr:NHLF,OVERLAP:chmm13hetr:any",
				"hg19_chmm_rcnv14":"OVERLAP:chmm14rcnv:GM12878,OVERLAP:chmm14rcnv:H1hESC,OVERLAP:chmm14rcnv:HepG2,OVERLAP:chmm14rcnv:HMEC,OVERLAP:chmm14rcnv:HSMM,OVERLAP:chmm14rcnv:HUVEC,OVERLAP:chmm14rcnv:K562,OVERLAP:chmm14rcnv:NHEK,OVERLAP:chmm14rcnv:NHLF,OVERLAP:chmm14rcnv:any",
				"hg19_chmm_rcnv15":"OVERLAP:chmm15rcnv:GM12878,OVERLAP:chmm15rcnv:H1hESC,OVERLAP:chmm15rcnv:HepG2,OVERLAP:chmm15rcnv:HMEC,OVERLAP:chmm15rcnv:HSMM,OVERLAP:chmm15rcnv:HUVEC,OVERLAP:chmm15rcnv:K562,OVERLAP:chmm15rcnv:NHEK,OVERLAP:chmm15rcnv:NHLF,OVERLAP:chmm15rcnv:any",
			"hg19methylation":"OVERLAP:rrbs:H1hESC:unmeth,OVERLAP:rrbs:GM12878:unmeth,OVERLAP:rrbs:HeLaS3:unmeth,OVERLAP:rrbs:HepG2:unmeth,OVERLAP:rrbs:K562:unmeth,OVERLAP:rrbs:HSMM:unmeth,OVERLAP:rrbs:HMEC:unmeth",
				"HMEC":"OVERLAP:rrbs:HMEC:unmeth,OVERLAP:rrbs:HMEC:meth",
				"HSMM":"OVERLAP:rrbs:HSMM:unmeth,OVERLAP:rrbs:HSMM:meth",
				"K562":"OVERLAP:rrbs:K562:unmeth,OVERLAP:rrbs:K562:meth",
				"HepG2":"OVERLAP:rrbs:HepG2:unmeth,OVERLAP:rrbs:HepG2:meth",
				"HeLaS3":"OVERLAP:rrbs:HeLaS3:unmeth,OVERLAP:rrbs:HeLaS3:meth",
				"GM12878":"OVERLAP:rrbs:GM12878:unmeth,OVERLAP:rrbs:GM12878:meth",
				"H1hESC":"OVERLAP:rrbs:H1hESC:unmeth,OVERLAP:rrbs:H1hESC:meth"
		},
		"mm9":{
			"mm9summary":"OVERLAP:bhist:H3K4me1:any,OVERLAP:bhist:H3K4me3:any,OVERLAP:tfbs:CTCF:any,OVERLAP:tfbs:Pol2:any,OVERLAP:DNaseIa:any,OVERLAP:repeats:any,OVERLAP:cons,OVERLAP:genes,OVERLAP:promoters_def,OVERLAP:ucscCGI,OVERLAP:LaminaB1:any",
			"repeats":"OVERLAP:repeats:any,OVERLAP:repeats:DNA,OVERLAP:repeats:snRNA,OVERLAP:repeats:Low_complexity,OVERLAP:repeats:LINE,OVERLAP:repeats:SINE,OVERLAP:repeats:Simple_repeat,OVERLAP:repeats:srpRNA,OVERLAP:repeats:scRNA,OVERLAP:repeats:LTR,OVERLAP:repeats:RC,OVERLAP:repeats:rRNA,OVERLAP:repeats:RNA,OVERLAP:repeats:tRNA,OVERLAP:repeats:Satellite,OVERLAP:repeats:Other,OVERLAP:repeats:Unknown",
			"mm9_repeat_masker":"OVERLAP:repeats:any,OVERLAP:repeats:DNA,OVERLAP:repeats:snRNA,OVERLAP:repeats:Low_complexity,OVERLAP:repeats:LINE,OVERLAP:repeats:SINE,OVERLAP:repeats:Simple_repeat,OVERLAP:repeats:srpRNA,OVERLAP:repeats:scRNA,OVERLAP:repeats:LTR,OVERLAP:repeats:RC,OVERLAP:repeats:rRNA,OVERLAP:repeats:RNA,OVERLAP:repeats:tRNA,OVERLAP:repeats:Satellite,OVERLAP:repeats:Other,OVERLAP:repeats:Unknown",
			"mm9_uw_DNaseI":"OVERLAP:DNaseI:any,OVERLAP:DNaseI:GM12878,OVERLAP:DNaseI:H1hESC,OVERLAP:DNaseI:HepG2,OVERLAP:DNaseI:NHLF,OVERLAP:DNaseI:HUVEC,OVERLAP:DNaseI:NHEK,OVERLAP:DNaseI:K562,OVERLAP:DNaseI:HeLaS3,OVERLAP:DNaseI:HMEC",
			"DNaseI":"OVERLAP:DNaseI:any,OVERLAP:DNaseI:GM12878,OVERLAP:DNaseI:H1hESC,OVERLAP:DNaseI:HepG2,OVERLAP:DNaseI:NHLF,OVERLAP:DNaseI:HUVEC,OVERLAP:DNaseI:NHEK,OVERLAP:DNaseI:K562,OVERLAP:DNaseI:HeLaS3,OVERLAP:DNaseI:HMEC",
			"generelated":"OVERLAP:genes,OVERLAP:promoters_def,OVERLAP:promoters_cen,OVERLAP:promoters_reg,OVERLAP:exons,OVERLAP:promoters_TSS",
			"mm9histones":"OVERLAP:bhist:H3K4me1:any,OVERLAP:bhist:H3K4me3:any,OVERLAP:bhist:H3K27ac:any,OVERLAP:bhist:H3K27me3:any,OVERLAP:bhist:H3K36me3:any,OVERLAP:bhist:H3K79me2:any,OVERLAP:bhist:H3K9ac:any",
				"mm9_Broad_Histones_H3K27ac":"OVERLAP:bhist:H3K27ac:any,OVERLAP:bhist:H3K27ac:Heart,OVERLAP:bhist:H3K27ac:Liver,OVERLAP:bhist:H3K27ac:Kidney,OVERLAP:bhist:H3K27ac:Bmarrow,OVERLAP:bhist:H3K27ac:Esb4_emb,OVERLAP:bhist:H3K27ac:Mef,OVERLAP:bhist:H3K27ac:Testis,OVERLAP:bhist:H3K27ac:Wbrain_emb,OVERLAP:bhist:H3K27ac",
				"mm9_Broad_Histones_H3K27me3":"OVERLAP:bhist:H3K27me3:any,OVERLAP:bhist:H3K27me3:Heart,OVERLAP:bhist:H3K27me3:Liver",
				"mm9_Broad_Histones_H3K36me3":"OVERLAP:bhist:H3K36me3:any,OVERLAP:bhist:H3K36me3:Heart,OVERLAP:bhist:H3K36me3:Liver",
				"mm9_Broad_Histones_H3K4me1":"OVERLAP:bhist:H3K4me1:any,OVERLAP:bhist:H3K4me1:Heart,OVERLAP:bhist:H3K4me1:Liver,OVERLAP:bhist:H3K4me1:Kidney,OVERLAP:bhist:H3K4me1:Bmarrow,OVERLAP:bhist:H3K4me1:Esb4_emb,OVERLAP:bhist:H3K4me1:Mef,OVERLAP:bhist:H3K4me1:Testis,OVERLAP:bhist:H3K4me1:Wbrain",
				"mm9_Broad_Histones_H3K4me3":"OVERLAP:bhist:H3K4me3:any,OVERLAP:bhist:H3K4me3:Heart,OVERLAP:bhist:H3K4me3:Liver,OVERLAP:bhist:H3K4me3:Kidney,OVERLAP:bhist:H3K4me1:H3K4me3,OVERLAP:bhist:H3K4me1:H3K4me3,OVERLAP:bhist:H3K4me1:Mef,OVERLAP:bhist:H3K4me1:Testis,OVERLAP:bhist:H3K4me1:Wbrain",
				"mm9_Broad_Histones_H3K79me2":"OVERLAP:bhist:H3K79me2:any,OVERLAP:bhist:H3K79me2:Heart,OVERLAP:bhist:H3K79me2:Liver",
				"mm9_Broad_Histones_H3K9ac":"OVERLAP:bhist:H3K9ac:any,OVERLAP:bhist:H3K9ac:Heart,OVERLAP:bhist:H3K9ac:Liver",
			"chmm":"OVERLAP:chmm01aprom:TISSUE,OVERLAP:chmm02wprom:TISSUE,OVERLAP:chmm03pprom:TISSUE,OVERLAP:chmm04strenh:TISSUE,OVERLAP:chmm05strenh:TISSUE,OVERLAP:chmm06wenh:TISSUE,OVERLAP:chmm07wenh:TISSUE,OVERLAP:chmm08ins:TISSUE,OVERLAP:chmm09trtr:TISSUE,OVERLAP:chmm10trel:TISSUE,OVERLAP:chmm11wtrx:TISSUE,OVERLAP:chmm12prepr:TISSUE,OVERLAP:chmm13hetr:TISSUE,OVERLAP:chmm14rcnv:TISSUE,OVERLAP:chmm15rcnv:TISSUE",
				"chmm01aprom":"OVERLAP:chmm01aprom:GM12878,OVERLAP:chmm01aprom:H1hESC,OVERLAP:chmm01aprom:HepG2,OVERLAP:chmm01aprom:HMEC,OVERLAP:chmm01aprom:HSMM,OVERLAP:chmm01aprom:HUVEC,OVERLAP:chmm01aprom:K562,OVERLAP:chmm01aprom:NHEK,OVERLAP:chmm01aprom:NHLF,OVERLAP:chmm01aprom:any",
				"chmm02wprom":"OVERLAP:chmm02wprom:GM12878,OVERLAP:chmm02wprom:H1hESC,OVERLAP:chmm02wprom:HepG2,OVERLAP:chmm02wprom:HMEC,OVERLAP:chmm02wprom:HSMM,OVERLAP:chmm02wprom:HUVEC,OVERLAP:chmm02wprom:K562,OVERLAP:chmm02wprom:NHEK,OVERLAP:chmm02wprom:NHLF,OVERLAP:chmm02wprom:any",
				"chmm03pprom":"OVERLAP:chmm03pprom:GM12878,OVERLAP:chmm03pprom:H1hESC,OVERLAP:chmm03pprom:HepG2,OVERLAP:chmm03pprom:HMEC,OVERLAP:chmm03pprom:HSMM,OVERLAP:chmm03pprom:HUVEC,OVERLAP:chmm03pprom:K562,OVERLAP:chmm03pprom:NHEK,OVERLAP:chmm03pprom:NHLF,OVERLAP:chmm03pprom:any",
				"chmm04strenh":"OVERLAP:chmm04strenh:GM12878,OVERLAP:chmm04strenh:H1hESC,OVERLAP:chmm04strenh:HepG2,OVERLAP:chmm04strenh:HMEC,OVERLAP:chmm04strenh:HSMM,OVERLAP:chmm04strenh:HUVEC,OVERLAP:chmm04strenh:K562,OVERLAP:chmm04strenh:NHEK,OVERLAP:chmm04strenh:NHLF,OVERLAP:chmm04strenh:any",
				"chmm05strenh":"OVERLAP:chmm05strenh:GM12878,OVERLAP:chmm05strenh:H1hESC,OVERLAP:chmm05strenh:HepG2,OVERLAP:chmm05strenh:HMEC,OVERLAP:chmm05strenh:HSMM,OVERLAP:chmm05strenh:HUVEC,OVERLAP:chmm05strenh:K562,OVERLAP:chmm05strenh:NHEK,OVERLAP:chmm05strenh:NHLF,OVERLAP:chmm05strenh:any",
				"chmm06wenh":"OVERLAP:chmm06wenh:GM12878,OVERLAP:chmm06wenh:H1hESC,OVERLAP:chmm06wenh:HepG2,OVERLAP:chmm06wenh:HMEC,OVERLAP:chmm06wenh:HSMM,OVERLAP:chmm06wenh:HUVEC,OVERLAP:chmm06wenh:K562,OVERLAP:chmm06wenh:NHEK,OVERLAP:chmm06wenh:NHLF,OVERLAP:chmm06wenh:any",
				"chmm07wenh":"OVERLAP:chmm07wenh:GM12878,OVERLAP:chmm07wenh:H1hESC,OVERLAP:chmm07wenh:HepG2,OVERLAP:chmm07wenh:HMEC,OVERLAP:chmm07wenh:HSMM,OVERLAP:chmm07wenh:HUVEC,OVERLAP:chmm07wenh:K562,OVERLAP:chmm07wenh:NHEK,OVERLAP:chmm07wenh:NHLF,OVERLAP:chmm07wenh:any",
				"chmm08ins":"OVERLAP:chmm08ins:GM12878,OVERLAP:chmm08ins:H1hESC,OVERLAP:chmm08ins:HepG2,OVERLAP:chmm08ins:HMEC,OVERLAP:chmm08ins:HSMM,OVERLAP:chmm08ins:HUVEC,OVERLAP:chmm08ins:K562,OVERLAP:chmm08ins:NHEK,OVERLAP:chmm08ins:NHLF,OVERLAP:chmm08ins:any",
				"chmm09trtr":"OVERLAP:chmm09trtr:GM12878,OVERLAP:chmm09trtr:H1hESC,OVERLAP:chmm09trtr:HepG2,OVERLAP:chmm09trtr:HMEC,OVERLAP:chmm09trtr:HSMM,OVERLAP:chmm09trtr:HUVEC,OVERLAP:chmm09trtr:K562,OVERLAP:chmm09trtr:NHEK,OVERLAP:chmm09trtr:NHLF,OVERLAP:chmm09trtr:any",
				"chmm10trel":"OVERLAP:chmm10trel:GM12878,OVERLAP:chmm10trel:H1hESC,OVERLAP:chmm10trel:HepG2,OVERLAP:chmm10trel:HMEC,OVERLAP:chmm10trel:HSMM,OVERLAP:chmm10trel:HUVEC,OVERLAP:chmm10trel:K562,OVERLAP:chmm10trel:NHEK,OVERLAP:chmm10trel:NHLF,OVERLAP:chmm10trel:any",
				"chmm11wtrx":"OVERLAP:chmm11wtrx:GM12878,OVERLAP:chmm11wtrx:H1hESC,OVERLAP:chmm11wtrx:HepG2,OVERLAP:chmm11wtrx:HMEC,OVERLAP:chmm11wtrx:HSMM,OVERLAP:chmm11wtrx:HUVEC,OVERLAP:chmm11wtrx:K562,OVERLAP:chmm11wtrx:NHEK,OVERLAP:chmm11wtrx:NHLF,OVERLAP:chmm11wtrx:any",
				"chmm12prepr":"OVERLAP:chmm12prepr:GM12878,OVERLAP:chmm12prepr:H1hESC,OVERLAP:chmm12prepr:HepG2,OVERLAP:chmm12prepr:HMEC,OVERLAP:chmm12prepr:HSMM,OVERLAP:chmm12prepr:HUVEC,OVERLAP:chmm12prepr:K562,OVERLAP:chmm12prepr:NHEK,OVERLAP:chmm12prepr:NHLF,OVERLAP:chmm12prepr:any",
				"chmm13hetr":"OVERLAP:chmm13hetr:GM12878,OVERLAP:chmm13hetr:H1hESC,OVERLAP:chmm13hetr:HepG2,OVERLAP:chmm13hetr:HMEC,OVERLAP:chmm13hetr:HSMM,OVERLAP:chmm13hetr:HUVEC,OVERLAP:chmm13hetr:K562,OVERLAP:chmm13hetr:NHEK,OVERLAP:chmm13hetr:NHLF,OVERLAP:chmm13hetr:any",
				"chmm14rcnv":"OVERLAP:chmm14rcnv:GM12878,OVERLAP:chmm14rcnv:H1hESC,OVERLAP:chmm14rcnv:HepG2,OVERLAP:chmm14rcnv:HMEC,OVERLAP:chmm14rcnv:HSMM,OVERLAP:chmm14rcnv:HUVEC,OVERLAP:chmm14rcnv:K562,OVERLAP:chmm14rcnv:NHEK,OVERLAP:chmm14rcnv:NHLF,OVERLAP:chmm14rcnv:any",
				"chmm15rcnv":"OVERLAP:chmm15rcnv:GM12878,OVERLAP:chmm15rcnv:H1hESC,OVERLAP:chmm15rcnv:HepG2,OVERLAP:chmm15rcnv:HMEC,OVERLAP:chmm15rcnv:HSMM,OVERLAP:chmm15rcnv:HUVEC,OVERLAP:chmm15rcnv:K562,OVERLAP:chmm15rcnv:NHEK,OVERLAP:chmm15rcnv:NHLF,OVERLAP:chmm15rcnv:any",
			"mm9methylation":"OVERLAP:rrbs:brain:unmeth,OVERLAP:rrbs:heart:unmeth,OVERLAP:rrbs:liver:unmeth"
		}
	};
	var groupsummary;
	if (groupsummaryValues[settings['genome']][groupName] !== undefined){
		groupsummary = groupsummaryValues[settings['genome']][groupName];
	}else{
		groupsummary = "";
	}
	return groupsummary;
}
function getTextForPlotDescription(plotType){
	var plotTypeDescriptions = {
		"genes": "The table lists all Ensembl genes located within 5kb of (at least) one of the regions in the selected region set. Clicking the black triangle next to a gene name will select all regions that overlap with this specific gene.",
		"goterms": "The table lists the most common Gene Ontology (GO) terms among Ensembl genes located within 5kb of (at least) one of the regions in the selected region set. The Ratio column lists the odds ratio, i.e. the percent of genes with this annotation among the co-located genes divided by the overall percentage of genes with this annotation. In the word cloud on the right, font size is proportional to this ratio. Clicking the black triangle next to a GO term will select all regions that overlap with genes annotated with this GO term.",
		"gowords": "The table lists the most common words occurring in Gene Ontology (GO) terms for Ensembl genes located within 5kb of (at least) one of the regions in the selected region set. Clicking the black triangle next to a GO word will select all regions that overlap with genes annotated with a GO term containing this word.",
		"omimterms": "The table lists the most common disease association terms (based on the OMIM database) among Ensembl genes located within 5kb of (at least) one of the regions in the selected region set. The Ratio column lists the odds ratio, i.e. the percent of genes with this annotation among the co-located genes divided by the overall percentage of genes with this annotation. In the word cloud on the right, font size is proportional to this ratio. Clicking the black triangle next to an OMIM term will select all regions that overlap with genes annotated with this OMIM term.",
		"omimwords": "The table lists the most common words occurring in disease association (OMIM) terms for Ensembl genes located within 5kb of (at least) one of the regions in the selected region set. Clicking the black triangle next to an OMIM word will select all regions that overlap with genes annotated with an OMIM term containing this word.",
		"rangepie":"The pie chart on the left shows the overall distribution of the score, and the area chart / histogram on the right offers a more detailed view of a specific range of the distribution. Clicking a sector of the pie chart (or its corresponding legend item) visualizes this subset of the distribution in the form of an area chart.",
		"rangecolumn":"The stacked column chart shows the overall distribution of the score for the current dataset (left) and the reference set (right), and the area chart / histogram on the right offers a more detailed view of a specific range of the distribution. Clicking a sector of the pie chart (or its corresponding legend item) visualizes this subset of the distribution in the form of an area chart.",
		"ratio": "The area chart / histogram displays the distribution of a particular score value across the selected set of genomic regions. The y-axis shows the percentage of regions falling within the range indicated on the x-axis.",
		"neighborhoodref": "The neighborhood chart illustrates the relative distribution of histone marks in the vicinity of the selected region set, averaging across all genomic regions in the set. The x-axis shows an ordered list of predefined positions relative to the start and the end of the regions, and the y-axis specifies in what percent of the regions a particular histone modification is observed in particular tissue at the relative position. If strand information is available for the region set, it is taken into account to plot all regions from 5' to 3' end. The connecting lines are for illustration purposes only and do not necessarily imply a continuous trend in between the measurement point. Clicking specific cell types in the table will update the visualization.",
		"neighborhoodsingle": "The neighborhood chart illustrates the relative distribution of histone marks in the vicinity of the selected region set, averaging across all genomic regions in the set. The x-axis shows an ordered list of predefined positions relative to the start and the end of the regions, and the y-axis specifies in what percent of the regions a particular histone modification is observed in particular tissue at the relative position. If strand information is available for the region set, it is taken into account to plot all regions from 5' to 3' end. The connecting lines are for illustration purposes only and do not necessarily imply a continuous trend in between the measurement point. Clicking specific cell types in the legend will remove the corresponding lines from the figure.",
		"overlaptable":"The bar chart visualizes the percentage of regions in the selected region set that overlap with any of the listed features on the x-axis. If available, clicking the magnifying glass icon in the menu on the left provides quantitative information on the distribution of overlap percentages.",
		"summary":"The bar chart visualizes the percentage of regions in the selected region set that overlap with any of the listed genomic and epigenomic features on the x-axis.",
		"summary_bars":"The bar chart visualizes the percentage of regions in the selected region set that overlap with any of the listed genomic and epigenomic features on the x-axis.",
		"summary_bubbles": "The bubbles chart visualizes the percentage of regions overlapping with genomic and epigenomic annotations against the genome coverage of these annotations. When EpiExplorer is in comparison mode, the x-axis is changed to percent of overlapping control set regions and the genome coverage is visualized as bubble size.",
		"summaryWithConfidence":"The bar chart visualizes the percentage of regions in the selected region set that overlap with any of the listed genomic and epigenomic features on the x-axis. An additional confidence measure is displayed on top of each bar. The set of regions is split by random into 10 equal parts and overlap with each annotation is computed for each them. The confidence measure shows the minimum, maximum, 25 and 75 percentiles of these 10 values.",
		"nodescription":""
	};
	var plotDescription;
	if (plotTypeDescriptions[plotType] !== undefined){
		plotDescription = plotTypeDescriptions[plotType];
	}else{
		plotDescription = "'"+plotType+"' plot description (TODO insert description for this figure type)";
	}
	return plotDescription;
}
function getTextForFeatureDescription(featureName){
	var featureDescriptions = {
		"hg18_dna_sequence":"Frequency of observed DNA sequence patterns. For every region R, the frequency for a pattern P is measured as number of occurrences of P in the DNA sequence of R divided by the length of the region",
		"hg19_dna_sequence":"Frequency of observed DNA sequence patterns. For every region R, the frequency for a pattern P is measured as number of occurrences of P in the DNA sequence of R divided by the length of the region",
		//"hg18summary":"shows general information for the dataset",
		//"regionList:":"shows several regions from the current refinement",
		"Elength_magnitude:":"Lengths (in bp) of the regions. The length is measured as (chromosome end - chromosome start + 1)",
		"hg18_repeat_masker":"Information about overlap information for different types of repeat elements obtained with the repeat masker program <a href='http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=165805886&c=chr12&g=rmskRM327' target='_blank'>Source</a>",
		"hg19_repeat_masker":"Information about overlap information for different types of repeat elements obtained with the repeat masker program <a href='http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=165805886&c=chr12&g=rmskRM327' target='_blank'>Source</a>",
		"repeats":"Information about overlap with different types of repeat elements obtained with the repeat masker program <a href='http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=165805886&c=chr12&g=rmskRM327' target='_blank'>Source</a>",
		"location":"Information about distribution on chromosomes",
		"generelated":"Information about overlap and proximity to nearest gene structural elements (gene bodies, promoters, transcription start sites and exons) or gene annotations such as GO and OMIM terms and categories <a href='http://www.ensembl.org/Homo_sapiens/Info/Index' target='_blank'>Source</a>",
			"hg18_ensembl_gene_genes":"Information about overlap and proximity to Ensembl gene bodies <a href='http://www.ensembl.org/Homo_sapiens/Info/Index' target='_blank'>Source</a>",
			"hg19_ensembl_gene_genes":"Information about overlap and proximity to Ensembl gene bodies <a href='http://www.ensembl.org/Homo_sapiens/Info/Index' target='_blank'>Source</a>",
			"promoters":"Information about overlap and proximity to gene promoter annotations varying in positioning relative to Ensembl gene transcription start sites",
			"hg18_ensembl_gene_promoters":"Information about overlap and proximity to gene promoters, which are defined as 5kb upstream to 1kb downstream of Ensembl gene TSS",
			"hg19_ensembl_gene_promoters":"Information about overlap and proximity to gene promoters, which are defined as 5kb upstream to 1kb downstream of Ensembl gene TSS",
			"hg18_ensembl_gene_promoters_centered":"Information about overlap and proximity to gene promoters, which are defined as 1kb upstream to 1kb downstream of Ensembl gene TSS",
			"hg19_ensembl_gene_promoters_centered":"Information about overlap and proximity to gene promoters, which are defined as 1kb upstream to 1kb downstream of Ensembl gene TSS",
			"hg18_ensembl_gene_promoters_region":"Information about overlap and proximity to gene promoters, which are defined as 10kb upstream to 2kb downstream of Ensembl gene TSS",
			"hg19_ensembl_gene_promoters_region":"Information about overlap and proximity to gene promoters, which are defined as 10kb upstream to 2kb downstream of Ensembl gene TSS",
			"hg18_ensembl_gene_TSS":"Information about overlap and proximity to Ensembl gene transcription start sites",
			"hg19_ensembl_gene_TSS":"Information about overlap and proximity to Ensembl gene transcription start sites",
			"hg18_ensembl_gene_exons":"Information about overlap and proximity to Ensembl gene exons",
			"hg19_ensembl_gene_exons":"Information about overlap and proximity to Ensembl gene exons",
		"hg18_conservation":"Information about overlap and proximity to conserved elements from the UCSC Genome Browser track <a href='http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=171724329&c=chr17&g=mostConserved28way' target='_blank'>Source</a>",
		"hg19_conservation":"Information about overlap and proximity to conserved elements from the UCSC Genome Browser track <a href='http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=171724329&c=chr17&g=mostConserved28way' target='_blank'>Source</a>",
		"hg18_ucsc_cpg_islands":"Information about overlap and proximity to UCSC Genome Browser CpG islands track <a href='http://genome.ucsc.edu/cgi-bin/hgTables?db=hg18&hgta_group=regulation&hgta_track=cpgIslandExt&hgta_table=cpgIslandExt&hgta_doSchema=describe+table+schema' target='_blank'>Source</a>",
		"hg19_ucsc_cpg_islands":"Information about overlap and proximity to UCSC Genome Browser CpG islands track <a href='http://genome.ucsc.edu/cgi-bin/hgTables?db=hg18&hgta_group=regulation&hgta_track=cpgIslandExt&hgta_table=cpgIslandExt&hgta_doSchema=describe+table+schema' target='_blank'>Source</a>",
		"hg18_cgihunter_CpG_Islands":"Information about overlap and proximity to CpG island Gardiner-Garden annotation computed using the CGIHunter software <a href='http://cgihunter.bioinf.mpi-inf.mpg.de/index.php' target='_blank'>Source</a>",
		"hg19_cgihunter_CpG_Islands":"Information about overlap and proximity to CpG island Gardiner-Garden annotation computed using the CGIHunter software <a href='http://cgihunter.bioinf.mpi-inf.mpg.de/index.php' target='_blank'>Source</a>",
		"hg18_uw_DNaseI":"Information about overlap and proximity to DNaseI hypersensitivity sites measured genome-wide in different cell lines using the Digital DNaseI methodology <a href='http://genome.ucsc.edu/cgi-bin/hgTables?db=hg18&hgta_group=regulation&hgta_track=wgEncodeUwDnaseSeq&hgta_table=wgEncodeUwDnaseSeqPeaksRep2Gm12865&hgta_doSchema=describe+table+schema' target='_blank'>Source</a>",
		"hg19_uw_DNaseI":"Information about overlap and proximity to DNaseI hypersensitivity sites measured genome-wide in different cell lines using the Digital DNaseI methodology <a href='http://genome.ucsc.edu/cgi-bin/hgTables?db=hg18&hgta_group=regulation&hgta_track=wgEncodeUwDnaseSeq&hgta_table=wgEncodeUwDnaseSeqPeaksRep2Gm12865&hgta_doSchema=describe+table+schema' target='_blank'>Source</a>",
		"DNaseI":"Information about overlap and proximity to DNaseI hypersensitivity sites measured genome-wide in different cell lines using the Digital DNaseI methodology <a href='http://genome.ucsc.edu/cgi-bin/hgTables?db=hg18&hgta_group=regulation&hgta_track=wgEncodeUwDnaseSeq&hgta_table=wgEncodeUwDnaseSeqPeaksRep2Gm12865&hgta_doSchema=describe+table+schema' target='_blank'>Source</a>",
		"histones":"Information about overlap, proximity and enrichment around peaks of multiple histone modifications generated by the Broad/MGH ENCODE group using ChIP-seq <a href='http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=165805886&c=chr12&g=wgEncodeBroadChipSeq' target='_blank'>Source</a>",
			"CTCF":"Information about overlap, proximity and enrichment around peaks for CTCF zinc finger transcription factor. A sequence specific DNA binding protein that functions as an insulator, blocking enhancer activity. It has also been suggested to block the spreading of chromatin structure in certain instances.<a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22CTCF%22' target='_blank'>Source</a>",
			"Pol2b":"Information about overlap, proximity and enrichment around peaks for RNA polymerase II. Is responsible for RNA transcription. It is generally enriched at 5' gene ends, probably due to higher rate of occupancy associated with transition from initiation to elongation.<a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22Pol2%28b%29%22' target='_blank'>Source</a>",
			"H3K9ac":"Information about overlap, proximity and enrichment around peaks for histone H3 (acetyl K9). As with H3K27ac, associated with transcriptional initiation and open chromatin structure. <a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22H3K9ac%22' target='_blank'>Source</a>",
			"H3K27ac":"Information about overlap, proximity and enrichment around peaks for histone H3 (acetyl K27). As with H3K9ac, associated with transcriptional initiation and open chromatin structure. It remains unknown whether acetylation has can have different consequences depending on the specific lysine residue targeted. In general, though, there appears to be high redundancy. Histone acetylation is notable for susceptibility to small molecules and drugs that target histone deacetylases.<a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22H3K27ac%22' target='_blank'>Source</a>",
			"H3K4me1":"Information about overlap, proximity and enrichment around peaks for histone H3 (mono methyl K4). Is associated with enhancers, and downstream of transcription starts.<a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22H3K4me1%22' target='_blank'>Source</a>",
			"H3K4me2":"Information about overlap, proximity and enrichment around peaks for histone H3 (di methyl K4). Marks promoters and enhancers. Most CpG islands are marked by H3K4me2 in primary cells. May be associated also with poised promoters.<a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22H3K4me2%22' target='_blank'>Source</a>",
			"H3K4me3":"Information about overlap, proximity and enrichment around peaks for histone H3 (tri methyl K4). Marks promoters that are active or poised to be activated.<a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22H3K4me3%22' target='_blank'>Source</a>",
			"H3K9me1":"Information about overlap, proximity and enrichment around peaks for histone H3 (mono-methyl K9). Is associated with active and accessible regions. NOTE CONTRAST to H3K9me3 which is associated with repressive heterochromatic state.<a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22H3K9me1%22' target='_blank'>Source</a>",
			"H3K27me3":"Information about overlap, proximity and enrichment around peaks for histone H3 (tri-methyl K27). Marks promoters that are silenced by Polycomb proteins in a given lineage; large domains are found at inactive developmental loci.<a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22H3K27me3%22' target='_blank'>Source</a>",
			"H3K36me3":"Information about overlap, proximity and enrichment around peaks for histone H3 (tri-methyl K36). Marks regions of RNAPII elongation, including coding and non-coding transcripts. <a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22H3K36me3%22' target='_blank'>Source</a>",
			"H4K20me1":"Information about overlap, proximity and enrichment around peaks for histone H4 (mono-methyl K20). Is associated with active and accessible regions. In mammals, PR-Set7 specifically catalyzes H4K20 monomethylation. NOTE CONTRAST to H3K20me3 which is associated with heterochromatin and DNA repair.<a href='http://genome.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&target=%22H4K20me1%22' target='_blank'>Source</a>",
		"distanceTo":"Information about distance from current selection of regions to the nearest element",
		"methylation":"DNA methylation was obtained using the reduced representation bisulphite sequencing method (see Meissner and Mikkelsen et al. Nature 2008). For every region, the number of CpGs for which there was available RRBS information as computed, the average DNA methylation percentage that is the avergae of the methylation scores of all CpGs, minimum and maximum methylaiton ratio for an individual CpG as well as the standard deviation of the methylation ratios of the ",
			'Fetal_lung':"",
			'hES_H1_p38':"",
			'hES_H9_p58':"",
			'hFib_11_p8':"",
			'Fetal_brain':"",
			'fetal_heart':"",
			'Smooth_muscle':"",
			'hEB16d_H1_p38':"",
			'NPC_H9_derived':"",
			'Stomach_mucosa':"",
			'Skeletal_muscle':"",
			'Neuron_H9_derived':"",
			'Human_blood_CD34_mobilized_REMC':"",
		'chmm':"Genome segmentation based on epigenetic profile",
			"chmm01aprom":"Active promoters (1)",
			"chmm02wprom":"Weak promoters (2)",
			"chmm03pprom":"Poised promoters (3)",
			"chmm04strenh":"Strong enhancers (4)",
			"chmm05strenh":"Strong enhancers (5)",
			"chmm06wenh":"Weak enhancers (6)",
			"chmm07wenh":"Weak enhancers (7)",
			"chmm08ins":"Insulators (8)",
			"chmm09trtr":"Transcriptional transition (9)",
			"chmm10trel":"Transcriptional elongation (10)",
			"chmm11wtrx":"Weak transcribed (11)",
			"chmm12prepr":"Polycomb repressed (12)",
			"chmm13hetr":"Heterochromatin (low signal) (13)",
			"chmm14rcnv":"Repetitive/CNV (14)",
			"chmm15rcnv":"Repetitive/CNV (15)",
		"User":"overlaps and distance to user-defined genome annotations"};
	//alert("Feature description text for "+featureName)
	var featureDescription;
	if (featureDescriptions[featureName] !== undefined){
		featureDescription = featureDescriptions[featureName];
	}else{
		featureDescription = "'"+featureName + "' description (TODO insert description for this feature)";
		featureDescription = ""
	}
	//alert("Feature description text is "+featureDescription)
	return featureDescription;
}

function getTextForFeatureGroup(prefix){
	//featureGroupNames = {};
	var groupName;
	if (featureGroupNames[prefix] !== undefined){
		groupName = featureGroupNames[prefix];
	}else{
		//alert("Start "+prefix)
		groupName = prefix;
		$.ajax({
			type: "GET",
			url: "relay.php",
			dataType: "json",
			async:false,
			data: "type=getDatasetInfo&datasetName="+prefix+"&property=officialName",
			success: function (result){
				if(result["officialName"] !== undefined){
					groupName = result["officialName"];
					featureGroupDescription[prefix] = result["description"];
					featureGroupNames[prefix] = result["officialName"];
					featureGroupCategories[prefix] = result["categories"];
					overlapMarks[prefix] = result["overlappingText"];
				}else{
					groupName = prefix;
				}
				featureGroupNames[prefix] = groupName;
			}
		});
	}

	return groupName;
}
function getOverlapLabels(overlapKey){
	label = overlapLabels[overlapKey];
	if (label == undefined) {
		//alert("NO OVERLAP LABEL FOR " + overlapKey);
		return overlapKey;
	}
	return label;
}

function getDescriptionForFeatureGroup(prefix){
	var groupDescription;
	if (featureGroupDescription[prefix] !== undefined){
		return featureGroupDescription[prefix];
	}
	//alert(prefix);
	return null;
}

function getDNAsequencePatternText(pattern){
	if (pattern[0] == "E"){
		if (pattern == "EA"){
			text = "A+T";
		}else if (pattern == "EC"){
			text = "G+C";
		}else if (pattern == "ETG"){
			text = "TG+CA";
		}else{
			text = pattern+" on both strands";
		}
	}else{
		text = pattern;
	}
	return text;
}
function getTextForFeaturePrefix(prefix){
	var text;
	if (prefix == "Elength_magnitude:"){
		text = "Region lengths";
	}else if (prefix == "Echr:"){
		text = "by chromosome";
	}else if (prefix.startsWith("Emud:")){
		text = "upstream";
	}else if (prefix.startsWith("Emdd:")){
		text = "downstream";
	}else if (prefix.startsWith("Emmd:chmm")){
		text = prefix.split(":")[2];
	}else if (prefix.startsWith("Emmd:DNaseI")){
		text = prefix.split(":")[2];
	}else if (prefix.startsWith("Emmd:LaminaB1:")){
		text = prefix.split(":")[2];
	}else if (prefix.startsWith("Emmd:")){
		text = "Distance to nearest";
	}else if (prefix.startsWith("-OVERLAP")){
		text = "Not overlapping";
	}else if (prefix.startsWith("OVERLAP")){
		text = "Overlapping";
	}else if (prefix.startsWith("Eor:")){
		text = "Percent overlap (relative to region length)";
	}else if (prefix.startsWith("Ednaseq:")){
		var pattern = prefix.split(":")[1];
		text = "Frequency of "+getDNAsequencePatternText(pattern);
	}else if (prefix.startsWith("Enbh:")){
		text = "Neighborhood";
	}else if (prefix.startsWith("regionList:")){
		text = "List the regions";
	}else if (prefix.startsWith("GENENAME:ENSEMBL")){
		text = "Gene names (Ensembl)";
	}else if (prefix.startsWith("GO:TERMS")){
		text = "Gene ontology (words)";
	}else if (prefix.startsWith("GO:ALL")){
		text = "Gene ontology (terms)";
	}else if (prefix.startsWith("OMIM:TERMS")){
		text = "OMIM (words)";
	}else if (prefix.startsWith("OMIM:ALL")){
		text = "OMIM (terms)";
	}else if (prefix.startsWith("EmethCpG:")){
		text = "Number of observed CpGs";
	}else if (prefix.startsWith("EmethR:")){
		text = "Average CpG methylation ratio";
	}else if (prefix.startsWith("EmethRmin:")){
		text = "Min methylation ratio of a CpG";
	}else if (prefix.startsWith("EmethRmax:")){
		text = "Max methylation ratio of a CpG";
	}else if (prefix.startsWith("EmethRstd:")){
		text = "Deviation of the methylation ratios of CpGs";
	}else if (prefix == "Ersc:"){
		text = "Region score";
	}else if (prefix == "Erst:"){
		text = "Region strand";
	}else{
		text = prefix;
	}
	return text;
}

function getTypeForFeaturePrefix(prefix){
	var featureType;
	if (prefix.startsWith("Elength_magnitude")){
		featureType = "featureRange";
	}else if (prefix.startsWith("Emmd:")){
		featureType = "featureRange";
	}else if (prefix.startsWith("Emud:")){
		featureType = "featureRange";
	}else if (prefix.startsWith("Emdd:")){
		featureType = "featureRange";
	}else if (prefix.startsWith("Echr:")){
		featureType = "featureText";
	}else if (prefix.startsWith("Erst:")){
		featureType = "featureText";
	}else if (prefix.startsWith("-OVERLAP:")){
		featureType = "featureText";
	}else if (prefix.startsWith("OVERLAP:")){
		featureType = "featureText";
	}else if (prefix.startsWith("Eor:")){
		featureType = "featureRatio";
	}else if (prefix.startsWith("Ehyper:")){
		featureType = "featureRatio";
	}else if (prefix.startsWith("Ehypo:")){
		featureType = "featureRatio";
	}else if (prefix.startsWith("Erank:")){
		featureType = "featureRatio";
	}else if (prefix.startsWith("Ersc:")){
		featureType = "featureRatio";
	}else if (prefix.startsWith("Ednaseq:")){
		featureType = "featureRatio";
	}else if (prefix.startsWith("EmethR")){
		featureType = "featureRatio";
	}else if (prefix.startsWith("EmethCpG")){
		//featureType = "featureRange";
		featureType = "featureRatio";
	}else if (prefix.startsWith("Enbh:")){
		featureType = "featureNeighborhood";
	}else if (prefix.startsWith("GO:")){
		featureType = "featureTable";
	}else if (prefix.startsWith("GENENAME:")){
		featureType = "featureTable";
	}else if (prefix.startsWith("OMIM:")){
		featureType = "featureTable";
	}else if (prefix.startsWith("regionList:")){
		featureType = "featureRegionsList";
	}
	return featureType;
}
function getTissueDescription(tissue){
	var tissueStr = {
		"NHLF":"NHLF (Normal Lung Fibroblasts)",
		"NHEK":"NHEK (Normal Epidermal Keratinocytes)",
		"K562":"K562 (Leukemia)",
		"HUVEC":"HUVEC (Umbilical Vein Endothelial Cell)",
		"NSMM":"NSMM (Normal Skeletal Muscle Myoblasts)",
		"HMEC":"HMEC (Mammary Epithelial Cells)",
		"HepG2":"HepG2 (Liver Carcinoma)",
		"H1hESC":"H1-hESC (Human Embryonic Stem Cells)",
		"GM12878":"GM12878 (Lymphoblastoid)"
	};
	var tissueDesc;
	if (tissueStr[tissue] !== undefined){
		tissueDesc = tissueStr[tissue];
	}else{
		tissueDesc = tissue;
	}
	return tissueDesc;
}

function initDatasets(){
	$.ajax({
			type: "GET",
			url: "relay.php",
			dataType: "json",
			async:false,
			data: "type=getDatasetInfo&datasetName=all&properties=description;officialName;categories;overlappingText",
			success: function (result){
				$.each(result,function(datasetID,datasetNameDict){
					featureGroupDescription[datasetID] = datasetNameDict["description"];
					featureGroupNames[datasetID] = datasetNameDict["officialName"];
					featureGroupCategories[datasetID] = datasetNameDict["categories"];
					overlapMarks[datasetID] = datasetNameDict["overlappingText"];

				});
			}
		});
}

function initDatasetCoverage(genome, datasetName){
	$.ajax({
			type: "GET",
			url: "relay.php",
			dataType: "json",
			async:false,
			data: "type=getCoverages&genome="+genome+"&regiontype="+datasetName,
			success: function (result){
				$.each(result,function(datasetSimpleName,coverage){
					if (typeof currentState["datasetInfo"][datasetSimpleName] == 'undefined') {
						currentState["datasetInfo"][datasetSimpleName] = {};
					}
					currentState["datasetInfo"][datasetSimpleName]["coverage"] = coverage;
				});
			}
		});
}

var datasetDescriptionCache = {}
function getDatasetDescription(datasetName){
	if (typeof datasetDescriptionCache[datasetName] == 'undefined') {
		$.ajax({
			type: "GET",
			url: "relay.php",
			dataType: "json",
			async:false,
			data: "type=getDatasetDescriptions&dataset="+datasetName,
			success: function (result){
				datasetDescriptionCache[datasetName] = result;
			},
		});
	}
	info = datasetDescriptionCache[datasetName];
	info["ini_description"] = getDescriptionForFeatureGroup(datasetName);
	return  info;
}

function buildDescription(info) {
	var result = "";

	var description = "";
	if (info["histonemark_info"] != undefined) {
		description = info["histonemark_description"];
	} else if (info["description"] != undefined) {
		description = info["description"];
	}

	if (description != "") {
		result += "<b>Data description</b>: ";
		result += description;
		result += "</br>";
		result += "</br>";
	}
	//sometimes this description is the same as the above description
	if (info["ini_description"] != undefined && description != info["ini_description"]) {
		result += "<b>Description</b>: ";
		result += info["ini_description"];
		result += "</br>";
		result += "</br>";
	}

	if (info["processed"] != undefined) {
		result += "<b>EpiExplorer processing</b>: ";
		result += info["processed"];
		result += "</br>";
		result += "</br>";
	}

	if (info["tissues_descriptions"] != undefined) {
		result += "<b>Tissues description and protocol:</b>";
		result += "<table border=\"0\">";
		result += "<tr><th><b>Name</b></th><th><b>Description</b></th>";
		if (info["dataURL"] != undefined) {
			result += "<th><b>Raw Data</b>";
			if (info["data_date"] != undefined) {
				result += " (downloaded on ";
				result += info["data_date"];
				result += ")";
			}
			result += "<th><b>Protocol</b></th></th>";
		}
		result += "</tr>";
		$.each(info["tissues_descriptions"], function(tissue, description) {
			result += "<tr>";
			result += "<td>"+tissue+"</td>";
			result += "<td>"+description+"</td>";
			details = info["tissues_details"][tissue];
			result += "</td>";
			if (info["dataURL"] != undefined && (info["dataURL"][tissue] != undefined  || info["dataURL"]["any"])) {
				result += "<td>";
				if (info["dataURL"][tissue] != undefined) {
					result += "<a href=\""+info["dataURL"][tissue]+"\">data</a></br>";
				} else {
					result += "<a href=\""+info["dataURL"]["any"]+"\">data</a></br>";
				}
				result += "</td>";
			}
			result += "<td>";
			for (i = 0; i < details.length; i++ ) {
				result += "<a href=\""+details[i][1]+"\">"+details[i][0]+"</a></br>";
			}
			result += "</td>";
			result += "</tr>";
		});
		result  += "</table>";
		result += "</br>";
	}
	return result;
}

function hasDatasetInfo(datasetName,datasetProperty){
	if (currentState["datasetInfo"][datasetName] == undefined) {
		return false;
	}else if (currentState["datasetInfo"][datasetName][datasetProperty] == undefined){
		return false;
	}else{
		return true;
	}
}

var textStyles = {"legend":{
				fontName : 'Verdana',//"Tahoma"
				fontSize : 13
			},
			"mainTitle":{
				fontName : 'Verdana',//"Tahoma"
				fontSize : 15
			},
			"axisTitle":{
				fontName : 'Verdana',//"Tahoma"
				fontSize : 13,
				italic : false
			},
			"axisText":{
				fontName : "Tahoma",
				fontSize : 11
			}}
