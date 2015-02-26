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
 		$body = "On ".date("H:i:s d.m.y")." requested by ".$_SERVER["REMOTE_ADDR"]." (".gethostbyaddr($_SERVER["REMOTE_ADDR"])."\nStatus:'".$arrayResponse."'";
 		if (mail($contact_email, $subject, $body)) {
   			header( 'Location: maintenance.php') ;
  		} else {
   			header( 'Location: maintenance.php') ;
  		}  		
	}  	 	
?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

	<link href="menu/menu.css" rel="stylesheet" type="text/css" />
	<script type="text/javascript" src="jQuery/js/jquery-1.4.2.min.js"></script>
	<script type="text/javascript" src="commonCGS.js"></script>	
	<link href="testIndex.css" rel="stylesheet" type="text/css" />
  
  <!-- The purpose of the jQuery UI is to use the slider, remove them if the slider is removed -->
  <script type="text/javascript" src="jQuery/js/jquery-ui-1.8.5.custom.min.js"></script>		
	<link type="text/css" href="jQuery/css/custom-theme/jquery-ui-1.8.5.custom.css" rel="stylesheet" />
    
  <!--script type="text/javascript" src="jqtransformplugin/jquery.jqtransform.js"></script>		
	<link type="text/css" href="jqtransformplugin/jqtransform.css" rel="stylesheet" /-->
    
	<link href="jQueryUI-mine/jquery-ui-mine.css" rel="stylesheet" type="text/css" />
	
	<script src="jQueryElastic/jquery.elastic.js" type="text/javascript" charset="utf-8"></script>
	
	<!-- jqPlot specific code and styles -->


<title>Search for similar regions</title>

<style>
.notoverlap	{
	background:#91FF73;
}
.overlap	{
	background:#FC896F;
}
.hiddenstuff{
	display:none;
}
.results {
	float:left;
	width:60%;	
}
.listhits{
	float:left;
	width:40%;	
	padding-top:30px;
	
}
</style>
<script type="text/javascript">		
	
	/*####----####---- Start if jQuery onReady ----####----####*/
