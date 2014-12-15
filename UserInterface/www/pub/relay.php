<?php
  require_once("grab_globals.lib.php");  
  include("xmlrpc_submit.php");
  include("settings.php");
  include("utils.php");
  require_once 'phpJSON/JSON.php';
   
$xmlrpc_output_options = array( 
	#			"output_type" => "xml", 
	#			"verbosity" => "no_white_space", 
	#			"escaping" => array("markup", "non-ascii", "non-print"), 
				"version" => "xmlrpc", 
				"encoding" => "ISO-8859-1");
				
  				
  function epiSendRequestDebug($host, $url, $request, $port = 80) {

      error_reporting(E_ALL);
	    
    $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
    if ($socket === false) {
    	echo "socket_create() failed: reason: " . socket_strerror(socket_last_error()) . "\n";
    	return FALSE;
    }    

    $address = gethostbyname($host);     
    if (!socket_connect ($socket, $address, $port)) {
    	echo socket_strerror(socket_last_error());
    	return FALSE; 
    }
    
    $httpQuery = "POST ". $url ." HTTP/1.0\r\n";
    $httpQuery .= "User-Agent: xmlrpc\r\n";
    $httpQuery .= "Host: ". $host ."\r\n";
    $httpQuery .= "Content-Type: text/xml\r\n";
    $httpQuery .= "Content-Length: ". strlen($request) ."\r\n\r\n";
    $httpQuery .= $request ."\r\n";

    //echo $httpQuery;

    $httpQuery= utf8_encode($httpQuery);

    if (!socket_send($socket, $httpQuery , strlen($httpQuery), 0)) {
    	echo socket_strerror(socket_last_error());
    	return FALSE;
    }

    $xmlResponse = "";
    $buff = "";
    while ($bytes = socket_recv($socket, $buff, 1024, MSG_WAITALL) > 0) {
        $xmlResponse .= $buff;
      //  echo $buff;
    }

#    echo "socket_recv() failed; reason: " . socket_strerror(socket_last_error($socket)) . "\n";

    socket_close($socket);

    $logxmlRequest = xmlrpc_encode_request('log_me', array("response: ".$xmlResponse.":-)"));
    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
    $xmlResponse = substr($xmlResponse, strpos($xmlResponse, "\r\n\r\n") +4);     
    $xmlResponse = xmlrpc_decode($xmlResponse);

    // Returns the result.
    return  $xmlResponse;
}				

     
  if (isset($_GET['type'])) {
  	$queryType =  $_GET['type']; 	
	
  	if ( $queryType == "regiontypes"){
  		$sourceType = $_GET['sourceType'];  		
  		$genome = $_GET['genome'];
  		// This part send a request for basic information for the regions supported by the current started server
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requests the active servers of type $sourceType for genome $genome "));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    if ($sourceType == "baseExplore"){
  			$xmlRequest = xmlrpc_encode_request('getActiveServers', array($genome, true));
  			$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	    }else if ($sourceType == "exploreII27"){
	    	$xmlRequest = xmlrpc_encode_request('getActiveServers', array($genome, false,"II27"));
  			$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	    }else{
	    	$arrayResponse = "Invalid source type ".$sourceType;
	    }
		echo json_encode($arrayResponse);

  	}else if ($queryType == "logPageView"){
  		$regionType = $_GET['regionType'];
  		$visType = $_GET['visType'];
  		$genome = $_GET['genome'];
  		$tissueType = $_GET['tissueType'];
  		$overlapType = $_GET['overlapType'];
  		$summaryChartType = $_GET['summaryChartType'];
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." vislogged VISTYPE=(".$visType."):SUMMARYCHARTTYPE=(".$summaryChartType."):OVERLAP=(".$overlapType."):TISSUE=(".$tissueType."):REGIONSET=(".$regionType."):GENOME=(".$genome.")" ));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);  		  	
  	}else if ($queryType == "getfeaturesOld"){
  		$regionType = $_GET['regiontype'];
  		$genome = $_GET['genome'];
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested all features for regiontype ".$regionType));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
  		if ($regionType == "exploreII27"){
  			$features = file_get_contents('./hg18_features_II27.txt');  				
			echo $features;
  		}else{
  			$features = file_get_contents('./'.$genome.'_features_temp.txt');	
			echo $features;
  		}  	
  	}else if ($queryType == "getfeatures"){  		
  		$genome = $_GET['genome'];
  		$regionType = $_GET['regiontype'];
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested all features for $genome regiontype $regionType"));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    $xmlRequest = xmlrpc_encode_request('getVisualizationFeatures', array($genome, $regionType));
  		$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
  		echo json_encode($arrayResponse);
  	
  	} else if ($queryType == "getCoverages"){  		
  		$genome = $_GET['genome'];
  		$regionType = $_GET['regiontype'];  	
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested all features for $genome regiontype $regionType"));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    $xmlRequest = xmlrpc_encode_request('getCoverages', array($genome, $regionType));
  		$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
  		echo json_encode($arrayResponse);
  		
	}else if ($queryType == "getDatasetDescriptions"){  		
  		$dataset = $_GET['dataset'];
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." Dataset Descriptions for $dataset "));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	   	$xmlRequest = xmlrpc_encode_request('getDatasetDescriptions', array($dataset));
  		$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
  		echo json_encode($arrayResponse);  		
  		
  	}else if ($queryType == "getGeneExtraInfoDebug"){
			$genome = "hg19";
			$infoType = "GO";			
			$elements = array('GO:0044428', 'GO:0044422', 'GO:0044425', 'GO:0044424', 'GO:0043412', 'GO:0006464', 'GO:0009889', 'GO:0003824', 'GO:0016020', 'GO:0016021', 'GO:0048522', 'GO:0048523', 'GO:0090304', 'GO:0019538', 'GO:0051171', 'GO:0001882', 'GO:0001883', 'GO:0080090', 'GO:0042221', 'GO:0048869', 'GO:0019222', 'GO:0005488', 'GO:0005886', 'GO:0005524', 'GO:0031090', 'GO:0050896', 'GO:0010556', 'GO:0010468', 'GO:0016740', 'GO:0003677', 'GO:2000112', 'GO:0005622', 'GO:0019219', 'GO:0006139', 'GO:0032502', 'GO:0032501', 'GO:0050794', 'GO:0009058', 'GO:0032991', 'GO:0044249', 'GO:0044260', 'GO:0044267', 'GO:0035639', 'GO:0009987', 'GO:0044464', 'GO:0051252', 'GO:0043170', 'GO:0005634', 'GO:0005737', 'GO:0050789', 'GO:0031326', 'GO:0051716', 'GO:0016787', 'GO:0031323', 'GO:0006810', 'GO:0048856', 'GO:0065007', 'GO:0043227', 'GO:0043167', 'GO:0044459', 'GO:0043169', 'GO:0008150', 'GO:0008152', 'GO:0006355', 'GO:0005575', 'GO:0046914', 'GO:0003674', 'GO:0006807', 'GO:0003676', 'GO:0044446', 'GO:0044444', 'GO:0051234', 'GO:0032555', 'GO:0043228', 'GO:0043229', 'GO:0043226', 'GO:0045449', 'GO:0032559', 'GO:0031224', 'GO:0017076', 'GO:0071842', 'GO:0071841', 'GO:0071840', 'GO:0060255', 'GO:0016043', 'GO:0034641', 'GO:0008270', 'GO:0000166', 'GO:0046872', 'GO:0044237', 'GO:0044238', 'GO:0043234', 'GO:0043231', 'GO:0043232', 'GO:0032553', 'GO:0005515', 'GO:0007165', 'GO:0048519', 'GO:0048518', 'GO:0030554');
					  			
	  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested getGeneExtraInfo for $genome $infoType $elements"));
		    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
		    		    		   
		    $xmlRequest = xmlrpc_encode_request('getGeneExtraInfo', array($genome,$infoType,$elements), $xmlrpc_output_options);
			$arrayResponse = epiSendRequestDebug($rpc_server, '/', $xmlRequest, $rpc_port);		
			echo json_encode($arrayResponse);		  		  		  	  
  		  		
  	}else if ($queryType == "basequery"){
  		$query =  $_GET['query'];
  		$regionType = $_GET['regiontype'];
  		if (isset($_GET['ncompl'])){
  			$nc = $_GET['ncompl'];  			
  		}else{
  			$nc = "10";
  		}
  		if (isset($_GET['nhits'])){
  			$nh = $_GET['nhits'];
  		}else{
  			$nh = "10";
  		}
  		$extraSettings = $_GET['extraSettings'];
  		//query, completions,hits, selectedRegionsSet
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." sends a query ".$query." with ".$nc." completions and ".$nh." hits for regiontype ".$regionType));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
  		$xmlRequest = xmlrpc_encode_request('answerQuery', array($query,$nc,$nh,$regionType,$extraSettings));
  		$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
  		print("query\t".$arrayResponse[0]."\n");
  		print("nc\t".$arrayResponse[1]."\n");
  		print("nh\t".$arrayResponse[2]."\n");
  		arsort($arrayResponse[3]);
  		foreach ($arrayResponse[3] as $completion => $noDocuments) {  			
    		print("completion\t".$completion."\t".$noDocuments."\n");
			}
			foreach ($arrayResponse[4] as $title => $url) {  			
	    		print("hits\t".$title."\t".$url."\n");
			}
  		//print_r($arrayResponse);
  	}else if ($queryType == "basequeryJSON"){
  		$query =  $_GET['query'];
  		$regionType = $_GET['regiontype'];
  		if (isset($_GET['ncompl'])){
  			$nc = $_GET['ncompl'];  			
  		}else{
  			$nc = "10";
  		}
  		if (isset($_GET['nhits'])){
  			$nh = $_GET['nhits'];
  		}else{
  			$nh = "10";
  		}
  		$extraSettings = str_replace("%26","&",$_GET['extraSettings']);
  		//query, completions,hits, selectedRegionsSet
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." sends a query ".$query." with ".$nc." completions and ".$nh." hits for regiontype ".$regionType));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    
  		$xmlRequest = xmlrpc_encode_request('answerQuery', array($query,$nc,$nh,$regionType,$extraSettings));
  		$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
  		//returns (self.query,self.totalCompletions,self.totalHits,self.completions,self.hits) 
  		echo json_encode( $arrayResponse);	

  	}else if ($queryType == "basequeryRaw"){
  		/*//Currently not used
  		$query =  $_GET['query'];  		
  		
  		if (isset($_GET['port'])){
  			$port = $_GET['port'];  			
  		}else{
  			$port = "8801";
  		}
  		if (isset($_GET['host'])){
  			$host = $_GET['host'];  			
  		}else{
  			$host = "infao3806";
  		}
  		if (isset($_GET['ncompl'])){
  			$nc = $_GET['ncompl'];  			
  		}else{
  			$nc = "10";
  		}
  		if (isset($_GET['nhits'])){
  			$nh = $_GET['nhits'];
  		}else{
  			$nh = "0";
  		}
  		$fullQuery = "http://$host:$port/?q=$query&h=$nh&c=$nc"; 
  		$xmlRequest = xmlrpc_encode_request('answerQueryRaw', array($fullQuery));
  		$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
  		//returns (self.query,self.totalCompletions,self.totalHits,self.completions,self.hits) 
  		print_r($arrayResponse);
  		*/

  	}else if ($queryType == "exportRegions"){
  		$query =  $_GET['query'];
  		$regionType = $_GET['regiontype'];
  		$mail = $_GET['mail'];
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested exportRegions for ".$regionType." with query ".$query." to email ".$mail));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    $xmlRequest = xmlrpc_encode_request('exportQueryRegions', array($regionType,$query,$mail));
	    sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
  		echo "The dataset is being computed. You will be notified via email when it is ready!";  		
  	}else if ($queryType == "exportRegionsAndSendBack"){
  		$regionType = $_GET['regiontype'];
  		$query =  $_GET['query'];  	
  		if (isset($_GET['exportType'])){
  			$exportType = $_GET['exportType'];
  			$genome = $_GET['genome'];
  			if ($exportType == "GALAXY"){
  				$datasetURL = str_replace("exportType=GALAXY","exportType=URL","http://".$_SERVER['SERVER_NAME'].$_SERVER['REQUEST_URI']);
  				$datasetURL = str_replace("&","&amp;",$datasetURL);
  				echo "<html><body>Automated export to Galaxy is under development and will be available soon. <br><br> In the meantime, the following work-around will transfer region sets from EpiExplorer into Galaxy:  <br><ol><li>Copy the following link to the tab-separated dataset into the clipboard: <br><a href=\"$datasetURL\"><code><code>$datasetURL</code></a></li><br><li>Paste this link into the 'URL/Text' field of the <a href=\"http://main.g2.bx.psu.edu/root?tool_id=upload1\" target=\"_blank\">Galaxy upload tool</a><br></li><li>Set 'file format' to 'bed' and 'genome' to '$genome'<br/></li><li>Press the 'Execute' button to import the region file into Galaxy<br></li></ol></body></html>";
  				return;
  			}else if ($exportType == "HYPERBROWSER"){
  				$datasetURL = str_replace("exportType=HYPERBROWSER","exportType=URL","http://".$_SERVER['SERVER_NAME'].$_SERVER['REQUEST_URI']);
  				$datasetURL = str_replace("&","&amp;",$datasetURL);
  				echo "<html><body>Automated export to the Genomic HyperBrowser is under development and will be available soon.<br><br>In the meantime, the following work-around will transfer region sets from EpiExplorer into the Genomic HyperBrowser:<br><ol><li>Copy the following link to the tab-separated dataset into the clipboard: <br><a href=\"$datasetURL\"><code>$datasetURL</code></a></li><br><li>Paste this link into the 'URL/Text' field of the <a href=\"http://hyperbrowser.uio.no/hb/root?tool_id=upload1\" target=\"_blank\">Genomic HyperBrowser upload tool</a><br></li><li>Set 'file format' to 'bed' and 'genome' to '$genome'<br/></li><li>Press the 'Execute' button to import the region file into the Genomic HyperBrowser<br></li></ol></body></html>";
  				return;
  			}else if ($exportType == "ENSEMBL"){
  				$genome = $_GET['genome'];
  				
  				if ($genome == "hg18"){
  					$baseExportURL = "http://may2009.archive.ensembl.org/Homo_sapiens/UserData/SelectFile?db=core"; 
  				}else if ($genome == "hg19"){
  					$baseExportURL = "http://www.ensembl.org/Homo_sapiens/UserData/SelectFile?db=core";
  				}else if ($genome == "mm9"){
  					$baseExportURL = "http://www.ensembl.org/Mus_musculus/UserData/SelectFile?db=core";
  				}
  				
  				$datasetURL = str_replace("exportType=ENSEMBL","exportType=UCSC","http://".$_SERVER['SERVER_NAME'].$_SERVER['REQUEST_URI']);
  				$datasetURL = str_replace("&","&amp;",$datasetURL);
  				echo "<html><body>Automated export to the Ensembl is under development and will be available soon.<br><br>In the meantime, the following work-around will transfer region sets from EpiExplorer into Ensembl:<br><ol><li>Copy the following link to the tab-separated dataset into the clipboard: <br><a href=\"$datasetURL\"><code>$datasetURL</code></a></li><br><li>Paste this link into the 'File URL' field of the <a href=\"$baseExportURL\" target=\"_blank\">Ensembl upload form</a><br></li><li>Set 'Data format' to 'bed' and add a name for this dataset'<br/></li><li>Press the 'Upload' button to import the region file into Ensembl<br></li></ol></body></html>";
  				return;
  			}
  		}else{
  			$exportType = "URL";
  		} 		
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested exportRegionsAndSendBack for ".$regionType." export of type ".$exportType." with query ".$query));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    $xmlRequest = xmlrpc_encode_request('exportQueryRegionAndSendBack', array($regionType,$query,$exportType));
	    $arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	    if ($exportType == "URL" || $exportType == "UCSC" || $exportType == "GALAXY" || $exportType == "HYPERBROWSER"){
	    	header('Content-Type: text/plain'); // plain text file	
	    }else if ($exportType == "TEXTFILE"){
	    	header('Content-disposition: attachment; filename=.EpiExplorerExport.txt');
	    	header('Content-Type: application/force-download');
			header('Content-Type: application/octet-stream');
			header('Content-Type: application/download');
			header('Content-Description: File Transfer');
	    }
	    	    	    
  		echo $arrayResponse;  		
  	}else if ($queryType == "exportGenesAndSendBack"){
  		$regionType = $_GET['regiontype'];
  		$query =  $_GET['query'];  		  		
  		$exportType =  $_GET['exportType'];
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested exportGenesAndSendBack for ".$regionType." with query ".$query." of type ".$exportType));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    $xmlRequest = xmlrpc_encode_request('exportGenesAndSendBack', array($regionType,$query,$exportType));
	    $arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	    header('Content-Type: text/plain'); // plain text file	    	    
  		echo $arrayResponse;  		
  	}else if ($queryType == "exportGOsAndSendBack"){
  		$regionType = $_GET['regiontype'];
  		$query =  $_GET['query'];  		  		
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested exportGOsAndSendBack for ".$regionType." with query ".$query));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    $xmlRequest = xmlrpc_encode_request('exportGOsAndSendBack', array($regionType,$query));
	    $arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	    header('Content-Type: text/plain'); // plain text file	    	    
  		echo $arrayResponse;  		
  	}else if ($queryType == "exportGOTermsAndSendBack"){
  		$regionType = $_GET['regiontype'];
  		$query =  $_GET['query'];  		  		
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested exportGOTermsAndSendBack for ".$regionType." with query ".$query));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    $xmlRequest = xmlrpc_encode_request('exportGOTermsAndSendBack', array($regionType,$query));
	    $arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	    header('Content-Type: text/plain'); // plain text file	    	    
  		echo $arrayResponse;  		
  	}else if ($queryType == "exportOMIMTermsAndSendBack"){
  		$regionType = $_GET['regiontype'];
  		$query =  $_GET['query'];  		  		
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested exportOMIMTermsAndSendBack for ".$regionType." with query ".$query));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    $xmlRequest = xmlrpc_encode_request('exportOMIMTermsAndSendBack', array($regionType,$query));
	    $arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	    header('Content-Type: text/plain'); // plain text file	    	    
  		echo $arrayResponse;  		
  	}else if ($queryType == "activateUserDataset"){
  		$datasetID = $_GET['datasetID'];
			$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." activates a dataset named $datasetID"));
	    	sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
			//echo "Dataset ID is ".$_POST['datasetID']."<br/>";
			$xmlRequest = xmlrpc_encode_request('activateUserDataset', array($datasetID));
			$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
			
			if ($arrayResponse[0] == 1){
				// Error				
				echo json_encode( array($arrayResponse[0],"Error:".$arrayResponse[1]));				
			}else{
				echo json_encode( array($arrayResponse[0],"OK: ".$arrayResponse[1],$arrayResponse[2]));				
			}	
  	}else if ($queryType == "exportQueryData"){  		
  		$query =  $_GET['query'];
  		$regionType = $_GET['regiontype'];
  		$mail = $_GET['mail'];
  		$datasets = $_GET['datasets'];
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested exportQueryData for ".$regionType." with query ".$query." to email ".$mail." for datasets ".$datasets));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    $xmlRequest = xmlrpc_encode_request('exportQueryData', array($regionType,$query,$mail,$datasets));
	    sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
  		echo "The dataset is being computed. You will be notified via email when it is ready!";  		  	
  	}else if ($queryType == "getFullLog"){ 		
  		if (isset($_GET['last'])){
  			$last = (int)$_GET['last'];  			
  		}else{
  			$last = 10000;
  		}
  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested the log (the last ".$last." chars)"));
	    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
  		$logFile = substr(file_get_contents('/TL/www/epiexplorer/CGS.log'),-1*$last);	  		
  		//echo $logFile;
  		echo str_replace("\n","<br>\n",htmlentities($logFile));  		
  	}else if ($queryType == "getDatasetInfo"){ 	
  			
  		if (isset($_GET['datasetName'])){
  			$dataset = $_GET['datasetName'];  			
  			$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." the dataset info for $dataset"));
	    	sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	    	if (isset($_GET['properties'])){  				
  				$xmlRequest = xmlrpc_encode_request('getDatasetInfo', array($dataset,explode(";",$_GET['properties'])));  			
  			}else{
  				$xmlRequest = xmlrpc_encode_request('getDatasetInfo', array($dataset));
  			}
			$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
			//if (count($arrayResponse) == 0){
			//	echo json_encode("No dataset named $dataset");
			//}else{
				echo json_encode($arrayResponse);
			//}
  			
  		}else{
  			echo json_encode("No dataset name!");
  		}  		
  		
  	}else if ($queryType == "getDefaultAnnotationSettings"){
  		$genome = "";
  		if (isset($_GET['genome'])){
  			$genome = $_GET['genome'];
  		}
  		$xmlRequest = xmlrpc_encode_request('getDatasetAnnotationSettings', array($genome,"",array("hasFeatures","useNeighborhood","patterns","includeGO","includeOMIM","includeGeneDescriptions")));
	    $arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
  		echo json_encode($arrayResponse);
  		
  	}else if ($queryType == "getLink"){  	
	  	$xmlRequest = xmlrpc_encode_request('getSelectionLink', array(array($_GET["genome"],$_GET["currentSelection"],$_GET["currentQuery"],$_GET["currentView"],$_GET["rGenome"],$_GET["rSelection"],$_GET["rQuery"],$_GET["rNORegions"])));	  	
		$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
		//echo json_encode(array("0","aaaaaaa"));
	  	echo json_encode($arrayResponse);  	
	  
	  }else if ($queryType == "getLinkData"){  	
	  	$xmlRequest = xmlrpc_encode_request('getLinkSelection', array($_GET["analysisLink"]));
		$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	  	echo json_encode($arrayResponse);  	
	  
	  }else{
  		echo "Invalid type'".$queryType."'";
  	}
  	
  }else{
  	if (isset($_POST['type'])) {
  		$posttype = $_POST['type'];   		
  		if ($posttype == "feedback"){
  			$name = htmlentities($_POST['name']);
  			$email = htmlentities($_POST['email']);
  			$ftype = htmlentities($_POST['ftype']);
  			$feedback = str_replace("\n"," \\\\ ",htmlentities($_POST['feedback']));
  			//echo "feedback is '$feedback'";
  			$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." ($name , $email) sends the $ftype feedback $feedback"));
  			sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
  			$xmlRequest = xmlrpc_encode_request('sendFeedbackEmail', array($ftype,$name,$email,$feedback));
  			$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);  			
  		}else if ($posttype == "searchSingle"){
  			$chrom = $_POST['chrom'];
  			$chromstart = $_POST['chromstart'];
  			$chromend = $_POST['chromend'];
  			$genome = $_POST['genome'];
  			$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." searchSingle for region ($chrom, $chromstart, $chromend)"));
  			sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
  			$xmlRequest = xmlrpc_encode_request('getGenomicRegionProperties', array($genome,array($chrom,$chromstart,$chromend)));
  			$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);  			
  			echo json_encode($arrayResponse);
		}else if ($posttype == "getGeneExtraInfo"){ 						
	  		if (isset($_POST['genome'])){
	  			$genome = $_POST['genome'];
	  		}
	  		if (isset($_POST['infoType'])){
	  			//currently accepts genes, GO and OMIM
	  			$infoType = $_POST['infoType'];
	  		}
	  		if (isset($_POST['elements'])){
	  			//coma separated values
	  			$elements = $_POST['elements'];
	  		}
	
	  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested getGeneExtraInfo for $genome $infoType $elements"));
		    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
		    // FA version testing the python2.5--xmlrpc--php bug
		    //$xmlRequest = xmlrpc_encode_request('getGeneExtraInfo', array($genome,$infoType,$elements), $xmlrpc_output_options);		   
			//$arrayResponse = epiSendRequestDebug($rpc_server, '/', $xmlRequest, $rpc_port);
			$xmlRequest = xmlrpc_encode_request('getGeneExtraInfo', array($genome,$infoType,$elements));
			$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);	
					
			echo json_encode($arrayResponse);		  		
  		
  		}else if ($posttype == "baseQueryPostJSON"){
	  		$query =  $_POST['query'];
	  		$regionType = $_POST['regiontype'];
	  		if (isset($_POST['ncompl'])){
	  			$nc = $_POST['ncompl'];  			
	  		}else{
	  			$nc = "10";
	  		}
	  		if (isset($_POST['nhits'])){
	  			$nh = $_POST['nhits'];
	  		}else{
	  			$nh = "10";
	  		}
	  		$extraSettings = str_replace("%26","&",$_POST['extraSettings']);
	  		//query, completions,hits, selectedRegionsSet
	  		$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." sends a query ".$query." with ".$nc." completions and ".$nh." hits for regiontype ".$regionType));
		    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
		    
	  		$xmlRequest = xmlrpc_encode_request('answerQuery', array($query,$nc,$nh,$regionType,$extraSettings));
	  		$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	  		//returns (self.query,self.totalCompletions,self.totalHits,self.completions,self.hits) 
	  		echo json_encode( $arrayResponse);	

          
    } else if ($posttype == "storeData"){
        $software = $_POST['software'];
        $name = $_FILES["data"]["name"];
        $data =file_get_contents($_FILES["data"]["tmp_name"]);
        $format = "BED";
        $logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." storing data ".$name." from software ".$software));
        sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
        
        $xmlRequest = xmlrpc_encode_request('storeData', array($name, $software, $format, $data));
        $arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
        echo json_encode( $arrayResponse);  

    } else if ($posttype == "processInfiniumDataset"){
        $file_id = $_POST['file_id'];
        $software = $_POST['software'];
        $referenceDataset = $_POST['reference_dataset'];
        $name = $_POST['name'];
        $scoresIndex = $_POST['scores_index'];
        $hypoIndex = $_POST['hypo_index'];
        $hyperIndex = $_POST['hyper_index'];
        $rankIndex = $_POST['rank_index'];
        $email = $_POST['email'];
        $moreInfoLink = $_POST['more_info_link'];
        $description = $_POST['description'];

        $logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." processing ".$name." from software ".$software));
        sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);

        $xmlRequest = xmlrpc_encode_request('processInfiniumDataset', array($file_id, $software, $referenceDataset, 
          $name, $scoresIndex, $hypoIndex, $hyperIndex, $rankIndex, $email, $moreInfoLink, $description  ));
        $arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
        echo json_encode( $arrayResponse);  
		}else{
  			echo "POST incorrect".$posttype;
		}
  	}else{
  		echo "Nothing selected. You must specify the 'type' parameter";
  	}  	
  }  	
?>
