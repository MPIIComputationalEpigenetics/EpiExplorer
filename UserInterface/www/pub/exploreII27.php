<?php
  require_once("grab_globals.lib.php");  
  include("xmlrpc_submit.php");
  include("settings.php");
  include("utils.php");
  
	// This part send a request for basic information for the regions supported by the current started server
	ob_start();
	$xmlRequest = xmlrpc_encode_request('getStatus', array());
	$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	ob_end_clean();	
	if($arrayResponse === "OK") {		
	}else{
		//echo "not ok $arrayResponse";
 		$subject = "CGS XMLRPC Server is not working! (".date("H:i:s d.m.y")." , ".anonimizedUser().")";
 		$body = "On ".date("H:i:s d.m.y")." requested by ".anonimizedUser()."\nStatus:'".$arrayResponse."'";
 		if (mail($contact_email, $subject, $body)) {
   			header( 'Location: maintenance.php') ;
  		} else {
   			header( 'Location: maintenance.php') ;
  		}  		
	}  	 	
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

	<link href="menu/menu.css" rel="stylesheet" type="text/css" />
	<script type="text/javascript" src="jQuery/js/jquery-1.4.2.min.js"></script>
	<script type="text/javascript" src="commonCGS.js"></script>
	<script type="text/javascript" src="commonExploreCGS.js"></script>
	<script type="text/javascript" src="exploreII.js"></script>	
	<link href="testIndex.css" rel="stylesheet" type="text/css" />
    <!-- The purpose of the jQuery UI is to use the slider, remove them if the slider is removed -->
  <script type="text/javascript" src="jQuery/js/jquery-ui-1.8.5.custom.min.js"></script>		
	<link type="text/css" href="jQuery/css/custom-theme/jquery-ui-1.8.5.custom.css" rel="stylesheet" />
    
  <!--script type="text/javascript" src="jqtransformplugin/jquery.jqtransform.js"></script>		
	<link type="text/css" href="jqtransformplugin/jqtransform.css" rel="stylesheet" /-->
    
    <style></style>

	<link href="jQueryUI-mine/jquery-ui-mine.css" rel="stylesheet" type="text/css" />
	<!-- jqPlot specific code and styles -->
	<link type="text/css" href="jqPlot/jquery.jqplot.min.css" rel="stylesheet"/>	
	<script type="text/javascript" src="jqPlot/jquery.jqplot.min.js"></script>			
	<script type="text/javascript" src="jqPlot/plugins/jqplot.logAxisRenderer.min.js"></script>
	<script type="text/javascript" src="jqPlot/plugins/jqplot.barRenderer.min.js"></script>		
	<script type="text/javascript" src="jqPlot/plugins/jqplot.cursor.min.js"></script>		
	<script type="text/javascript" src="jqPlot/plugins/jqplot.highlighter.min.js"></script>			
	<script type="text/javascript" src="jqPlot/plugins/jqplot.categoryAxisRenderer.min.js"></script>			
	<script type="text/javascript" src="jqPlot/plugins/jqplot.canvasTextRenderer.min.js"></script>
	<script type="text/javascript" src="jqPlot/plugins/jqplot.canvasAxisTickRenderer.min.js"></script>	
  <script type="text/javascript" src="jqPlot/plugins/jqplot.canvasAxisLabelRenderer.min.js"></script>  
  <script type="text/javascript" src="jqPlot/plugins/jqplot.pointLabels.min.js"></script>  
  
  <!-- jQuery checkboxes -->
  <script type="text/javascript" src="jCheckbox/jquery.checkboxes.pack.js"></script>	

<title>Complete Genome Search alpha</title>
		
<script type="text/javascript">
	
	// THE VARIABLE FOR ALL SETTINGS
	var settings = {};
	// THE VARIABLE FOR ALL CURRENT STATE THINGS
	var currentState = {};
	
