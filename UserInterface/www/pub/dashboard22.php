<?php

include("xmlrpc_submit.php");
require_once("grab_globals.lib.php");

$password = "secretpass";
session_start(); 
if ((isset($_POST["password"]) && ($_POST["password"]=="$password")) || (isset($_SESSION["password"]) && ($_SESSION["password"]=="$password"))) {
	$_SESSION["password"] = "$password";
	//	$url = 'http://mpiat3502.ag3.mpi-sb.mpg.de/cosgen/management.php?'.$_SERVER['QUERY_STRING'];
	$url = 'http://moebius.ag3.mpi-sb.mpg.de/epiexplorer/dashboard.php';
        $str = file_get_contents($url);
	print($str);
}else{
// Wrong password or no password entered display this message
	if (isset($_POST['password']) || $password == "") {
  		print "<p align=\"center\"><font color=\"red\"><b>Incorrect Password</b><br>Please enter the correct password</font></p>";
  	}
  	print "<form method=\"post\"><p align=\"center\">Please enter your password for access<br>";
  	print "<input name=\"password\" type=\"password\" size=\"25\" maxlength=\"10\"><input value=\"Login\" type=\"submit\"></p></form>";
	
}

?>
