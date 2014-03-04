<?php 
	require_once("grab_globals.lib.php");
  include("xmlrpc_submit.php");
  $rpc_server = 'infao3806';
  $rpc_dataset_port = '51525';
  $rpc_query_port = '51515';  
  
  if (isset($_GET["id"])){  	
  	$exportID =  $_GET["id"]; 
  	$logxmlRequest = xmlrpc_encode_request('log_me', array(anonimizedUser()." requested the exported dataset ". $exportID));
  	sendRequest($rpc_server, '/', $logxmlRequest, $rpc_dataset_port);
		
	$dir="/TL/www/cosgen/www/pub/Datasets/";
    $file=$dir.$exportID.".zip";    
      	
    if (file_exists($file)){
    	    // Generate the server headers
    	    header('Content-type: application/x-compressed'."\n");
    	    header('Content-type: application/zip'."\n");
 					header('Content-Disposition: filename="'.basename($file).'"');
 					header("Content-Transfer-Encoding: binary");
 					header('Accept-Ranges: bytes');
 					header('Content-length: '.filesize($file)."\n");
 
				 /* The three lines below basically make the 
				    download non-cacheable */
				 header("Cache-control: private");
				 header('Pragma: private');
				 header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");

				 @readfile($file);
				 die();
    }else{
    	echo "No file corresponding to id ".$exportID;
    }    
	}else{
    echo "No file selected";
	}	
?>