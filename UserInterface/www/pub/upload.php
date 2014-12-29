<?php
  require_once("grab_globals.lib.php");  
  include("xmlrpc_submit.php");
  include("settings.php");
  include("utils.php");
  
	// This part send a request for basic information for the regions supported by the current started server
	ob_start();
	$xmlRequest = xmlrpc_encode_request('getStatus', array($_SERVER['SERVER_NAME'],"upload"));
	$arrayResponse = sendRequest($rpc_server, '/', $xmlRequest, $rpc_port);
	ob_end_clean();	
	if($arrayResponse === "OK") {
		//header('Content-Type: text/html'); // plain html file		
	}else{
		//echo "not ok $arrayResponse";	
		if (strlen(strstr($_SERVER['SERVER_NAME'],'moebius')) == 0){
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
  	
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<link rel="SHORTCUT ICON" href="extras/new_logo_symbol_16.ico"/>
	<link href="menu/menu.css" rel="stylesheet" type="text/css" />
	
	<script type="text/javascript" src="jQuery/js/jquery-1.4.2.min.js"></script>
	<script type="text/javascript" src="commonCGS.js"></script>
		
	<link href="testIndex.css" rel="stylesheet" type="text/css" />
  
  <!-- The purpose of the jQuery UI is to use the slider, remove them if the slider is removed -->
  <script type="text/javascript" src="jQuery/js/jquery-ui-1.8.5.custom.min.js"></script>		
	<link type="text/css" href="jQuery/css/custom-theme/jquery-ui-1.8.5.custom.css" rel="stylesheet" />
    
  <!--script type="text/javascript" src="jqtransformplugin/jquery.jqtransform.js"></script-->		
  <!--link type="text/css" href="jqtransformplugin/jqtransform.css" rel="stylesheet" /-->
	<!--  Try niceForms -->
	<!--script type="text/javascript" src="jquery.niceforms/niceforms.js"></script>
	<link type="text/css" href="jquery.niceforms/niceforms-default.css" rel="stylesheet" /-->		
	
  
  <link href="jQueryUI-mine/jquery-ui-mine.css" rel="stylesheet" type="text/css" />
  
  <script src="jQueryElastic/jquery.elastic.js" type="text/javascript" charset="utf-8"></script>
  
  <!-- jQuery cookies -->	
  <script type="text/javascript" src="jquery.cookie/jquery.cookie.js"></script>
	<!-- jqPlot specific code and styles -->
	
	  <!-- jquery simple drop-won menu -->
  <link rel="stylesheet" type="text/css" href="jsddm/jsddm.css"/>
  <script type="text/javascript" src="jsddm/jsddm.js"></script>


<title>EpiExplorer upload</title>

<style type="text/css"></style>
<script type="text/javascript">		
var datasetNames = {};
var datasetProperties = {};
var userDatasets = [];
var alreadyUploaded = {};
	function emailvalidate(form_id,email) {
	   //alert('Javascript email check');
	   var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
	   var address = document.forms[form_id].elements[email].value;
	   if (address != ""){//If there is something provided then we should make sure it is valid
		   if(reg.test(address) == false) {	   	  
		   	  //$('#datasetEmailTD').html('<h4 style="color:#FF0000;">(*)</h>');
		   	  $('#beforeUploadStatus').html('<h4 style="color:#FF0000;"> Please provide a valid email address</h>');
		   	  $('#beforeUploadStatus').show();	      
		      document.forms[form_id].elements[email].focus();	      
		      return false;
		   }else{
		   		//$('#datasetEmailTD').html("(*)");		   			   		
		   		$.cookie("cgs:settings:email", address, { expires: 30});	   		
		   		return true;
		   }
	   }else{	   	 	 
	   	 return true;
	   }
	}
	function validate(form_id,email,datasetName,datasetUploadedFile,dataList) {	
					
		setFullSettings();
		
		var datasetNameValue = document.forms[form_id].elements[datasetName].value;
						
		if (datasetNameValue.length > 0){
						
			if (alreadyUploaded[datasetNameValue] !== undefined){
				alert("You already uploaded a dataset named '"+datasetNameValue+"'. Please rename your dataset and try again!");
				return false;				
			}else{
				alreadyUploaded[datasetNameValue] = true;
			}		
				
			$('#datasetNameTD').html('(*)');
			if (document.forms[form_id].elements[datasetUploadedFile].value.length > 0 || document.forms[form_id].elements[dataList].value.length > 0){
				
				$('#datasetFileTD').html('(*)');
				$('#datasetAreaTD').html('(*)');
				if (emailvalidate(form_id,email)){
										
					$('#uploadStatus').show();
					
					$("#dialog-confirm" ).dialog({							
							resizable: false,
							height:450,
							width:450,
							modal: false,
							buttons: {								
								OK: function() {
									$( this ).dialog( "close" );
									$('#uploadStatus').attr("src","")
									$('#beforeUploadStatus').html("");
								}
							}
					});
					$('#beforeUploadStatus').html('<h4 style="color:#FF0000;">Uploading...</h4><br/><img src="http://epiexplorer.mpi-inf.mpg.de/extras/ajax-loader-big.gif" alt="Processing"/>');
					return true;
				}else{
					return false;
				};						
			}else{				
				document.forms[form_id].elements[datasetUploadedFile].focus();				
				$('#beforeUploadStatus').html('<h4 style="color:#FF0000;"> Please provide a dataset, either as a file or as plain text</h>');
				$('#datasetFileTD').html('<h4 style="color:#FF0000;">(*)</h>');
				$('#datasetAreaTD').html('<h4 style="color:#FF0000;">(*)</h>');
				$('#beforeUploadStatus').show();	   			
				return false;
			}
		}else{
			$('#datasetNameTD').html('<h4 style="color:#FF0000;">(*)</h>');
			$('#beforeUploadStatus').html('<h4 style="color:#FF0000;"> Please provide a name for your dataset</h>');			
			document.forms[form_id].elements[datasetName].focus();
			$('#beforeUploadStatus').show();
			return false;
		}
	}	
	function setFullSettings(){
		var fullSettings = "";
		var index = 1;
		$('#advancedOptions tr').each(function(){
			index = index + 1;
			if (index > 3){			 
				//alert($(this).text());
				//alert($(this).find("td input:hidden").length)
				var datasetName = $(this).find("input:hidden")[0].value;
				//alert(datasetName);
				var hasFeatures = Number($($(this).find('input[name="hasFeatures"]')[0]).is(':checked'));
				fullSettings = fullSettings + datasetName+":hasFeatures:"+hasFeatures+",";
				//alert(hasFeatures);
				if (hasFeatures){ 			
					var useNeighborhoodList = $(this).find('input[name="useNeighborhood"]');
					//alert(useNeighborhoodList.length);
					if (useNeighborhoodList.length > 0){
						var useNeighborhood = Number($(useNeighborhoodList[0]).is(':checked'));
						//alert(useNeighborhood);
						fullSettings = fullSettings + datasetName+":useNeighborhood:"+useNeighborhood+",";
					}
					var includeOMIMList = $(this).find('input[name="includeOMIM"]');
					//alert(includeOMIMList.length);
					if (includeOMIMList.length > 0){
						var includeOMIM = Number($(includeOMIMList[0]).is(':checked'));
						//alert(includeOMIM);
						fullSettings = fullSettings + datasetName+":includeOMIM:"+includeOMIM+",";
					}
					var includeGOList = $(this).find('input[name="includeGO"]');
					//alert(includeGOList.length);
					if (includeGOList.length > 0){
						var includeGO = Number($(includeGOList[0]).is(':checked'));
						//alert(includeGO);
						fullSettings = fullSettings + datasetName+":includeGO:"+includeGO+",";
					}
					var includeGeneDescriptionsList = $(this).find('input[name="includeGeneDescriptions"]');
					//alert(includeGeneDescriptionsList.length);
					if (includeGeneDescriptionsList.length > 0){
						var includeGeneDescriptions = Number($(includeGeneDescriptionsList[0]).is(':checked'));
						//alert(includeGeneDescriptions);
						fullSettings = fullSettings + datasetName+":includeGeneDescriptions:"+includeGeneDescriptions+",";
					}
				}
			}		
		});
		var input = $('input[name="fullSettings"]');	
		$(input).val(fullSettings);	
	}

$(function() {	
	
	
	/*####----####---- Start if jQuery onReady ----####----####*/
	function initAdvancedOptionsClosed(){
		$('#advancedOptions tr').remove();
		$('#showhideAdvancedOptions').one("click",initiateAdvancedOptionsOpen);
		$('#showhideAdvancedOptions').val("Set custom annotation settings")
		var input = $('input[name="fullSettings"]');	
		$(input).val("");	
	}
	function initiateAdvancedOptionsOpen(){
		//alert("open");
		var curGenome = $('select[name="genomeSelect"] option:selected').val();
		$.ajax({
	  			type: 'GET',
	  			url: "relay.php",
	  			data: { "type": "getDefaultAnnotationSettings",
						"genome": curGenome ,
		   			  },	   		
		   		dataType:"json",
	  			success: function(jsonResult){
	  				var tableHeader = $('<tr><th>Selected</th><th>Annotation name</th><th>Annotation specific</th></tr>');
	  				$('#advancedOptions tr').remove();
					$('#advancedOptions').append(tableHeader);
					var line = $('<tr></tr>');
					var deselectAllButton = $('<td colspan="2"><input type="button" id="deselectAllCheckedButtonID" value="Deselect all"></input></td>');
					line.append(deselectAllButton);
					deselectAllButton.click(function(){
						$(".datasetCheckClass").attr('checked',false)
					})						
					
					$('#advancedOptions').append(line);
	  				var sortedDatasetNames = [];
	  				$.each(jsonResult,function( dName, value ){
						sortedDatasetNames.push(dName);
					});				
					sortedDatasetNames.sort();
	  				$.each(sortedDatasetNames,function(index,datasetName){  					
	  					var datasetProperties = jsonResult[datasetName];
	  					var line = $('<tr></tr>');
	  					if (! (datasetName in datasetNames)){
							line.append($('<td>'+datasetName+'<input type="hidden" value="'+datasetName+'" class="datasetCheckClass"/></td>'));
						}else{
							line.append($('<td>'+datasetNames[datasetName]+'<input type="hidden" value="'+datasetName+'"/></td>'));
						}
	  					$.each(datasetProperties,function(propertyName,propertyValue){
	  						if (propertyName == "hasFeatures"){
	  							if (propertyValue){
	  								line.prepend($('<td><input name="hasFeatures" type="CHECKBOX" class="datasetCheckClass" checked/></td>'));
	  							}else{
	  								line.prepend($('<td><input name="hasFeatures" type="CHECKBOX" class="datasetCheckClass"/></td>'));  								
	  							}
	  						}else if (propertyName == "useNeighborhood"){  							
	  							if (propertyValue){
	  								line.append($('<td><input name="useNeighborhood" type="CHECKBOX" class="datasetCheckClass" checked/><label>Neighborhood</label></td>'));
	  							}else{
	  								line.append($('<td><input name="useNeighborhood" type="CHECKBOX" class="datasetCheckClass"/><label>Neighborhood</label></td>'));  								
	  							}
	  						}else if (propertyName == "includeGeneDescriptions"){
	  							if (propertyValue){
	  								line.append($('<td><input name="includeGeneDescriptions" type="CHECKBOX" class="datasetCheckClass" checked/><label>Gene descriptions</label></td>'));
	  							}else{
	  								line.append($('<td><input name="includeGeneDescriptions" type="CHECKBOX" class="datasetCheckClass"/><label>Gene descriptions</label></td>'));  								
	  							}
	  						}else if (propertyName == "includeGO"){
	  							if (propertyValue){
	  								line.append($('<td><input name="includeGO" type="CHECKBOX" class="datasetCheckClass" checked/><label>GO descriptions</label></td>'));
	  							}else{
	  								line.append($('<td><input name="includeGO" type="CHECKBOX" class="datasetCheckClass" /><label>GO descriptions</label></td>'));  								
	  							}
	  						}else if (propertyName == "includeOMIM"){
	  							if (curGenome == "hg18" || curGenome == "hg19"){
		  							if (propertyValue){
		  								line.append($('<td><input name="includeOMIM" type="CHECKBOX" class="datasetCheckClass" checked/><label>OMIM descriptions</label></td>'));
		  							}else{
		  								line.append($('<td><input name="includeOMIM" type="CHECKBOX" class="datasetCheckClass" /><label>OMIM descriptions</label></td>'));  								
		  							}
	  							}
	  						}else if (propertyName == "patterns"){
	  							line.append($('<td><label>'+propertyValue.join(", ")+'</label></td>'));  							
	  						}else{
	  							line.append($('<td>'+propertyName+'</td>'))
	  						}
	  					});
	  					$('#advancedOptions').append(line);	
	  				});
	  				// Add the user datasets
	  				//alert("Initializing user datasets")
	  				$.each(userDatasets,function(index,userDatasetName){
	  					//alert(userDatasetName)
	  					var line = $('<tr></tr>');
	  					if (! (userDatasetName in datasetNames)){
							line.append($('<td>'+userDatasetName+'<input type="hidden" value="'+userDatasetName+'"/></td>'));
						}else{
							line.append($('<td>'+datasetNames[userDatasetName]+'<input type="hidden" value="'+userDatasetName+'"/></td>'));
	  					}			
	  					line.prepend($('<td><input name="hasFeatures" type="CHECKBOX" class="datasetCheckClass" /></td>'));
	  					$('#advancedOptions').append(line);
	  				});			
	  			}  			
			 });	
		$('#showhideAdvancedOptions').one("click",initAdvancedOptionsClosed);
		$('#showhideAdvancedOptions').val("Use default annotation settings")
		
	}
	
	function initDatasetsInfo(){
		$.ajax({
				type: "GET",
				url: "relay.php",
				dataType: "json",				 			
				data: "type=getDatasetInfo&datasetName=all",
				success: function (result){	
					$.each(result,function(datasetName,datasetProperties){					
						datasetNames[datasetName] = datasetProperties["officialName"];						
					});				
				}
		});	
	}
	function initUserDatasetsFromGenome(){
		userDatasets = [];
		if ($.cookie("cgs:settings:userdatasets:"+$('#genomeSelectControl').val())){
			 userDatasets = $.cookie("cgs:settings:userdatasets:"+$('#genomeSelectControl').val()).split(";");		 
			 if (userDatasets[0].length > 0){
			 	userDatasets = userDatasets;
			 }else{
			 	userDatasets = [];
			 } 
		}
		//alert(userDatasets);
	}
	initBasicButtons();
	
	$('textarea.tobeElastic').elastic();
	$('#uploadStatus').hide();
	$('#beforeUploadStatus').show();
	
	$('#clearThePasteForm').click(function(){		
		$('#pasteDataForm').val("");
		$('#datasetUploadedFileID').val("");
	});
	if ($.cookie("cgs:settings:email")){
		$('#emailField').val($.cookie("cgs:settings:email"));
	}
	if ($.cookie("cgs:settings:genome")){
		$('#genomeSelectControl').val($.cookie("cgs:settings:genome"));
	}else{
		$('#genomeSelectControl').val("hg18");;
			
	}
	
	initUserDatasetsFromGenome();
	
	initAdvancedOptionsClosed();
	initDatasetsInfo();
	
	$("#uploadStatus").load(function (){
		$('#beforeUploadStatus').html("");
	})
	
	$('#genomeSelectControl').change(function(){
		//alert("Genome changed");
  		initAdvancedOptionsClosed();
  		initUserDatasetsFromGenome();		
	});
	$('#mergeOverlapsID').change(function(){
		var checked = $(this).attr('checked');
		if (checked){
			$("#useScoreID").attr('checked',false)									
			$("#useStrandID").attr('checked',false)						
		}
		$("#useScoreID").attr('disabled',checked)
		$("#useStrandID").attr('disabled',checked)
			
	});
	
		
	
	
});
</script>
<style type="text/css">
  	div.container {
  		padding-left:20px;
  	}		
 </style>
</head>

<body>
<!--div class="container"-->    
<div class="uploadcontainer">
    	  	   
          		<p>
					<h4>Upload a user dataset</h4>
					<div>
						Users can upload custom sets of genomic region for exploration and analysis with EpiExplorer. User-uploaded region sets are annotated with a broad range of genomic attributes and can be used in the same way as the default region sets of EpiExplorer. Because the initial annotation can take several hours for large datasets, providing an e-mail address is recommended. EpiExplorer will send an e-mail to this address upon successful preparation of the user-uploaded dataset. 
						<br><br>
						All uploaded datasets must be in UCSC Genome Browser compatible <a href="http://genome.ucsc.edu/FAQ/FAQformat.html#format1" target="_blank">BED format</a>, which is essentially a text file with tab-separated columns. Every line should have at least 3 values: the first one is the chromosome symbol (e.g. chr1), the second value is the chromosome start position and the third is the chromosome end position. User-uploaded datasets cannot contain more than 500,000 regions. Furthermore, regions should not be of size larger than 10,000,000 basepairs and should have chromosome end larger than chromosome start (i.e. be at least one basepair long). Pasting from a properly formatted Excel sheet usually results in valid BED files, while pasting from Word is not recommended.
						<br/>
						<p style="color:#999999;">
							Example :<br/>
						<textarea name="textarea" cols="40" rows="3" wrap="VIRTUAL" readonly="readonly" style="color:#999999;">chr1	243807616	243807827
chr15	18364154	18364715
chrX	73428918	73429294</textarea>							
						</p>
					 </div><!-- end div unnamed -->
				</p>
	
	
	<div id="formcontainer">
	
	<form id="form_upload" enctype="multipart/form-data" action="<?php if (strlen(strstr($_SERVER['SERVER_NAME'],'mpiat3502'))>0 || strlen(strstr($_SERVER['SERVER_NAME'],'moebius'))>0){echo "../cgi-bin/epiexplorer/upload2.cgi";}else{echo "./cgi-bin/upload2.cgi";}?>" method="POST" onsubmit="javascript:return validate('form_upload','email','datasetName','datasetUploadedFile', 'dataList');" target="uploadStatus">
	
	<input type="button" value="Set custom annotation settings" id="showhideAdvancedOptions"/>
	<table id="advancedOptions">
		<input type="hidden" value="" name="fullSettings"/>		
	</table>
	<table>	
	
	<tr class="rowElem">				
		<td><label>Name of the dataset: </label></td>
		<td align="left"><input type="text" name="datasetName" size="40" value=""/></td>
		<td id="datasetNameTD"><h4 style="color:#FF0000;">(*)</h4></td>
	<input type="hidden" name="action" value="upload"/>
	</tr>
	<tr class="rowElem">				
		<td><label>Genome: </label></td>
		<td align="left">
			<!--select name="genomeSelect" id="genomeSelectControl" disabled="disabled"-->
			<!-- If this disabled is removed, then the upload2.cgi should also be updated to get the value from the genomeSelect form element and not use the default -->   
			<select name="genomeSelect" id="genomeSelectControl">
				<option value="hg18">hg18</option>
				<option value="mm9">mm9</option>
				<option value="hg19">hg19</option>									
			</select>	
		</td>							
		<td></td>							
	</tr>
	<tr class="rowElem">
		<td><label>Dataset description:</label></td>
		<td><textarea class="tobeElastic" rows="5" cols="60" name="datasetDesc"></textarea></td>
		<td></td>
		<br\>
	</tr>
	
	<tr class="rowElem">
		<td><label>Paste your dataset data here (in <a href="http://genome.ucsc.edu/FAQ/FAQformat.html#format1" target="_blank">BED format</a>):</label><input type="button" value="Clear" id="clearThePasteForm"/></td>
		<td><textarea rows="10" cols="60" id="pasteDataForm" name="dataList"></textarea></td>
		<td id="datasetAreaTD"><h4 style="color:#FF0000;">(*)</h4></td>
		<br\>
	</tr>	
	<tr class="rowElem">			
		<td><label for="datasetConvertSpacesToTabs">Convert spaces to tabs</label></td>
		<td><input type="checkbox" name="datasetConvertSpacesToTabs" id="datasetConvertSpacesToTabsID"/></td>
		<td></td>	
	</tr>
	<tr class="rowElem">			
		<td><label for="datasetUploadedFile">or select the dataset file: </label></td>
		<td align="left"><input type="file" name="datasetUploadedFile" id='datasetUploadedFileID'/></td>
		<td id="datasetFileTD"><h4 style="color:#FF0000;">(*)</h4></td>
	<br/>
	</tr>
	<tr class="rowElem">			
		<td><label for="ignoreNonStandardChromosomes">Automatically skip regions from non supported chromosomes (for example, we only support chr1 - chr22, chrX and chrY for human)?</label></td>
		<td><input type="checkbox" name="ignoreNonStandardChromosomes" id="ignoreNonStandardChromosomesID"/></td>
		<td></td>	
	</tr>	
	<tr class="rowElem">			
		<td><label for="useStrand">Use the strand data? (expects "+" or "-" on position 6)</label></td>
		<td><input type="checkbox" name="useStrand" id="useStrandID"/></td>
		<td></td>	
	</tr>
	<tr class="rowElem">			
		<td><label for="useScore">Use the score data? (expects integer scores between 0 and 1000 on position 5)</label></td>
		<td><input type="checkbox" name="useScore" id="useScoreID"/></td>
		<td></td>	
	</tr>		
	<tr class="rowElem">			
		<td><label for="mergeOverlaps">Merge overlapping regions?</label></td>
		<td><input type="checkbox" name="mergeOverlaps" id="mergeOverlapsID"/></td>
		<td></td>	
	</tr>
	<tr class="rowElem">			
		<td><label for="computeReference">Compute a shuffled control set?</label></td>
		<td><input type="checkbox" name="computeReference" id="computeReferenceID"/></td>
		<td></td>	
	</tr>
	<tr class="rowElem">			
		<td><label>Email for automated notification (<b>recommended</b>):</label></td>
		<td align="left"><input name="email" type="text" size="40" value="" id="emailField"/></td>
		<td id="datasetEmailTD"><h4 style="color:#FF0000;"></h4></td>
	<br/>
	</tr>	
	<tr class="rowElem">
		<td></td><td><input type="submit" value="Upload region set" id="uploadFormSubmit"></td><td></td>
	</tr>
	
	</table>					
	</form>
	</div> <!-- End of formcontainer -->
	<div id="dialog-confirm" title="Upload dataset status">
		<p id="beforeUploadStatus"></p>
		<!--iframe name="uploadStatus" id="uploadStatus" width="400px" height="300px" title="Upload dataset status" frameborder="0" scrolling="auto"-->		
		<iframe name="uploadStatus" id="uploadStatus" width="90%" height="90%" title="Upload dataset status" frameborder="0" scrolling="auto">
		</iframe>
	</div>
	
	
	</div><!-- End of container-->						

	
</body>
</html>


		 