/*####----####---- Start if jQuery onReady ----####----####*/
$(function() {
	
	/* SETTINGS */
	// Indicates by how many pixels should the items in the feature listing be shifted in with each level
	settings["standardIdentation"] = 20;
	// Inidcates which analysis are we in, this variable should not be accessed in geenral
	settings["sourceType"] = "exploreII27";
	// The variable that indicates which are the default overlaps we should display
	settings["overlapSelection"] = ["Eoverlaps:repeats:any","Eoverlaps:cons","Eoverlaps:genes","Eoverlaps:promoters_def","Eoverlaps:DNaseI:any","Eoverlaps:ucscCGI","Eoverlaps:bhist:H3k4me2:any","Eoverlaps:bhist:H3k4me1:any","Eoverlaps:bhist:H3k4me3:any","Eoverlaps:bhist:H3k9ac:any","Eoverlaps:bhist:H3k27me3:any","Eoverlaps:bhist:Ctcf:any","Eoverlaps:bhist:Pol2b:any"];
	// Default variable for currentOverlaps. It is used to reset its state
	settings["defaultCurrentOverlaps"] = "None"; 
	// Default variable for the region selected
	settings["defaultRegionSelected"] = "";
	// wheather it is possible to remove regions selection
	settings["allowRemoveRegionSelection"] = true;
		
	/* ENDOF SETTINGS*/
	/* CURRENT  AND DEFAULT STATE */
	currentState["exploreRegionSelected"] = settings["defaultRegionSelected"];	
	// a variable to store all the data about the reference state
	currentState["referenceQuery"] = {"genome":"",
									  "dataset":"",
									  "query":"",
									  "values":{},
									  "totalNumber":0
									  };
	// The variable that indicates which are the overlaps we should display
	currentState["overlapSelection"] = settings["overlapSelection"];
	// A variable to store the current overlap data
	currentState["currentOverlaps"] = settings["defaultCurrentOverlaps"];
	// This variable stores the current number of regions under inspection
	currentState["totalNumberOfRegions"] = 0;
	// This variable stores the current number of regions under inspection
	currentState["totalNumberOfSamples"] = 0;
	// User datasets to be activated or currently activated
	currentState["userDatasets"] = [<?php
		if (isset($_GET['userdatasets'])){
			$userdatasets = explode(";",$_GET['userdatasets']);
			foreach ($userdatasets as $dataset){				
				$xmlRequest = xmlrpc_encode_request('activateUserDataset', array($dataset));
				$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);			
				if ($arrayResponse[0]==0){
					echo '["'.$dataset.'",'.$arrayResponse[2].'],';
				}				
			}
		}
	?>];
	//this variable stores the info for all active region sets
	currentState["datasetInfo"] = {};	
	
	/* ENDOF CURRENT AND DEFAULT STATE */	
	
	  	
	/* INITIALIZATION */
	//initialize all delegation
	initEventDelegationRegionsTable();
	initEventDelegationFeatureListing();	
	// initialize button properties
	initBasicButtons();		
	// dowload the information for the dataset
	initExploreButtons();	
	//activate II datasets
	activateIlluminaInfoniumDatsets();
	//alert(4);
	// initialize the default region set
	initRegionSets();
	//alert(5);
	//initialize the list of features
	initFeatures();
	//alert(6);		
	//default start
	activateMode_ExploreRegionSelection();
	//alert(7);
	/* ENDOF INITIALIZATION*/	
});
	
		
</script>		
</head>

<body>

