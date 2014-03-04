<html>
	<head><title>Code Snippet</title></head>
	<body>
		<div>
		<?php
			require_once("d3-helpers.php"); 
			require_once("inc_ag3/config.inc.php");
			include_once("classes/class.navigation.php");
			
			$DEBUG = 1;		// 1 = debug on, 0 = off
			
			$mpi_env = WebDomain::getDetails("epiexplorer");

			debugSection($mpi_env);

		?>
		</div>
	</body>
</html>
