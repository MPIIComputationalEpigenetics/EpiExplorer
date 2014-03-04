function activateIlluminaInfoniumDatsets(){}
function activateIlluminaInfoniumDatsetsDEPRECATED(){
	var activeIIServers = [];	
	var currentIIServers = ['II_Bork', 'II_Chari', 'II_Chung', 'II_Encode', 'II_Gibbs', 'II_Groenninger', 'II_Hagemann', 'II_Kerkel', 'II_Kim', 'II_Lui', 'II_Rakyan_SB', 'II_Rakyan_WB', 'II_Terschendorff_Cervical', 'II_Terschendorff_WB', 'II_Terschendorff_WB_diabetes', 'II_Uddin', 'II_vdAuwera_normal', 'II_Walker', 'II_Zhang'];
	$.ajax({
		type: "GET",
		url: "relay.php",
		async:false,				 			
		dataType: "json",
		data: "type=regiontypes&sourceType="+settings["sourceType"]+"&genome="+settings["genome"],
		success: function (result){
			$.each(result,function(index,value){
				var idx = currentIIServers.indexOf(value); // Find the index
				if(idx!=-1) currentIIServers.splice(idx, 1); // Remove it if really found!
				
			});
		}
	});
	var counter = currentIIServers.length;
	$.each(currentIIServers,function(index,datasetID){
		$.ajax({
			type: "GET",
			url: "relay.php",			
			dataType: "json",				 			
			data: "type=activateUserDataset&datasetID="+datasetID,
			success: function(result){
				counter = counter - 1;
				//alert("Started:"+datasetID);
			}		
		});
	});
	while(counter > 0){
		alert("Waiting for all II servers to be started. Currently "+counter+" more");		
	}	
}

var b;
var t;
var bhist = ["Ctcf","H3k4me1","H3k4me2","H3k4me3","H3k9ac","H3k9me1","H3k27ac","H3k27me3","H4k20me1","H3k36me3","Pol2b"];
var tissues = ["any","Gm12878", "H1hesc", "Hepg2", "Hmec", "Hsmm", "Huvec", "K562", "Nhek", "Nhlf"];
for (b in bhist){	
	for (t in tissues){
		if (tissues[t] == "any"){
			overlapLabels["Eoverlaps:bhist:"+bhist[b]+":"+tissues[t]] = bhist[b];
		}else{
			overlapLabels["Eoverlaps:bhist:"+bhist[b]+":"+tissues[t]] = "in "+tissues[t];
		}
	}
}

// gets the current query. This loads all query elements form the page (class queryPrexix)
// orders them to ensure uniqueness (Not implemented yet)
// and return the query text
function getQuery(sep,queryPrefix){
	var negativeQueryText = "";
	var positiveQueryText = "";		
	var queryText = "";		
	
	$('span.queryPrefixRaw').each(function(index){
		var queryPrefixRaw = $(this).text();
		if (queryPrefix.startsWith("IIS:")){
			if (!queryPrefixRaw.startsWith("IIS:")){							
				return 1;
			}			
		}else{
			if (queryPrefixRaw.startsWith("IIS:")){
				return 1;
			}
		}		
		if (queryPrefixRaw.charAt(0)=="-"){
			//negative query								
			if (negativeQueryText.length > 0){
				//there has been some terms already added
				negativeQueryText = negativeQueryText +sep+ queryPrefixRaw;
			}else{
				//this is the first term to be added
				negativeQueryText = queryPrefixRaw;
			}					
		}else{
			//positive query								
			if (positiveQueryText.length > 0){
				//there has been some terms already added
				positiveQueryText = positiveQueryText +sep+ queryPrefixRaw;
			}else{
				//this is the first term to be added
				positiveQueryText = queryPrefixRaw;
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

function updateResultsAndDocuments(uResults,uDocuments){
	
	if (uResults || uDocuments){
		var query = getQuery(" ","Eregion");
		nh = 0;
		if (uResults){
			nh = 10;
		}					
		var regiontype = currentState["exploreRegionSelected"];	
		answerQuery(regiontype,query,0,nh,function(msg){
			//update the results
			if (uResults){					
				updateResults(msg);				
				
			}
			//update the documents					
			if (uDocuments){					
				updateNumberOfDocuments(msg);
			}									
		});
	}
	updateNumberOfSamples();
}

function updateNumberOfSamples(){
	var sampleQuery = getQuery(" ","IIS:sample");			
	var regiontype = currentState["exploreRegionSelected"];
	answerQuery(regiontype,sampleQuery,0,0,function(msg){
		var lines = msg.split("\n");						 		 						
		$.each(lines,function( index, value ){    							
			var valueList = value.split("\t");
			if (valueList[0] == "nh"){
				//add the row of the table
				currentState["totalNumberOfSamples"] = parseInt(valueList[1]);
				$('#totalSamples').text(numberWithCommas(currentState["totalNumberOfSamples"]));				
			}				
		});						
														
	});		
}
function addResultsRefinementAndUpdate(refinementTitle,refinementRaw,numberOfDocuments,update){
	if (numberOfDocuments == 0 || numberOfDocuments == "0"){
		alert("This refinement will lead to 0 remaining results!");
	}
	//if clicked
	//remove the query link
	//hide the query export buttons			 
	$('#queryOutputLink').html("");
	$('#queryOutputLink').hide();
	//remvoe the current plot
	$('#rangeFeaturePlot').remove();
	$('#convertPlotToImage').remove();									
	//add to the query listing
	addRefinementToTheQueryListing(refinementTitle,refinementRaw);
								
	if (update){
		//21.10.10 KH: The functionality used to be that the current open feature is again updated 
		// but maybe it is better to refresh the general feature
		//updateOpenFeature(true,true,numberOfDocuments == -1);
		//alert(1);
		closeOpenFeatureBox();
		//alert(2); 
		updateCurrentSelectionOverlapPlot();
		//alert(3);			
	}
			
	// update the total number of documents
	if (numberOfDocuments != -1){			
		currentState["totalNumberOfRegions"] = parseInt(numberOfDocuments.replace(",",""));;			
		$('#totalDocuments').text(numberWithCommas(currentState["totalNumberOfRegions"]));
		updateNumberOfSamples();
	}else{			
		updateResultsAndDocuments(false,true);
	}
	//alert("From within addResultsRefinementAndUpdate");
}	
// selects a region set
function activateMode_ExploreRegionChosen(reloadPlot){
	$('#totalDocuments').text(numberWithCommas(currentState["totalNumberOfRegions"]));
	updateNumberOfSamples();
	$(".queryResults").show();
	$(".features").show();
	$(".regionsSelection").hide();	
	$('.regionsSelected h2.boxheader').html("<b title=\"You can change it by clicking the buttons below\">Current selection</b>");
	addRegionSelectionToTheQueryListing(currentState["datasetInfo"][currentState["exploreRegionSelected"]]["officialName"],currentState["exploreRegionSelected"]);	
	$(".regionsSelected").show();
	$(".visualization").show();
	$("#exportRegionsDialog").hide();	
	$("#exportQueryDataDialog").hide();	
	$("#rangeFeaturePlotMain").show();
	$(".infobox").show();	
	$("#exportMenu").show();	
	if (reloadPlot){
		updateCurrentSelectionOverlapPlot();
	}		
}