<div class="container">
    <div class="leftside">
        <div class="logo">
        	<a href="index.php"><img src="extras/logo_tes.PNG" width="242px" height="90px" align="bottom" style="border-width:0px"></a>
        </div>
        
        <div class="regions">
	        <div class="regionsSelection">
        		<h2 class="boxheader">Select a dataset</h2>
            	<table id="regionsTable" class="regionsTableClass activeSearchBox" cellspacing=0>		 		
		 		</table>
            </div>
            <div class="regionsSelected">
	            <h2 class="boxheader"></h2>
              <p class="exploreDefaultDatasetsButton ui-corner-left">Select another dataset</p>
            </div>
        </div>
        
        <div class="features activeSearchBox">
        	<h2 class="boxheader">Explore the dataset properties</h2>            
        </div>
        <div id="iconLegend" style="padding-left:10px;">              
              <!-- The box in the right that will include all results -->
              <i>
              <p>Icons legend</p>
              
              <span>
              <div style="float:left;" class="ui-icon ui-icon-info"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Indicates a default set of regions</p><br/>
              <div style="float:left;" class="ui-icon ui-icon-person"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Indicates a user dataset</p><br/>
              <div style="float:left;" class="ui-icon ui-icon-play"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Allows to select the set of regions for exploration</p><br/>
              <br/>
              <div style="float:left;" class="ui-icon ui-icon-plusthick"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Points to a closed group of features</p><br/>
              <div style="float:left;" class="ui-icon ui-icon-minusthick"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Points to an open group of features</p><br/>
              <div style="float:left;" class="ui-icon ui-icon-search"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Indicates a dynamic feature</p><br/>              
              <div style="float:left;" class="ui-icon ui-icon-circle-check"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Indicates the active dynamic feature</p><br/>
              <div style="float:left;" class="ui-icon ui-icon-triangle-1-e"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Direcly selects a refinement</p><br/>
              <div style="float:left;" class="ui-icon ui-icon-zoomin"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Shows an advanced visualization</p><br/>              
              <br/>
              <div style="float:left;" class="ui-icon ui-icon-closethick"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Removes a refinement</p><br/>
              <div style="float:left;" class="ui-icon ui-icon-arrowthick-2-e-w"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Adds an OR condition</p><br/>
              <div style="float:left;" class="ui-icon ui-icon-cancel"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Stops OR clause selection</p><br/>
              <div style="float:left;" class="ui-icon ui-icon-flag"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Selects the current set of regions as reference</p><br/>
              <br/>
              <div style="float:left;" class="ui-icon ui-icon-script"></div><p style="float:left;margin:0px;padding-left:10px;height:16px;">Shows 10 regions from the current selection</p><br/>
              
              </span>
              </i>
          </div> <!-- End of  icon legend-->
        
    </div>

	<div class="rightside">
		<div class="header">
          <h1 align="center">
          	<b style="font-family: Verdana, Geneva, sans-serif; color: #B1C4C0;">Complete</b> 
          	<b style="font-family: 'Comic Sans MS', cursive; font-style: italic; color: #122DFF; font-weight: bold;">Genome</b> 
          	<b style="font-family: Verdana, Geneva, sans-serif; color: #FA9627;">Search</b>
          	<b style="font-family: Verdana, Geneva, sans-serif;">alpha</b>
          </h1>
	    </div>
    
    
    	<div class="menujq">          
            <ul id="menu">
                <li><span>Explore</span>
	                <ul id="firstmenu">
                        <li id="exploreDefaultDatasetsLink">
                        	<span>Genomic regions</span>
                        	<img class="corner_inset_right" alt="" src="menu/corner_inset_right.png"/>
                        </li>                        
                        <li id="exploreII27Button">
                        	<span>Illumina Infinium sets</span>
                        </li>
						<li class="last">
                            <img class="corner_left" alt="" src="menu/corner_left.png"/>
                            <img class="middle" alt="" src="menu/dot.gif"/>
                            <img class="corner_right" alt="" src="menu/corner_right.png"/>
                        </li>
                    </ul>
                </li>
                <!-- Upload is currently not avaialble for the II27 datasets
                <li><span>Upload</span>
               		 <ul>
                        <li id="uploadUserDatasetsButton" class="">
                            <img class="corner_inset_left" alt="" src="menu/corner_inset_left.png"/>
                            <span>Your own region set</span>
                            <img class="corner_inset_right" alt="" src="menu/corner_inset_right.png"/>
                        </li>
                        <li id="uploadUserGeneSetButton" class="notimplementedButton">
                       	  <span >Your own gene sets</span>
                   </li>
                        <li class="last">
                            <img class="corner_left" alt="" src="menu/corner_left.png"/>
                            <img class="middle" alt="" src="menu/dot.gif"/>
                            <img class="corner_right" alt="" src="menu/corner_right.png"/>
                        </li>
                    </ul>
                </li>
                -->
                <li id="searchButton"><span>Search</span>   
                	<!--ul>
			            <li id="searchButton" class="notimplementedButton">
                            <img class="corner_inset_left" alt="" src="menu/corner_inset_left.png"/>
                            <span>for similar regions</span>
                            <img class="corner_inset_right" alt="" src="menu/corner_inset_right.png"/>
                        </li>
                        <li class="last">
                            <img class="corner_left" alt="" src="menu/corner_left.png"/>
                            <img class="middle" alt="" src="menu/dot.gif"/>
                            <img class="corner_right" alt="" src="menu/corner_right.png"/>
                        </li>
                    </ul-->                 
      			</li>
                <li id="exportMenu"><span>Export</span>   
               		 <ul>
                        <li class="exportRegionsButton" >
                            <img class="corner_inset_left" alt="" src="menu/corner_inset_left.png"/>
                            <span>The current set of regions</span>
                            <img class="corner_inset_right" alt="" src="menu/corner_inset_right.png"/>
                        </li>
                        <li id="exportRegionsToGalaxyButton" class="notimplementedButton">
                            <img class="corner_inset_left" alt="" src="menu/corner_inset_left.png"/>
                            <span>The regions to Galaxy</span>
                            <img class="corner_inset_right" alt="" src="menu/corner_inset_right.png"/>
                        </li>
                        <li id="exportRegionsDataButton" class="notimplementedButton">
                        	<span >The current set of regions annotated with genomic data</span>
                        </li>
						<li id="exportCurrentQueryButton" class="notimplementedButton">
                        	<span >The current query</span>
                        </li>
                        <li class="last">
                            <img class="corner_left" alt="" src="menu/corner_left.png"/>
                            <img class="middle" alt="" src="menu/dot.gif"/>
                            <img class="corner_right" alt="" src="menu/corner_right.png"/>
                        </li>
                    </ul>                 
     			 </li>
                <li id="giveFeedbackButton"><span>Feedback</span>                	                
                </li>
                <li id="aboutButton"><span>About</span>
                	                  
                </li>
                <img style="float:left;" alt="" src="menu/menu_right.png"/>
            </ul>           
         </div>
         <div style="float:none; clear:both;"></div>
	 	

		<div class="content">			
            <div class="visualization">
            	<!-- The content of the modal dialog for not implemented follows -->
				<!--div id="exportQueryDataDialog" class="hiddenstuff">
								<p>Please, select the datasets you want exported and give us an email address to send you the link to your results</p>
								<span style="color: red;"></span>
								<br/>
								<form class="jqtransform" id="exportQueryDataForm">		
									<table>          	
			          		<tr class="rowElem" >
											<td><input id="regionsCheckBox" name="regions" type="checkbox" checked="checked" disabled="disabled" /></td>
											<td><label>Regions</label></td>
										</tr>																
										<tr class="rowElem">
				          			<td><label>Email: </label></td>
				          			<td><input name="email" type="text" size="30"></input></td>
				          	</tr>	
									</table>
									<div id="toggleCheckBoxes">Toggle</div>
									<div id="checkCheckBoxes">Check all</div>
									<div id="uncheckCheckBoxes">Uncheck all</div>
								</form>	
								<input class="exportRegionsDataSubmit" type="button" value="Submit"/>
							</div><!-- End of exportQueryDataDialog-->
							
              <!--div id="exportRegionsDialog" class="hiddenstuff">
								<p>Please, provide your email address to send you the link to your results</p>
								<span style="color: red;"></span>
								<br/>
								<form class="jqtransform" id="exportRegionsForm">		
									<table>          	
			          	<tr class="rowElem">
			          			<td><label>Email: </label></td>
			          			<td><input name="email" type="text" size="30"></input></td>
			          	</tr>
									<tr class="rowElem">
										<td></td>	
										<td></td>
									</tr>
								</table>
								</form>	
								<input class="exportRegionsSubmit" type="button" value="Submit"/>				
							</div><!-- End of exportRegionsDialog-->
              
              
              <div id="rangeFeaturePlotMain">
								<div class="jqPlot" id="rangeFeaturePlot">									
								</div><!-- End of rangeFeaturePlot-->
								
			  			</div><!-- End of rangeFeaturePlotMain-->  			
						</div><!-- End of visualization-->
				
            <div class="infobox">   
            	Select a region set you would like to explore           
						</div><!-- End of infobox-->
						
	    </div>

		<div class="querySide">
          <div class="queryResults">             
              <div id="totalNumberOfDocuments">
               	  <p>
                      <label>Total number of samples:</label>
                      <label id="totalSamples">0</label>                                            
                  </p>
                  <p>
                      <label>Total number of regions:</label>
                      <label id="totalDocuments">0</label>
                      <span style="float:left;" class="showNext10Results ui-icon ui-icon-zoomin"></span>                      
                  </p>		
              </div> <!-- End of  number of documents in the current query listing-->
              
              
              <div id="resultsHitsListing">                  
                  <!-- The box in the right that will include all results -->
                  <p></p>
              </div> <!-- End of  results top hits listing-->                                                                           
          </div> <!-- End of queryResults listing-->    
          <div id="referenceListing">              
              <!-- The box in the right that will include all results -->
          </div> <!-- End of  reference listing-->
	    </div><!-- End of querySide listing--> 
	    
	</div><!-- End of rightside-->
	</div><!-- End of container-->
	
    <div class="hiddenstuff">
    	<!-- The content of the modal dialog for not implemented follows -->
				
				
				
    </div>
</body>
</html>