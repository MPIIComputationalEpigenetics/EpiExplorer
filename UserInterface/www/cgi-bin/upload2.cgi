#!/usr/bin/python

print "Content-Type: text/html\n\n"     # HTML is following

import cgi
import xmlrpclib
import os
#import urllib

#u = urllib.urlopen("http://epiexplorer.mpi-inf.mpg.de/server.php")
#s = u.readline()
#s = "http://" + s;
s = "http://" + os.environ["forwardServerHost"] + ":" + os.environ["forwardServerPort"]

# Change this to read forwardServer.ini, which should be written by CGSServer init to
# a file in the web hierarchy, preferable not something that is publicly visible!



server = xmlrpclib.Server(s)

#cgi.print_environ()
#print os.environ["SERVER_NAME"]

form = cgi.FieldStorage()

def checkEmail(email):
	return True
def checkDatasetName(datasetName):
	return True

def processAnnotationSettings(annotationSettingsText):
	annotationParts = annotationSettingsText.split(",")
	annotationSettings = {}
	if annotationSettingsText == "":
		return annotationSettings
	for annotationPart in annotationParts:
		annotation = annotationPart.split(":")
		if len(annotation) == 3:
			if not annotationSettings.has_key(annotation[0]):
				 annotationSettings[annotation[0]] = {}
			annotationSettings[annotation[0]][annotation[1]] = bool(int(annotation[2]))

	return annotationSettings

def main():
	if not checkEmail(form["email"].value):
		statusText = "Invalid email address! Please provide a valid email, otherwise you will not be able to use your dataset";
		return [1,statusText]
	#print "1. Email check passed<br>"
	if not checkDatasetName(form["datasetName"].value):
		statusText = "Invalid dataset name! Please provide a dataset name"
		return [1,statusText]
	#print "2. Dataset name passed<br>"
	fileContent = form["datasetUploadedFile"].file.read()
	if len(form['dataList'].value) == 0 and not len(fileContent):
	   statusText = "Please provide a dataset, either as file, or as plain text"
	   return [1,statusText]
	#print "3. Dataset data passed <br>"
	##The contents look in order now send it to the backend server
	if len(fileContent):
		#print "Read from file <br>"
		regionsContent = fileContent
	elif len(form['dataList'].value) > 0:
		#print "Read from textarea <br>"
		regionsContent = form['dataList'].value

	if len(regionsContent) == 0:
		statusText = "Error: We could not receive your dataset. Please make sure it does not exceed the current limit of 100MB. For uploading a larger file, you can contact the EpiExplorer support team at epiexplorer@mpi-inf.mpg.de "
		return [1,statusText]
	else:
		#print "4. Data was successfully read: ",len(regionsContent)," <br>"
		if form.has_key("datasetConvertSpacesToTabs") and str(form["datasetConvertSpacesToTabs"].value)=="on":
			import re
			regionsContent = re.sub(" +", "\t", regionsContent)
		#print "4.0"
		computeSettings = {}
		for cs in ["computeReference","mergeOverlaps","useScore","useStrand","ignoreNonStandardChromosomes"]:
			#compute reference
			computeSettings[cs]= False
			if form.has_key(cs) and str(form[cs].value)=="on":
				computeSettings[cs] = True
		if "mpiat3502.ag3.mpi-sb.mpg.de" in os.environ["SERVER_NAME"] or "moebius.ag3.mpi-sb.mpg.de" in os.environ["SERVER_NAME"]:
			# Submissions from the internal web server are unlimmited
			# mpiat3502.ag3.mpi-sb.mpg.de/cosgen
			# http://moebius.ag3.mpi-sb.mpg.de/epiexplorer/
			computeSettings["noLineLimit"] = True
		else:
			# Submissions from the external web server are limmited
			computeSettings["noLineLimit"] = False
		#print "4.1",computeSettings
		#process the additional settings
		annotationSettings = {}
		if form["fullSettings"].value:
			annotationSettings = processAnnotationSettings(form["fullSettings"].value)
		#print "4.2"
		genomeValue = "hg18"
		if form.has_key("genomeSelect") and form["genomeSelect"].value:
			genomeValue = str(form["genomeSelect"].value)
    	#print "4.3 Genome:",genomeValue
		#log the request
		logmeData = str(cgi.escape(os.environ["REMOTE_ADDR"]))+" uploads a dataset named "+str(form["datasetName"].value)+" of size "+str(len(regionsContent))+" for genome "+str(genomeValue)+" and provided email: "+str(form["email"].value)+" with dataset description '"+str(form["datasetDesc"].value)+"' and annotation settings '"+str(annotationSettings)+"' computeSettings="+str(computeSettings)
		#print "5. logme about to be send "+str(logmeData)+"<br>"
		server.log_me(logmeData)
		#print "6. logme success<br>"
    	# send the actual request $_POST['datasetName'],$regionsContent,$_POST['genomeSelect'],$_POST['email'],False,"",$_POST['datasetDesc']
    	try:
    	   arrayResponse = server.processUserDatasetFromBuffer(str(form["datasetName"].value),
														    regionsContent,
														    str(genomeValue),
														    annotationSettings ,
														    str(form["email"].value),
														    False,
														    "",
														    str(form["datasetDesc"].value),
														    computeSettings)
    	except Exception,ex:
    		arrayResponse = [1,str(ex)]

    	#print "7. send request success<br>"
    	if arrayResponse[0] == 1:
    		statusText = "<b>ERROR</b><br>\nError message: "+str(arrayResponse[1])
    		return arrayResponse
    	else:
    		if arrayResponse[2] > 0:
    			statusText = '<div style="color:#00FF00;"><b>Success! Your dataset is being processed ('+str(arrayResponse[2])+' lines omitted).</b><br><br>\n'
    		else:
    			statusText = '<div style="color:#00FF00;"><b>Success! Your dataset is being processed.</b><br><br>\n'

    		if len(form["email"].value) > 0:
    		    statusText += '</div><b>You will receive an email with the dataset information when it is ready</b><br/><br/>'
    		    statusText += '<br>You can check the status of your dataset computation at the following link:<br/>\n'
    		else:
    			statusText += '</div><b><div style="color:#FF0000;">IMPORTANT</div> Make sure to store the link below as it will be updated with instructions about how to access your dataset once it is fully processed. <br/>Since you chose not to provide an email this is the only way to notify you when the dataset is ready!</b><br/><br/>\n'
    			statusText += '<br>The status of your dataset computation will be updated automatically at the following link:<br/>\n'

    		#link = 'checkDatasetStatus.php?datasetId=aaa'+arrayResponse[3]
    		link = 'http://epiexplorer.mpi-inf.mpg.de/checkDatasetStatus.php?datasetID='+str(arrayResponse[1])
    		statusText += '<a href="'+link+'" target="_blank">Dataset</a><br/>\n'
    		if computeSettings["computeReference"]:
    			refNameR = arrayResponse[1].rfind("_")
    			refName = arrayResponse[1][:refNameR]+"_ref"+arrayResponse[1][refNameR:]
    			refLink = 'http://epiexplorer.mpi-inf.mpg.de/checkDatasetStatus.php?datasetID='+str(refName)
    			statusText += '<a href="'+refLink+'" target="_blank">Reference</a><br/>\n'
    		return [0,statusText]
	return statusText

status = main()
#print '<h1>' , s , '</h1>'
if status[0] == 1:
	#error
	print '<h4 style="color:#FF0000;">',status[1],'</h4>'
else:
	print '<h4>',status[1],'</h4>'
