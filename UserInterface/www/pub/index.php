<?php
	require_once("grab_globals.lib.php");
  	include("xmlrpc_submit.php");
  	include("settings.php");
  	include("utils.php");

  	// This part send a request for basic information for the regions supported by the current started server
  	ob_start();
  	$xmlRequest = xmlrpc_encode_request('getStatus', array($_SERVER['SERVER_NAME'],"main"));
  	$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	ob_end_clean();	

	if($arrayResponse === "OK") {
		//header('Content-Type: text/html'); // plain html file		
	}else if(strlen(strstr($_SERVER['SERVER_NAME'],'epiex.mpi-inf.mpg.de')) != 0){
		//We are at a test server that is currently not working, but is only accessible from google and from MPI services
	}else{
		//echo "not ok $arrayResponse";	
		if (strlen(strstr($_SERVER['SERVER_NAME'],'moebius')) == 0){
			// Do not send mails if test servers (located on http://moebius... ) are not working
 			$subject = "EpiExplorer XMLRPC Server is not working! (".date("H:i:s d.m.y")." , ".anonimizedUser().")";
 			$body = "On ".date("H:i:s d.m.y")." requested by ".$_SERVER["REMOTE_ADDR"]." (".gethostbyaddr($_SERVER["REMOTE_ADDR"])."\n"."Status:'".$arrayResponse."'\n"."More info: \n"."Server name:  ".$_SERVER['SERVER_NAME']."\n"."Request URI:  ".$_SERVER['REQUEST_URI']."\n"."Http referer:  ".$_SERVER['HTTP_REFERER']."\n";

	 		if (mail($contact_email, $subject, $body)) {
	   			header( 'Location: maintenance.php') ;
	  		} else {
	   			header( 'Location: maintenance.php') ;
	  		}  		
		}else{
			header( 'Location: maintenance.php') ;
		}
	}

	// Define the optional twitter html
  	$twitter_html='';

 	if(isset($twitter_handle)){
	  	$twitter_html = "<li><a href=\"http://twitter.com/#!/$twitter_handle\" target=\"_blank\">
		   					<img src=\"extras/twitter_newbird_blue_32.png\" class=\"menusubicon\" alt=\"Twitter\"/>Contact us via Twitter</a>
			    		 </li>";
  	}

	if (strlen(strstr($_SERVER['SERVER_NAME'],'cosgen.bioinf')) == 0 && strlen(strstr($_SERVER['SERVER_NAME'],'epiex.mpi-inf.mpg.de')) == 0){
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
		
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<link rel="SHORTCUT ICON" href="extras/new_logo_symbol_16.ico"/>
	<link href="menu/menu.css" rel="stylesheet" type="text/css" />
	<script type="text/javascript" src="jQuery/js/jquery-1.4.2.min.js"></script>	
	
	<?php 
		// Temporary switch this idea off
		// Somehow it messes up with global variables defined in CGSTexts.js
		//if (strlen(strstr($_SERVER['SERVER_NAME'],'mpiat3502'))>0)
		//{
		//	//Internal test server, use the test, not minimized javascript
		//	echo '<script type="text/javascript" src="commonCGS.js"></script>';
		//	echo '<script type="text/javascript" src="CGSTexts.js"></script>';
		//	echo '<script type="text/javascript" src="commonExploreCGS.js"></script>';			
		//}else{
		//	echo '<script type="text/javascript" src="packedjs/EpiExplorer.pack.120202.js"></script>';			
		//}
	?>	
	<!--script type="text/javascript" src="packedjs/EpiExplorer.pack.120202.js"></script-->

	<script type="text/javascript" src="commonCGS.js"></script>
	<script type="text/javascript" src="CGSTexts.js"></script>	
	<script type="text/javascript" src="commonExploreCGS.js"></script>
		
	<link href="testIndex.css" rel="stylesheet" type="text/css" />
	
    <!-- The purpose of the jQuery UI is to use the slider, remove them if the slider is removed -->
  	<script type="text/javascript" src="jQuery/js/jquery-ui-1.8.5.custom.min.js"></script>
  			
	<link type="text/css" href="jQuery/css/custom-theme/jquery-ui-1.8.5.custom.css" rel="stylesheet" />
	
  
    <style type="text/css"></style>

	<link href="jQueryUI-mine/jquery-ui-mine.css" rel="stylesheet" type="text/css" />
	
  
  <!-- jQuery checkboxes -->
  <script type="text/javascript" src="jCheckbox/jquery.checkboxes.pack.js"></script>
  
  <!-- jQuery cookies -->	
  <script type="text/javascript" src="jquery.cookie/jquery.cookie.js"></script>
  
  <!-- jQuery slider >
  <script type="text/javascript" src="jquery.slider/jquery.simpleSlide_min.js"></script-->
  <!-- jQuery bx slider >
  <script type="text/javascript" src="jquery.bxSlider/jquery.bxSlider.min.js"></script-->
  <!-- the google visualizations -->
  <script type="text/javascript" src="http://www.google.com/jsapi"></script>
  
  <!-- Try the term cloud thing -->
  <link rel="stylesheet" type="text/css" href="termCloud/tc.css"/>
  <script type="text/javascript" src="termCloud/tc.js"></script>
  
  <!-- jquery simple drop-won menu -->
  <link rel="stylesheet" type="text/css" href="jsddm/jsddm.css"/>
  <script type="text/javascript" src="jsddm/jsddm.js"></script>
  
  
  <!-- jquery UI.layout plugin -->
  <script type="text/javascript" src="ui.layout/jquery.layout.min-1.2.0.js"></script>
  
  <link rel="stylesheet" type="text/css" href="ui.layout/layout-default.css"/>
  
  <!--script type="text/javascript" src="jQuery/development-bundle/ui/jquery.ui.selectmenu.js"></script-->
  <!--link rel="stylesheet" type="text/css" href="jQuery/development-bundle/themes/base/jquery.ui.selectmenu.css"/-->
  
  <script type="text/javascript" src="canvg/rgbcolor.js"></script> 
  
  <script type="text/javascript" src="canvg/canvg-1.0.js"></script>
   

<title>EpiExplorer</title>
	
<script type="text/javascript">
	google.load('visualization', '1', {packages: ['table','corechart', 'controls']});
	// THE VARIABLE FOR ALL SETTINGS
	var settings = {};
	// THE VARIABLE FOR ALL CURRENT STATE THINGS
	var currentState = {};
	
/*####----####---- Start if jQuery onReady ----####----####*/
$(function() {

	/* SETTINGS */
	// Show whcih genome to be shown by default	
	if ($.cookie("cgs:settings:genome")){
		settings["genome"] = $.cookie("cgs:settings:genome");
	}else{
		settings["genome"] = "hg19";
		$.cookie("cgs:settings:genome", settings["genome"], { expires: 30});	
	}
	// User datasets to be activated or currently activated
	//This is the code in which the starting genome is decided. 
	// The rule is in decreasing order of priority:
	// "hg18",from the cookie,from the user dataset in the params, from the analysis in the params	
	<?php
		$genome = "";
		echo 'var directUserDatasets = [';
		if (isset($_GET['userdatasets'])){
			$userdatasets = explode(";",$_GET['userdatasets']);
			foreach ($userdatasets as $dataset){				
				$xmlRequest = xmlrpc_encode_request('activateUserDataset', array($dataset));
				$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);			
				if ($arrayResponse[0]==0){
					echo '"'.$dataset.'",';
					$genome = $arrayResponse[2]["genome"];
				}				
			}
		}
		echo '];', PHP_EOL;
		if ($genome != ""){
			echo 'settings["genome"] = "'.$genome.'";', PHP_EOL;	
			echo '$.cookie("cgs:settings:genome", settings["genome"], { expires: 30});', PHP_EOL;	
		}
	?>
	currentState["analysisLinkData"] = {};
	currentState["analysisLinkData"]["param"] = getParameterByName('analysisLink');
	if (currentState["analysisLinkData"]["param"] != null){	
		setCurrentStatus("Loading analysis data ...",true);	
		$.ajax({
  			type: 'GET',
  			url: "relay.php",
  			async:false,  			
  			data: {'type':'getLinkData',
  				   'analysisLink':currentState["analysisLinkData"]["param"]},	   		
	   		dataType:"json",
  			success: function(jsonResult){  				  				
  				//alert(jsonResult)		
  				//Check if we have currently selected the wrong geneome, change it
  				currentState["analysisLinkData"]["result"] = jsonResult;
  				settings['genome'] = jsonResult[0];
  				setCurrentStatus(null,false);	
  			}});
	}
	
	if ($.cookie("cgs:settings:userdatasets:"+settings["genome"])){
		 var userDatasets = $.cookie("cgs:settings:userdatasets:"+settings["genome"]).split(";");
		 
		 if (userDatasets[0].length > 0){
		 	currentState["userDatasets"] = userDatasets;
		 }else{
		 	currentState["userDatasets"] = [];
		 } 
	}else{
		currentState["userDatasets"] = [];
		$.cookie("cgs:settings:userdatasets:"+settings["genome"], currentState["userDatasets"].join(";"), { expires: 30});	
	}
	// Show which overlapSetting to be shown by default
	if ($.cookie("cgs:settings:overlap")){
		settings["overlap"] = $.cookie("cgs:settings:overlap");
	}else{
		settings["overlap"] = "Eoverlaps";
		$.cookie("cgs:settings:overlap", settings["overlap"], { expires: 30});	
	}
	// Show which tissue to be shown by default in the summary plots
	if ($.cookie("cgs:settings:tissue")){
		settings["tissue"] = $.cookie("cgs:settings:tissue");
	}else{
		settings["tissue"] = "any";
		$.cookie("cgs:settings:tissue", settings["tissue"], { expires: 30});	
	}
	// Should a confirmation message be shown at each refinement 
	if ($.cookie("cgs:settings:showRefinementNotification")){
		settings["showRefinementNotification"] = $.cookie("cgs:settings:showRefinementNotification");
	}else{
		settings["showRefinementNotification"] = "true";
		$.cookie("cgs:settings:showRefinementNotification", settings["showRefinementNotification"], { expires: 60});	
	}
	
	
	// Indicates by how many pixels should the items in the feature listing be shifted in with each level
	settings["standardIdentation"] = 20;
	// Inidcates which analysis are we in, this variable should not be accessed in geenral
	settings["sourceType"] = "baseExplore";
	// The variable that indicates which are the default overlaps we should display
	settings["overlapSelection"] = {};	
	settings["overlapSelection"]["hg18"] = ["OVERLAP:bhist:H3K4me1:TISSUE","OVERLAP:bhist:H3K4me3:TISSUE","OVERLAP:bhist:H3K27me3:TISSUE","OVERLAP:bhist:H3K36me3:TISSUE","OVERLAP:DNaseI:TISSUE","OVERLAP:chmm04strenh:TISSUE","OVERLAP:chmm08ins:TISSUE","OVERLAP:ucscCGI","OVERLAP:cons","OVERLAP:repeats:any","OVERLAP:promoters_def","OVERLAP:genes"];	
	settings["overlapSelection"]["hg19"] = ["OVERLAP:bhist:H3K4me1:TISSUE","OVERLAP:bhist:H3K4me3:TISSUE","OVERLAP:bhist:H3K27me3:TISSUE","OVERLAP:bhist:H3K36me3:TISSUE","OVERLAP:DNaseI:TISSUE","OVERLAP:chmm04strenh:TISSUE","OVERLAP:chmm08ins:TISSUE","OVERLAP:ucscCGI","OVERLAP:cons","OVERLAP:repeats:any","OVERLAP:promoters_def","OVERLAP:genes"];	
	settings["overlapSelection"]["mm9"] = ["OVERLAP:bhist:H3K4me1:any","OVERLAP:bhist:H3K4me3:any","OVERLAP:tfbs:CTCF:any","OVERLAP:tfbs:Pol2:any","OVERLAP:DNaseIa:any","OVERLAP:repeats:any","OVERLAP:cons","OVERLAP:genes","OVERLAP:promoters_def","OVERLAP:ucscCGI","OVERLAP:LaminaB1:any"];	

	// Default variable for currentOverlaps. It is used to reset its state
	settings["defaultCurrentOverlaps"] = "None"; 
	// Default variable for the region selected
	settings["defaultRegionSelected"] = "";
	//
	settings["defaultCurrentOverlapStats"] = {};
	
	// wheather it is possible to remove regions selection
	settings["allowRemoveRegionSelection"] = true;
	//default tissues
	settings["defaultTissues"] = ["any","GM12878","HMEC","NHLF","NHEK","HUVEC","H1hESC"];
	// Show confidence on overlap plots
	settings['showConfidence'] = true;
	settings['showBubbleChart'] = true;
	
	if ($.cookie("cgs:settings:leftwidth")){
		settings["leftwidth"] = $.cookie("cgs:settings:leftwidth");
	}else{
		settings["leftwidth"] = 400;
		$.cookie("cgs:settings:leftwidth", settings["leftwidth"], { expires: 30});	
	}
	settings['maxOverlapCompletions'] = 2000;
	settings['layout'] = $("div.container").layout({
		//	name:					'containerLayout' // for debugging and auto-adding buttons (see below)		
		//,	west__paneSelector: 	'.leftside'
		//,	center__paneSelector: 	'.rightside'
		west__size: 			settings["leftwidth"],		// percentage size expresses as a decimal
		//,	center__size: 			".70"		// percentage size expresses as a decimal
		west__minSize:			200,
		west__maxSize:			600,
		center__minSize:		600,
		//,	minSize:				"100"
		autoResize:				true,	// try to maintain pane-percentages
		west__onresize_end : function(){
			settings["leftwidth"] = settings['layout'].state.west.size;
			$.cookie("cgs:settings:leftwidth", settings["leftwidth"], { expires: 30});
		},
		south__resizable: 				false,
		south__slidable:				false,		
		south__spacing_open:			1,			// cosmetic spacing
		south__togglerLength_open:		0,			// HIDE the toggler button
		south__togglerLength_closed:	-1,			// "100%" OR -1 = full width of pane
		south__fxName:					"none",
	});
			
	/* ENDOF SETTINGS*/
	/* CURRENT  AND DEFAULT STATE */
		
	currentState["isRegionSelected"] = false;
	currentState["exploreRegionSelected"] = settings["defaultRegionSelected"];
	currentState["exploreRegionSelected"] = "<?php	if (isset($_GET['genomeregions'])){echo $_GET['genomeregions'];}?>";
	// a variable to store all the data about the reference state
	currentState["referenceQuery"] = getDefaultReferenceState();	
	// The variable that indicates which are the overlaps we should display
	currentState["overlapSelection"] = settings["overlapSelection"][settings["genome"]];
	// A variable to store the current overlap data
	currentState["currentOverlaps"] = settings["defaultCurrentOverlaps"];	                                  
	// This variable handles confidence computation, should be reset every time currentState["currentOverlaps"] is reset
	currentState["currentOverlapsStat"] = settings["defaultCurrentOverlapStats"];
	// A variable to store the current neighborhood
	currentState["currentNeighborhood"] = settings["defaultCurrentOverlaps"];
	// This variable stores the current number of regions under inspection
	currentState["totalNumberOfRegions"] = 0;
	//This variable stores preprocessed features for some dataset	
	currentState["datasetFeatures"] = {};
	//This variable stores the data needed for the current plot	
	currentState["plotData"] = null;
	// This variable stores the links to the DOM elements corresponding to various visualization elements
	currentState["featuresElements"] = {};
	// This variable stores the last visualization
	currentState["featureCurrentVisualization"] = "";
	// The user dataset link that initiated this session
	currentState["loadedUserDatasetFromLink"] = "";
	//this variable stores the info for all active region sets
	currentState["datasetInfo"] = {};
	// the following variable holds the information for the active charts. It is used in the clearCharts method
	currentState["activeChart"] = [];
	// the kind of chart that will be displayed as data overview
	currentState["currentDefaultChart"] = "bars";
	
	$.each(directUserDatasets,function(index,datasetID){
		if (datasetID != undefined){
			currentState["loadedUserDatasetFromLink"] = datasetID;
			if (jQuery.inArray(datasetID, currentState["userDatasets"]) == -1){
					currentState["userDatasets"].push(datasetID);					
					$.cookie("cgs:settings:userdatasets:"+settings["genome"], currentState["userDatasets"].join(";"), { expires: 30});
			}
		}	
	});
	/* ENDOF CURRENT AND DEFAULT STATE */	
	
	  	
	/* INITIALIZATION */	
	
	//initialize the settings
	initSettings();	
	//initialize all delegation
	initEventDelegationRegionsTable();
	initEventDelegationFeatureListing();
	// initialize button properties
	initBasicButtons();
	initExploreButtons();
	initDatasets();
	// initialize the default region set
	initRegionSets(true);
	//initialize start settigns
	initStartingSettings();	
	
	/* ENDOF INITIALIZATION*/
		
});
	
		
</script>
<!-- userfeedbacktest ideascale -->	
<!--script id="is-feedback-widget" src="http://tets.ideascale.com/userimages/sub-1/900035/panel-13940-feedback-widget.js"></script-->	
</head>

