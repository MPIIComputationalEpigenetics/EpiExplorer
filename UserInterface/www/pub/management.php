<?php
require_once("grab_globals.lib.php");
include("utils.php");
include("xmlrpc_submit.php");
include("settings.php");
include("epiexplorer_logs.php");

//function getIPDescription($ip){}
function getIPDescription($ip){
   $deanonIP = str_replace("XYZ", "255", $ip);	 
   $file = fopen("http://api.hostip.info/get_html.php?ip=$deanonIP","r");
   $data = "";
   $i = 0;
   while(!feof($file) && $i < 2 )
   {
  	$line =  explode(":",fgets($file));
  	$data = $data.$line[1].", ";
  	$i = $i + 1;
   }
   fclose($file);
   return $data;
}

if (strlen(strstr($_SERVER['SERVER_NAME'],'mpiat3502'))>0 || strlen(strstr($_SERVER['SERVER_NAME'],'moebius'))>0){
		// Internal server show info
	$title = "default";
	$header = "<th>This</th><th>table</th><th>will</th><th>be</th><th>filled</th>";
	$filelines = Array();
	if (isset($_GET['last'])){
		$last = (int)$_GET['last'];
	}else{
		$last = 1000000;
	}
	if (isset($_GET['type'])) {
		$logFile = htmlentities(substr(file_get_contents('/TL/www/epiexplorer/CGS.log'),-1*$last));
		$filelines = array_reverse(explode("\n", $logFile));
		if ($_GET['type'] == "queries"){
			$title = "Queries";
			$filelines = preg_grep("/^.*answerQuery\: called.*$/", $filelines);
		}if ($_GET['type'] == "errors"){
			$title = "Errors";
			$filelines = preg_grep("/^.*Error.*$/", $filelines);
		}else if ($_GET['type'] == "logme"){
			$title = "Logged user access";
			$filelines = preg_grep("/^.*log_me.*$/", $filelines);
		}else if ($_GET['type'] == "logmequery"){
			$title = "Logged user queries";
			$filelines = preg_grep("/^.*log_me.*sends a query.*$/", $filelines);
		}else if ($_GET['type'] == "currentDatasetComputations"){
			$title = "Current dataset computations";
			$filelines = preg_grep("/^.*(is about to be allowed to be computed|is now computing).*$/", $filelines);
		}else if ($_GET['type'] == "datasetStatuses"){
			$title = "Dataset status checks";
			$filelines = preg_grep("/^.*requests the status for dataset.*$/", $filelines);
		}else if ($_GET['type'] == "today"){
			$todaysDate = substr($filelines[1],0,5);
			$title = "Today's (".$todaysDate.") activity";
			$filelines = preg_grep("/^$todaysDate.*$/", $filelines);
		}else if ($_GET['type'] == "sortbyip"){
			$title = "User queries by IP";
			$filelines = preg_grep("/^.*log_me.*sends a query.*$/", $filelines);
			preg_match_all("|ST.*log_me\:(.*)sends a query.*\n|U",
    			"ST".implode("\nST",$filelines)."\n",
    			$out, PREG_PATTERN_ORDER);
			$counts = array_count_values($out[1]);
			arsort($counts);
			$filelines = Array();
			foreach ($counts as $key => $value){
				array_push  ($filelines,"$key (".getIPDescription($key)."): $value");
			}
		}else if ($_GET['type'] == "sortbyregion"){
			$title = "User queries by regionset";
			$filelines = preg_grep("/^.*log_me.*sends a query.*$/", $filelines);
			preg_match_all("|ST.*for regiontype(.*)\n|U",
    			"ST".implode("\nST",$filelines)."\n",
    			$out, PREG_PATTERN_ORDER);
			$counts = array_count_values($out[1]);
			arsort($counts);
			$filelines = Array();
			foreach ($counts as $key => $value){
				array_push  ($filelines,"$key : $value");
			}
		}else if ($_GET['type'] == "sortbyquery"){
			$title = "User queries by exact queries";
			$filelines = preg_grep("/^.*log_me.*sends a query.*$/", $filelines);
			preg_match_all("|ST.*sends a query (.*) with .*\n|U",
    			"ST".implode("\nST",$filelines)."\n",
    			$out, PREG_PATTERN_ORDER);
			$counts = array_count_values($out[1]);
			arsort($counts);
			$filelines = Array();
			foreach ($counts as $key => $value){
				array_push  ($filelines,"$key : $value");
			}
                }else if ($_GET['type'] == "get_single_ip_entries") {
                    header("Content-Type: text/html");
                    header("Content-Disposition: attachment; filename=\"epiexplorer_logs.txt\"");
                    print all_ip_entries();
                    return;
                }
		$logxmlRequest = xmlrpc_encode_request('log_me', array($_SERVER["REMOTE_ADDR"]." requested the log for requests of type: ".$_GET['type']));
  		sendRequest($rpc_server, '/', $logxmlRequest, $rpc_port);
	}else{
		////$title =  "Select action on the right";
		//$body = "";
	}
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>EpiExplorer LOG</title>
<style type="text/css">
<!--
body {
	font: 100%/1.4 Verdana, Arial, Helvetica, sans-serif;
	background: #e5e4e5;
	margin: 0;
	padding: 0;
	color: #000;
}

/* ~~ Element/tag selectors ~~ */
ul, ol, dl { /* Due to variations between browsers, it's best practices to zero padding and margin on lists. For consistency, you can either specify the amounts you want here, or on the list items (LI, DT, DD) they contain. Remember that what you do here will cascade to the .nav list unless you write a more specific selector. */
	padding: 0;
	margin: 0;
}
h1, h2, h3, h4, h5, h6, p {
	margin-top: 0;	 /* removing the top margin gets around an issue where margins can escape from their containing div. The remaining bottom margin will hold it away from any elements that follow. */
	padding-right: 15px;
	padding-left: 15px; /* adding the padding to the sides of the elements within the divs, instead of the divs themselves, gets rid of any box model math. A nested div with side padding can also be used as an alternate method. */
}
a img { /* this selector removes the default blue border displayed in some browsers around an image when it is surrounded by a link */
	border: none;
}

/* ~~ Styling for your site's links must remain in this order - including the group of selectors that create the hover effect. ~~ */
a:link {
	color:#e5e4e5;
	text-decoration: underline; /* unless you style your links to look extremely unique, it's best to provide underlines for quick visual identification */
}
a:visited {
	color: #4E5869;
	text-decoration: underline;
}
a:hover, a:active, a:focus { /* this group of selectors will give a keyboard navigator the same hover experience as the person using a mouse. */
	text-decoration: none;
}

/* ~~ this container surrounds all other divs giving them their percentage-based width ~~ */
.container {
	width: 100%;/* a max-width may be desirable to keep this layout from getting too wide on a large monitor. This keeps line length more readable. IE6 does not respect this declaration. */
	min-width: 780px;/* a min-width may be desirable to keep this layout from getting too narrow. This keeps line length more readable in the side columns. IE6 does not respect this declaration. */
	background: #e5e4e5;
	margin: 0 auto; /* the auto value on the sides, coupled with the width, centers the layout. It is not needed if you set the .container's width to 100%. */
	overflow: hidden; /* this declaration makes the .container clear all floated columns within it. */
	height: 100%;
}
.logcontent {
	width: 95%;
	max-height: 800px;
	overflow: auto;
}

/* ~~ These are the columns for the layout. ~~

1) Padding is only placed on the top and/or bottom of the divs. The elements within these divs have padding on their sides. This saves you from any "box model math". Keep in mind, if you add any side padding or border to the div itself, it will be added to the width you define to create the *total* width. You may also choose to remove the padding on the element in the div and place a second div within it with no width and the padding necessary for your design.

2) No margin has been given to the columns since they are all floated. If you must add margin, avoid placing it on the side you're floating toward (for example: a right margin on a div set to float right). Many times, padding can be used instead. For divs where this rule must be broken, you should add a "display:inline" declaration to the div's rule to tame a bug where some versions of Internet Explorer double the margin.

3) Since classes can be used multiple times in a document (and an element can also have multiple classes applied), the columns have been assigned class names instead of IDs. For example, two sidebar divs could be stacked if necessary. These can very easily be changed to IDs if that's your preference, as long as you'll only be using them once per document.

4) If you prefer your nav on the right instead of the left, simply float these columns the opposite direction (all right instead of all left) and they'll render in reverse order. There's no need to move the divs around in the HTML source.

*/
.sidebar1 {
	float: left;
	width: 20%;
	background: #e5e4e5;
	padding-bottom: 10px;
}
.content {
	padding: 10px 0;
	width: 80%;
	float: left;
}

/* ~~ This grouped selector gives the lists in the .content area space ~~ */
.content ul, .content ol {
	padding: 0 15px 15px 40px; /* this padding mirrors the right padding in the headings and paragraph rule above. Padding was placed on the bottom for space between other elements on the lists and on the left to create the indention. These may be adjusted as you wish. */
}

/* ~~ The navigation list styles (can be removed if you choose to use a premade flyout menu like Spry) ~~ */
ul.nav {
	list-style: none; /* this removes the list marker */
	border-top: 1px solid #666; /* this creates the top border for the links - all others are placed using a bottom border on the LI */
	margin-bottom: 15px; /* this creates the space between the navigation on the content below */
}
ul.nav li {
	border-bottom: 1px solid #666; /* this creates the button separation */
}
ul.nav a, ul.nav a:visited { /* grouping these selectors makes sure that your links retain their button look even after being visited */
	padding: 5px 5px 5px 15px;
	display: block; /* this gives the link block properties causing it to fill the whole LI containing it. This causes the entire area to react to a mouse click. */
	text-decoration: none;
	background: #8090AB;
	background: #ffffc8;
	color: #000;
}
ul.nav a:hover, ul.nav a:active, ul.nav a:focus { /* this changes the background and text color for both mouse and keyboard navigators */
	background: #6F7D94;
	color: #FFF;
	background: #FA9627;
	color: #000;
}

/* ~~miscellaneous float/clear classes~~ */
.fltrt {  /* this class can be used to float an element right in your page. The floated element must precede the element it should be next to on the page. */
	float: right;
	margin-left: 8px;
}
.fltlft { /* this class can be used to float an element left in your page. The floated element must precede the element it should be next to on the page. */
	float: left;
	margin-right: 8px;
}
.clearfloat { /* this class can be placed on a <br /> or empty div as the final element following the last floated div (within the #container) if the overflow:hidden on the .container is removed */
	clear:both;
	height:0;
	font-size: 1px;
	line-height: 0px;
}
-->
</style><!--[if lte IE 7]>
<style type="text/css">
.content { margin-right: -1px; } /* this 1px negative margin can be placed on any of the columns in this layout with the same corrective effect. */
ul.nav a { zoom: 1; }  /* the zoom property gives IE the hasLayout trigger it needs to correct extra whiltespace between the links */
</style>
<![endif]--></head>
<body>
<div class="container">
  <div class="sidebar1">
  	<div class="logo">
        <a href="index.php"><img src="extras/new_logo.png" width="100%" align="bottom" style="border-width:0px" alt="Management"/></a>
     </div>
    <ul class="nav">

      <li><a href="?type=logme&last=<?php echo $last;?>">Show all log_me data</a></li>
      <li><a href="?type=logmequery&last=<?php echo $last;?>">Show all user queries</a></li>
      <li><a href="?type=queries&last=<?php echo $last;?>">Show all queries</a></li>
      <li><a href="?type=errors&last=<?php echo $last;?>">Show errors</a></li>
      <li><a href="?type=currentDatasetComputations&last=<?php echo $last;?>">Show datasets computations</a></li>
      <li><a href="?type=datasetStatuses&last=<?php echo $last;?>">Show datasets status checks</a></li>
      <li><a href="?type=today&last=<?php echo $last;?>">Show only data for today</a></li>
      <li><a href="?type=sortbyip&last=<?php echo $last;?>"># queries per ip</a></li>
      <li><a href="?type=sortbyregion&last=<?php echo $last;?>"># queries per regionset</a></li>
      <li><a href="?type=sortbyquery&last=<?php echo $last;?>"># queries per query</a></li>
      <li><a href="?type=get_single_ip_entries">Log file: Access by ip</a></li>
    </ul>
    <!-- end .sidebar1 --></div>
  <div class="content">
    <h1><?php echo $title." : ".count($filelines);?></h1>
    <div class="logcontent">
    <?php echo implode("<br>\n",$filelines); ?>
    </div>

    <!-- end .content --></div>
  <!-- end .container --></div>
</body>
</html>
<?php
	}else{
		echo "To be done";
	}
?>
