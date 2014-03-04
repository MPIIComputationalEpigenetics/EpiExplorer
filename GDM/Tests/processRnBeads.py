import xmlrpclib
import socket
import time

#dataStorageServer = xmlrpclib.Server("http://localhost:51525",encoding='ISO-8859-1',allow_none=True)
#f = open("/Users/albrecht/data/forEpiExplorer/Nazor.iPSC.vs.ESC.txt", "r")
#f_data = f.read()
#file_id = dataStorageServer.store_data("Nazor.iPSC.vs.ESC", "test_data", "BED", f_data)
#print file_id

#f = open("/Users/albrecht/Downloads/Szulwach_5hmC_peaks_with_scores.bed", "r")
#buffer = f.read()
#computeSettings = {}
#computeSettings["useScore"] = True
#server.processUserDatasetFromBuffer("Szulwach", buffer, "hg18", {}, "albrecht@mpi-inf.mpg.de", True, "", "Super cool.", computeSettings)

#print "upload okay: " + file_id

#file_id = "Nazor.iPSC.vs.ESC_test_data_1354029116_207605"

#hyperIndex = 0
#hypoIndex = 1
#rankIndex = 2
#scoresIndex = 3

#datasetName = server.processInfiniumDataset(file_id, "test_data", "hg19_Infinium450CpGs", "Nazor.pluripotent.vs.diff",
#	scoresIndex, hypoIndex, hyperIndex, rankIndex, "blah@blah.blah", "", "")

#print datasetName

server = xmlrpclib.Server("http://shiva.local:51525",encoding='ISO-8859-1',allow_none=True)
datasets = ['hg19_rnbeads_cpgislands', 'hg19_rnbeads_genes', 'hg19_rnbeads_probes450', 'hg19_rnbeads_promoters', 'hg19_rnbeads_tiling']

for dataset in datasets:
	print "Processing " + dataset
	server.processInfinumReference(dataset, True, {})
