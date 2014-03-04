<?php
    require_once("d3-helpers.php"); 
    require_once("inc_ag3/config.inc.php");
    include_once("classes/class.navigation.php");

    $mpi_env = WebDomain::getDetails("epiexplorer");

    echo($mpi_env["rpc_server"].":".$mpi_env["rpc_port"]);

    debugSection($mpi_env);

?>
