<?php
  require_once("grab_globals.lib.php");  
  include("xmlrpc_submit.php");
  include("settings.php");
  include("utils.php");
  require_once 'phpJSON/JSON.php';
  
  
  header('Content-Type: text/html'); // plain html file	
  if (isset($_GET['datasetID'])) {
  	$datasetID = $_GET['datasetID'];
  	// This part send a request for basic information for the regions supported by the current started server
	$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requests the status for dataset:'$datasetID' "));
    sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
    $xmlRequest = xmlrpc_encode_request('getDatasetStatus', array($datasetID));
  	$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);  	
  	if ($arrayResponse[0] == 0){
  		echo "Your dataset was successfully processed and is ready to use! <br/><br/>You can access it directly <a href='index.php?userdatasets=$datasetID' target='_blank'>here</a> or load it from the <a href=\"index.php\" target='_blank'>EpiExplorer</a> menu using its unique identifier <b>$datasetID</b>";  		
  	}else if ($arrayResponse[0] == 1){
  		echo "Your dataset is annotated by EpiExplorer at the moment! <br/><b>".$arrayResponse[1]."</b><br/> Please check again later.<br/> <i>We recommend providing your email for dataset computation as you will receive an automatic notification as soon as your dataset is processed.</i>";
  	}else if ($arrayResponse[0] == 2){
  		if (count($arrayResponse) > 1){
  			echo "Your dataset is still in the waiting queue.<br/> There are ".$arrayResponse[1]." computations scheduled before it.<br/><br/> Please check again later. <br/><i>We recommend providing your email for dataset computation as you will receive an automatic notification as soon as your dataset is processed.</i>'";
  		}else{
  			echo "Your dataset is still in the waiting queue.<br/><br/> Please check again later. <br/><i>We recommend providing your email for dataset computation as you will receive an automatic notification as soon as your dataset is processed.</i>'";
  		}
  	}else if ($arrayResponse[0] == 3){  		
  		echo "There was an error when processing your dataset.<br/><br/> The error message was '".$arrayResponse[1]."'<br/><br/> If the error message is unclear please contact us for more information at epiexplorer@mpi-inf.mpg.de";	
  	}else if ($arrayResponse[0] == -1){
  		echo "No such dataset!";
  	}
  }else{
  	echo "Error: No dataset identifier provided!";
  }  
?>