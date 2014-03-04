<?php
function checkRequestID($requestID){
	if (strlen($requestID) == 15){		
		if( intval($requestID[2])+ intval($requestID[11]) == 9){
			return true;
		}
	}
	return false;		
}

function generateRequestID(){
	$id = "";
	for ($i = 1; $i <= 15; $i++) {
    	$id = $id.strval(rand(0,9));
	}
	$e1 = rand(0,9);
	$e2 = 9 - $e1;
	$id[2] = strval($e1);
	$id[11] = strval($e2);
	return $id;
}
$id = generateRequestID();
echo $id."<br>";
echo "'".checkRequestID($id)."'<br>";
?>