$(function() {
	
		function checkStartEnd(startS,endS){
			var reg = /^(\d)+$/;
			if(reg.test(startS) == false || reg.test(endS) == false) {
				if (reg.test(startS) == false)alert(startS + 1);
				if (reg.test(endS) == false)alert(endS + 2);
				return false;
			}			
			var start = parseInt(startS,10);
			var end = parseInt(endS,10);
			//			alert(start+" -- "+end);
			if (start < end){
				return true;
			}
			//alert(2);
			return false;			
		}
		function checkChrom(chromValue){
			var reg = /^chr([1-9XY])+$/;	   	
	   	if(reg.test(chromValue) == false) {
	   		return false;
	   	}			
			var found = false;
			var i;
			for(i=1;i<23;i=i+1){
				if (chromValue == "chr"+i){
					found = true;
					break;
				}				
			}
			if (chromValue == "chrX") found = true; 
			if (chromValue == "chrY") found = true; 
			return found;			
		}
		
		function loadRegionWords(results){
			var resultQuery = "<table>\n<br/>";
			resultQuery = resultQuery + "<tr><th>Selected</th><th class=\"hiddenstuff\">Region set</th><th>Description</th><th class=\"hiddenstuff\">Word value</th><th class=\"hiddenstuff\">Other info</th></tr>\n<br/>";						
			
			$.each(results,function( regionSet, regionWords ){
				//alert("start ");
				//alert(regionSet);
				var datasetName = regionSet;
				if (regionSet in defaultRegionSets){
					datasetName = defaultRegionSets[regionSet]["officialName"];
				}
				//alert("start "+defaultRegionSets[regionSet]["officialName"]);
				
				
				if (regionWords.length == 0){
					//alert(regionSet +" has no words ");
					resultQuery = resultQuery + "<tr class=\"notoverlap\"><td><input type=\"checkbox\"/></td><td class=\"hiddenstuff\">"+regionSet+"</td><td>Does not overlap with "+datasetName+"</td><td class=\"hiddenstuff queryPart\">-"+regionSetOverlapWords[regionSet]+"</td></tr>\n<br/>";
				}else{
					//alert(regionSet +" has words. First is "+regionWords[0][0]);
					var overlaps = true;
					$.each(regionWords,function( wordIndex, regionWord ){
						if (regionWord[0] == "mmd" || regionWord[0] == "mud" || regionWord[0] == "mdd"){
							overlaps = false;
						}else if (regionWord[0] == "dmm" || regionWord[0] == "dum" || regionWord[0] == "ddm"){
							overlaps = false;
						}
					});
					if (overlaps){
						resultQuery = resultQuery + "<tr class=\"overlap\"><td><input type=\"checkbox\"/></td><td class=\"hiddenstuff\">"+regionSet+"</td><td>Overlaps with "+datasetName+"</td><td class=\"queryPart hiddenstuff\">"+regionSetOverlapWords[regionSet]+"</td><td class=\"hiddenstuff\">"+regionWords+"</td></tr>\n<br/>";						
					}else{
						resultQuery = resultQuery + "<tr class=\"notoverlap\"><td><input type=\"checkbox\"/></td><td class=\"hiddenstuff\">"+regionSet+"</td><td>Does not overlap with "+datasetName+"</td><td class=\"queryPart hiddenstuff\">-"+regionSetOverlapWords[regionSet]+"</td><td class=\"hiddenstuff\">"+regionWords+"</td></tr>\n<br/>";
					}										
				}
			});			
			
			resultQuery = resultQuery + "</table>\n<br/>";
			
			//alert("end");
			return resultQuery;				
		}
	function getQuery(sep,queryPrefix){
		var negativeQueryText = "";
		var positiveQueryText = "";		
		var queryText = ""	
		$('td input:checked').each(function(index) {		
			var queryPartText = $(this).parent().siblings("td.queryPart").text();
			if (queryPartText.charAt(0)=="-"){
				//negative query								
				if (negativeQueryText.length > 0){
					//there has been some terms already added
					negativeQueryText = negativeQueryText +sep+ queryPartText;
				}else{
					//this is the first term to be added
					negativeQueryText = queryPartText;
				}					
			}else{
				//positive query								
				if (positiveQueryText.length > 0){
					//there has been some terms already added
					positiveQueryText = positiveQueryText +sep+ queryPartText;
				}else{
					//this is the first term to be added
					positiveQueryText = queryPartText;
				}					
			}
		});
		if (positiveQueryText.length > 0){
			queryText = positiveQueryText;
			// add the query prefix if exists
			if (queryPrefix.length > 0){
				queryText = queryText+sep+queryPrefix;
			}				
			if (negativeQueryText.length > 0){
				// if there is a negative query we put at at the end and we are sure there is sth before that
				queryText = queryText+sep+negativeQueryText;
			}
		}else{
			//there is no positive query
			if (negativeQueryText.length > 0){
				//if there is a negative query we have to make sure there is a request before it
				if (queryPrefix.length > 0){
					queryText = queryPrefix+sep+negativeQueryText;
				}else{
					//the query has no positive part so add ID:*
					queryText = "Eregion"+sep+negativeQueryText;
				}
			}else{
				queryText = queryPrefix;
			}					
		}		
		return queryText;			
	}	
	var regionSetOverlapWords = {
				"broad_histones":"overlaps:bhist:*",
				// NJ Unclear what would need adding here for Blueprint
				"ensembl_gene_promoters_centered":"overlaps:promoters_centered",
				"repeat_masker":"overlaps:repeats:all",
				"ensembl_gene_genes":"overlaps:genes",				
				"ensembl_gene_TSS":"overlaps:TSS",				
				"ensembl_gene_exons":"overlaps:exons",
				"ensembl_gene_introns":"overlaps:introns",				
				"ensembl_gene_promoters":"overlaps:promoters",
				"ensembl_gene_promoters_region":"overlaps:promoters_region",
				"uw_DNaseI":"overlaps:DNaseI:all",
				"conservation":"overlaps:conserved",
				"cgihunter_CpG_Islands":"overlaps:cgihunter_CpG_Islands",
				"ucsc_cpg_islands":"overlaps:ucsc_CpG_Islands"
			};	
		
	initBasicButtons();
	
	var defaultRegionSets = {};
	$.ajax({
				type: "GET",
				url: "relay.php",				
				dataType: "json",
				data: "type=regiontypes&genome="+settings["genome"],
				success: function (result){	
					$.each(result,function( datasetKey, datasetInfo ){
						//alert(datasetKey +" - "+ result[datasetKey]["isDefault"]);
						if (result[datasetKey]["isDefault"]){
							defaultRegionSets[datasetKey] = result[datasetKey];						
						}
					});
					
					//$.each(defaultRegionSets,function( index, value ){alert(index +" - - " + value["numberOfRegions"]);});
	}});	
	
	//alert(defaultRegionSets);
	
	$('textarea').elastic();
	
	//$("form.jqtransform").jqTransform();
	
	$('#searchSimilarRegionsButton').click(function(){	
		if (checkChrom($('#chrom').val()) == false){
			$('.results').text("Please provide a valid chromosome name (chr1,chrX, etc)");
			return 1;
		}		
		if (checkStartEnd($('#chromstart').val(),$('#chromend').val()) == false){
			$('.results').text("Please provide a valid chromosome start and end");
			return 1;
		}
		
		//alert("checks are over");
		$.ajax({
  			type: 'POST',
  			url: "relay.php",  			
  			data: {"type": "searchSingle",
							 "chrom": $('#chrom').val(), 
		   				 "chromstart": $('#chromstart').val(),
		   				 "chromend": $('#chromend').val()},		   				
		   	dataType: "json",
  			success: function(result){
  				//alert("Success " + result[1]['uw_DNaseI'].length);
  				var queryTable = loadRegionWords(result[1]);
  				queryTable = '<h2 class="boxheader ui-corner-left">Region properties</h2>\n'+queryTable;  				
  				$('.searchQuery').html(queryTable);  				
  				
  				$('.searchQuery').append($('<div id="submitcurrentQuery">Search similar</div>'));
  				
  				$('#submitcurrentQuery').button().click(function(){  					
  					var resultsTable = '<table><tr class="listRegionHits"><th>Name</th><th>Total number</th><th>Fitting the query</th></tr></table>';
  					$('.results').html(resultsTable);
  					
  					$.each(defaultRegionSets,function( datasetKey, datasetInfo ){
  						var query = getQuery(" ","ID:*");  						  						
  						var line = $('<tr><td>'+datasetInfo["officialName"]+'</td><td>'+datasetInfo["numberOfRegions"]+'</td><td><img src="images/ajax-loader.gif" align="center"></img></td></tr>');
  						$('.results table').append(line);
  						if (query.search("\-"+regionSetOverlapWords[datasetKey]) != -1){  							
  							//alert("No "+datasetKey);
  							line.find("td:nth-child(3)").text("0");
  							//return;
  						}else{ 
  							var localQuery = query;
  							if (query.search(regionSetOverlapWords[datasetKey])!= -1){
  								//alert("Yes "+datasetKey);
  								localQuery = query.replace(regionSetOverlapWords[datasetKey],"");
  								localQuery = localQuery.replace("  "," ");
  								//alert(localQuery);
  							}  							
  							var datastr = "type=basequeryJSON&regiontype="+datasetKey+"&query="+localQuery+"&ncompl=100";
  							line.find("td:nth-child(3)").text(datastr);  							
  							$.ajax({
	  							type: 'GET',
	  							url: "relay.php",  			
	  							data: datastr,		   				
			   				 	dataType: "json",
	  							success: function(result){	  								
	  								line.find("img").remove();
	  								if (result[1] > 0){ 
	  									var showResultsButton = $("<div>"+result[1]+"</div>");
	  									showResultsButton.button().click(function(){
	  										var listingText = "";
	  										$.each(result[3],function( completion, numberOfHits ){
	  											listingText = listingText + completion+"<br/>";
	  										});
	  										$('.listhits').html(listingText);	  										
	  									});
	  									line.find("td:nth-child(3)").text("");
	  									line.find("td:nth-child(3)").append(showResultsButton);
	  								}else{
	  									line.find("td:nth-child(3)").text("0");
	  								}
	  							}
	  						});	  						
  						}
  						
  					});
  					
  				});
  			}  			
		 });		 
   });
});
</script>		
</head>

