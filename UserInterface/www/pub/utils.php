<?php
 
 function anonimizedUser(){	
	$pattern = '/(\d+)\.(\d+)\.(\d+)\.(\d+)/i';
	$replacement = '${1}.${2}.${3}.XYZ';
	return preg_replace($pattern, $replacement, $_SERVER["REMOTE_ADDR"]);	
}
?>