<body>

<div class="container">
    <div class="leftside ui-layout-west">
        <div class="logo">
        	<!--a href="index.php"><img src="extras/logo_tes.PNG" width="242px" height="90px" align="bottom" style="border-width:0px"></a-->
        	<!--a href="index.php"><img src="extras/EE_text_color_blurred_noice_transparent_small.png" width="242px" height="90px" align="bottom" style="border-width:0px"></a-->
        	<a href="index.php"><img src="extras/new_logo.png" width="80%" align="bottom" style="border-width:0px" alt="Logo"/></a>
        	
        </div>
        
        <div class="regions">
	        <div class="regionsSelection">
		        <table style="width:100%;margin-bottom:10px" class="header">
	              	
					<tr>
						<td class="opmenuTD hoverChangeIcon showReloadUserDatasetButton">							
							<img src="extras/document-open.png" class="opmenuicon" alt="Reload"/>
							<div>Reload</div>
						</td>
						<td class="opmenuTD hoverChangeIcon uploadNewDatasetButton">							
							<img src="extras/folder-new.png" class="opmenuicon" alt="Upload"/>
							<div>Upload</div>							
						</td>						
					</tr>
					<tr>
						<td colspan="2">
							<b>
							<div class="opmenuTDText">
								_							
							</div>
							</b>
						</td>
					</tr>
					<tr class="reloadUserDatasetTD">
						<td colspan="2"> 
							<input id="userDatasetID" type="text" title="Paste here a dataset ID and press enter or the icon on the right"/>
							<div class="activateUserDataset"></div>
						</td>					
					</tr>
					<tr class="reloadUserDatasetTD">
						<td colspan="2">
							<span style="color:red;" class="activateUserDatasetSpan"></span>
						</td>
					</tr>
				</table>
        		<!--h2 class="boxheader">Select a dataset</h2-->
            	<table id="regionsTable" class="regionsTableClass activeSearchBox" cellspacing="0">		 		
		 		</table>
            </div>
            
            <div class="regionsSelected">
	            <!--h2 class="boxheader"></h2-->
              <!--p align="right">
                      <label>Current number of regions:</label>
                      <label id="totalDocuments">0</label>
              </p-->
              <table style="width:100%;margin-bottom:20px" class="header">
              	
				<tr>
					<td class="opmenuTD hoverChangeIcon exploreDefaultDatasetsButton">
						<!--a href="#" class="exploreDefaultDatasetsButton"-->
							<img src="extras/document-revert.png" class="opmenuicon" alt="Back"/>
							<div>Select another region set</div>
						<!--/a-->
					</td>
					<td class="opmenuTD hoverChangeIcon useAsReferenceButton">
						<!--a href="#" class="useAsReferenceButton"-->
							<img src="extras/split.png" class="opmenuicon" alt="Compare"/>
							<div>Use the current selection in comparison mode</div>
						<!--/a-->
					</td>
					<td class="opmenuTD hoverChangeIcon getLinkButton">
						<!--a href="#" class="getLinkButton"-->
							<img src="extras/document-save_32.png" class="opmenuicon" alt="Save as URL"/>
							<div>Save the current analysis as a URL</div>
						<!--/a-->
					</td>
					<td class="opmenuTD hoverChangeIcon exportToUCSCAsCustomTrack">
						<!--a href="#" class="getLinkButton"-->
							<img src="extras/epiexplorer_export_ucsc.png" class="opmenuicon" alt="Export to UCSC Genome Browser"/>
							<div>Export to UCSC Genome Browser</div>
						<!--/a-->
					</td>
					<td class="opmenuTD hoverChangeIcon exportToEnsemblAsCustomTrack">
						<!--a href="#" class="getLinkButton"-->
							<img src="extras/epiexplorer_export_ensembl.png" class="opmenuicon" alt="Export to Ensembl"/>
							<div>Export to Ensembl </div>
						<!--/a-->
					</td>
					<td class="opmenuTD hoverChangeIcon exportToGalaxy">
						<!--a href="#" class="getLinkButton"-->
							<img src="extras/epiexplorer_export_galaxy.png" class="opmenuicon" alt="Export to Galaxy"/>
							<div>Export to Galaxy</div>
						<!--/a-->
					</td>
					<td class="opmenuTD hoverChangeIcon exportToHyperBrowser">
						<!--a href="#" class="getLinkButton"-->
							<img src="extras/epiexplorer_export_hyperbrowser2.png" class="opmenuicon" alt="Export to the Genomic HyperBrowser"/>
							<div>Export to the Genomic HyperBrowser</div>
						<!--/a-->
					</td>
					<td class="opmenuTD hoverChangeIcon gotoListingOfRegions">
						<!--a href="#" class="getLinkButton"-->
							<img src="extras/format-list-ordered.png" class="opmenuicon" alt="List the regions and view in UCSC"/>
							<div>List the regions and view in UCSC</div>
						<!--/a-->
					</td>
				</tr>
				<tr>
					<td colspan="8">
						<b>
						<div class="opmenuTDText">
							_							
						</div>
						</b>
					</td>
				</tr>
			</table>
				              	
              
              
            </div>
            <div id="referenceListing">              
          		<!-- The box in the right that will include all results -->
      		</div> <!-- End of  reference listing-->
        </div>

		<hr class="menuSeparator" />

        <div class="features activeSearchBox">
        	<!--h2 class="boxheader">Explore the dataset properties</h2-->            
        </div> 
    </div>	
	<div class="rightside ui-layout-center">		
		<noscript><h1>You need to activate JavaScript to use EpiExplorer.</h1></noscript>
		<div class="header">
			<!--ul class="jsddm" align="right"-->
			<ul class="jsddm">
				<li>
					<a href="#">
						<img src="extras/system-help_32.png" class="menuicon" alt="Support"/>
						<!--img src="extras/help-browser_32.png" class="menuicon"/-->
						<!--img src="extras/help-contents_32.png" class="menuicon"/-->
												
						<div class="menuicontext">Support</div>
					</a>
					<ul>
						<!--li>
							<a href="http://epiexplorer.userecho.com/forum/8403-frequently-asked-questions/" target="_blank">
								<img src="extras/help-contents_32.png" class="menusubicon"/>FAQ
							</a>						
						</li-->
						<li><!--a onmouseover="UE.Popin.preload();" href="#" onclick="UE.Popin.show(); return false;">Questions, problems, ideas?</a-->
							<a href="http://epiexplorer.userecho.com/forum/5999-feedback/" target="_blank">
								<img src="extras/userecho_32.png" class="menusubicon" alt="Questions, problems, ideas"/>Questions, problems, ideas?
							</a>						
						</li>

						<?php echo $twitter_html; ?>

						<li><a href="mailto:<?php echo $contact_email; ?>">
								<img src="extras/mail-mark-unread_32.png" class="menusubicon" alt="Email"/>Contact us via email</a>
						</li>

						<li>
							<a href="welcome.php" onclick="return false;" id="showWelcomePageInFrame">
								<img src="extras/applications-education.png" class="menusubicon" alt="Slideshows"/>Slideshows
							</a>
						</li>
						<li>
							<a href="#" onclick="return false;" id="presentationModeSwitch">
								<img src="extras/measure.png" class="menusubicon" alt="Presentation mode on"/>Presentation mode On
							</a>
						</li>
						<li>
							<a href="DownloadSourceCodeMain.php" onclick="return false;" id="showDownloadPageInFrame">
								<img src="extras/code.png" class="menusubicon" alt="Source code"/>Access the source code
							</a>
						</li>
						<li>
							<a href="about_epiexplorer.php" onclick="return false;" id="showAboutPageInFrame">
								<img src="extras/help-about_32.png" class="menusubicon" alt="About"/>About EpiExplorer
							</a>
						</li>
						<li>
							<a href="cite.php" onclick="return false;" id="showCitePageInFrame">
								<img src="extras/help-about_32.png" class="menusubicon" alt="How to cite"/>How to cite
							</a>
						</li>
						<!--li><a href="http://epiexplorer.userecho.com/forum/5999-feedback/filter-17845/order-top/">Bugs?</a></li-->
						<!--li><a href="http://epiexplorer.userecho.com/forum/5999-feedback/filter-17845/order-top/">Ideas?</a></li-->
						<!--a href="feedback.php">Feedback</a-->
					</ul>
				</li>
				
				<!--li>
					<a href="uploadManagement.php">
						<img src="extras/folder-new-hover.png" class="menuicon">
						<div class="menuicontext">Upload</div>
					</a>
				</li-->
				
				<li>
					<a href="#" id="genomeSelectLabel">
						<img src="extras/user-identity_32.png" class="menuicon" alt="Genome"/>
						<div class="menuicontext">Genome (hg18)</div>
					</a>
					<ul>
						
						<li><a href="#" class="genomeSelect">hg18</a></li>			
						<li><a href="#" class="genomeSelect">hg19</a></li>						
						<li><a href="#" class="genomeSelect">mm9</a></li>
						<li>Please use the <b>feedback</b> to suggest other genomes (or annotations) EpiExplorer can support</li>
					</ul>
				</li>
				<li>
					<a href="index.php">
						<img src="extras/go-home_32.png" class="menuicon" alt="Restart"/>
						<div class="menuicontext">Start over</div>
					</a>
				</li>
				<!--li>
					<a href="#" class="getLinkButton">						
						<img src="extras/document-save_32.png" class="menuicon" alt="Get link"/>
						<div class="menuicontext">Get link</div>
					</a>
				</li-->	
				
			</ul>
			<br/>
			<div id="currentLinkLocation"></div>
	    </div>
		<div id="currentStatus"></div>		
		<div class="content">			
            <div class="visualization">            	 	
	         	 <div id="rangeFeaturePlotMain">					
								
			  	 </div><!-- End of rangeFeaturePlotMain-->  			
			</div><!-- End of visualization-->
			
            <div class="infoboxMain">   
            	<table>    
            		<tr><td><div class="infoboxPlot infoboxDetail tutorialMode">
            		</div><!-- End of infoboxPlot--></td></tr>        	              
					
					<tr><td><div class="infoboxFeature infoboxDetail tutorialMode">
					</div><!-- End of infoboxReature--></td></tr>
					
					<tr><td><div class="infoboxRegions infoboxDetail">
					</div><!-- End of infoboxRegions--></td></tr>
					
				</table>  	              
			</div><!-- End of infoboxMain-->
			
			<!--iframe src="welcome.php" width="90%" height="95%" frameborder="0" class="infoWelcome">
  					<p>Your browser does not support iframes.</p>
			</iframe-->
			
			
						
	    </div><!--END of content -->	
	    <div class="contentFrame">
			<iframe id="contentFrameID" src="" width="100%" height="100%" frameborder="0" scrolling="auto">
				<p>Your browser does not support iframes.</p>
			</iframe>
			
		</div>
	    
	    <!--div class="footer ui-layout-south">Contact us via <a href="mailto:<?php echo $contact_email;?>">email</a>, <a href="http://twitter.com/#!/hEpiExplorer">twitter</a> or in our <a href="http://epiexplorer.userecho.com/forum/5999-feedback/">feedback forum</a>.</div-->
	    	
	    
	</div><!-- End of rightside-->
	
	</div><!-- End of container-->
	
    <div class="hiddenstuff">
				
    </div>
    <div> <!-- userfeedbacktest -->						

		<!-- userecho -->
		<!-- script type='text/javascript'>
		
		var _ues = {
		host:'epiexplorer.userecho.com',
		forum:'5999',
		lang:'en',
		tab_corner_radius:10,
		tab_font_size:22,
		tab_image_hash:'RmVlZGJhY2s%3D',
		tab_alignment:'right',
		tab_text_color:'#000000',
		tab_bg_color:'#FFFFC8',
		tab_hover_color:'#FA9627'
		};
		
		(function() {
			var _ue = document.createElement('script'); _ue.type = 'text/javascript'; _ue.async = true;
			_ue.src = ('https:' == document.location.protocol ? 'https://s3.amazonaws.com/' : 'http://') + 'cdn.userecho.com/js/widget-1.4.gz.js';
			var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(_ue, s);
		  })();
		
		</script -->
	</div><!-- userfeedbacktest -->
	<div id="dialog-notification" title="Notification">
		<div id="notificationTitle"></div>
		<div id="notificationParagraph"></div>		
	</div>

    
</body>
</html>
<?php
	}else{
		echo "The EpiExplorer server moved to a nicer domain: <a href='http://epiexplorer.mpi-inf.mpg.de'>http://epiexplorer.mpi-inf.mpg.de</a>";
	}
?>
