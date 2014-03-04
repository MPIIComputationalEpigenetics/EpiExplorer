<?php

 //$rpc_server = 'wks-13-15';
 #$rpc_server =  "infao3700";
 #$rpc_port = '56572';

require_once("d3-helpers.php");
require_once("inc_ag3/config.inc.php");
include_once("classes/class.navigation.php");

$mpi_env = WebDomain::getDetails("epiexplorer");

$rpc_server = $mpi_env["rpc_server"];
$rpc_port = $mpi_env["rpc_port"];

?>