<body>

<div class="container">
    <div class="leftside">
        <div class="logo">
        	<img src="images/logo_tes.PNG" width="242px" height="90px" align="bottom">
        </div>
        
        <div class="regions">
        	<div class="regionsSelection">
        		<h2 class="boxheader ui-corner-left">Provide a region</h2>
	        	<form class="jqtransform">          	
	          	<table>          	
		          	<tr class="rowElem">
		          		<td><label>Chromosome:</label></td>
		          		<td><input type='text' id='chrom' value="chr1"/></td>
		          		<br\>		          		
		         	 	</tr>
		         	 	<tr class="rowElem">
		          		<td><label>Start:</label></td>
		          		<td><input type='text' id='chromstart' value="777230"/></td>
		          		<br\>
		         	 	</tr>
		         	 	<tr class="rowElem">
		          		<td><label>End:</label></td>
		          		<td><input type='text' id='chromend' value="777602"/></td>
		          		<br\>
		         	 	</tr>
		         	 	<tr class="rowElem">
	          			<td></td>
	          			<td><input id="searchSimilarRegionsButton" type="button" value="Search..." /></td>
	          			
	          			
	          		</tr>	
	         		</table>
	        	</form>
	        </div>	        
        </div>
        <div class="searchQuery">        	
        </div>
        	
        
    </div>

	<div class="rightside">
		<div class="header">
          <h1 align="center">
          	<b style="font-family: Verdana, Geneva, sans-serif; color: #B1C4C0;">Complete</b> 
          	<b style="font-family: 'Comic Sans MS', cursive; font-style: italic; color: #122DFF; font-weight: bold;">Genome</b> 
          	<b style="font-family: Verdana, Geneva, sans-serif; color: #FA9627;">Search</b> 
          </h1>
	    </div>
    
    
    	<div class="menujq">          
            <ul id="menu">
                <li id="exploreDefaultDatasetsLink"><span>Explore</span>

                </li>
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
                <li id="searchButton"><span>Search</span>   
               
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
      
	    <div class="results">          
	    </div>
	    <div class="listhits"> 
	    	listhits         
	    </div>
	</div><!-- End of rightside-->
	</div><!-- End of container-->
    <div class="hiddenstuff">
    </div>
</body>
</html>