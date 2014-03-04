<?php
if (strlen(strstr($_SERVER['SERVER_NAME'],'mpiat3502'))>0 || strlen(strstr($_SERVER['SERVER_NAME'],'moebius'))>0){
?>
<html>
<head>
   <script type="text/javascript" src="https://www.google.com/jsapi"></script>
   <script type="text/javascript" src="dashboard.js"></script>
</head>

<body>
   <!--Div that will hold the pie chart-->
   <div id="table" style="width: 1600px; height: 600px;"></div>

   <div id="infos"></div>
</body>
 </html>
<?php
}else{
		echo "To be done";
}
?>