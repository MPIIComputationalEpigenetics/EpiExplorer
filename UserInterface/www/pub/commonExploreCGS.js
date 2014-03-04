
function getQuery(sep, queryPrefix, queryType) {
	var queryParts = [];
	var querySelector = "span.nonExistingClass";
	if (queryType == "main") {
		querySelector = 'span.queryPrefixRaw';
		queryParts = [ "Eregion" ]
	} else if (queryType == "ref") {
		querySelector = 'span.referencePrefixRaw'
		queryParts = [ "Eregion" ]
	} else {
		alert("Invalid query type " + queryType)
	}
	$(querySelector).each(function(index) {
		queryParts.push($(this).text())
	});
	return getQueryFromParts(sep, queryPrefix, queryParts)
}

// gets the current query. This loads all query elements form the page (class
// queryPrexix)
// orders them to ensure uniqueness (Not implemented yet)
// and return the query text
function getQueryFromParts(sep, queryPrefix, queryParts) {
	var negativeQueryText = "";
	var positiveQueryText = "";
	var queryText = "";
	var joinParts = [];
	$.each(queryParts, function(index, queryPartRawText) {
		if (queryPartRawText.charAt(0) == "-") {
			// negative query
			if (negativeQueryText.length > 0) {
				// there has been some terms already added
				negativeQueryText = negativeQueryText + sep + queryPartRawText;
			} else {
				// this is the first term to be added
				negativeQueryText = queryPartRawText;
			}
		} else if (queryPartRawText.charAt(0) == "[") {
			// this is a join part
			joinParts.push(queryPartRawText.replace(/ /g, sep));
		} else {
			// positive query
			if (positiveQueryText.length > 0) {
				// there has been some terms already added
				positiveQueryText = positiveQueryText + sep + queryPartRawText;
			} else {
				// this is the first term to be added
				positiveQueryText = queryPartRawText;
			}
		}
	});
	if (positiveQueryText.length > 0) {
		queryText = positiveQueryText;
		// add the query prefix if exists
		if (queryPrefix.length > 0) {
			queryText = queryText + sep + queryPrefix;
		}
		if (negativeQueryText.length > 0) {
			// if there is a negative query we put at at the end and we are sure
			// there is sth before that
			queryText = queryText + sep + negativeQueryText;
		}
	} else {
		// there is no positive query
		if (negativeQueryText.length > 0) {
			// if there is a negative query we have to make sure there is a
			// request before it
			if (queryPrefix.length > 0) {
				queryText = queryPrefix + sep + negativeQueryText;
			} else {
				// the query has no positive part so add ID:*
				queryText = "Eregion" + sep + negativeQueryText;
			}
		} else {
			queryText = queryPrefix;
		}
	}
	if (joinParts.length > 0) {
		if (queryText.length > 0) {
			queryText = joinParts.join(sep) + sep + queryText;
		} else {
			queryText = joinParts.join(sep)
		}
	}
	queryText = queryText.replace(/OVERLAP/g, settings["overlap"]).replace(
			/TISSUE/g, settings["tissue"]);
	return queryText;
}

function getQueryComplexJoin(sep, joinPrefix1, finalSuffix, joinField,
		joinPrefix2) {
	// query = getQueryComplexJoin("
	// ","Eregion",otherParameters[1],otherParameters[2],otherParameters[3])
	if (joinPrefix1.length > 0) {
		var joinFull1 = joinPrefix1 + sep + joinField;
	} else {
		var joinFull1 = joinField;
	}
	if (joinPrefix2.length > 0) {
		var joinFull2 = joinPrefix2 + sep + joinField;
	} else {
		var joinFull2 = joinField;
	}
	var baseQuery = getQuery(sep, joinFull1, "main");
	// alert("start query: "+baseQuery)
	var extraJoinParts = [];
	var startOfJoinPart = baseQuery.indexOf("[")
	// alert(startOfJoinPart)
	while (startOfJoinPart > -1) {
		var endOfJoinPart = baseQuery.indexOf("]")
		// alert(endOfJoinPart)
		extraJoinParts.push(baseQuery.substring(startOfJoinPart,
				endOfJoinPart + 1))
		// alert("Join part added:
		// "+baseQuery.substring(startOfJoinPart,endOfJoinPart+1))
		var newBaseQuery = "";
		if (startOfJoinPart > 0) {
			newBaseQuery = baseQuery.substring(0, startOfJoinPart - 1)
		}
		if (endOfJoinPart < baseQuery.length - 1) {
			newBaseQuery = newBaseQuery
					+ baseQuery.substring(endOfJoinPart + 2)
		}
		baseQuery = newBaseQuery;
		// alert("New base query: "+baseQuery)
		var startOfJoinPart = baseQuery.indexOf("[")
	}

	query = "[" + baseQuery + "%23" + joinFull2 + "]";
	if (finalSuffix != "") {
		query = query + sep + finalSuffix
	}
	if (extraJoinParts.length > 0) {
		query = extraJoinParts.join(sep) + sep + query
	}
	return query;

}

function selectCast() {
	// Hide other Bs
	$('td.castItem b').hide();
	$('td.castItem a').show();
	// switch the current one to visible more
	$(this).hide()
	$(this).siblings("b").show()
	// Chage the cast source
	$('#castFrame').attr("src", $(this).siblings("input:hidden")[0].value)
}
function removeUserDatasetFromLists(userDatasetID) {
	// alert(currentState["userDatasets"])
	// alert(userDatasetID);
	var indexOfUserDataset = jQuery.inArray(userDatasetID,
			currentState["userDatasets"]);
	// alert(indexOfUserDataset);
	if (indexOfUserDataset != -1) {
		// alert(currentState["userDatasets"]);
		currentState["userDatasets"].splice(indexOfUserDataset, 1);
		// alert(currentState["userDatasets"]);
		$.cookie("cgs:settings:userdatasets:" + settings["genome"],
				currentState["userDatasets"].join(";"), {
					expires : 30
				});
	}
}
function addUserDatasetRow(datasetID) {

	var regionRow = $('<tr class="regionsButton regionsButtonHover regionUser" title="See more information"></tr>');
	// the dataset name
	// regionRow.append($('<input type="hidden" value="'+datasetID+'"/>'));
	// the dataset icon
	// var removeButton = $('<td title="Remove this custom dataset"
	// class="ui-icon ui-icon-closethick ui-icon-turnred removeUserDataset"
	// style="float:left;padding:0;"></td>');
	var removeButton = $('<td title="Remove this custom dataset" class="removeUserDataset hoverChangeIcon"><img src="extras/edit-clear-locationbar-ltr.png" class="removeDatasetIcon" alt="Remove dataset"/><input type="hidden" value="'
			+ datasetID + '"/></td>');
	removeButton.click(function(event) {
		event.stopPropagation();
		var userDatasetRow = $(this).parent();
		var userDatasetID = $(this).children("input:hidden").val();

		removeUserDatasetFromLists(userDatasetID);
		userDatasetRow.remove();
	});

	regionRow.append(removeButton);

	// var add as compariosn dataset button
	regionRow
			.append($('<td title="Add this dataset as comparison" class="compareDatasetButton hoverChangeIcon"><img src="extras/split.png" class="compareDatasetIcon" alt="Compare to dataset"/><div class="selectDatasetText">Compare</div><input type="hidden" value="'
			+ datasetID + '"/></td>'));	
	// the datasrt offcial name
	// <div class="ui-icon ui-icon-person" style="float:left;padding:0;"></div>
	regionRow
			.append($('<td class="regionsetSelectButton" align="left" title="Explore this dataset">'
					+ currentState["datasetInfo"][datasetID]["officialName"]
					+ '<input type="hidden" value="' + datasetID + '"/></td>'));
	// the dataset number
	// regionRow.append($('<td align="right"> '+
	// numberWithCommas(currentState["datasetInfo"][datasetID]["numberOfRegions"])
	// +' </td><td class="regionsetSelectButton"
	// style="float:right;padding-left:0px;" title="Explore this region
	// set"><span class="ui-icon ui-icon-play ui-icon-turnred"
	// style="float:left;"></span>Select</td>'));//style="float:right;padding:0;"
	regionRow
			.append($('<td class="regionsetSelectButton" align="right" title="Explore this dataset"> '
					+ numberWithCommas(currentState["datasetInfo"][datasetID]["numberOfRegions"])
					+ ' <input type="hidden" value="' + datasetID + '"/></td>'));
	regionRow
			.append($('<td align="center" class="regionsetSelectButton hoverChangeIcon" title="Explore this dataset"><img src="extras/media-playback-start.png" class="selectDatasetIcon" alt="Select dataset"></img><div class="selectDatasetText">Select</div><input type="hidden" value="'
					+ datasetID + '"/></td>'));

	$("#regionsTable").prepend(regionRow);

}
function activateUserDatasetFunction(datasetID, updateSpan, asynchronous,
		addRow) {
	// alert("Activating '"+datasetID+"'")
	if (datasetID == "Paste here a dataset ID and press enter") {
		// alert("default id")
		if (updateSpan) {
			$(".activateUserDatasetSpan").show();
			$(".activateUserDatasetSpan").text(
					"You need to enter a dataset ID, first").fadeOut(2000,
					function() {

					});
		}
	} else if (datasetID == "") {
		if (updateSpan) {
			// alert("no id")
			$(".activateUserDatasetSpan").show();
			$(".activateUserDatasetSpan").text(
					"Please, insert a valid user dataset ID").fadeOut(4000,
					function() {
						$(".activateUserDatasetSpan").text("");
					});
		}
	} else {
		if (updateSpan == true) {
			$(".activateUserDatasetSpan").show();
			$(".activateUserDatasetSpan").text("Activating the dataset..");
		}
		$
				.ajax({
					type : "GET",
					url : "relay.php",
					async : asynchronous,
					dataType : "json",
					data : "type=activateUserDataset&datasetID=" + datasetID,
					success : function(result) {
						if (result[0] == 1) {
							// There was an error, while loading the dataset
							// alert("error+"+result[1])
							removeUserDatasetFromLists(datasetID)
							if (updateSpan == true) {
								$(".activateUserDatasetSpan").show();
								$(".activateUserDatasetSpan").text(result[1]);
							}
						} else {
							currentState["datasetInfo"][datasetID] = result[2];
							
							featureGroupDescription[datasetID] = result[2]["description"];
							featureGroupNames[datasetID] = result[2]["officialName"];
							featureGroupCategories[datasetID] = result[2]["categories"];
							overlapMarks[datasetID] = result[2]["overlappingText"];
							
							// Check if the dataset being activated has the same
							// active genome
							// otherwise chnage the active genome
							if (currentState["datasetInfo"][datasetID]["genome"] != settings["genome"]) {
								// alert("Genome to be changed to
								// "+currentState["datasetInfo"][datasetID]["genome"])
								settings["genome"] = currentState["datasetInfo"][datasetID]["genome"];
								// alert(currentState["userDatasets"])
								genomeChanged(false);
								// alert(currentState["userDatasets"])
								// alert("Genome changed to
								// "+settings["genome"])
							}
							currentState["datasetInfo"][datasetID] = result[2];
							// alert(1)

							// alert(datasetID+" -- "+updateSpan)
							if (updateSpan == true) {
								// alert("With update")
								// $(".activateUserDatasetSpan").show();
								$(".activateUserDatasetSpan")
										.text(result[1])
										.fadeOut(
												1000,
												function() {
													$(
															".activateUserDatasetSpan")
															.text("");
													// $(".activateUserDatasetSpan").hide();
													if (addRow) {
														addUserDatasetRow(datasetID);
													}
													// alert(2)
													showInfoRegionSet(
															datasetID, true);
													// alert(1)
													currentState["exploreRegionSelected"] = datasetID;
													updateCurrentSelectionOverlapPlot(false);
												});

							} else {
								if (addRow) {
									addUserDatasetRow(datasetID);
								}
							}
							// alert(1)
							if (jQuery.inArray(datasetID,
									currentState["userDatasets"]) == -1) {
								currentState["userDatasets"].push(datasetID);
								$.cookie("cgs:settings:userdatasets:"
										+ settings["genome"],
										currentState["userDatasets"].join(";"),
										{
											expires : 30
										});
							}

						}
					}
				});
	}
}

function updateResultsAndDocuments(uResults, uDocuments,async) {

	if (uResults || uDocuments) {
		var query = getQuery(" ", "Eregion", "main");
		nh = 0;
		if (uResults) {
			nh = 10;
		}
		var regiontype = currentState["exploreRegionSelected"];
		answerQuery(regiontype, query, 0, nh, async, "", function(result) {
			// update the results
			if (uResults) {
				updateResults(result);
			}
			// update the documents
			if (uDocuments) {
				updateNumberOfDocuments(result);
			}
		});
	}
}
function updateOpenFeature(uResults, uFeature, uDocuments) {
	showInfoPlot("nodescription")
	$('.infoboxRegions').hide();
	$('#openedFeatureResults tr').remove();
	$('#openedFeatureResults div.featureRangeOrRatioResults').remove();
	$('#openedFeatureResults').append(
			$('<div class="featureRangeOrRatioResults"></div>'));
	if (uFeature) {
		$('.featureBoxOpened')
				.each(
						function(index) {
							var hiddenInputs = $(this).children("input:hidden");
							// alert("classes changed "+hiddenInputs.length);
							var queryPrefix = hiddenInputs[0].value;
							if (currentState["featuresElements"][queryPrefix] !== undefined) {
								// alert("Changed the current visualization to
								// "+queryPrefix)
								updateCurrentVisualization(queryPrefix,true)
								$('#currentLinkLocation').text("")
								// $('.visualizationLinks').append('<a href="#"
								// class="visualizationDirectLink"
								// onclick="return
								// false;">'+queryPrefix+'</a><br/>')
							}
							// alert(queryPrefix);
							var boxtypePrefix = hiddenInputs[1].value;
							// other params
							var otherParameters = [ queryPrefix ];
							if (boxtypePrefix == 'featureRange'
									|| boxtypePrefix == 'featureRatio'
									|| boxtypePrefix == 'featureNeighborhood') {
								// The number of digits
								otherParameters.push(hiddenInputs[2].value);
								// The base
								otherParameters.push(hiddenInputs[3].value);
							} else if (boxtypePrefix == 'featureTable') {
								// The outside query part
								otherParameters.push(hiddenInputs[2].value);
								// The join field
								otherParameters.push(hiddenInputs[3].value);
								// The join query
								otherParameters.push(hiddenInputs[4].value);
								// Update the autocompletion field
								otherParameters.push(true);
							} else if (boxtypePrefix == 'featureTable') {
								otherParameters = [ "Eregion" ];
							}

							// alert(boxtypePrefix);
							var regiontype = currentState["exploreRegionSelected"];
							// alert(regiontype);
							var query;
							if (boxtypePrefix != 'featureTable') {
								if (queryPrefix.charAt(0) == "-") {
									query = getQuery(" ", queryPrefix.substr(1)
											+ "*", "main");
								} else {
									query = getQuery(" ", queryPrefix + "*",
											"main");
								}
							} else {
								// alert("Form query for featureTable")
								query = getQueryComplexJoin(" ", "Eregion",
										otherParameters[1], otherParameters[2],
										otherParameters[3])
								// alert("Final query: "+query)
								// alert(query)
							}

							// alert(query);
							var nc = 0;
							var nr = 0;
							var extraSettings = "";
							if (uFeature) {
								if (boxtypePrefix == 'featureText') {
									nc = 40;
									extraSettings = "rw=3a"
								} else if (boxtypePrefix == 'featureRange') {
									nc = 1000;
								} else if (boxtypePrefix == 'featureRatio') {
									nc = 1000;
								} else if (boxtypePrefix == 'featureNeighborhood') {
									nc = 1500;
								} else if (boxtypePrefix == 'featureTable') {
									if (otherParameters[0]
											.startsWith("GENENAME")) {
										nr = 200;
									} else if (otherParameters[0]
											.startsWith("GO:ALL")) {
										// nc = 300;
										nc = 100;
										extraSettings = "rw=1d"
										// the completions to be sorted by score
										// and the scores to be summed up
										// extraSettings = "rw=0d%26s=MMMS"
									} else if (otherParameters[0]
											.startsWith("GO:TERMS")) {
										nc = 200;
									} else if (otherParameters[0]
											.startsWith("OMIM:ALL")) {
										// nc = 300;
										nc = 100;
										extraSettings = "rw=1d"
										// //the completions to be sorted by
										// score and the scores to be summed up
										// extraSettings = "rw=0d%26s=MMMS"
									} else if (otherParameters[0]
											.startsWith("OMIM:TERMS")) {
										nc = 200;
									}

									// extraSettings = "rw=0a%26rd=0a"
								} else if (boxtypePrefix == 'featureRegionsList') {
									nc = 300;
									nr = 200;
								}
							}

							// Retrieve and update the opened feature results
							updateOpenedFeatureCore(boxtypePrefix, regiontype,
									query, nc, nr, extraSettings,
									otherParameters);

						});
	}
	// $('#openedFeatureResults').unbind('click');
	updateResultsAndDocuments(uResults, uDocuments, true);
}
function updateOpenedFeatureCore(boxtypePrefix, regiontype, query, nc, nr,
		extraSettings, otherParameters) {
	answerQuery(regiontype, query, nc, nr, true, extraSettings,
			function(result) {
				// update the table
				// check if there is reference
				// CONVERT_BASEQUERY_TO_JSON
				if (boxtypePrefix == 'featureText') {
					updateOpenedFeatureTable(result, otherParameters);
				} else if (boxtypePrefix == 'featureRange') {
					updateOpenedFeatureRange(result, otherParameters);
				} else if (boxtypePrefix == 'featureRatio') {
					updateOpenedFeatureRatio(result, otherParameters);
				} else if (boxtypePrefix == 'featureNeighborhood') {
					updateOpenedFeatureNeighborhood(result, otherParameters);
				} else if (boxtypePrefix == 'featureRegionsList') {
					updateOpenedFeatureRegionsList(result, otherParameters);
				} else if (boxtypePrefix == 'featureTable') {
					updateOpenedFeatureJTable(result, otherParameters);
				}
				// remove the progress image
				$('.progress_image_feature').remove();
				$('.progress_image_feature_plot').remove();
				setCurrentStatus(null, false);
			});
}
// updates the results section from the result of a query
function updateResults(result) {
	var total = 0;
	$('.progress_image_hits').remove();
	// $('#resultsHitsListing > p').html("");
	var count = 0;
	$.each(result[4], function(index, value) {
		count = count + 1;
		var titleParts = index.split("_");
		var url = "http://genome.ucsc.edu/cgi-bin/hgTracks?db="
				+ settings["genome"] + "&position="
				+ titleParts[titleParts.length - 3] + "%3A"
				+ titleParts[titleParts.length - 2] + "-"
				+ titleParts[titleParts.length - 1];
		$('#resultsHitsListing > p').append(
				$('<a href="' + url + '" target=\"_blank\">'
						+ titleParts[titleParts.length - 3] + ' '
						+ titleParts[titleParts.length - 2] + ' '
						+ titleParts[titleParts.length - 1] + '</a><br>'));
	});

	if (count < 10) {
		$('#resultsHitsListing > p').prepend(
				$('<h4>All ' + count + ' results</h4>'));
	} else {
		$('#resultsHitsListing > p').prepend($('<h4>First 10 results</h4>'));
		var showAllButton = $('<div class="exportRegionsButton">Export all</div>');
		showAllButton.button();
		$('#resultsHitsListing > p').append(showAllButton);
	}

}
function updateCurrentSelectionOverlapPlotOnlyPlotGoogle() {
	var l;
	var visualizationData = {
		'cols' : [ {
			'label' : 'Annotation',
			'type' : 'string'
		} ],
		'rows' : []
	};
	var widthChart = 800;
	var heightChart = 350;
	var fontSizeChart = 10;
	var slantedTextAngleChart = 10;
	var slantedTextChart = false;
	if (currentState["overlapSelection"].length > 12) {
		fontSizeChart = 9;
		widthChart = currentState["overlapSelection"].length * 82;
		// slantedTextChart = true;
	}
	var plotTitle;
	if (isInSummary()) {
		plotTitle = 'Summary of '
				+ numberWithCommas(currentState["totalNumberOfRegions"])
				+ " "
				+ currentState["datasetInfo"][currentState["exploreRegionSelected"]]['officialName'];
	} else {
		plotTitle = getTextForFeatureGroup(currentState["featureCurrentVisualization"])
				+ " summary of "
				+ numberWithCommas(currentState["totalNumberOfRegions"])
				+ " "
				+ currentState["datasetInfo"][currentState["exploreRegionSelected"]]['officialName'];
	}

	var options = {
		width : widthChart,
		height : heightChart,
		focusTarget : 'category',
		title : plotTitle,
		//bar:{groupWidth:"80%"},
		titleTextStyle:textStyles["mainTitle"],
		
		legend : {position:'top',
				  textStyle:textStyles["legend"]
				  },
		
		hAxis : {
			maxAlternation : 1,
			textStyle : textStyles["axisText"],
			titleTextStyle:textStyles["axisTitle"],
			slantedText : slantedTextChart,
			slantedTextAngle : slantedTextAngleChart,
			showTextEvery : 1
		},
		vAxis : {
			title : "Percent of overlapping regions",
			titleTextStyle : textStyles["axisTitle"],
			format : '#,###%',
			minValue : 0,
			maxValue : 1
		},
		chartArea : {
			left : 60,
			// top:26,
			width : (widthChart - 60)
		},
		forceIFrame: true
	}
	if (currentState["referenceQuery"]["genome"] != "") {
		// alert("1.1")
		visualizationData['cols'].push({
			'label' : 'Current selection ('
					+ numberWithCommas(currentState["totalNumberOfRegions"])
					+ ')',
			'type' : 'number'
		})
		visualizationData['cols']
				.push({
					'label' : 'Control set ('
							+ numberWithCommas(currentState["referenceQuery"]["totalNumber"])
							+ ')',
					'type' : 'number'
				})
		// visualizationData['rows'] = [
		// {c:[{v: 'Test1 ref'}, {v: 1.0, f: 'One'}, {v: 7.0, f: 'three'}]},
		// {c:[{v: 'Test2 ref'}, {v: 2.0, f: 'Two'}, {v: 10.0, f: 'five'}]}]

		options['colors'] = [ '#FA9627', '#999999' ]
	} else {
		// alert("1.2")
		visualizationData['cols'].push({
			'label' : 'Current selection',
			'type' : 'number'
		})
		// visualizationData['rows'] = [
		// {c:[{v: 'Test1cs'}, {v: 1.0, f: 'One'}]},
		// {c:[{v: 'Test2cs'}, {v: 2.0, f: 'Two'}]}]
		options['legend'] = 'none'
		options['colors'] = [ '#FA9627' ]
	}
	var overlapKeyIndeces = [];
	$
			.each(
					currentState["overlapSelection"],
					function(index, key) {
						overlapKeyIndeces.push(key);
						var updatedKey = key.replace(/OVERLAP/g,
								settings["overlap"]).replace(/TISSUE/g,
								settings["tissue"]);
						// alert(updatedKey)
						label = getOverlapLabels(updatedKey);

						if (currentState["currentOverlaps"][updatedKey] !== undefined) {
							row = []
							row.push({
								'v' : label
							});
							var ratio = currentState["currentOverlaps"][updatedKey]
									/ currentState["totalNumberOfRegions"];
							row
									.push({
										'v' : ratio,
										'f' : numberWithCommas(currentState["currentOverlaps"][updatedKey])
												+ " ("
												+ Math.round(ratio * 1000)
												/ 10
												+ "%)"
									});
							// plotRatios.push(currentState["currentOverlaps"][updatedKey]/currentState["totalNumberOfRegions"]);
							// plotValues.push(currentState["currentOverlaps"][updatedKey]);
							if (currentState["referenceQuery"]["genome"] != "") {
								if (currentState["referenceQuery"]["values"][updatedKey] !== undefined) {
									var ratio = currentState["referenceQuery"]["values"][updatedKey]
											/ currentState["referenceQuery"]["totalNumber"];
									row
											.push({
												'v' : ratio,
												'f' : numberWithCommas(currentState["referenceQuery"]["values"][updatedKey])
														+ " ("
														+ Math
																.round(ratio * 1000)
														/ 10 + "%)"
											});
									// refValues.push(currentState["referenceQuery"]["values"][updatedKey]);
									// refRatios.push(currentState["referenceQuery"]["values"][updatedKey]/currentState["referenceQuery"]["totalNumber"]);
								} else {
									row.push({
										'v' : 0,
										'f' : "0"
									});
									// refValues.push(0);
									// refRatios.push(0);
								}
							}
							visualizationData['rows'].push({
								'c' : row
							})

						} else {
							// alert("Bad label "+updatedKey+" from "+key);
						}
					});

	var dt = new google.visualization.DataTable(visualizationData, 0.6);

	// var chart = new
	// google.visualization.ColumnChart(document.getElementById('rangeFeaturePlot'));
	var chart = new google.visualization.ChartWrapper({
		'chartType' : 'ColumnChart',
		'containerId' : 'rangeFeaturePlot',
		'dataTable' : dt,
		'options' : options
	});
	currentState["activeChart"].push(chart);

	// chart.draw(dt, options);
	chart.draw();
	function chartSelectHandler() {
		if (currentState["isRegionSelected"] == false) {
			// alert("region selection mode")
			return;
		}
		var selection = chart.getChart().getSelection();
		for ( var i = 0; i < selection.length; i++) {
			if (selection[i].row != null) {
				var currentVisualization = currentState["featureCurrentVisualization"];
				var currentItem = overlapKeyIndeces[selection[i].row];
				// alert(currentState["featureCurrentVisualization"])
				// alert(selection[i].row)
				// alert(overlapKeyIndeces[selection[i].row])//The overlap id of
				// the
				// alert(visualizationData['rows'][selection[i].row]["c"][0]["v"])//
				// The overlap name
				var newVisualizationItem = getForwardVisualizationID(
						currentVisualization, currentItem);
				// alert(newVisualizationItem)
				loadVisualizationByID(newVisualizationItem)
			}
		}
	}
	;
	google.visualization.events
			.addListener(chart, 'select', chartSelectHandler);
	var difShow = $('<tr class="showTableLink"><td colspan="2"><a href="#" onclick="return false">Show as table</a></td></tr>');
	difShow.click(function() {
		if (chart.getChartType() == "Table") {
			chart.setChartType('ColumnChart')
			chart.setOption("height", heightChart)
			$(".showTableLink a").text("Show as table");
			$('tr.toPNGRow').show()
		} else {
			chart.setChartType("Table")
			chart.setOption("height", null)
			$(".showTableLink a").text("Show as chart");
			$('tr.toPNGRow').hide()
		}
		chart.draw()
	});

	$('.showTableLink').remove();
	$('#rangeFeaturePlotTable').append(difShow);
	// Image convertion
	$('tr.toPNGRow').remove();
	var toImageButton = $('<tr class="toPNGRow"><td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
			+ options["width"]
			+ '"/> <input type="hidden" value="'
			+ options["height"]
			+ '"/><input type="hidden" value="'
			+ chart.getContainerId() + '"/></td></tr>')
	$('#rangeFeaturePlotTable').append(toImageButton)
	// Adding intervals
	if (settings['showConfidence']) {
		$('tr.showConfidenceIntervals').remove();
		if (currentState["datasetInfo"][currentState["exploreRegionSelected"]]["hasBinning"]) {
			var showConfidenceButton = $('<tr class="showConfidenceIntervals"><td class="toConfidenceIntervals"><a href="#" onclick="return false">Show confidence</a></td></tr>')
			$('#rangeFeaturePlotTable').append(showConfidenceButton)
		}
	}
}

function isInState(stateName) {
	return currentState["featureCurrentVisualization"].indexOf(stateName) != -1;
}

function isInSummary() {
	return (currentState["featureCurrentVisualization"] == ""
		   || currentState["featureCurrentVisualization"] == settings["genome"] + "summary");
}

function isActualChart(chartType) {
	return currentState["currentDefaultChart"] == chartType;
}

function updateCurrentSelectionOverlapPlot(forceUpdate) {
	var fcv = currentState["featureCurrentVisualization"];
	closeOpenFeatureBox();	
	updateCurrentVisualization(fcv,true)

	// $('#rangeFeaturePlot').remove();
	// $('#convertPlotToImage').remove();
	
	if (!isInState("methylation")) {
		showInfoPlot("summary_"+currentState["currentDefaultChart"]);
	} else {
		showInfoPlot("summary_bars");
	}
	
	if ( isInSummary() ) {
		$('.infoboxRegions').show();
	} else {
		$('.infoboxRegions').hide();
	}

	$('#rangeFeaturePlotMain').children().remove()
	$('#rangeFeaturePlotMain').show();
	$('#rangeFeaturePlotMain').append( $('<table id="rangeFeaturePlotTable"></table>') );
		
	$('#rangeFeaturePlotTable').append('<tr><td width="70%"></td><td width="30%"><table><tr><td class="selection"></td></tr></table></td></tr>');

	
	if (!isActualChart("bars") && !isInState("methylation")) {
		$('td.selection').append('<td class="toOverlapeBars"><a href="#" onclick="return false"><img src="extras/icon_bars.png" alt="Display data as Overlap Bars" height="50" width="80"/></a></td>');
	} else {
		$('td.selection').append('<td class="toOverlapeBars_dark"><img src="extras/icon_bars_dark.png" alt="Display data as Overlap Bars (Inactive)" height="50" width="80"/></td>');
	}	
	
	if (!isActualChart("bubbles") && !isInState("methylation")) {
		$('td.selection').append('<td class="toCoverageBubbles"><a href="#" onclick="return false"><img src="extras/icon_bubble.png" alt="Display data as Bubble Chart" height="50" width="80" /></a></td>');
	} else {
		$('td.selection').append('<td class="toCoverageBubbles_dark"><img src="extras/icon_bubble_dark.png" alt="Display data as Bubble Chart (Inactive)" height="50" width="80" /></td>');
	}
	
	
	
//	$('tr.selection').append('<td class="toTable"><a href="#" onclick="return false">As Table</a></td>');
	
	$('#rangeFeaturePlotTable').append('<tr><td colspan="2"><div id="rangeFeaturePlot"></div></td></tr>');
	
	// $('#rangeFeaturePlotMain').append($('<div class="jqPlot"
	// id="rangeFeaturePlot"></div><div id="convertPlotToImage">to PNG</div>'));
	// $('#overlapSelect').remove();
	if (currentState["overlapSelection"].join("_").search("OVERLAP") > -1) {
		$('#rangeFeaturePlotTable')
				.append(
						'<tr><td>Select overlap criterion:</td><td><select id="overlapSelect"><option value="Eoverlaps">Any overlap (at least 1bp)</option><option value="Eoverlaps10p">Medium overlap (at least 10%)</option><option value="Eoverlaps50p">Strong overlap (at least 50%)</option></select></td></tr>')
		$('#overlapSelect').val(settings["overlap"]);
		// $('select#overlapSelect').selectmenu();
	}
	// $('#tissueSelect').remove();
	if (currentState["overlapSelection"].join("_").search("TISSUE") > -1 && (!isActualChart("bubbles") || !isDataset(currentState["featureCurrentVisualization"]))) {
		$('#rangeFeaturePlotTable')
				.append(
						'<tr><td>Select tissue:</td><td><select id="tissueSelect"></select></td></tr>');
		$.each(settings["defaultTissues"], function(index, tissueKey) {
			$('#tissueSelect').append(
					$('<option value="' + tissueKey + '">'
							+ getTissueDescription(tissueKey) + '</option>'))
		});
		$('#tissueSelect').val(settings["tissue"]);
		// $('select#tissueSelect').selectmenu();
	}
		
	// alert("NO?")
	// $('#convertPlotToImage').button().hide();
	// currentOverlaps are nullified whenever the query is updated
	if (forceUpdate
			|| currentState["currentOverlaps"] == settings["defaultCurrentOverlaps"]) {
		// refresh the total number of cases
		var regiontype = currentState["exploreRegionSelected"];
		var totalquery = getQuery(" ", "Eregion", "main");
		// this relies on the fact that CS is started as single threaded and
		// hence the totla number query
		// will finish before the overlap query
		answerQuery(regiontype, totalquery, 0, 0, true, "",
				updateNumberOfDocuments);

		var query = getQuery(" ", settings["overlap"] + ":*", "main");
		setCurrentStatus("Loading visualization data...", true)
		// $("#currentStatus").append($('<img name="progress_image_feature_plot"
		// src="extras/ajax-loader-big.gif" class="progress_image_feature_plot"
		// align="center" alt="Processing..."></img>'));
		// $(".visualization").append($('<img name="progress_image_feature_plot"
		// src="extras/ajax-loader-big.gif" class="progress_image_feature_plot"
		// align="center" alt="Processing..."></img>'));
		answerQuery(
				regiontype,
				query,
				settings['maxOverlapCompletions'],
				0,
				true,
				"",
				function(result) {
					// alert("reading query started");
					currentState["currentOverlaps"] = {};
					// currentState["currentOverlaps"] =
					// settings["defaultCurrentOverlaps"];
					currentState["currentOverlapsStat"] = settings["defaultCurrentOverlapStats"];
					// CONVERT_BASEQUERY_TO_JSON var lines = msg.split("\n");
					totalNumber = parseInt(result[2], 10);
					// alert("total number read "+totalNumber);
					$.each(result[3], function(index, value) {
						value = parseInt(value, 10);
						currentState["currentOverlaps"][index] = value;
						// alert("read completion "+index +" - "+value);
					});
					/*
					 * CONVERT_BASEQUERY_TO_JSON $.each(lines,function( index,
					 * value ){ var valueList = value.split("\t"); var
					 * totalNumber = 1; if (valueList[0] == "nh"){ totalNumber =
					 * parseInt(valueList[1], 10); }else if (valueList[0] ==
					 * "completion"){ //add another possible completion var nwc =
					 * parseInt(valueList[2], 10);
					 * currentState["currentOverlaps"][valueList[1]] = nwc; }
					 * });
					 *  // CONVERT_BASEQUERY_TO_JSON
					 */
					// If there is reference update the reference data also
					if (currentState["referenceQuery"]["genome"] != "") {
						// alert("Reference query values to be retrieved");
						/* REFERENCE UPDATE */
						referenceQuery = currentState["referenceQuery"]["query"]
								.replace(/BASEREFQUERY/g, settings["overlap"]
										+ ":*")
						// alert(referenceQuery);
						/* REFERENCE UPDATE */
						answerQuery(
								currentState["referenceQuery"]["dataset"],
								referenceQuery,
								settings['maxOverlapCompletions'],
								0,
								true,
								"",
								function(result) {
									// alert("reading query started");
									// currentState["referenceQuery"]["values"]
									// = {};
									/* REFERENCE UPDATE */
									// currentState["referenceQuery"]["totalNumber"]
									// = parseInt(result[2], 10);
									// alert("total number read
									// "+currentState["referenceQuery"]["totalNumber"]);
									$
											.each(
													result[3],
													function(index, value) {
														value = parseInt(value,
																10);
														currentState["referenceQuery"]["values"][index] = value;
														// alert("read
														// completion "+index +"
														// - "+value);
													});
									// CONVERT_BASEQUERY_TO_JSON*/
									updateCurrentSelectionPlot();
									$('.progress_image_feature_plot').remove();
									setCurrentStatus(null, false);
									// alert("Query complete");
								});
					} else {
						// No reference proceed directly
						// alert("Values (no ref) retrieved");
						updateCurrentSelectionPlot();
						$('.progress_image_feature_plot').remove();
						setCurrentStatus(null, false);
					}
					// alert("Query complete");
				});
	} else {
		//		
		// the overlaps were already updated so just refresh the plot
		// alert("Query cashe side "+currentState["currentOverlaps"]);
		updateCurrentSelectionPlot();
	}
	// alert("YES!")
}

function updateCurrentSelectionPlot() {
	if (currentState["currentDefaultChart"] == "bubbles" && isInState("methylation")) {
		updateCurrentSelectionOverlapPlotOnlyPlotGoogle();		
	} else if (currentState["currentDefaultChart"] == "bars") {
		updateCurrentSelectionOverlapPlotOnlyPlotGoogle();
	} else if (currentState["currentDefaultChart"] == "bubbles") {
		updateBubbleChart();		
	} 		
}

function updateOpenedFeatureNeighborhood(result, otherParameters) {
	// alert("retriving neighborhood values");
	var neighborhoodValues = {};
	var histones = {};
	var tissues = {};
	// Enbh:bhist:H4K20me1:any:ae500

	/*
	 * // For the purpose of the new visualizations the data is restructured to //
	 * from mark, tissue,position to position,tissue,mark
	 * $.each(result[3],function( completion, numberOfCases){ var
	 * completionParts = completion.split(":"); if
	 * (neighborhoodValues[completionParts[2]] == undefined){
	 * neighborhoodValues[completionParts[2]] = {}; histoneCount = histoneCount +
	 * 1; } if (neighborhoodValues[completionParts[2]][completionParts[3]] ==
	 * undefined){ neighborhoodValues[completionParts[2]][completionParts[3]] =
	 * {}; }
	 * neighborhoodValues[completionParts[2]][completionParts[3]][completionParts[4]] =
	 * numberOfCases;
	 * 
	 * });
	 */
	$
			.each(
					result[3],
					function(completion, numberOfCases) {
						var completionParts = completion.split(":");
						if (neighborhoodValues[completionParts[4]] == undefined) {
							neighborhoodValues[completionParts[4]] = {};
							// histoneCount = histoneCount + 1;
						}
						if (neighborhoodValues[completionParts[4]][completionParts[3]] == undefined) {
							neighborhoodValues[completionParts[4]][completionParts[3]] = {};
						}
						neighborhoodValues[completionParts[4]][completionParts[3]][completionParts[2]] = [
								numberOfCases, 0 ];
						histones[completionParts[2]] = true;
						tissues[completionParts[3]] = true;

					});
	if (currentState["referenceQuery"]["genome"] != "") {
		// alert("Reference query values to be retrieved");
		/* REFERENCE UPDATE */
		referenceQuery = currentState["referenceQuery"]["query"].replace(
				/BASEREFQUERY/g, otherParameters[0] + "*")
		// alert(referenceQuery);
		/* REFERENCE UPDATE */
		var error = false;
		answerQuery(
				currentState["referenceQuery"]["dataset"],
				referenceQuery,
				1500,
				0,
				false,
				"",
				function(resultRef) {
					// alert("reading query started");
					/* REFERENCE UPDATE */

					$
							.each(
									resultRef[3],
									function(completion, numberOfCases) {
										var completionParts = completion
												.split(":");
										if (neighborhoodValues[completionParts[4]] == undefined) {
											neighborhoodValues[completionParts[4]] = {};
											// histoneCount = histoneCount + 1;
										}
										if (neighborhoodValues[completionParts[4]][completionParts[3]] == undefined) {
											neighborhoodValues[completionParts[4]][completionParts[3]] = {};
										}
										if (neighborhoodValues[completionParts[4]][completionParts[3]][completionParts[2]] !== undefined) {
											neighborhoodValues[completionParts[4]][completionParts[3]][completionParts[2]] = [
													neighborhoodValues[completionParts[4]][completionParts[3]][completionParts[2]][0],
													numberOfCases ];
										} else {
											// if (error == false){
											// error = true;
											// alert(completionParts)
											// }
											neighborhoodValues[completionParts[4]][completionParts[3]][completionParts[2]] = [
													0, numberOfCases ];
										}
										histones[completionParts[2]] = true;
										tissues[completionParts[3]] = true;
									});
					// alert("reading query over");

				});
	}
	// initialize the histone marks
	var histoneMarks = [];
	$.each(histones, function(histoneMark, value) {
		histoneMarks.push(histoneMark);
	});
	// initialize the tissues for which we have data
	var tissueMarks = [];
	$.each(tissues, function(tissue, value) {
		tissueMarks.push(tissue);
	});
	tissueMarks.sort()
	// alert("2. retriving neighborhood values");
	var plotTitle = "";
	// var plotData = [];
	var plotDataGoogle = [];
	// var plotLabels = [];
	var plotLabelsGoogle = [];
	var plotXLabels = [];
	var positions = {};
	var posIndex = 0;
	var beforeStart = []
	$.each(otherParameters[1].split(":"), function(index, value) {
		beforeStart.push("0".repeat(6 - value.length) + value)
	});
	beforeStart.sort()
	beforeStart.reverse()

	$.each(beforeStart, function(index, value) {
		var number = parseInt(value, 10);
		plotXLabels.push("start - " + parseInt(number, 10));
		positions["bs" + number] = posIndex;
		posIndex = posIndex + 1;
	});
	var afterEnd = otherParameters[2].split(":");
	var afterEnd = []
	$.each(otherParameters[2].split(":"), function(index, value) {
		afterEnd.push("0".repeat(6 - value.length) + value)
	});
	afterEnd.sort()

	$.each(afterEnd, function(index, value) {
		var number = parseInt(value, 10);
		plotXLabels.push("end + " + number);
		positions["ae" + number] = posIndex;
		posIndex = posIndex + 1;
	});

	var numberFound = 0;
	// make the plot with normal axes
	if (histoneMarks.length > 1) {
		// alert("2.1 retriving neighborhood values");
		// multiple histone mod, show for the chose tissue
		/*
		 * the code below is working for showing multiple histone marks for a
		 * single tissue However it was switched off, due to performance issues
		 * 
		 * plotTitle = "Neighborhood histone modification overlap of
		 * "+currentState["datasetInfo"][currentState["exploreRegionSelected"]]['officialName'];
		 * $.each(neighborhoodValues,function( histoneMark, histoneMarkData){ if
		 * (histoneMarkData[settings["tissue"]] !== undefined){ numberFound =
		 * numberFound + 1; //alert("2.1.1 Start Adding "+histoneMark);
		 * plotLabels.push({label:histoneMark});
		 * plotLabelsGoogle.push(histoneMark); var plotDataLabel = [];
		 * $.each(plotXLabels,function(){plotDataLabel.push(0)});
		 * 
		 * $.each(histoneMarkData[settings["tissue"]],function(position,numberOfCases){
		 * plotDataLabel[positions[position]] = parseInt(numberOfCases); });
		 * //alert(histoneMark+" - "+plotDataLabel);
		 * plotData.push(plotDataLabel); //alert("2.1.1 Done Adding
		 * "+histoneMark); } });
		 */
	} else {

		// alert("2.2 retriving neighborhood values");
		var histoneMark = histoneMarks[0];
		plotTitle = histoneMark
				+ " neighborhood for "
				+ currentState["datasetInfo"][currentState["exploreRegionSelected"]]['officialName'];
		// alert(plotTitle);
		// alert(plotXLabels)
		// alert(tissueMarks);
		$.each(plotXLabels, function(positionIndex, positionValue) {
			// alert(positionValue)
			var positionArray = [ {
				'v' : positionValue
			} ];
			$.each(tissueMarks, function(tissueindex, tissueName) {
				positionArray.push({
					'v' : 0,
					'f' : "0 cases"
				});
			});
			if (currentState["referenceQuery"]["genome"] != "") {
				// adding another column for the reference values
				$.each(tissueMarks, function(tissueindex, tissueName) {
					positionArray.push({
						'v' : 0,
						'f' : "0 cases"
					});
				});
			}
			// alert(positionArray)
			plotDataGoogle.push({
				'c' : positionArray
			});
			// alert("pushed")
		});
		plotLabelsGoogle = tissueMarks;
		// alert("Initialized the google plot data")
		// single histone mod, show for all tissues
		$
				.each(
						neighborhoodValues,
						function(position, positionData) {
							// alert(position)
							$
									.each(
											tissueMarks,
											function(tissueIndex, tissueName) {
												// alert(tissueName)
												if (positionData[tissueName] !== undefined) {
													if (positionData[tissueName][histoneMark] !== undefined) {
														var numberOfCases = parseInt(
																positionData[tissueName][histoneMark][0],
																10);
														plotDataGoogle[positions[position]]['c'][tissueIndex + 1] = {
															'v' : numberOfCases
																	/ currentState["totalNumberOfRegions"],
															'f' : numberOfCases
																	+ " cases"
														};
													} else {
														alert("No histone mark "
																+ histoneMark
																+ " data for tissue "
																+ tissueName);
													}
												} else {
													// alert("No data for tissue
													// "+tissueName)
												}
												// alert("2.2.1 Done Adding
												// "+tissue);
											});
							if (currentState["referenceQuery"]["genome"] != "") {
								$
										.each(
												tissueMarks,
												function(tissueIndex,
														tissueName) {
													// alert(tissueName)
													if (positionData[tissueName] !== undefined) {
														if (positionData[tissueName][histoneMark] !== undefined) {
															var numberOfCases = parseInt(
																	positionData[tissueName][histoneMark][1],
																	10);
															plotDataGoogle[positions[position]]['c'][tissueMarks.length
																	+ tissueIndex
																	+ 1] = {
																'v' : numberOfCases
																		/ currentState["referenceQuery"]["totalNumber"],
																'f' : numberOfCases
																		+ " cases"
															};
														} else {
															alert("No histone mark "
																	+ histoneMark
																	+ " data for tissue "
																	+ tissueName);
														}
													} else {
														// alert("No data for
														// tissue "+tissueName)
													}
													// alert("2.2.1 Done Adding
													// "+tissue);
												});
								// alert("Success")
							}
						});
	}
	// alert("Data initialized")
	// if (numberFound == 0){
	// $('#rangeFeaturePlot').html("<p style=\"color: #FA9627;\"> No
	// neighborhood data for the tissue "+settings["tissue"]+". Please try a
	// different one.</p>");
	// $('.progress_image_feature').remove();
	// $('.progress_image_feature_plot').remove();
	// return;
	// }
	// standard jqplot version
	// updateOpenedFeatureNeighborhoodPlot(plotTitle,plotData,plotLabels,plotXLabels);
	// updated google visualizations version
	if (currentState["referenceQuery"]["genome"] == "") {
		updateOpenedFeatureNeighborhoodGooglePlotSingle(plotTitle,
				plotDataGoogle, tissueMarks);
	} else {
		updateOpenedFeatureNeighborhoodGooglePlotReference(plotTitle,
				plotDataGoogle, tissueMarks);
	}

}
function updateOpenedFeatureNeighborhoodGooglePlotReference(plotTitle,
		plotData, plotLabels) {

	$('#rangeFeaturePlotMain').children().remove()
	// $('#rangeFeaturePlot').remove();
	$('#rangeFeaturePlotMain').show();
	showInfoPlot("neighborhoodref")
	// alert("with reference")
	$('#rangeFeaturePlotMain')
			.append(
					$('<table id="rangeFeaturePlotTable"><tr><td><div id="neighborhoodReferencetissueSelectionTable"></div></td><td><div id="rangeFeaturePlot"></div></td></tr></table>'))

	var tableVisualizationCols = [];
	$.each(plotLabels, function(index, tissue) {
		tableVisualizationCols.push({
			'c' : [ {
				'v' : tissue
			} ]
		})
	})
	var tableVisualizationData = {
		'cols' : [ {
			'label' : 'Select tissue',
			'type' : 'string'
		} ],
		'rows' : tableVisualizationCols
	}
	var tableReferenceData = new google.visualization.DataTable(
			tableVisualizationData, 0.6);

	var heightChart = 400;
	var tissueTableVisualization = new google.visualization.ChartWrapper({
		'chartType' : 'Table',
		'containerId' : 'neighborhoodReferencetissueSelectionTable',
		'dataTable' : tableReferenceData,
		'options' : {
			width : 100,
			height : heightChart
		}
	});
	currentState["activeChart"].push(tissueTableVisualization);
	// var tissueTableVisualization = new
	// google.visualization.Table(document.getElementById('neighborhoodReferencetissueSelectionTable'));

	// tissueTableVisualization.draw(tableReferenceData,{width: 100,height:
	// 400});
	tissueTableVisualization.draw()
	var chart;

	function changeReferenceTissue(tissueIndex) {
		// An alternative implementation is with DataView.
		// to be done if this becomes too slow
		var dataCols = [
				{
					type : 'string',
					label : "Position relative to the "
							+ currentState["datasetInfo"][currentState["exploreRegionSelected"]]['officialName']
				},
				{
					type : 'number',
					label : plotLabels[tissueIndex]
							+ ' (Current selection '
							+ numberWithCommas(currentState["totalNumberOfRegions"])
							+ ')'
				},
				{
					type : 'number',
					label : plotLabels[tissueIndex]
							+ ' (Control set '
							+ numberWithCommas(currentState["referenceQuery"]["totalNumber"])
							+ ')'
				} ];

		var dataRows = [];
		$.each(plotData, function(index, value) {
			dataRows.push({
				'c' : [ value['c'][0], value['c'][tissueIndex + 1],
						value['c'][plotLabels.length + tissueIndex + 1] ]
			})
		})
		var visualizationData = {
			'cols' : dataCols,
			'rows' : dataRows
		}
		var data = new google.visualization.DataTable(visualizationData, 0.6);

		var widthChart = 750;
		var options = {
			title : plotTitle,
			titleTextStyle:textStyles["mainTitle"],
			width : widthChart,
			legend : {position:'top',
					 textStyle: textStyles["legend"]},
			height : heightChart,
			focusTarget : 'category',
			vAxis : {
				title : 'Percent of cases',
				titleTextStyle : textStyles["axisTitle"],
				textStyle: textStyles["axisText"],
				format : '###.##%'
			},
			pointSize : 5,
			hAxis : {				
				title : "Relative position",
				titleTextStyle : textStyles["axisTitle"],
				showTextEvery : 1,
				slantedText : 1,
				slantedTextAngle : 20
			},
			chartArea : {
				// top:26,
				left : 60,
				width : widthChart - 60
			},
			colors : [ '#FA9627', '#999999' ],
			forceIFrame: true
		};
		// chart = new
		// google.visualization.LineChart(document.getElementById('rangeFeaturePlot'));
		chart = new google.visualization.ChartWrapper({
			'chartType' : 'LineChart',
			'containerId' : 'rangeFeaturePlot',
			'dataTable' : data,
			'options' : options
		});
		currentState["activeChart"].push(chart);
		// chart.draw(data, options);
		chart.draw();
		var difShow = $('<tr class="showTableLink"><td></td><td ><a href="#" onclick="return false">Show as table</a></td></tr>');
		difShow.click(function() {
			if (chart.getChartType() == "Table") {
				chart.setChartType('LineChart')
				chart.setOption("height", heightChart)
				$(".showTableLink a").text("Show as table");
				$("tr.toPNGRow").show()
			} else {
				chart.setChartType("Table")
				chart.setOption("height", null)
				$(".showTableLink a").text("Show as chart");
				$("tr.toPNGRow").hide()
			}
			chart.draw()
		});
		$('.showTableLink').remove();
		$('#rangeFeaturePlotTable').append(difShow);
		// Image convertion
		$('tr.toPNGRow').remove();
		var toImageButton = $('<tr class="toPNGRow"><td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
				+ options["width"]
				+ '"/> <input type="hidden" value="'
				+ options["height"]
				+ '"/><input type="hidden" value="'
				+ chart.getContainerId() + '"/></td></tr>')
		$('#rangeFeaturePlotTable').append(toImageButton)

	}
	// by default load the first tissue
	changeReferenceTissue(0);
	function tissueTableSelectHandler() {
		var item = tissueTableVisualization.getChart().getSelection()[0];
		if (item.row != null) {
			// var str = tableReferenceData.getFormattedValue(item.row, 0);
			changeReferenceTissue(item.row);
		}
	}
	google.visualization.events.addListener(tissueTableVisualization, 'select',
			tissueTableSelectHandler);

}
function updateOpenedFeatureNeighborhoodGooglePlotSingle(plotTitle, plotData,
		plotLabels) {
	$('#rangeFeaturePlotMain').children().remove()
	// $('#rangeFeaturePlot').remove();
	$('#rangeFeaturePlotMain').show();
	showInfoPlot("neighborhoodsingle")

	$('#rangeFeaturePlotMain')
			.append(
					$('<table id="rangeFeaturePlotTable"><tr><td colspan="2"><div id="rangeFeaturePlot"></div></td></tr></table>'))

	var dataCols = []

	dataCols
			.push({
				type : 'string',
				label : "Position relative to the "
						+ currentState["datasetInfo"][currentState["exploreRegionSelected"]]['officialName']
			});

	$.each(plotLabels, function(index, seriesLabel) {
		// data.addColumn('number', seriesLabel);
		dataCols.push({
			'type' : 'number',
			'label' : seriesLabel
		})
		// datacolCount = datacolCount +1
	});
	var visualizationData = {
		'cols' : dataCols,
		'rows' : plotData
	}
	var data = new google.visualization.DataTable(visualizationData, 0.6);

	var heightChart = 400;
	var widthChart = 800;
	var options = {
		title : plotTitle,
		titleTextStyle:textStyles["mainTitle"],
		width : widthChart,
		height : heightChart,
		focusTarget : 'category',
		legend : {position:'top',
				  textStyle: textStyles["legend"]},
		vAxis : {
			title : 'Percent of cases',
			titleTextStyle : textStyles["axisTitle"],
			textStyle : textStyles["axisText"],
			format : '###.##%'
		},
		pointSize : 5,
		hAxis : {
			title : "Relative position",
			titleTextStyle : textStyles["axisTitle"],
			showTextEvery : 1,
			slantedText : 1,
			slantedTextAngle : 20
		},
		chartArea : {
			// top:26,
			left : 60,
			width : widthChart - 60
		},
		forceIFrame: true
	};
	// var chart = new
	// google.visualization.LineChart(document.getElementById('rangeFeaturePlot'));
	var chart = new google.visualization.ChartWrapper({
		'chartType' : 'LineChart',
		'containerId' : 'rangeFeaturePlot',
		'dataTable' : data,
		'options' : options
	});
	currentState["activeChart"].push(chart);
	function chartSelectHandler() {
		var item = chart.getChart().getSelection()[0];
		if (item.column != null) {
			data.removeColumn(item.column)
			chart.draw(data, options);
		}
	}

	google.visualization.events
			.addListener(chart, 'select', chartSelectHandler);

	// chart.draw(data, options);
	chart.draw();

	var difShow = $('<tr class="showTableLink"><td ><a href="#" onclick="return false">Show as table</a></td><td></td></tr>');

	difShow.click(function() {
		if (chart.getChartType() == "Table") {
			chart.setChartType('LineChart')
			chart.setOption("height", heightChart)
			$(".showTableLink a").text("Show as table");
			$('tr.toPNGRow').show()
		} else {
			chart.setChartType("Table")
			chart.setOption("height", null)
			$(".showTableLink a").text("Show as chart");
			$('tr.toPNGRow').hide()
		}
		chart.draw()

		// difShow.remove();
		// var originalVisualization = new
		// google.visualization.Table(document.getElementById('rangeFeaturePlot'));
		// var tableoptions = {'page':'enable'};
		// originalVisualization.draw(data,{width: 800, height: 600});
	});
	$('.showTableLink').remove();
	$('#rangeFeaturePlotTable').append(difShow);
	// Image convertion
	$('tr.toPNGRow').remove();
	var toImageButton = $('<tr class="toPNGRow"><td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
			+ options["width"]
			+ '"/> <input type="hidden" value="'
			+ options["height"]
			+ '"/><input type="hidden" value="'
			+ chart.getContainerId() + '"/></td></tr>')
	$('#rangeFeaturePlotTable').append(toImageButton)

}

function updateOpenedFeatureRatio(result, otherParameters) {

	// remove the current list in the feature refinement

	updateOpenedFeatureRatioLines(result, otherParameters);

}
function updateOpenedFeatureRatioLines(result, otherParameters) {
	// CONVERT_BASEQUERY_TO_JSON
	var convertMethod = function(x) {
		return convertRatioToNumber(x, otherParameters[1])
	};
	var completionsValues = [];
	var completionsValuesPlot = [];
	var completionsValuesPlotGoogle = {};
	var minValue = Math.pow(10, otherParameters[1]);
	var maxValue = 0;
	$.each(result[3], function(completion, numberOfCases) {
		var nwc = parseInt(numberOfCases, 10);
		var complText = completion.split(":").pop();
		var compl = parseInt(complText, 10);
		if (minValue > compl) {
			minValue = compl;
		}
		if (maxValue < compl) {
			maxValue = compl;
		}
		completionsValues[compl] = nwc;

		// completionsValuesPlotGoogle[compl] = [nwc,null]
		completionsValuesPlotGoogle[complText] = [ nwc, 0 ]
		// completionsValuesPlot.push([rn,nwc]);
	});
	var bothMinValue = minValue;
	var bothMaxValue = maxValue;
	if (currentState["referenceQuery"]["genome"] != "") {
		/* REFERENCE UPDATE */
		referenceQuery = currentState["referenceQuery"]["query"].replace(
				/BASEREFQUERY/g, otherParameters[0] + "*")
		// alert(referenceQuery);
		/* REFERENCE UPDATE */
		answerQuery(
				currentState["referenceQuery"]["dataset"],
				referenceQuery,
				1500,
				0,
				false,
				"",
				function(resultRef) {
					// currentState["referenceQuery"]["values"] = {};
					$
							.each(
									resultRef[3],
									function(index, value) {
										var rwc = parseInt(value, 10);
										var complText = index.split(":").pop();
										var compl = parseInt(complText, 10);
										if (bothMinValue > compl) {
											bothMinValue = compl;
										}
										if (bothMaxValue < compl) {
											bothMaxValue = compl;
										}
										var rn = convertMethod(compl);
										currentState["referenceQuery"]["values"][compl] = rwc;
										if (completionsValuesPlotGoogle[complText] !== undefined) {
											completionsValuesPlotGoogle[complText] = [
													completionsValuesPlotGoogle[complText][0],
													rwc ]
										} else {
											// completionsValuesPlotGoogle[compl]
											// = [null,rwc]
											completionsValuesPlotGoogle[complText] = [
													0, rwc ]
										}

									});
				});
	}

	// alert("with or without reference we go");
	if (completionsValues.length > 0) {
		if (completionsValues.length == 1 || minValue == maxValue) {
			// results with only single values better be processed by the table
			// processor
			updateOpenedFeatureTableLines(result, "", otherParameters, false);
		} else {
			// update the slider
			updateOpenedFeatureRatioSlider(completionsValues, minValue,
					maxValue, convertMethod, otherParameters);
		}
		// update the main plot
		updateOpenedFeatureRatioPlotGoogle(completionsValuesPlotGoogle,
				convertMethod, otherParameters);
	} else {
		// add the row to the table
		$('#rangeFeaturePlotMain').children().remove()
		$('#rangeFeaturePlotMain').show();

		$('#rangeFeaturePlotMain')
				.append(
						$('<table id="rangeFeaturePlotTable"><tr style="width:100%;"><td align="left">No regions fit this query</td><td></td></tr></table>'))
		var newTableLine = $('<tr style="width:100%;"><td ></td><td align="left">No regions fit this query</td><td align="right"></td></tr>');
		// add the row to the table
		$('#openedFeatureResults').append(newTableLine);
	}
}
function updateOpenedFeatureRatioPlotGoogle(completionsValuesPlotGoogle,
		convertMethod, otherParameters) {
	$('#rangeFeaturePlotMain').children().remove()
	$('#rangeFeaturePlotMain').show();
	showInfoPlot("ratio")

	$('#rangeFeaturePlotMain')
			.append(
					$('<table id="rangeFeaturePlotTable"><tr><td colspan="2"><div id="rangeFeaturePlot"></div></td></tr></table>'))
	var visualizationData = {
		'cols' : [ {
			'label' : 'ORatio',
			'type' : 'string'
		},
		// {'label':'ORatio','type':'number'},
		{
			'label' : 'Current selection',
			'type' : 'number'
		} ],
		'rows' : []
	};
	// var shown = true;
	// var completionValuesKeysTexts = {};
	// $.each(completionsValuesPlotGoogle,function(compl,value){
	// var rn = convertMethod(parseInt(compl,10));
	// completionValuesKeysTexts[rn] = compl;
	// });
	var completionValuesKeys = Object.keys(completionsValuesPlotGoogle);
	completionValuesKeys.sort();
	var prevKey = null;
	var nCScases = 0;
	var nRcases = 0;
	$.each(completionValuesKeys, function(index, complText) {
		var compl = parseInt(complText, 10)
		var rn = convertMethod(compl);
		var value = completionsValuesPlotGoogle[complText];

		if (prevKey != null && compl > prevKey + 1) {
			// alert(prevKey+"--"+compl)
			for ( var j = prevKey + 1; j < compl; j++) {
				var rnTemp = convertMethod(j);
				if (currentState["referenceQuery"]["genome"] != "") {
					visualizationData['rows'].push({
						c : [ {
							'v' : rnTemp
						}, {
							v : 0,
							f : "0 cases"
						}, {
							v : 0,
							f : "0 cases"
						} ]
					})
				} else {
					visualizationData['rows'].push({
						c : [ {
							'v' : rnTemp
						}, {
							v : 0,
							f : "0 cases"
						} ]
					})
				}
			}
		}
		prevKey = compl;

		// $.each(completionsValuesPlotGoogle,function(compl,value){
		// var rn = convertMethod(parseInt(compl,10));
		var rn1 = convertMethod(compl + 1);
		var currentSelectionValue = {
			'v' : 0
		};
		if (value[0] != null) {
			currentSelectionValue = {
				v : value[0] / currentState["totalNumberOfRegions"],
				f : value[0] + " cases"
			}
			nCScases = nCScases + parseInt(value[0], 10);
		}
		if (currentState["referenceQuery"]["genome"] != "") {
			var refValue = {
				'v' : 0
			};
			if (value[1] != null) {
				refValue = {
					v : value[1]
							/ currentState["referenceQuery"]["totalNumber"],
					f : value[1] + " cases"
				}
				nRcases = nRcases + parseInt(value[1], 10);
			}
			visualizationData['rows'].push({
				c : [ {
					'v' : rn
				// v:parseFloat(rn),
				// f:"Between "+parseFloat(rn)+" and "+parseFloat(rn1)
				}, currentSelectionValue, refValue ]
			})
		} else {
			visualizationData['rows'].push({
				'c' : [ {
					'v' : rn
				// 'v':parseFloat(rn),
				// 'f':"Between "+parseFloat(rn)+" and "+parseFloat(rn1)
				}, currentSelectionValue ]
			})
		}
	});
	// alert(visualizationData['rows'].length)

	var heightChart = 400;
	var widthChart = 850;
	var options = {
		width : widthChart,
		height : heightChart,
		focusTarget : 'category',
		chartArea : {
			// top:26,
			left : 60,
			width : widthChart - 60 - 50,
			right : 50
		},
		hAxis : {
			title : getTextForFeaturePrefix(otherParameters[0]),
			titleTextStyle : textStyles["axisTitle"],
			textStyle : textStyles["axisText"]
		},
		vAxis : {
			title : 'Percent of cases',
			titleTextStyle : textStyles["axisTitle"],
			textStyle : textStyles["axisText"],
			format : '###.##%',
			viewWindowMode : "pretty"
		},
		pointSize : 6,
		forceIFrame: true
	}
	// alert("ratio")
	if (currentState["referenceQuery"]["genome"] != "") {
		visualizationData['cols'].push({
			'label' : 'Control set',
			'type' : 'number'
		});
		options['legend'] = {position:'top',
				             textStyle: textStyles["legend"]};
		options['colors'] = [ '#FA9627', '#999999' ]
	} else {
		// alert("Two columns")
		options['legend'] = 'none';
		options['colors'] = [ '#AAAAAA' ];
	}

	var data = new google.visualization.DataTable(visualizationData, 0.6);

	// var ratiochart = new
	// google.visualization.ScatterChart(document.getElementById('rangeFeaturePlot'));
	options["hAxis"]["showTextEvery"] = Math
			.round(visualizationData['rows'].length / 10)
	options["hAxis"]["maxAlternation"] = 1
	options["hAxis"]["textStyle"] = {
		"fontSize" : 10
	}
	options["hAxis"]["slantedText"] = false
	// options["hAxis"]["slantedTextAngle"] = 10
	options["pointSize"] = 1
	var chart = new google.visualization.ChartWrapper({
		'chartType' : 'AreaChart',
		'containerId' : 'rangeFeaturePlot',
		'dataTable' : data,
		'options' : options
	});
	currentState["activeChart"].push(chart);
	// var chart = new
	// google.visualization.AreaChart(document.getElementById('rangeFeaturePlot'));
	chart.draw()
	// alert(otherParameters[0]+" "+nRcases+" "+nCScases)
	if (otherParameters[0].startsWith("Eor:")
			|| otherParameters[0].startsWith("Emeth")) {

		var nCSPercent = Math.round((100 * nCScases)
				/ currentState["totalNumberOfRegions"]);
		if (currentState["referenceQuery"]["genome"] != "") {
			var nRPercent = Math.round((100 * nRcases)
					/ currentState["referenceQuery"]["totalNumber"]);
			if (otherParameters[0].startsWith("Eor:")) {
				var noteShow = $('<tr class="noteShowRow"><td><i>Note: the visualization reports only data for the '
						+ numberWithCommas(nCScases)
						+ ' ('
						+ nCSPercent
						+ '%) overlapping regions from the current selection and '
						+ numberWithCommas(nRcases)
						+ ' ('
						+ nRPercent
						+ '%) reference regions</i></td><td></td></tr>');
			} else if (otherParameters[0].startsWith("Emeth")) {
				var noteShow = $('<tr class="noteShowRow"><td><i>Note: the visualization reports only data for the '
						+ numberWithCommas(nCScases)
						+ ' ('
						+ nCSPercent
						+ '%) current selection regions  and '
						+ numberWithCommas(nRcases)
						+ ' ('
						+ nRPercent
						+ '%) reference regions for which methylation data is available</i></td><td></td></tr>');
			}
		} else {
			if (otherParameters[0].startsWith("Eor:")) {
				var noteShow = $('<tr class="noteShowRow"><td><i>Note: the visualization reports only data for the '
						+ numberWithCommas(nCScases)
						+ ' ('
						+ nCSPercent
						+ '%) overlapping regions</i></td><td></td></tr>');
			} else if (otherParameters[0].startsWith("Emeth")) {
				var noteShow = $('<tr class="noteShowRow"><td><i>Note: the visualization reports only data for the '
						+ numberWithCommas(nCScases)
						+ ' ('
						+ nCSPercent
						+ '%) regions for which methylation data is available</i></td><td></td></tr>');
			}
		}
		$('.noteShowRow').remove();
		$('#rangeFeaturePlotTable').append(noteShow);
	}
	// ratiochart.draw(data, options);
	var difShow = $('<tr class="showTableLink"><td ><a href="#" onclick="return false">Show as table</a></td><td></td></tr>');
	difShow.click(function() {
		if (chart.getChartType() == "Table") {
			chart.setChartType('AreaChart')
			chart.setOption("height", heightChart)
			$(".showTableLink a").text("Show as table");
			$('tr.toPNGRow').show()
		} else {
			chart.setChartType("Table")
			chart.setOption("height", null)
			$(".showTableLink a").text("Show as chart");
			$('tr.toPNGRow').hide()
		}
		chart.draw()
	});
	$('.showTableLink').remove();
	$('#rangeFeaturePlotTable').append(difShow);
	// Image convertion
	$('tr.toPNGRow').remove();
	var toImageButton = $('<tr class="toPNGRow"><td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
			+ options["width"]
			+ '"/> <input type="hidden" value="'
			+ options["height"]
			+ '"/><input type="hidden" value="'
			+ chart.getContainerId() + '"/></td><td></td></tr>')
	$('#rangeFeaturePlotTable').append(toImageButton)

}

function updateOpenedFeatureRange(result, otherParameters) {
	// CONVERT_BASEQUERY_TO_JSON

	updateOpenedFeatureRangeLines(result, otherParameters);

}

function updateOpenedFeatureRangeLines(result, otherParameters) {
	// CONVERT_BASEQUERY_TO_JSON
	var convertMethod = function(x) {
		return convertRangeToNumber(x, otherParameters[1], otherParameters[2])
	};
	var completionsValues = [];
	var allcompletions = {};
	var completionsValuesPiePlot = {};
	var completionValuesPieChart = {};
	var completionsValuesColumnChart = {};
	var minValue = 1000;
	var maxValue = 0;

	// CONVERT_BASEQUERY_TO_JSON
	var text = "";
	$
			.each(
					result[3],
					function(completion, numberOfCases) {
						var nwc = parseInt(numberOfCases, 10);
						var complText = completion.split(":").pop();
						var compl = parseInt(complText, 10);
						if (completionValuesPieChart[complText[0]] !== undefined) {
							completionValuesPieChart[complText[0]][1] = completionValuesPieChart[complText[0]][1]
									+ nwc;
						} else {
							if (complText[0] == "0") {
								var minText = "0"
										.repeat((otherParameters[1] - 1))
										+ "1";
							} else {
								var minText = complText[0] + "1"
										+ "0".repeat((otherParameters[1] - 2));
							}
							var maxText = (parseInt(complText[0]) + 1) + "1"
									+ "0".repeat((otherParameters[1] - 2));
							// var maxText =
							// complText[0]+"9".repeat((otherParameters[1]-1));
							var legendText = "Between "
									+ numberWithCommas(convertMethod(minText))
									+ " and "
									+ numberWithCommas(convertMethod(maxText));
							completionValuesPieChart[complText[0]] = [
									legendText, nwc ];
							completionsValuesPiePlot[legendText] = []
						}
						// if (compl == 0){
						// var x = completion.split(":").pop();
						// }
						if (minValue > compl) {
							minValue = compl;
						}
						if (maxValue < compl) {
							maxValue = compl;
						}
						completionsValues[compl] = nwc;
						allcompletions[complText] = completionValuesPieChart[complText[0]][0];
						// var rn = convertMethod(compl);
						// var rn1 = convertMethod(compl+1);
						// completionsValuesPiePlot[completionValuesPieChart[complText[0]][0]].push([{v:rn,f:"Between
						// "+rn+" and "+rn1},{v:nwc,f:nwc+" cases"}])
					});

	var csNumberOfHits = parseInt(result[2], 10);
	// alert(currentState["totalNumberOfRegions"]+"--"+csNumberOfHits)
	if (currentState["totalNumberOfRegions"] > csNumberOfHits) {
		completionValuesPieChart["OVERLAP"] = [ "Overlapping",
				currentState["totalNumberOfRegions"] - csNumberOfHits ];
	}
	var refNumberOfHits = 1;
	if (currentState["referenceQuery"]["genome"] != "") {
		// alert("start processing reference")
		$.each(completionValuesPieChart, function(legendText, legendValue) {
			// alert(legendText +legendValue)
			legendValue.push(0)
			completionValuesPieChart[legendText] = legendValue;
			// alert(legendText + legendValue)
		})
		// alert("redone completionValues")
		/* REFERENCE UPDATE */
		referenceQuery = currentState["referenceQuery"]["query"].replace(
				/BASEREFQUERY/g, otherParameters[0] + "*")
		/* REFERENCE UPDATE */
		answerQuery(
				currentState["referenceQuery"]["dataset"],
				referenceQuery,
				1500,
				0,
				false,
				"",
				function(resultRef) {
					// alert("start processing reference range values")
					// currentState["referenceQuery"]["values"] = {};
					$
							.each(
									resultRef[3],
									function(completion, value) {
										// alert("start "+rn+" "+nwc)
										var nwc = parseInt(value, 10);
										var complText = completion.split(":")
												.pop();
										var compl = parseInt(complText, 10);
										if (completionValuesPieChart[complText[0]] !== undefined) {
											completionValuesPieChart[complText[0]][2] = completionValuesPieChart[complText[0]][2]
													+ nwc;
										} else {
											if (complText[0] == "0") {
												var minText = "0"
														.repeat((otherParameters[1] - 1))
														+ "1";
											} else {
												var minText = complText[0]
														+ "1"
														+ "0"
																.repeat((otherParameters[1] - 2));
											}
											var maxText = complText[0]
													+ "9"
															.repeat((otherParameters[1] - 1));
											var legendText = "Between "
													+ numberWithCommas(convertMethod(minText))
													+ " and "
													+ numberWithCommas(convertMethod(maxText));
											completionValuesPieChart[complText[0]] = [
													legendText, 0, nwc ];
											completionsValuesPiePlot[legendText] = []
										}
										currentState["referenceQuery"]["values"][compl] = nwc;
										allcompletions[complText] = completionValuesPieChart[complText[0]][0];
									});

					refNumberOfHits = parseInt(resultRef[2], 10);
					// alert(currentState["referenceQuery"]["totalNumber"]+"--"+refNumberOfHits)
					if (currentState["totalNumberOfRegions"] > csNumberOfHits
							|| currentState["referenceQuery"]["totalNumber"] > refNumberOfHits) {
						completionValuesPieChart["OVERLAP"] = [
								"Overlapping",
								currentState["totalNumberOfRegions"]
										- csNumberOfHits,
								currentState["referenceQuery"]["totalNumber"]
										- refNumberOfHits ];
					}
					completionsValuesColumnChart = {
						'cols' : [ {
							'label' : "Range",
							'type' : 'string'
						} ],
						'rows' : [
								{
									c : [ {
										v : "Current selection ("
												+ currentState["totalNumberOfRegions"]
												+ ")"
									} ]
								},
								{
									c : [ {
										v : "Control set ("
												+ currentState["referenceQuery"]["totalNumber"]
												+ ")"
									} ]
								} ]
					}
					var completionValuesPieChartKeys = Object
							.keys(completionValuesPieChart);
					completionValuesPieChartKeys.sort();
					$
							.each(
									completionValuesPieChartKeys,
									function(index, legendText) {
										var legendValue = completionValuesPieChart[legendText];
										completionsValuesColumnChart['cols']
												.push({
													'label' : legendValue[0]
															+ '',
													'type' : 'number',
													'id' : legendText[0] + ''
												})
										completionsValuesColumnChart['rows'][0]['c']
												.push({
													'v' : legendValue[1]
															/ currentState["totalNumberOfRegions"],
													'f' : legendValue[1] + ''
												})
										completionsValuesColumnChart['rows'][1]['c']
												.push({
													'v' : legendValue[2]
															/ currentState["referenceQuery"]["totalNumber"],
													'f' : legendValue[2] + ''
												})
									});
				});

	}

	var allcompletionsKeys = Object.keys(allcompletions);
	allcompletionsKeys.sort();
	var prevPieSection = null;
	var prevComplKey = 0;

	$.each(allcompletionsKeys, function(index, complText) {
		var compl = parseInt(complText, 10);

		var pieSection = allcompletions[complText];

		if (pieSection == prevPieSection && prevComplKey + 1 < compl) {
			// There were missing completions. We must fill them with zeroes
			var i = prevComplKey + 1;

			for (i = prevComplKey + 1; i < compl; i++) {
				var rnTemp = convertMethod(i);
				if (currentState["referenceQuery"]["genome"] != "") {
					completionsValuesPiePlot[pieSection].push([ {
						v : rnTemp + ""
					}, 0, 0 ])
				} else {
					completionsValuesPiePlot[pieSection].push([ {
						v : rnTemp + ""
					}, 0 ])
				}
			}
		}
		prevPieSection = pieSection;
		prevComplKey = compl;

		var rn = convertMethod(parseInt(compl, 10));
		var rn1 = convertMethod(parseInt(compl, 10) + 1);
		if (currentState["referenceQuery"]["genome"] != "") {
			var curSelValue = 0;
			if (completionsValues[compl] !== undefined) {
				curSelValue = {
					v : completionsValues[compl]
							/ currentState["totalNumberOfRegions"],
					f : completionsValues[compl] + " cases"
				};
			}
			var refValue = 0;
			if (currentState["referenceQuery"]["values"][compl] !== undefined) {
				refValue = {
					v : currentState["referenceQuery"]["values"][compl]
							/ currentState["referenceQuery"]["totalNumber"],
					f : currentState["referenceQuery"]["values"][compl]
							+ " cases"
				};
			}

			completionsValuesPiePlot[pieSection].push([// {v:parseInt(rn,10),f:"Between
														// "+rn+" and "+rn1},
			{
				v : rn + ""
			}, curSelValue, refValue ])
		} else {

			var curSelValue = 0;
			if (completionsValues[compl] !== undefined) {
				curSelValue = {
					v : parseInt(completionsValues[compl], 10)
							/ currentState["totalNumberOfRegions"],
					f : completionsValues[compl] + " cases"
				};
			}
			// v:"Between "+rn+" and "+rn1
			completionsValuesPiePlot[pieSection].push([// {v:parseInt(rn,10),f:"Between
														// "+rn+" and "+rn1},
			{
				v : rn + ""
			}, curSelValue ])
		}
	})

	// alert("Data processing complete ")
	if (completionsValues.length > 0) {

		// alert("plot updated");
		if (minValue == maxValue) {
			// results with only single values better be processed by the table
			// processor
			updateOpenedFeatureTableLines(result, "", otherParameters, false);
		} else {
			// update the slider
			updateOpenedFeatureRangeSlider(completionsValues, minValue,
					maxValue, convertMethod, otherParameters);
		}
		// update the main plot
		if (currentState["referenceQuery"]["genome"] != "") {
			// with reference
			updateOpenedFeatureRangePlotColumn(completionsValuesColumnChart,
					completionsValuesPiePlot, otherParameters, convertMethod);
		} else {
			// single then pie
			var completionValuesPieChartArray = [];
			var completionValuesKeys = Object.keys(completionValuesPieChart);
			completionValuesKeys.sort();
			$.each(completionValuesKeys, function(index, key) {
				completionValuesPieChartArray
						.push(completionValuesPieChart[key]);
			});
			// completionValuesPieChartArray.sort()
			// alert(completionValuesPieChartArray)
			updateOpenedFeatureRangePlotPie(completionValuesPieChartArray,
					completionsValuesPiePlot, otherParameters, convertMethod);
		}
	} else {
		// add the row to the table
		$('#rangeFeaturePlotMain').children().remove()
		$('#rangeFeaturePlotMain').show();

		$('#rangeFeaturePlotMain')
				.append(
						$('<table id="rangeFeaturePlotTable"><tr style="width:100%;"><td align="left">No regions fit this query</td><td></td></tr></table>'))
		var newTableLine = $('<tr style="width:100%;"><td ></td><td align="left">No regions fit this query</td><td align="right"></td></tr>');
		// add the row to the table
		$('#openedFeatureResults').append(newTableLine);
	}
}
function updateOpenedFeatureRangePlotColumn(completionsValuesColumnChart,
		completionsValuesPiePlot, otherParameters, convertMethod) {
	$('#rangeFeaturePlotMain').children().remove()
	$('#rangeFeaturePlotMain').show();
	showInfoPlot("rangecolumn");

	$('#rangeFeaturePlotMain')
			.append(
					$('<table id="rangeFeaturePlot"><tr><td><div id="rangeFeaturePlotPie" ></div></td><td><div id="rangeFeaturePlotScatter" ></div></td></tr></table>'));

	var data = new google.visualization.DataTable(completionsValuesColumnChart,
			0.6);
	// var chart = new
	// google.visualization.ColumnChart(document.getElementById('rangeFeaturePlotPie'));
	var heightChart = 400;
	var widthChart = 450;
	var options = {
		width : widthChart,
		height : heightChart, // is3D: true,
		title : getTextForFeaturePrefix(otherParameters[0]),
		titleTextStyle:textStyles["mainTitle"],
		isStacked : true,
		enableInteractivity : true,
		legend : {position:'top',
				  textStyle : {
						fontSize : 10}
				  },
		// vAxis:{format:'#,###%'},
		chartArea : {
			// top:26,
			left : 50,
			width : widthChart - 50
		},
		vAxis : {
			format : '###.##%'
		},
		legendTextStyle : {
			fontSize : 10
		},
		forceIFrame: true
	};
	var columnchart = new google.visualization.ChartWrapper({
		'chartType' : 'ColumnChart',
		'containerId' : 'rangeFeaturePlotPie',
		'dataTable' : data,
		'options' : options
	});
	currentState["activeChart"].push(columnchart);
	// chart.draw(data,options );
	columnchart.draw();
	function chartSelectHandler() {
		var selection = columnchart.getChart().getSelection();
		for ( var i = 0; i < selection.length; i++) {
			var item = selection[i];
			if (item.row != null && item.column != null) {
				// message += '{row:' + item.row + ',column:' + item.column +
				// '}';
				message = data.getColumnLabel(item.column)
			} else if (item.row != null) {
				// message = '{row:' + item.row + '}';
				message = "";
			} else if (item.column != null) {
				// message += '{column:' + item.column + '}';
				message = data.getColumnLabel(item.column)
			}
		}
		if (completionsValuesPiePlot[message] !== undefined) {
			updateOpenedFeatureRangePlotGoogle(
					completionsValuesPiePlot[message], otherParameters);
		}
	}
	google.visualization.events.addListener(columnchart, 'select',
			chartSelectHandler);

	var showTableLinkLine = $('<tr class="showTableLink"></tr>');
	var difShow = $('<td><a href="#" onclick="return false">Show as table</a></td>');
	difShow.click(function() {
		if (columnchart.getChartType() == "Table") {
			columnchart.setChartType('ColumnChart')
			columnchart.setOption("height", heightChart)
			$(".showTableLink td:eq(0) a").text("Show as table");
			$("tr.toPNGRow td:eq(0) ").show();
		} else {
			columnchart.setChartType("Table")
			columnchart.setOption("height", null)
			$(".showTableLink td:eq(0) a").text("Show as chart");
			$("tr.toPNGRow td:eq(0) a").hide();
		}
		columnchart.draw()
	});

	$('.showTableLink').remove();
	$(showTableLinkLine).append(difShow)
	$('#rangeFeaturePlot').append(showTableLinkLine);

	$('tr.toPNGRow').remove();

	var toImageButton = $('<tr class="toPNGRow"><td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
			+ options["width"]
			+ '"/> <input type="hidden" value="'
			+ options["height"]
			+ '"/><input type="hidden" value="'
			+ columnchart.getContainerId() + '"/></td></tr>')

	$('#rangeFeaturePlot').append(toImageButton)

	updateOpenedFeatureRangePlotGoogle(completionsValuesPiePlot[data
			.getColumnLabel(1)], otherParameters);

}

function updateOpenedFeatureRangePlotPie(completionValuesPieChartArray,
		completionsValuesPiePlot, otherParameters, convertMethod) {
	$('#rangeFeaturePlotMain').children().remove()
	$('#rangeFeaturePlotMain').show();
	showInfoPlot("rangepie");

	$('#rangeFeaturePlotMain')
			.append(
					$('<table id="rangeFeaturePlot"><tr><td><div id="rangeFeaturePlotPie" ></div></td><td><div id="rangeFeaturePlotScatter" ></div></td></tr></table>'));

	var data = new google.visualization.DataTable();
	data.addColumn('string', 'Range');
	data.addColumn('number', 'Number fo regions');

	data.addRows(completionValuesPieChartArray);

	// var chart = new
	// google.visualization.PieChart(document.getElementById('rangeFeaturePlotPie'));
	var heightChart = 400;
	var widthChart = 450;
	var options = {
		width : widthChart,
		height : heightChart, // is3D: true,
		title : getTextForFeaturePrefix(otherParameters[0]),
		legend : 'right',
		sliceVisibilityThreshold : 0.0001,
		chartArea : {
			// top:26,
			left : 0,
			width : widthChart - 0
		},
		is3D : true,
		legendTextStyle : {
			fontSize : 10
		},
		forceIFrame: true
	};
	var chart = new google.visualization.ChartWrapper({
		'chartType' : 'PieChart',
		'containerId' : 'rangeFeaturePlotPie',
		'dataTable' : data,
		'options' : options
	});
	currentState["activeChart"].push(chart);
	// chart.draw(data,options );
	chart.draw();

	function chartSelectHandler() {
		var selection = chart.getChart().getSelection();
		var message = '';
		for ( var i = 0; i < selection.length; i++) {
			var item = selection[i];
			message = data.getValue(item.row, 0);
			var number = data.getValue(item.row, 1);
		}
		if (completionsValuesPiePlot[message] !== undefined) {
			updateOpenedFeatureRangePlotGoogle(
					completionsValuesPiePlot[message], otherParameters);
		}
	}
	;

	google.visualization.events
			.addListener(chart, 'select', chartSelectHandler);
	var showTableLinkLine = $('<tr class="showTableLink"></tr>');
	var difShow = $('<td><a href="#" onclick="return false">Show as table</a></td>');
	difShow.click(function() {
		if (chart.getChartType() == "Table") {
			chart.setChartType('PieChart')
			chart.setOption("height", heightChart)
			$("tr.showTableLink td:eq(0) a").text("Show as table");
			$("tr.toPNGRow td:eq(0) a").show();
		} else {
			chart.setChartType("Table")
			chart.setOption("height", null)
			$("tr.showTableLink td:eq(0) a").text("Show as chart");
			$("tr.toPNGRow td:eq(0) a").hide();
		}
		chart.draw()
	});
	$('.showTableLink').remove();
	$(showTableLinkLine).append(difShow)
	$('#rangeFeaturePlot').append(showTableLinkLine);
	$('tr.toPNGRow').remove();
	var toImageButton = $('<tr class="toPNGRow"><td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
			+ options["width"]
			+ '"/> <input type="hidden" value="'
			+ options["height"]
			+ '"/><input type="hidden" value="'
			+ chart.getContainerId() + '"/></td></tr>')
	$('#rangeFeaturePlot').append(toImageButton)

	updateOpenedFeatureRangePlotGoogle(
			completionsValuesPiePlot[completionValuesPieChartArray[0][0]],
			otherParameters);

}
function updateOpenedFeatureRangePlotGoogle(completionsValuesPlot,
		otherParameters) {
	var data = new google.visualization.DataTable();
	var heightChart = 400;
	var widthChart = 500;
	var options = {
		width : widthChart,
		height : heightChart,
		focusTarget : 'category',
		chartArea : {
			// top:26,
			left : 60,
			width : widthChart - 60 - 40,
			right : 40
		},
		vAxis : {
			title : 'Percent of cases',
			titleTextStyle : textStyles["axisTitle"],
			textStyle : textStyles["axisText"],
			format : '###.##%'
		},
		hAxis : {
			title : getTextForFeaturePrefix(otherParameters[0]),
			titleTextStyle : textStyles["axisTitle"],
			showTextEvery : Math.round(completionsValuesPlot.length / 5),
			textStyle : textStyles["axisText"],
			slantedText : false,
			maxAlternation : 1
		},
		pointSize : 5,
		forceIFrame: true
	}

	// alert("setting start")
	if (currentState["referenceQuery"]["genome"] != "") {
		// data.addColumn('number', 'Length');
		data.addColumn('string', 'Length');
		data.addColumn('number', 'Current selection');
		data.addColumn('number', 'Control set');
		options['legend'] = {position:'top',
				             textStyle: textStyles["legend"]};
		options['colors'] = [ '#FA9627', '#999999' ]
	} else {
		// alert("Two columns")
		// data.addColumn('number', 'Length');
		data.addColumn('string', 'Length');
		data.addColumn('number', 'Current selection');
		options['legend'] = 'none';
		options['colors'] = [ '#AAAAAA' ];

	}
	data.addRows(completionsValuesPlot);

	// var rangechart = new
	// google.visualization.ScatterChart(document.getElementById('rangeFeaturePlotScatter'));

	// rangechart.draw(data, options);
	var rangechart = new google.visualization.ChartWrapper({
		'chartType' : 'AreaChart',
		'containerId' : 'rangeFeaturePlotScatter',
		'dataTable' : data,
		'options' : options
	});
	currentState["activeChart"].push(rangechart);
	rangechart.draw()
	// var difShow = $('<tr class="showTableLink"><td></td><td ><a href="#"
	// onclick="return false">Show as table</a></td></tr>');
	var difShow = $('<td><a href="#" onclick="return false">Show as table</a></td>');
	difShow.click(function() {
		if (rangechart.getChartType() == "Table") {
			rangechart.setChartType('AreaChart')
			rangechart.setOption("height", heightChart)
			difShow.children("a").text("Show as table");
			$('tr.toPNGRow td:eq(1) a').show()
		} else {
			rangechart.setChartType("Table")
			rangechart.setOption("height", null)
			difShow.children("a").text("Show as chart");
			$('tr.toPNGRow td:eq(1) a').hide()
		}
		rangechart.draw()
	});
	$('tr.showTableLink td:gt(0)').remove()
	$('tr.showTableLink').append(difShow)
	// $('.showTableLink').remove();
	// $('#rangeFeaturePlot').append(difShow);
	// Image convertion
	$('tr.toPNGRow td:eq(1)').remove();
	var toImageButton = $('<td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
			+ options["width"]
			+ '"/> <input type="hidden" value="'
			+ options["height"]
			+ '"/><input type="hidden" value="'
			+ rangechart.getContainerId() + '"/></td>')
	$('tr.toPNGRow').append(toImageButton)

}

function updateOpenedFeatureRatioSlider(completionsValues, minValue, maxValue,
		convertMethod, otherParameters) {
	var sliderMainDiv = $('<div><p id="featureRangeAmount"></p></div>');
	var sliderDiv = $('<div></div>');

	sliderDiv.slider({
		range : true,
		min : minValue,
		max : maxValue,
		values : [ minValue, maxValue ],
		slide : function(event, ui) {
			// if (ui.values[0] == ui.values[1]){
			// do not allow the two values to be the same
			// return false;
			// }
			var totalValues = completionsValues.sum(ui.values[0], ui.values[1])
			var totalPercent = Math.round((100 * totalValues)
					/ currentState["totalNumberOfRegions"]);
			$("#featureRangeAmount").text(
					getReadableFeatureText(otherParameters[0] + ui.values[0]
							+ "--" + otherParameters[0] + ui.values[1])
							+ ' for total of '
							+ totalValues
							+ ' hits ('
							+ totalPercent + '%)');
		}
	});
	// alert("2 updated");
	sliderMainDiv.append(sliderDiv);

	var addButton = $('<span title="Filter to this selection" style="margin:5px;">Filter to this selection</span>');
	addButton.button();
	// alert("3 updated");
	addButton.one("click", function(event) {
		// KH June2011 There are two mistakes in this method. One is the
		// otherParameters[1] should be actually 2
		// Also there is a problem between 100 and 110 when having 3 numbers

		event.stopPropagation();
		// make range query
		// var rangePrexix =
		// $('#openedFeatureResults').siblings("input")[0].value;
		var sliderMinValueAny = parseInt($('#openedFeatureResults .ui-slider')
				.slider("values", 0), 10);
		var sliderMaxValueAny = parseInt($('#openedFeatureResults .ui-slider')
				.slider("values", 1), 10);
		var sliderMaxValue = completionsValues.searchSE(sliderMaxValueAny)
		// alert(sliderMaxValueAny+"->"+sliderMaxValue)
		var sliderMinValue = completionsValues.searchLE(sliderMinValueAny)
		// alert(sliderMinValueAny+"->"+sliderMinValue)
		if (otherParameters[2] != 0) {
			// This parameter is meant to show how many digits must there be
			sliderMinValue = "0".repeat(otherParameters[2]
					- (sliderMinValue + "").length)
					+ sliderMinValue;
			sliderMaxValue = "0".repeat(otherParameters[2]
					- (sliderMaxValue + "").length)
					+ sliderMaxValue;
			// alert(sliderMinValue+"--"+sliderMaxValue)
		} else {
			// This is code to support all datasets
			// Must be removed at some point
			if (sliderMinValue < 100
					&& (otherParameters[1] == 3 || otherParameters[1] == 0)) {
				sliderMinValue = "0" + sliderMinValue;
			}
			if (sliderMinValue < 10) {
				sliderMinValue = "0" + sliderMinValue;

			}

			if (sliderMaxValue < 100
					&& (otherParameters[1] == 3 || otherParameters[1] == 0)) {
				sliderMaxValue = "0" + sliderMaxValue;
			}
			if (sliderMaxValue < 10) {
				sliderMaxValue = "0" + sliderMaxValue;
			}
		}
		var rangeQuery = otherParameters[0] + sliderMinValue + "--"
				+ otherParameters[0] + sliderMaxValue;
		// alert(rangeQuery);
		// make range description
		// var rangeDescription=
		// $('#openedFeatureResults').siblings("h4").text()+" is between
		// "+convertMethod(sliderMinValue)+ " and
		// "+convertMethod(sliderMaxValue+1);
		var rangeDescription = getReadableFeatureText(rangeQuery);
		// alert(rangePrexix);
		addResultsRefinementAndUpdate(rangeDescription, rangeQuery, -1, true);
	});
	// alert("4 updated");
	sliderMainDiv.append(addButton);
	// $("#featureRangeAmount").text('Range between ' + convertMethod(minValue)
	// + ' - ' + convertMethod(maxValue+1) + ' for total of ' +
	// completionsValues.sum(0,99)+' hits');
	$('#openedFeatureResults div.featureRangeOrRatioResults').append(
			sliderMainDiv);
	var totalValues = completionsValues.sum(minValue, maxValue);
	var totalPercent = Math.round((100 * totalValues)
			/ currentState["totalNumberOfRegions"]);
	$("#featureRangeAmount").text(
			getReadableFeatureText(otherParameters[0] + minValue + "--"
					+ otherParameters[0] + maxValue)
					+ ' for total of '
					+ totalValues
					+ ' hits ('
					+ totalPercent
					+ '%)');
}
function updateOpenedFeatureRangeSlider(completionsValues, minValue, maxValue,
		convertMethod, otherParameters) {
	// alert("1 updated");
	var sliderMainDiv = $('<div><p id="featureRangeAmount"></p></div>');
	var sliderDiv = $('<div></div>');

	sliderDiv.slider({
		range : true,
		min : minValue,
		max : maxValue,
		values : [ minValue, maxValue ],
		slide : function(event, ui) {
			if (ui.values[0] == ui.values[1]) {
				// do not allow the two values to be the same
				return false;
			}
			var totalValues = completionsValues.sum(ui.values[0], ui.values[1])
			var totalPercent = Math.round((100 * totalValues)
					/ currentState["totalNumberOfRegions"]);
			$("#featureRangeAmount").text(
					getReadableFeatureText(otherParameters[0] + ui.values[0]
							+ "--" + otherParameters[0] + ui.values[1])
							+ ' for total of '
							+ totalValues
							+ ' hits ('
							+ totalPercent + '%)');
		}
	});
	// alert("2 updated");
	sliderMainDiv.append(sliderDiv);

	var addButton = $('<span title="Filter to this selection" style="margin:5px;">Filter to this selection</span>');
	addButton.button();
	// alert("3 updated");
	addButton.one("click", function(event) {
		// alert("Add button clicked");
		event.stopPropagation();
		// make range query
		// var rangePrexix =
		// $('#openedFeatureResults').siblings("input")[0].value;
		var sliderMinValue = parseInt($('#openedFeatureResults .ui-slider')
				.slider("values", 0), 10);
		if (sliderMinValue < 100 && otherParameters[1] == 3) {
			sliderMinValue = "0" + sliderMinValue;
		}
		if (sliderMinValue < 10) {
			sliderMinValue = "0" + sliderMinValue;

		}
		var sliderMaxValue = $('#openedFeatureResults .ui-slider').slider(
				"values", 1);
		if (sliderMaxValue < 100 && otherParameters[1] == 3) {
			sliderMaxValue = "0" + sliderMaxValue;
		}
		if (sliderMaxValue < 10) {
			sliderMaxValue = "0" + sliderMaxValue;
		}
		var rangeQuery = otherParameters[0] + sliderMinValue + "--"
				+ otherParameters[0] + sliderMaxValue;
		// alert(rangeQuery);
		// make range description
		// var rangeDescription=
		// $('#openedFeatureResults').siblings("h4").text()+" is between
		// "+convertMethod(sliderMinValue)+ " and
		// "+convertMethod(sliderMaxValue+1);
		var rangeDescription = getReadableFeatureText(rangeQuery);
		// alert(rangePrexix);
		addResultsRefinementAndUpdate(rangeDescription, rangeQuery, -1, true);
	});
	// alert("4 updated");
	sliderMainDiv.append(addButton);
	// $("#featureRangeAmount").text('Range between ' + convertMethod(minValue)
	// + ' - ' + convertMethod(maxValue+1) + ' for total of ' +
	// completionsValues.sum(0,99)+' hits');
	$('#openedFeatureResults div.featureRangeOrRatioResults').append(
			sliderMainDiv);
	var totalValues = completionsValues.sum(minValue, maxValue);
	var totalPercent = Math.round((100 * totalValues)
			/ currentState["totalNumberOfRegions"]);
	$("#featureRangeAmount").text(
			getReadableFeatureText(otherParameters[0] + minValue + "--"
					+ otherParameters[0] + maxValue)
					+ ' for total of '
					+ totalValues
					+ ' hits ('
					+ totalPercent
					+ '%)');
}
function updateOpenedFeatureJTable(result, otherParameters) {

	updateOpenedFeatureJTableLines(result, otherParameters);

}
function updateOpenedFeatureJTableLines(result, otherParameters) {
	// alert("featureTable 2")
	// CONVERT_BASEQUERY_TO_JSON
	var completionsValues = [];
	var currentTotalNumber = parseInt($('#totalDocuments').text().replace(/,/g,
			""), 10);
	$('tr.noResultsRow').remove();

	// alert("featureTable 3");
	if (otherParameters[0].startsWith("GENENAME:")) {
		// alert("featureTable 3.1g");
		completionsValues = updateOpenedFeatureJTableLinesGENENAMES(result,
				otherParameters);
		// alert("featureTable 3.1g");
	} else if (otherParameters[0].startsWith("GO:ALL")) {
		completionsValues = updateOpenedFeatureJTableLinesGONAMES(result,
				otherParameters);
	} else if (otherParameters[0].startsWith("GO:TERMS")) {
		completionsValues = updateOpenedFeatureJTableLinesTERMS(result,
				otherParameters, "selectGOterm", 5);
	} else if (otherParameters[0].startsWith("OMIM:ALL")) {
		// alert("the listing of the OMIM categories needs to be tested after
		// the index is recomputed")
		completionsValues = updateOpenedFeatureJTableLinesOMIMNAMES(result,
				otherParameters);
		// alert(2+" "+completionsValues.length)
	} else if (otherParameters[0].startsWith("OMIM:TERMS")) {
		// alert(1)
		completionsValues = updateOpenedFeatureJTableLinesTERMS(result,
				otherParameters, "selectOMIMterm", 6);
		// alert(2+" "+completionsValues.length)
	}
	
	// alert("featureTable 4 "+completionsValues.length)
	if (completionsValues.length > 0) {
		// alert("featureTable 5")
		// make the visual effects
		// update the plot
		updateOpenedFeatureJTablePlot(result, completionsValues,
				otherParameters);
		// alert("featureTable 9")

	} else {
		// alert("featureTable 5.1")
		var newTableLine = $('<tr style="width:100%;" class="noResultsRow"><td ></td><td align="left">Your last query returned no results. If you belive this to be a mistake, please save the current session as URL from the button in the top left and send us the link together with a short description at epiexplorer@mpi-inf.mpg.de</td><td align="right"></td></tr>');
		// add the row to the table
		$('#openedFeatureResults tr').remove();
		$('#openedFeatureResults').append(newTableLine);
		// $('#rangeFeaturePlot').remove();
		if (otherParameters[4]) {
			// $('#rangeFeatureAutocompleteSearch').remove(); //
			$('#rangeFeaturePlotMain').children().remove()
			rangePlot = $('<table id="rangeFeaturePlot"><tr><td><div id="rangeFeaturePlotTable" ></div></td><td><div id="rangeFeaturePlotTableCloud" ></div></td></tr><tr class="noResultsRow">Your last query returned no results. If you belive this to be a mistake, please save the current session as URL from the button in the top left and send us the link together with a short description at epiexplorer@mpi-inf.mpg.de </tr></table>');
			$('#rangeFeaturePlotMain').append(rangePlot);
			// var rangePlot = $('<div id="rangeFeaturePlot">No results fit this
			// query</div>');
			// $('#rangeFeaturePlotMain').append(rangePlot);
		} else {
			if (otherParameters[0].startsWith("GO:ALL")) {
				$('#rangeFeaturePlot tr:gt(3)').remove();// remove all but
															// the first row
			} else {
				$('#rangeFeaturePlot tr:gt(0)').remove();// remove all but
															// the first row
			}
			$('#rangeFeaturePlot')
					.append(
							$('<tr><td><div id="rangeFeaturePlotTable" ></div></td><td><div id="rangeFeaturePlotTableCloud" ></div></td></tr>'));
			$('#rangeFeaturePlot')
					.append(
							$('<tr class="noResultsRow"><td colspan="2">Your last query returned no results. If you belive this to be a mistake, please save the current session as URL from the button in the top left and send us the link together with a short description at epiexplorer@mpi-inf.mpg.de </td></tr>'));
		}
	}
}
function updateOpenedFeatureJTableLinesGONAMES(result, otherParameters) {
	var completionsCounts = {}
	$.each(result[3],
			function(completion, numberOfCases) {
				completionsCounts[completion.slice(4)] = parseInt(
						numberOfCases, 10) - 1;
			});

	var completionsValues = [];
	$
			.ajax({
				type : 'POST',
				url : "relay.php",
				async : false,
				dataType : "json",
				data : {
					"type" : "getGeneExtraInfo",
					"genome" : settings["genome"],
					"infoType" : "GO",
					"elements" : Object.keys(completionsCounts)
				// .join(",")
				},
				success : function(result, textStatus, jqXHR) {
					$
							.each(
									result[0],
									function(term, termData) {
										var description = termData[0];
										var title = '<a href="http://amigo.geneontology.org/cgi-bin/amigo/term_details?term='
												+ term
												+ '" target="_blank">'
												+ term + '</a>'
										var geneCount = parseInt(termData[2],
												10);
										var ratio = parseFloat((completionsCounts[term] / geneCount)
												.toPrecision(3));
										var icon = '<div class="CGSicon ui-icon ui-icon-play ui-icon-turnred selectGOName" title="Use this refinement"></div>'
										completionsValues.push([ title,
												completionsCounts[term],
												geneCount, description, ratio,
												icon ]);
									});
				},

				error : function(jqXHR, textStatus, errorThrown) {
					alert("error")
					alert(jqXHR);
					alert(textStatus);
					alert(errorThrown);
				}
			});

	/*
	 * var GOquery = getQueryComplexJoin("
	 * ","Eregion","GOterm",otherParameters[2],otherParameters[3])
	 * answerQuery(currentState["exploreRegionSelected"],GOquery,0,500,false,"rd=0d",function(resultGO){
	 * $.each(resultGO[4],function( title, url ){ var titleParts = title.split("
	 * "); //alert(titleParts) if (completionsCounts[titleParts[1]] !==
	 * undefined){ var description = titleParts.slice(3).join(" "); var title = '<a
	 * href="http://amigo.geneontology.org/cgi-bin/amigo/term_details?term='+titleParts[1]+'"
	 * target="_blank">'+titleParts[1]+'</a>' var geneCount =
	 * parseInt(titleParts[2], 10); var ratio =
	 * parseFloat((completionsCounts[titleParts[1]]/geneCount).toPrecision(3));
	 * var icon = '<div class="CGSicon ui-icon ui-icon-play ui-icon-turnred
	 * selectGOName"></div>'
	 * completionsValues.push([title,completionsCounts[titleParts[1]],geneCount,description,ratio,icon]); }
	 * }); //alert(completionsValues.length) });
	 */
	return completionsValues;
}
function updateOpenedFeatureJTableLinesOMIMNAMES(result, otherParameters) {
	var completionsCounts = {}

	$.each(result[3],
			function(completion, numberOfCases) {
				completionsCounts[completion.slice(7)] = parseInt(
						numberOfCases, 10) - 1;
			});
	var completionsValues = [];
	var completionsValues = [];
	$
			.ajax({
				type : 'POST',
				url : "relay.php",
				async : false,
				dataType : "json",
				data : {
					"type" : "getGeneExtraInfo",
					"genome" : settings["genome"],
					"infoType" : "OMIM",
					"elements" : Object.keys(completionsCounts)
				// .join(",")
				},
				success : function(result) {

					$
							.each(
									result[0],
									function(term, termData) {
										var description = termData[0]
										var title = '<a href="http://www.ncbi.nlm.nih.gov/omim/'
												+ term
												+ '" target="_blank">OMIM ID:'
												+ term + '</a>'
										var geneCount = parseInt(termData[1],
												10);
										var ratio = parseFloat((completionsCounts[term] / geneCount)
												.toPrecision(3));
										var icon = '<div class="CGSicon ui-icon ui-icon-play ui-icon-turnred selectOMIMName" title="Use this refinement"></div>'
										completionsValues.push([ title,
												completionsCounts[term],
												geneCount, description, ratio,
												icon ]);
										// completionsValues.push([title,completionsCounts[titleParts[1]],description,icon]);

									});
					// alert("Query complete");
				}
			});
	/*
	 * var OMIMquery = getQueryComplexJoin("
	 * ","Eregion","omim",otherParameters[2],otherParameters[3])
	 * answerQuery(currentState["exploreRegionSelected"],OMIMquery,0,500,false,"rd=1d&s=MMMS",function(resultGO){
	 * $.each(resultGO[4],function( title, url ){ var titleParts = title.split("
	 * "); //alert(titleParts) if (completionsCounts[titleParts[1]] !==
	 * undefined){ var description = titleParts.slice(3).join(" "); var title = '<a
	 * href="http://www.ncbi.nlm.nih.gov/omim/'+titleParts[1]+'"
	 * target="_blank">OMIM ID:'+titleParts[1]+'</a>' var geneCount =
	 * parseInt(titleParts[2], 10); var ratio =
	 * parseFloat((completionsCounts[titleParts[1]]/geneCount).toPrecision(3));
	 * var icon = '<div class="CGSicon ui-icon ui-icon-play ui-icon-turnred
	 * selectOMIMName"></div>'
	 * completionsValues.push([title,completionsCounts[titleParts[1]],geneCount,description,ratio,icon]);
	 * //completionsValues.push([title,completionsCounts[titleParts[1]],description,icon]); }
	 * }); });
	 */
	return completionsValues;
}
function updateOpenedFeatureJTableLinesGENENAMES(result, otherParameters) {
	var completionsValues = [];
	$
			.each(
					result[4],
					function(title, url) {
						var titleParts = title.split(" ");
						// alert("Gene name")
						if (settings["genome"] == "hg18"){
							var ensLink = '<a href="http://may2009.archive.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g='+titleParts[1]+'" target="_blank">'+titleParts[1]+'</a>'
						}else if (settings["genome"] == "hg19"){
							var ensLink = '<a href="http://www.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g='+titleParts[1]+'" target="_blank">'+titleParts[1]+'</a>'
						}else if (settings["genome"] == "mm9"){
							var ensLink = '<a href="http://www.ensembl.org/Mus_musculus/Gene/Summary?db=core;g='+titleParts[1]+'" target="_blank">'+titleParts[1]+'</a>'
						}
						// alert(ensLink)
						var description = titleParts.slice(3).join(" ");
						var sourceIndex = description.indexOf("[Source:")
						if (sourceIndex > -1) {
							var fulldescription = '<p title="'
									+ description.substring(sourceIndex) + '">'
									+ description.substring(0, sourceIndex)
									+ '</p>'
						} else {
							fulldescription = description;
						}
						var symbol = titleParts[2];
						// if (symbol.length > 0){
						// symbol = '<a
						// href="http://www.genecards.org/index.php?path=/Search/Symbol/'+symbol+'"
						// target="_blank">'+symbol+'</a>'
						// }
						var icon = '<div class="CGSicon ui-icon ui-icon-play ui-icon-turnred selectGeneName" title="Use this refinement"></div>'
						completionsValues.push([ ensLink, symbol,
								fulldescription, icon ]);
					});

	return completionsValues;
}
function termConvert(term) {
	return term.replace(/l/g, "+").replace(/d/g, "-").replace(/u/g, "_")
			.replace(/r/g, "i");

}
function updateOpenedFeatureJTableLinesTERMS(result, otherParameters,
		selectClassName, slicePos) {
	// alert("6.1")
	var completionsValues = [];
	$.each(result[3], function(completion, numberOfCases) {
		//
		var icon = '<div class="CGSicon ui-icon ui-icon-play ui-icon-turnred '
				+ selectClassName
				+ '" title="Use this refinement"><input type="hidden" value="'
				+ completion + '"/>'
		completionsValues.push([
				termConvert(completion.slice(slicePos)).toLowerCase(),
				parseInt(numberOfCases, 10), icon ]);
	});
	// alert("6.2" +completionsValues.length)

	return completionsValues;
}

function updateOpenedFeatureJTablePlot(result, completionsValues,
		otherParameters) {

	$('#openedFeatureResults tr').remove();
	// $('#convertPlotToImage').remove();
	var rangePlot;
	if (otherParameters[4]) {
		// $('#rangeFeaturePlot').remove();
		// $('#rangeFeatureAutocompleteSearch').remove();
		// $('#rangeFeaturePlotPieTable').remove();
		// $('#rangeFeaturePlotTableCloud').remove();
		$('#rangeFeaturePlotMain').children().remove()
		rangePlot = $('<table id="rangeFeaturePlot"><tr><td style="vertical-align:top;"><div id="rangeFeaturePlotTable" ></div></td><td><div id="rangeFeaturePlotTableCloud" ></div></td></tr></table>');
		$('#rangeFeaturePlotMain').append(rangePlot);
	} else {
		if (otherParameters[0].startsWith("GO:ALL")) {
			$('#rangeFeaturePlot tr:gt(4)').remove();// remove all but the
														// search row and the
														// two dropdown rows for
														// min and max genes
		} else {
			$('#rangeFeaturePlot tr:gt(1)').remove();// remove all but the
														// first row
		}
		rangePlot = $('#rangeFeaturePlot');
	}

	result[0] = result[0].replace(/#/g, "%23")
	// alert(result[0]);
	var exportQuery = result[0].replace(/ /g, "::qq::");
	// alert(exportQuery);

	// alert("6.1")
	// google.load('visualization', '1', {packages: ['table']});

	// var originalVisualization = new
	// google.visualization.Table(document.getElementById('rangeFeaturePlotTable'));
	// alert("6.2")
	var data = new google.visualization.DataTable();
	if (otherParameters[0].startsWith("GENENAME:")) {
		// alert("6.2.1")
		data.addColumn('string', 'Ensembl ID');
		data.addColumn('string', 'Gene symbol');
		data.addColumn('string', 'Description');
		data.addColumn('string', '');
		// alert("6.2.2")
	} else if (otherParameters[0].startsWith("GO:ALL")) {
		// alert("6.2.1")
		data.addColumn('string', 'GO');
		data.addColumn('number', 'Number of regions');
		data.addColumn('number', 'Number of genes');
		data.addColumn('string', 'Description');
		data.addColumn('number', 'Ratio');
		data.addColumn('string', '')
		// alert("6.2.2")
	} else if (otherParameters[0].startsWith("GO:TERMS")) {
		// alert("6.2.1")
		data.addColumn('string', 'Word');
		data.addColumn('number', 'Number of GOs with such description');
		data.addColumn('string', '');
		// alert("6.2.2")
	} else if (otherParameters[0].startsWith("OMIM:ALL")) {
		// alert("6.2.1")
		data.addColumn('string', 'OMIM');
		data.addColumn('number', 'Number of regions');
		data.addColumn('number', 'Number of genes');
		data.addColumn('string', 'Description');
		data.addColumn('number', 'Ratio');
		data.addColumn('string', '')
		// alert("6.2.2")
	} else if (otherParameters[0].startsWith("OMIM:TERMS")) {
		// alert("6.2.1")
		data.addColumn('string', 'Word');
		data.addColumn('number', 'Number of OMIMs with such description');
		data.addColumn('string', '');
		// alert("6.2.2")
	}
	// alert("6.2.3")
	data.addRows(completionsValues);
	// alert("6.3")
	var options = {};
	options['page'] = 'enable';
	options['height'] = null;

	options['pageSize'] = 10;
	options['pagingButtonsConfiguration'] = 'auto';

	options['sortColumn'] = 1;
	options['sortAscending'] = false;
	options['showRowNumber'] = true;
	options['allowHtml'] = true;
	options['forceIFrame'] = true;
	// alert("6.4")
	var originalVisualization = new google.visualization.ChartWrapper({
		'chartType' : 'Table',
		'containerId' : 'rangeFeaturePlotTable',
		'dataTable' : data,
		'options' : options
	});
	currentState["activeChart"].push(originalVisualization);
	// originalVisualization.draw(data,options);
	originalVisualization.draw();
	// alert("6.5")
	var autoCompleteCallbackMethod;
	var searchHereLabel = "Search here:";
	if (otherParameters[0].startsWith("GENENAME:")) {
		searchHereLabel = "Search gene symbols";
		var paraGraph = $('<td colspan="2"> Showing info for '
				+ completionsValues.length + ' genes out of ' + result[2]
				+ ' </td>');
		if (options['page'] == 'enable' && completionsValues.length > 10) {
			// if (page == 'enable' && completionsValues.length > 10){
			var showFullTable = $(' <a href="#" onclick="return false"> (Show all '
					+ completionsValues.length + ') </a> ');
			showFullTable.click(function() {
				originalVisualization.setOption('page', null)
				originalVisualization.setOption('height', "500px");
				originalVisualization.draw();
				$(this).remove();
			});
			paraGraph.append(showFullTable);
		}
		var showAllLink = false;
		$('#rangeFeaturePlotTableCloud').children().remove();
		$('#rangeFeaturePlotTableCloud')
				.append(
						$('<a href="relay.php?type=exportGenesAndSendBack&exportType=TABLE&regiontype='
								+ currentState["exploreRegionSelected"]
								+ '&query='
								+ exportQuery
								+ '" target="_blank"> Export to table</a><br\><br\>'));
		$('#rangeFeaturePlotTableCloud')
				.append(
						$('<a href="relay.php?type=exportGenesAndSendBack&exportType=ENSEMBL&regiontype='
								+ currentState["exploreRegionSelected"]
								+ '&query='
								+ exportQuery
								+ '" target="_blank"> Export Ensembl identfiers</a><br\><br\>'));
		$('#rangeFeaturePlotTableCloud')
				.append(
						$('<a href="relay.php?type=exportGenesAndSendBack&exportType=SYMBOL&regiontype='
								+ currentState["exploreRegionSelected"]
								+ '&query='
								+ exportQuery
								+ '" target="_blank"> Export gene symbols</a><br\><br\>'));
		// paraGraph.append(showAllLink)
		var newrow = $('<tr></tr>')
		newrow.append(paraGraph)
		rangePlot.append(newrow);
		autoCompleteCallbackMethod = autoCompleteCallbackGene;
		showInfoPlot("genes");
	} else if (otherParameters[0].startsWith("GO:ALL")) {
		searchHereLabel = "Search GO descriptions";
		var tc = new TermCloud(document
				.getElementById('rangeFeaturePlotTableCloud'));
		tc.draw(data, {
			'numberColumnIndex' : 4,
			'wordColumnIndex' : 3,
			'linkColumnIndex' : 0,
			'target' : '_blank'
		});
		var paraGraph = $('<td colspan="2">Showing top '
				+ completionsValues.length
				+ ' GOs (by number of regions) out of '
				+ numberWithCommas(result[1]) + ' </td>');
		// if (page == 'enable' && completionsValues.length > 10 ){
		if (options['page'] == 'enable' && completionsValues.length > 10) {
			var showFullTable = $(' <a href="#" onclick="return false"> (Show all '
					+ completionsValues.length + ') </a> ');
			showFullTable.click(function() {
				originalVisualization.setOption('page', null)
				originalVisualization.setOption('height', "500px");
				originalVisualization.draw();
				$(this).remove();
			});
			paraGraph.append(showFullTable);
		}
		var showAllLink = $(' <a href="relay.php?type=exportGOsAndSendBack&regiontype='
				+ currentState["exploreRegionSelected"]
				+ '&query='
				+ exportQuery + '" target="_blank">Export all</a> ');
		// paraGraph.append(showAllLink);
		var newrow = $('<tr></tr>')
		newrow.append(paraGraph)
		rangePlot.append(newrow);
		if (otherParameters[4]) {
			var query = getQueryComplexJoin(" ", "Eregion", "gGONG:*", "gGO:*",
					"GOterm gGONG:000--gGONG:999")
			answerQuery(
					currentState["exploreRegionSelected"],
					query,
					1000,
					0,
					false,
					"rw=3a",
					function(result) {
						// alert("Successfull result")
						var completionsValues = []
						var minValue = 999;
						var maxValue = 0;
						$.each(result[3], function(index, value) {
							value = parseInt(value, 10);
							var v = parseInt(index.slice(6), 10);
							completionsValues[v] = value;
							if (minValue > v) {
								minValue = v;
							}
							if (maxValue < v) {
								maxValue = v;
							}
						});

						if (completionsValues.length > 0 && minValue < maxValue) {
							// alert("value sprocessed")
							function updatePlotFromValues() {
								var minValue = $(
										'select.minGenesOFGO option:selected')
										.val();
								var maxValue = $(
										'select.maxGenesOFGO option:selected')
										.val();

								if (minValue > maxValue) {
									alert("The minimum value cannot be smaller than the maximum value")
									// $('select.minGenesOFGO').select("001")
									$('select.minGenesOFGO').val("001");
									$('select.maxGenesOFGO').val("450");
									return false;
								}
								$("#exampleAutocomplete").val("")

								var complexTerm = "GOterm gGONG:" + minValue
										+ "--gGONG:" + maxValue;
								var otherParameters = [ "GO:ALL:", "", "gGO:*",
										complexTerm, false ]
								var query = getQueryComplexJoin(" ", "Eregion",
										otherParameters[1], otherParameters[2],
										otherParameters[3])
								updateOpenedFeatureCore("featureTable",
										currentState["exploreRegionSelected"],
										query, 100, 0, "rw=1d",// "rw=0d%26s=MMMS",
										otherParameters);
							}
							var sliderRow = $('<tr></tr>');
							var sliderCell = $('<td></td>');
							var sliderCellTable = $('<table></table>');
							var sliderCellTableRow1 = $('<tr></tr>');

							var slidercellMin = $('<td style="padding-left:0px"><label>Exclude GO terms matching less than N genes</label></td>');

							sliderRow.append(sliderCell)
							sliderCell.append(sliderCellTable)
							sliderCellTable.append(sliderCellTableRow1)
							sliderCellTableRow1.append(slidercellMin)

							var selectMinCell = $('<td style="padding-left:0px"></td>');
							var selectMin = $('<select class="minGenesOFGO"></select>');
							selectMinCell.append(selectMin)
							sliderCellTableRow1.append(selectMinCell)
							selectMin
									.append($('<option value="001" selected="selected">1 (Min)</option>'))
							selectMin
									.append($('<option value="005">5</option>'))
							selectMin
									.append($('<option value="110">10</option>'))
							selectMin
									.append($('<option value="150">50</option>'))
							selectMin
									.append($('<option value="210">100</option>'))
							selectMin
									.append($('<option value="250">500</option>'))
							selectMin
									.append($('<option value="310">1,000</option>'))
							selectMin
									.append($('<option value="350">5,000</option>'))
							selectMin
									.append($('<option value="450">Max</option>'))
							var slidercellMax = $('<td style="padding-left:0px"><label>Exclude GO terms matching more than N genes</label></td>');
							var sliderCellTableRow2 = $('<tr></tr>');
							sliderCellTable.append(sliderCellTableRow2)
							sliderCellTableRow2.append(slidercellMax)
							var selectMaxCell = $('<td style="padding-left:0px"></td>');
							var selectMax = $('<select class="maxGenesOFGO"></select>');
							selectMaxCell.append(selectMax)
							sliderCellTableRow2.append(selectMaxCell)
							selectMax
									.append($('<option value="001">1 (min)</option>'))
							selectMax
									.append($('<option value="005">5</option>'))
							selectMax
									.append($('<option value="110">10</option>'))
							selectMax
									.append($('<option value="150">50</option>'))
							selectMax
									.append($('<option value="210">110</option>'))
							selectMax
									.append($('<option value="250">510</option>'))
							selectMax
									.append($('<option value="310">1,100</option>'))
							selectMax
									.append($('<option value="350">5,100</option>'))
							selectMax
									.append($('<option value="450" selected="selected">30,000 (Max)</option>'))
							sliderRow.append($('<td/>'))
							rangePlot.prepend(sliderRow);

							$(selectMin).change(updatePlotFromValues);
							$(selectMax).change(updatePlotFromValues);
							// var sliderRow = $('<tr><td><p>Slide below to
							// refine the GOs</p><div id="termSlider"></div><a
							// href="#" onclick="return false"
							// id="updateGOSliderButton"></a></td><td></td></tr>')
							// rangePlot.prepend(sliderRow);

							// addTermsSlider(minValue,maxValue,completionsValues,"gGONG:","termSlider","updateGOSliderButton")
							/*
							 * $("#updateGOSliderButton").click(function(){
							 * $("#exampleAutocomplete").val("") var
							 * sliderMinValueAny = $('#termSlider
							 * .ui-slider').slider("values",0)+""; var
							 * sliderMaxValueAny = $('#termSlider
							 * .ui-slider').slider("values",1)+""; var
							 * complexTerm = "GOterm
							 * gGONG:"+"0".repeat(3-sliderMinValueAny.length)+sliderMinValueAny+"--gGONG:"+"0".repeat(3-sliderMaxValueAny.length)+sliderMaxValueAny;
							 * var otherParameters =
							 * ["GO:ALL:","","gGO:*",complexTerm,false] var
							 * query = getQueryComplexJoin("
							 * ","Eregion",otherParameters[1],otherParameters[2],otherParameters[3])
							 * updateOpenedFeatureCore("featureTable",
							 * currentState["exploreRegionSelected"], query,
							 * 100, 0, "rw=1d",//"rw=0d%26s=MMMS",
							 * otherParameters); //alert("0810 end update") });
							 */
						}
					})
		}

		autoCompleteCallbackMethod = autoCompleteCallbackGOcategory;
		showInfoPlot("goterms");
	} else if (otherParameters[0].startsWith("GO:TERMS")) {
		searchHereLabel = "Search words in GO terms";
		// alert("Before adding term cloud")
		var tc = new TermCloud(document
				.getElementById('rangeFeaturePlotTableCloud'));

		tc.draw(data, null);
		// alert("drawn")
		var paraGraph = $('<td colspan="2">Showing the '
				+ completionsValues.length + ' most common words from the '
				+ result[2] + ' GO terms </td>');
		// if (page == 'enable' && completionsValues.length > 10){
		if (options['page'] == 'enable' && completionsValues.length > 10) {
			var showFullTable = $(' <a href="#" onclick="return false"> (Show all '
					+ completionsValues.length + ') </a> ');
			showFullTable.click(function() {
				originalVisualization.setOption('page', null)
				originalVisualization.setOption('height', "500px");
				originalVisualization.draw();
				$(this).remove();
			});
			paraGraph.append(showFullTable);
		}

		var showAllLink = $('<a href="relay.php?type=exportGOTermsAndSendBack&regiontype='
				+ currentState["exploreRegionSelected"]
				+ '&query='
				+ exportQuery + '" target="_blank"> Export all </a>');
		// paraGraph.append(showAllLink);
		var newrow = $('<tr></tr>')
		newrow.append(paraGraph)
		rangePlot.append(newrow);
		autoCompleteCallbackMethod = autoCompleteCallbackGOterm;
		// alert("6 "+otherParameters[4])
		showInfoPlot("gowords");
	} else if (otherParameters[0].startsWith("OMIM:ALL")) {
		searchHereLabel = "Search OMIM descriptions";
		var tc = new TermCloud(document
				.getElementById('rangeFeaturePlotTableCloud'));
		tc.draw(data, {
			'numberColumnIndex' : 4,
			'wordColumnIndex' : 3,
			'linkColumnIndex' : 0,
			'target' : '_blank'
		});
		var paraGraph = $('<td colspan="2">Showing top '
				+ completionsValues.length
				+ ' OMIMs (by number of regions) out of '
				+ numberWithCommas(result[1]) + ' </td>');
		// if (page == 'enable' && completionsValues.length > 10 ){
		if (options['page'] == 'enable' && completionsValues.length > 10) {
			var showFullTable = $(' <a href="#" onclick="return false"> (Show all '
					+ completionsValues.length + ') </a> ');
			showFullTable.click(function() {
				originalVisualization.setOption('page', null)
				originalVisualization.setOption('height', "500px");
				originalVisualization.draw();
				$(this).remove();
			});
			paraGraph.append(showFullTable);
		}
		var showAllLink = $(' <a href="relay.php?type=exportOMIMsAndSendBack&regiontype='
				+ currentState["exploreRegionSelected"]
				+ '&query='
				+ exportQuery + '" target="_blank">Export all</a> ');
		showAllLink = false;// Not yet implemented
		// paraGraph.append(showAllLink);
		var newrow = $('<tr></tr>')
		newrow.append(paraGraph)
		rangePlot.append(newrow);
		autoCompleteCallbackMethod = autoCompleteCallbackOMIMcategory;
		showInfoPlot("omimterms");
	} else if (otherParameters[0].startsWith("OMIM:TERMS")) {
		searchHereLabel = "Search words in OMIM terms";
		// alert("Before adding term cloud")
		var tc = new TermCloud(document
				.getElementById('rangeFeaturePlotTableCloud'));
		tc.draw(data, null);
		// alert("drawn")

		var paraGraph = $('<td colspan="2">Showing the '
				+ completionsValues.length + ' most common words from the '
				+ result[2] + ' OMIM terms </td>');
		// if (page == 'enable' && completionsValues.length > 10){
		if (options['page'] == 'enable' && completionsValues.length > 10) {
			var showFullTable = $(' <a href="#" onclick="return false"> (Show all '
					+ completionsValues.length + ') </a> ');
			showFullTable.click(function() {
				originalVisualization.setOption('page', null)
				originalVisualization.setOption('height', "500px");
				originalVisualization.draw();
				$(this).remove();

			});
			paraGraph.append(showFullTable);
		}

		var showAllLink = $('<a href="relay.php?type=exportOMIMTermsAndSendBack&regiontype='
				+ currentState["exploreRegionSelected"]
				+ '&query='
				+ exportQuery + '" target="_blank"> Export all </a>');
		showAllLink = false;// Not yet implemented
		// paraGraph.append(showAllLink);
		var newrow = $('<tr></tr>')
		newrow.append(paraGraph)
		rangePlot.append(newrow);
		autoCompleteCallbackMethod = autoCompleteCallbackOMIMterm;
		// alert("6 "+otherParameters[4])
		showInfoPlot("omimwords");
	}
	if (otherParameters[4]) {
		var autocompleteSearchRow = $('<tr id="rangeFeatureAutocompleteSearch"></tr>');
		var rowFull = $('<td><label style="float:left;">'
				+ searchHereLabel
				+ '</label><input id="exampleAutocomplete" type="text" size="30" style="float:left;"/></td>')

		if (otherParameters[0].startsWith("GENENAME:")) {
			var selectCurrentPrefix = $('<div class="ui-icon ui-icon-play ui-icon-turnred selectGeneSymbol" style="float:left;"></div>')

			rowFull.append(selectCurrentPrefix)
		}

		autocompleteSearchRow.append(rowFull)
		var secondTd = $('<td></td>')

		if (showAllLink) {
			secondTd.append(showAllLink);
		}
		autocompleteSearchRow.append(secondTd)
		// alert("8")

		rangePlot.prepend(autocompleteSearchRow);
		$("#exampleAutocomplete").autocomplete({
			source : autoCompleteCallbackMethod,
			delay : 400,
			minLength : 0
		});
		// alert("9")
	}

	$('#rangeFeaturePlotMain').show();

}

function addTermsSlider(minValue, maxValue, completionsValues, prefix,
		termSliderContainerID, termSliderTextContainerID) {
	var sliderDiv = $('<div></div>');
	// alert(1)
	sliderDiv.slider({
		range : true,
		min : minValue,
		max : maxValue,
		values : [ minValue, maxValue ],
		slide : function(event, ui) {

			// do not allow the two values to be the same
			// return false;
			// }
			// $("#termSliderText").text(getReadableFeatureText(prefix+ui.values[0]+"--"+prefix+ui.values[1])
			// + ' for total of ' +
			// completionsValues.sum(ui.values[0],ui.values[1])+' hits');
			if ((ui.values[0] < 10 || ui.values[0] > 109)
					&& (ui.values[1] < 10 || ui.values[1] > 109)) {
				$("#" + termSliderTextContainerID).text(
						"Show only the "
								+ completionsValues.sum(ui.values[0],
										ui.values[1])
								+ " "
								+ getReadableFeatureText(prefix + ui.values[0]
										+ "--" + prefix + ui.values[1]));
			}
		}
	});
	// alert("2 updated");
	// $("#termSlider").append(sliderDiv);
	$("#" + termSliderContainerID).append(sliderDiv);
}
function updateOpenedFeatureRegionsList(result, otherParameters) {
	// $('#rangeFeaturePlot').remove();
	$('#rangeFeaturePlotMain').children().remove()
	var rangePlot = $('<div id="rangeFeaturePlot"></div>');
	$('#rangeFeaturePlotMain').append(rangePlot);
	showInfoPlot("nodescription")
	rangePlot
			.append($('<div id="rangeFeaturePlotTable" style="float:left;"></div>'));
	// remove the progress image
	var dataLines = [];
	var count = 0;
	var toplineParts = null;
	$.each(result[4], function(index, value) {
		var titleParts = index.split("_");
		if (toplineParts == null) {
			toplineParts = titleParts;
		}
		var url = "http://genome.ucsc.edu/cgi-bin/hgTracks?db="
				+ settings["genome"] + "&position="
				+ titleParts[titleParts.length - 3] + "%3A"
				+ titleParts[titleParts.length - 2] + "-"
				+ titleParts[titleParts.length - 1];
		dataLines.push([ '<a href="' + url + '" target=\"_blank\">UCSC</a>',
				titleParts[titleParts.length - 3],
				parseInt(titleParts[titleParts.length - 2], 10),
				parseInt(titleParts[titleParts.length - 1], 10) ])
		count = count + 1;
	});
	// alert(dataLines.length + " "+dataLines[0])
	// var originalVisualization = new
	// google.visualization.Table(document.getElementById('rangeFeaturePlotTable'));

	// alert("6.2")
	var data = new google.visualization.DataTable();

	// alert("6.2.1")
	data.addColumn('string', 'URL');
	data.addColumn('string', 'chromosome');
	data.addColumn('number', 'start');
	data.addColumn('number', 'end');
	// alert("6.2.2")

	data.addRows(dataLines);
	// data.addRows([["test","test",11,22],["test2","test2",11,22]]);
	// alert("6.3")
	var options = {};
	options['page'] = 'enable';
	options['sortColumn'] = 1;
	options['sortAscending'] = false;
	options['allowHtml'] = true;
	options['width'] = "500px";
	options['forceIFrame'] = true;
	var originalVisualization = new google.visualization.ChartWrapper({
		'chartType' : 'Table',
		'containerId' : 'rangeFeaturePlotTable',
		'dataTable' : data,
		'options' : options
	});
	currentState["activeChart"].push(originalVisualization);
	// originalVisualization.draw(data,options);
	originalVisualization.draw();
	// alert("6.4")
	var query = getQuery("::qq::", "Eregion", "main");
	var regiontype = currentState["exploreRegionSelected"];
	var exportLinksDiv = $('<div id="exportLinksDiv"></div>')
	rangePlot.append(exportLinksDiv);
	exportLinksDiv
			.append($("<a href='relay.php?type=exportRegionsAndSendBack&exportType=URL&regiontype="
					+ regiontype
					+ "&query="
					+ query
					+ "&genome="
					+ settings["genome"]
					+ "' target='_blank'>Export all</a><br/><br/>"))
	exportLinksDiv
			.append($("<a href='relay.php?type=exportRegionsAndSendBack&exportType=TEXTFILE&regiontype="
					+ regiontype
					+ "&query="
					+ query
					+ "&genome="
					+ settings["genome"]
					+ "' target='_blank'>Download as text file</a><br/><br/>"))
	var ucscLink = "http://genome.ucsc.edu/cgi-bin/hgTracks?";
	ucscLink = ucscLink + "db=" + settings["genome"]
	ucscLink = ucscLink + "&position=" + toplineParts[toplineParts.length - 3]
			+ "%3A" + toplineParts[toplineParts.length - 2] + "-"
			+ toplineParts[toplineParts.length - 1]
	ucscLink = ucscLink
			+ "&hgt.customText="
			+ encodeURIComponent("http://epiexplorer.mpi-inf.mpg.de/relay.php?type=exportRegionsAndSendBack&exportType=UCSC&regiontype="
					+ regiontype
					+ "&query="
					+ query
					+ "&genome="
					+ settings["genome"])
	exportLinksDiv
			.append($("<a href='"
					+ ucscLink
					+ "' target='_blank'>Export as custom track in UCSC Genome Browser</a><br/><br/>"))

	if (settings["genome"] != "hg18") {
		/*
		 * if(settings["genome"] == "hg18" || settings["genome"] == "hg19"
		 * ||settings["genome"] == "mm9"){ var ensemblLink = "";
		 * if(settings["genome"] == "hg18"){ ensemblLink = ensemblLink +
		 * "http://may2009.archive.ensembl.org/Homo_sapiens/" }else
		 * if(settings["genome"] == "hg19"){ ensemblLink = ensemblLink +
		 * "http://www.ensembl.org/Homo_sapiens/" }else if(settings["genome"] ==
		 * "mm9"){ ensemblLink = ensemblLink +
		 * "http://www.ensembl.org/Mus_musculus/" } ensemblLink = ensemblLink +
		 * "Location/View?"; ensemblLink = ensemblLink +
		 * "r="+toplineParts[toplineParts.length-3].slice(3)+"%3A"+toplineParts[toplineParts.length-2]+"-"+toplineParts[toplineParts.length-1]+";";
		 * ensemblLink = ensemblLink +
		 * "contigviewbottom=url:"+encodeURIComponent("http://epiexplorer.mpi-inf.mpg.de/relay.php?type=exportRegionsAndSendBack&exportType=UCSC&regiontype="+regiontype+"&query="+query)
		 * exportLinksDiv.append($("<a href='"+ensemblLink+"'
		 * target='_blank'>Export as custom track in Ensembl Genome Browser</a><br/><br/>"))
		 * }else{ alert("Ensembl export to this genome assembly is not yet
		 * supported"); }
		 * 
		 * //http://www.ensembl.org/info/website/upload/sample_files/example.bed=half_height
		 * 
		 */
		exportLinksDiv
				.append($("<a href='relay.php?type=exportRegionsAndSendBack&exportType=ENSEMBL&regiontype="
						+ regiontype
						+ "&query="
						+ query
						+ "&genome="
						+ settings["genome"]
						+ "' target='_blank'>Export as custom track in Ensembl Genome Browser</a><br/><br/>"))
	}
	exportLinksDiv
			.append($("<a href='relay.php?type=exportRegionsAndSendBack&exportType=GALAXY&regiontype="
					+ regiontype
					+ "&query="
					+ query
					+ "&genome="
					+ settings["genome"]
					+ "' target='_blank'>Export to Galaxy</a><br/><br/>"))
	exportLinksDiv
			.append($("<a href='relay.php?type=exportRegionsAndSendBack&exportType=HYPERBROWSER&regiontype="
					+ regiontype
					+ "&query="
					+ query
					+ "&genome="
					+ settings["genome"]
					+ "' target='_blank'>Export to the Genomic HyperBrowser</a><br/><br/>"))

	if (count < 200) {
		rangePlot.append($("<p style='clear:both;'>Listing all " + count
				+ " regions</p>"))
	} else {
		rangePlot.append($("<p style='clear:both;'>Listing " + count
				+ " regions out of " + result[2] + "</p>"))
	}

	if (count > 10) {
		var showFullTable = $(' <a href="#" onclick="return false"> Show full table </a> ');
		showFullTable.click(function() {

			// options['page'] = null;
			originalVisualization.setOption('page', null)
			// options['height'] = "350px";
			originalVisualization.setOption('height', "350px")
			// originalVisualization.draw(data,options);
			originalVisualization.draw();
			showFullTable.remove();
		});
		rangePlot.append(showFullTable);
	}
	$('#rangeFeaturePlotMain').show();
}
function updateOpenedFeatureTable(result, otherParameters) {
	// CONVERT_BASEQUERY_TO_JSON
	// var lines = msg.split("\n");
	// for every completions in the results
	var queryPrefix = otherParameters[0].replace(/OVERLAP/g,
			settings["overlap"]).replace(/TISSUE/g, settings["tissue"]);
	updateOpenedFeatureTableLines(result, queryPrefix, otherParameters, true);

}
function updateOpenedFeatureTableLines(result, queryPrefix, otherParameters,
		updateReference) {
	updateReference = updateReference
			&& (currentState["referenceQuery"]["genome"] != "");
	// CONVERT_BASEQUERY_TO_JSON
	var completionsValues = [];
	var zoomInEvents = {};
	var keys = [];
	var values = [];
	var isNegativeQuery = queryPrefix.charAt(0) == "-";
	var currentTotalNumber = parseInt($('#totalDocuments').text().replace(/,/g,
			""), 10);
	var hasAdvancedVisualization = $('#openedFeatureResults').siblings(
			'input:hidden').length == 4;

	var completions = []
	if (updateReference) {
		// alert("start processing reference")
		/* REFERENCE UPDATE */
		if (isNegativeQuery) {
			referenceQuery = currentState["referenceQuery"]["query"].replace(
					/BASEREFQUERY/g, queryPrefix.substr(1) + "*")
		} else {
			referenceQuery = currentState["referenceQuery"]["query"].replace(
					/BASEREFQUERY/g, queryPrefix + "*")
		}
		/* REFERENCE UPDATE */
		answerQuery(
				currentState["referenceQuery"]["dataset"],
				referenceQuery,
				1500,
				0,
				false,
				"",
				function(resultRef) {
					// alert("start processing reference range values")
					// currentState["referenceQuery"]["values"] = {};
					$
							.each(
									resultRef[3],
									function(completion, value) {
										// alert("start "+rn+" "+nwc)
										var nwc = parseInt(value, 10);
										// if (isNegativeQuery){
										// currentState["referenceQuery"]["values"][completion]
										// =
										// currentState["referenceQuery"]["totalNumber"]
										// - nwc;
										// }else{
										currentState["referenceQuery"]["values"][completion] = nwc;
										// }
										completions.push(completion)
									});
				});

	}

	$.each(result[3], function(completion, numberOfCases) {
		completions.push(completion)
	})
	completions.sort()
	// CONVERT_BASEQUERY_TO_JSON $.each(lines,function( index, value ){
	if (completions.length == 0 && isNegativeQuery){
		completions.push(queryPrefix.substr(1));
	}
	var lastValue = null;
	$
			.each(
					completions,
					function(i, completion) {
						if (lastValue == completion) {
							return;
						}
						lastValue = completion;
						var numberOfCases = 0;
						if (result[3][completion] !== undefined) {
							numberOfCases = result[3][completion]
						}
						var refNumberOfCases = 0;
						if (updateReference
								&& currentState["referenceQuery"]["values"][completion] !== undefined) {
							refNumberOfCases = currentState["referenceQuery"]["values"][completion];
						}

						var complKey;
						// alert("Table lines completion for"+completion)
						if (overlapLabels[completion] != undefined) {
							// alert("1")
							if (queryPrefix.charAt(0) == "-") {
								// alert("1.1")
								complKey = "without "
										+ overlapLabels[completion];
							} else {
								// alert("1.2")
								complKey = overlapLabels[completion];
							}
						} else if (queryPrefix.length > 0
								&& completion.startsWith(queryPrefix)) {
							// alert("2")
							// starts with the prefix: hence non negative
							var potentialPrefix = completion
									.substr(queryPrefix.length)
							if (potentialPrefix.length > 0) {
								// alert("2.1")
								// if the prefix is not the full cut it
								complKey = potentialPrefix;
							} else {
								// leave it
								// alert("2.3")
								complKey = getReadableFeatureText(completion);
							}
						} else {
							// alert("3")
							// does not start with the prefix
							if (queryPrefix.charAt(0) == "-") {
								// alert("3.1")
								// if it is negative
								if (completion
										.startsWith(queryPrefix.substr(1))) {
									// alert("3.1.1")
									// make sure
									complKey = "without "
											+ completion
													.substr(queryPrefix.length - 1);
								} else {
									// alert("3.1.2")
									// we down't know
									complKey = completion;
								}
							} else {
								// alert("3.2")
								// not negative so leave it
								complKey = getReadableFeatureText(completion);
							}
						}

						var nwc;
						var rwc;
						if (isNegativeQuery) {
							nwc = currentTotalNumber
									- parseInt(numberOfCases, 10);
							if (updateReference) {
								rwc = currentState["referenceQuery"]["totalNumber"]
										- parseInt(refNumberOfCases, 10);
							}
							completionsValues[complKey] = [ nwc, rwc ];
						} else {
							nwc = numberWithCommas(numberOfCases);
							completionsValues[complKey] = [
									parseInt(numberOfCases, 10),
									refNumberOfCases ];
						}

						keys.push(complKey);
						values.push(completionsValues[complKey]);
						if (hasAdvancedVisualization) {
							var newTableLine = $('<tr class="listResults" style="width:100%;"><td align="left" title="Click to select only these regions">'
									+ complKey
									+ '</td><td align="right" title="Click to select only these regions">'
									+ nwc
									+ '</td><td class="zoomINAdvanced" title="See the full distribution ..."><span class="ui-icon ui-icon-zoomin ui-icon-turnred" style="float:right;"/></td></tr>');
						} else {
							var newTableLine = $('<tr class="listResults" style="width:100%;"><td class="ui-icon ui-icon-triangle-1-e" style="float:left;padding:0;" title=""></td><td align="left" title="Click to select only these regions">'
									+ complKey
									+ '</td><td align="right" title="Click to select only these regions">'
									+ nwc + '</td></tr>');
						}

						// add the action if clicked
						if (isNegativeQuery) {

							newTableLine.one("click", function(event) {
								event.stopPropagation();
								addResultsRefinementAndUpdate("", "-"
										+ completion, -1, true);
							});
							// add the row to the table
							$('#openedFeatureResults').prepend(newTableLine);
						} else {
							var hiddenInputs = $('#openedFeatureResults')
									.siblings('input:hidden');
							if (hiddenInputs.length == 4) {
								var zoominfunction = function() {
									var hiddenInputs = $(
											'#openedFeatureResults').siblings(
											'input:hidden');
									if (hiddenInputs.length == 4) {
										var subFeatureType = hiddenInputs[3].value;
										var subQueryPrefix = hiddenInputs[2].value;
										var mainQueryPart = completion;
										$
												.each(
														mainQueryPart
																.split(":"),
														function(index11,
																value11) {
															subQueryPrefix = subQueryPrefix
																	.replace(
																			"POS"
																					+ index11
																					+ "SOP",
																			value11);
														});
										// delete any old sub slider
										$('.featureRangeOrRatioResults')
												.remove();
										// create a new slider placeholder
										$(
												'<tr><td COLSPAN="3"><div class="featureRangeOrRatioResults"></div></td></tr>')
												.insertAfter(newTableLine);
										updateOpenedFeatureCore(
												subFeatureType,
												currentState["exploreRegionSelected"],
												getQuery(" ", subQueryPrefix
														+ "*", "main"), 100, 0,
												"", [ subQueryPrefix, 2, 0 ]);
									}
								};
								newTableLine.children('.zoomINAdvanced').click(
										function(event) {
											event.stopPropagation();
											zoominfunction();
										});
								zoomInEvents[complKey] = zoominfunction
							}
							newTableLine.one("click", function(event) {
								event.stopPropagation();
								addResultsRefinementAndUpdate("", completion,
										nwc, true);
							});
							// add the row to the table
							$('#openedFeatureResults').append(newTableLine);
						}
					});

	if (keys.length > 0) {
		// make the visual effects
		// if (keys.length > 1){
		// update the plot
		// updateOpenedFeatureTablePlot(completionsValues,keys,values);
		updateOpenedFeatureTablePlotGoogle(completionsValues, keys, values,
				zoomInEvents, otherParameters, updateReference);
		// }
	} else {
		// add the row to the table
		$('#rangeFeaturePlotMain').children().remove()
		$('#rangeFeaturePlotMain').show();

		$('#rangeFeaturePlotMain')
				.append(
						$('<table id="rangeFeaturePlotTable"><tr style="width:100%;"><td align="left">No regions fit this query</td><td></td></tr></table>'))

	}
}
function updateOpenedFeatureTablePlotGoogle(completionsValues, keys, values,
		zoomInEvents, otherParameters, updateReference) {
	// alert(currentState["featureCurrentVisualization"])
	// $('#rangeFeaturePlot').remove();
	// $('#convertPlotToImage').remove();
	$('#rangeFeaturePlotMain').children().remove()
	$('#rangeFeaturePlotMain').show();
	showInfoPlot("overlaptable")

	$('#rangeFeaturePlotMain')
			.append(
					$('<table id="rangeFeaturePlotTable"><tr><td colspan="2"><div id="rangeFeaturePlot"></div></td></tr></table>'))
	if (otherParameters[0].search("OVERLAP") > -1) {
		$('#rangeFeaturePlotTable')
				.append(
						'<tr><td>Select overlap criterion:</td><td><select id="overlapSelect"><option value="Eoverlaps">Any overlap (at least 1bp)</option><option value="Eoverlaps10p">Medium overlap (at least 10%)</option><option value="Eoverlaps50p">Strong overlap (at least 50%)</option></select></td></tr>')
		$('#overlapSelect').val(settings["overlap"]);
		// $('select#overlapSelect').selectmenu();
	}
	// $('#tissueSelect').remove();
	if (otherParameters[0].search("TISSUE") > -1) {
		$('#rangeFeaturePlotTable')
				.append(
						'<tr><td>Select tissue:</td><td><select id="tissueSelect"></select></td></tr>');
		$.each(settings["defaultTissues"], function(index, tissueKey) {
			$('#tissueSelect').append(
					$('<option value="' + tissueKey + '">'
							+ getTissueDescription(tissueKey) + '</option>'))
		});
		$('#tissueSelect').val(settings["tissue"]);
		// $('select#tissueSelect').selectmenu();
	}
	var heightChart = 400;
	var widthChart = 800;
	if (keys.length < 4) {
		widthChart = 250 * keys.length;
	}
	var visualizationData;
	var options = {
		width : widthChart,
		height : heightChart,
		// title: 'FILLIN',
		focusTarget : 'category',
		colors : [ '#FA9627', '#999999' ],
		legend : {position:'top',
				  textStyle : textStyles["legend"]},
		hAxis : {
			maxAlternation : 3,
			titleTextStyle : textStyles["axisTitle"],
			textStyle : textStyles["axisText"],
			// slantedText:true,
			// slantedTextAngle:20,
			showTextEvery : 1
		},
		vAxis : {
			title : "Percent of overlapping regions",
			titleTextStyle : textStyles["axisTitle"],
			textStyle : textStyles["axisText"],
			format : '#,###.##%',
			minValue : 0,
			maxValue : 1
		},
		chartArea : {
			// top:26,
			left : 60,
			width : widthChart - 60
		},
		forceIFrame: true
	}
	if (updateReference) {
		visualizationData = {
			'cols' : [
					{
						'label' : 'Overlap',
						'type' : 'string'
					},
					{
						'label' : 'Current selection ('
								+ numberWithCommas(currentState["totalNumberOfRegions"])
								+ ')',
						'type' : 'number'
					},
					{
						'label' : 'Control set ('
								+ numberWithCommas(currentState["referenceQuery"]["totalNumber"])
								+ ')',
						'type' : 'number'
					} ],
			'rows' : []
		};
		$
				.each(
						keys,
						function(index, key) {
							visualizationData['rows']
									.push({
										'c' : [
												{
													'v' : key,
													'f' : key
												},
												{
													'v' : (values[index][0] / currentState["totalNumberOfRegions"]),
													'f' : values[index][0] + ''
												},
												{
													'v' : (values[index][1] / currentState["referenceQuery"]["totalNumber"]),
													'f' : values[index][1] + ''
												} ]
									})
						})
	} else {
		visualizationData = {
			'cols' : [
					{
						'label' : 'Overlap',
						'type' : 'string'
					},
					{
						'label' : 'Current selection ('
								+ numberWithCommas(currentState["totalNumberOfRegions"])
								+ ')',
						'type' : 'number'
					} ],
			'rows' : []
		};
		$
				.each(
						keys,
						function(index, key) {
							visualizationData['rows']
									.push({
										'c' : [
												{
													'v' : key,
													'f' : key
												},
												{
													'v' : (values[index][0] / currentState["totalNumberOfRegions"]),
													'f' : values[index][0] + ''
												} ]
									})
						})
		options['legend'] = 'none'
	}
	var dt = new google.visualization.DataTable(visualizationData, 0.6);
	var altChartDesc = "";
	if (keys.length > 1) {
		chartType = "ColumnChart";
		altChartDesc = "table";
		options["width"] = widthChart;
		options["chartArea"]["width"] = widthChart - 60;
		options['height'] = heightChart;
	} else {
		chartType = "Table";
		altChartDesc = "chart";
		options["width"] = null;
		options["chartArea"]["width"] = null;
		options['height'] = null;
	}
	// dt.sort([{column: 0,desc: false}])
	// var chart = new
	// google.visualization.ColumnChart(document.getElementById('rangeFeaturePlot'));
	var chart = new google.visualization.ChartWrapper({
		'chartType' : chartType,
		'containerId' : 'rangeFeaturePlot',
		'dataTable' : dt,
		'options' : options
	});
	currentState["activeChart"].push(chart);
	// chart.draw(dt, options);
	chart.draw();
	function chartSelectHandler() {
		var selection = chart.getChart().getSelection();
		for ( var i = 0; i < selection.length; i++) {
			var item = selection[i];
			if (item.row != null && item.column != null) {
				if (zoomInEvents[dt.getValue(item.row, 0)] !== undefined) {
					zoomInEvents[dt.getValue(item.row, 0)]();
				}
			} else if (item.row != null) {
				if (zoomInEvents[dt.getValue(item.row, 0)] !== undefined) {
					zoomInEvents[dt.getValue(item.row, 0)]();
				}
			}
			// else if (item.column != null) {
			// A column is selected. Do nothing
			// }
		}

	}
	google.visualization.events
			.addListener(chart, 'select', chartSelectHandler);

	var difShow = $('<tr class="showTableLink"><td colspan="2"><a href="#" onclick="return false">Show as '
			+ altChartDesc + '</a></td></tr>');
	difShow.click(function() {
		if (chart.getChartType() == "Table") {
			chart.setChartType('ColumnChart')
			chart.setOption("height", heightChart)
			$(".showTableLink a").text("Show as table");
			$('tr.toPNGRow').show()
		} else {
			chart.setChartType("Table")
			chart.setOption("height", null)
			$(".showTableLink a").text("Show as chart");
			$('tr.toPNGRow').hide()
		}
		chart.draw()

	});
	$('.showTableLink').remove();
	$('#rangeFeaturePlotTable').append(difShow);
	// Image convertion
	$('tr.toPNGRow').remove();
	var toImageButton = $('<tr class="toPNGRow"><td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
			+ options["width"]
			+ '"/> <input type="hidden" value="'
			+ options["height"]
			+ '"/><input type="hidden" value="'
			+ chart.getContainerId() + '"/></td></tr>')
	$('#rangeFeaturePlotTable').append(toImageButton)

}
function referenceSelect(refGenome, refRegion, refQueryRefinements, updatePlot,
		asynchronous) {
	// alert("referenceSelect Start")
	/* REFERENCE UPDATE */
	currentState["referenceQuery"]["genome"] = refGenome;
	currentState["referenceQuery"]["dataset"] = refRegion;
	currentState["referenceQuery"]["editable"] = false;
	/* REFERENCE UPDATE */
	currentState["referenceQuery"]["queryParts"] = refQueryRefinements;
	// currentState["referenceQuery"]["query"] = getQueryFromParts("
	// ","BASEREFQUERY",currentState["referenceQuery"]["queryParts"]);
	// currentState["referenceQuery"]["values"] = {};
	/* REFERENCE UPDATE */
	referenceUpdate(updatePlot, asynchronous)
	// alert("referenceSelect end")

}
function referenceUpdate(updatePlot, asynchronous) {/* CHECK_FOR_MAJOR_REF_UPDATE */
	if (settings["showRefinementNotification"] == "true"){
		title = "Selected a reference dataset"
		message = "You have chosen to select a reference dataset. It will be shown in the left panel.<br/><br/>"
		message += "You can remove the reference dataset at any point by selecting the X on its right.<br/><br/>"
		message += "All further visualizations will show information for your current selection and your referecne set.<br/><br/>"
		message += "You can find more information on reference datasets and comparison mode in <a href='https://docs.google.com/presentation/embed?id=1B8XwiPPqm-uj5PczXHn43Q1qCN8yLWNpUO0XeXV3R08&start=false&loop=false&delayms=3000' target='_blank'>our tutorial</a>.<br/><br/>"
		
		showRefinementNotification(title,message);
	}
	// alert("referenceUpdate start")
	// alert(currentState["referenceQuery"]["queryParts"])
	var referenceQueryParts = currentState["referenceQuery"]["queryParts"]
			.slice(0);
	referenceQueryParts.push("Eregion")
	// alert(currentState["referenceQuery"]["queryParts"])
	currentState["referenceQuery"]["query"] = getQueryFromParts(" ",
			"BASEREFQUERY", referenceQueryParts);
	currentState["referenceQuery"]["values"] = {};
	answerQuery(
			currentState["referenceQuery"]["dataset"],
			currentState["referenceQuery"]["query"].replace(/BASEREFQUERY/g,
					"Eregion"),
			0,
			0,
			asynchronous,
			"",
			function(result) {
				// alert("referenceUpdateAnswerQuery start")
				currentState["referenceQuery"]["totalNumber"] = result[2];
				// alert("referenceUpdateAnswerQuery 1")
				if (currentState["referenceQuery"]["totalNumber"] <= 0) {
					// alert("referenceUpdateAnswerQuery 2")
					alert("The reference query must have some results");
					/* REFERENCE UPDATE */
					currentState["referenceQuery"] = getDefaultReferenceState();
				} else {
					// alert("referenceUpdateAnswerQuery 3")
					// write down the reference
					$('#referenceListing').show();
					$('#referenceListing').html("");

					// $('#referenceListing').append($('<h4>Control set</h4>'));

					var referenceListingParagraph = $("<p class='referencelistingParagraph' style='padding-left:"
							+ settings["standardIdentation"] + "px;'></p>")
					referenceListingParagraph.append($("<div><i>Genome</i>: "
							+ currentState["referenceQuery"]["genome"]
							+ "</div>"))
					referenceListingParagraph
							.append($("<div><i>Regions</i>: "
									+ currentState["datasetInfo"][currentState["referenceQuery"]["dataset"]]["officialName"]
									+ " ("
									+ numberWithCommas(currentState["referenceQuery"]["totalNumber"])
									+ ")</div>"))
					// alert("referenceUpdateAnswerQuery 4")
					// alert(currentState["referenceQuery"]["queryParts"])
					$
							.each(
									currentState["referenceQuery"]["queryParts"],
									function(index, value) {
										referenceListingParagraph
												.append($("<div><span class='referencePrefixRaw'>"
														+ value
														+ "</span><i>"
														+ getReadableFeatureText(value)
														+ "</i><span class='ui-icon ui-icon-closethick ui-icon-turnred referencelistingRefinementX' ></span></div>"));
									});
					// alert("referenceUpdateAnswerQuery 5")
					// close the paragraph
					$('#referenceListing').append(referenceListingParagraph);
					// alert(1)
					var removeReference = $('<div class="activeSearchBox" style="margin-top:10px;"><b style="padding-left:'
							+ settings["standardIdentation"]
					//		+ 'px;"><div class="referenceNameBox"><div class="editableNameBox">Control set regions</div></div></b></div>');
							+ 'px;">Control set regions</b></div>');

					// alert(2)
					var removerefButton = $('<span title="Remove the reference" class="ui-icon ui-icon-closethick ui-icon-turnred" style="margin-right:5px;float:right;"></span>');
					// alert(3)
					removerefButton
							.click(function() {
								$('#referenceListing').hide();
								$('#referenceListing').removeClass(
										"pretty-hover");
								$('#referenceListing').html("");
								// remove the link
								$('#currentLinkLocation').text("")
								/* REFERENCE UPDATE */
								currentState["referenceQuery"] = getDefaultReferenceState();
								if (currentState["exploreRegionSelected"] != settings["defaultRegionSelected"]) {
									updateCurrentSelectionOverlapPlot(false);
								}
								// alert("Removed?")
							});
					removeReference.append(removerefButton);
					// alert("referenceUpdateAnswerQuery 6")
					// alert(4)
					var maxrefButton = $('<span title="Show the reference text" class="ui-icon ui-icon-newwin ui-icon-turnred" style="margin-right:5px;float:left;"></span>');
					var minrefButton = $('<span title="Hide the reference text" class="ui-icon ui-icon-arrowthickstop-1-s ui-icon-turnred" style="margin-right:5px;float:left;"></span>');
					maxrefButton.click(function() {
						$('.referencelistingParagraph').show()
						maxrefButton.hide()
						minrefButton.show()
					});
					// removeReference.append(maxrefButton);
					removeReference.prepend(maxrefButton);
					maxrefButton.hide()
					minrefButton.click(function() {
						$('.referencelistingParagraph').hide()
						maxrefButton.show()
						minrefButton.hide()
					});
					// removeReference.append(minrefButton);
					removeReference.prepend(minrefButton);
					// Lock and unlock reference
					var lockReferenceButton = $('<span title="This control is currently dynamic. Press here, if you want to keep it static" class="ui-icon ui-icon-unlocked ui-icon-turnred" style="margin-right:5px;float:right;"></span>');
					var unlockReferenceButton = $('<span title="This control is currently static. Press here, if you want to make it dynamic" class="ui-icon ui-icon-locked ui-icon-turnred" style="margin-right:5px;float:right;"></span>');
					lockReferenceButton.click(function() {
						currentState["referenceQuery"]["editable"] = false;
						$('.referencelistingRefinementX').hide()
						lockReferenceButton.hide()
						unlockReferenceButton.show()
					});
					removeReference.append(lockReferenceButton);

					unlockReferenceButton.click(function() {
						currentState["referenceQuery"]["editable"] = true;
						$('.referencelistingRefinementX').show()
						lockReferenceButton.show()
						unlockReferenceButton.hide()
						maxrefButton.click()
					});
					removeReference.append(unlockReferenceButton);
					if (currentState["referenceQuery"]["editable"] == false) {
						lockReferenceButton.hide();
						$('.referencelistingRefinementX').hide();
					} else {
						unlockReferenceButton.hide();
						$('.referencelistingRefinementX').show();
					}

					// $('#referenceListing').append(removeReference);
					$('#referenceListing').prepend(removeReference);
					$('#referenceListing').prepend('')
					removerefButton.mouseleave()

					if (updatePlot) {
						// update the current state of the reference query
						updateCurrentSelectionOverlapPlot(true);
					}
					$('#currentLinkLocation').text("")
					// alert("referenceUpdateAnswerQuery end")
				}
			});
	// alert("Query storage complete");
	// alert("referenceUpdate end")

}

function addRegionSelectionToTheQueryListing(datasetName, datasetRawName,
		reloadVisual) {
	var queryRegionsTable = $('<table class="regionsListingTable" cellspacing="0"></table>')
	var queryRegionRow = $('<tr class="queryRegions" title="'
			+ datasetName
			+ '"><td><b><label id="totalDocuments" style="margin-right:5px;float:left;">'
			+ numberWithCommas(currentState["totalNumberOfRegions"])
			+ '</label><span style="float:left;" class="queryRegionsRaw">'
			+ datasetName + '</span></b></td></tr>');

	// queryRegionRow.append($(''));
	// var refButton = $('<td title="Use as reference" class="ui-icon
	// ui-icon-tag ui-icon-turnred useAsReferenceButton"></td>');

	/*
	 * refButton.click(function(){ //use the current query as reference
	 * $('#currentLinkLocation').text("")
	 * 
	 * var refQueryRefinements = [];
	 * $.each($('span.queryPrefixRaw'),function(index,value){
	 * refQueryRefinements.push($(value).text()); });
	 * referenceSelect(settings["genome"],currentState["exploreRegionSelected"],refQueryRefinements,true,true)
	 * 
	 * });
	 */
	queryRegionRow.append($('<td/>'));
	if (settings["allowRemoveRegionSelection"]) {
		var removeButton = $('<td title="Remove this selection and explore other regions"><span class="ui-icon ui-icon-closethick ui-icon-turnred"></span></td>');
		removeButton.one("click", activateMode_ExploreRegionSelection);
		queryRegionRow.append(removeButton);
	}
	queryRegionsTable.append(queryRegionRow);
	$('.regionsSelected').append(queryRegionsTable);
	if (reloadVisual) {
		highlightElement(queryRegionRow, 1000, 2);
	}
}
function addRefinementToTheQueryListing(refinementTitle, refinementRaw,
		doHighlight) {
	if (settings["showRefinementNotification"] == "true"){
		title = "Adding a refinement to your dataset"
		message = "You are about to apply the filter '<i>"+refinementTitle+"</i>' to your dataset. <br/><br/>"
		message += "The listing in the top left corner will update to show the number of regions that fulfil these conditions.<br/><br/>"
		message += "You can remove this and any other refinement by selecting the X on its right.<br/><br/>"
		message += "All further visualizations will show updated information for your refined set.<br/><br/>"
		showRefinementNotification(title,message);
	}
	var refinementDescription = refinementTitle;
	if (refinementTitle.length == 0) {
		refinementDescription = getReadableFeatureText(refinementRaw);
	}
	if (refinementDescription == "Unknown") {
		refinementDescription = refinementRaw;
	}
	currentState["currentOverlaps"] = settings["defaultCurrentOverlaps"];
	currentState["currentOverlapsStat"] = settings["defaultCurrentOverlapStats"];
	currentState["currentNeighborhood"] = settings["defaultCurrentOverlaps"];
	// remove the link
	$('#currentLinkLocation').text("")
	if ($('.queryRefinementORButtonActive').length > 0) {
		// add it to existing refiniment
		// change the icon and make in not clickable
		var activeORButton = $('.queryRefinementORButtonActive');
		deactivateORClause(activeORButton, false);
		// activeORButton.removeClass(queryRefinementORButtonDeactive);
		// add refinement to the row
		var currentActiveQueryPartRaw = activeORButton.parent().siblings(
				"td.queryPrefixMainTD").children("span.queryPrefixRaw")
		// alert(currentActiveQueryPartRaw.length)
		var currentValue = currentActiveQueryPartRaw.text();
		var newValue = currentValue + "|" + refinementRaw;
		currentActiveQueryPartRaw.text(newValue);
		// add refinement to the description
		var currentActiveQueryPartTitle = activeORButton.parent().siblings(
				"td.queryPrefixMainTD").children("span.queryPrefixTitle")
		// alert(currentActiveQueryPartTitle.length)
		var currentValueTitle = currentActiveQueryPartTitle.html();
		var newValueTitle = currentValueTitle + " <b>OR</b> "
				+ refinementDescription;
		currentActiveQueryPartTitle.html(newValueTitle);
		// if(doHighlight){
		// highlightElement(activeORButton.parent(),1000,2);
		// }
		updateResultsAndDocuments(false, true, true);
	} else {

		// No active OR clause , hence make new refinement
		var queryRefinementRow = $('<tr class="queryPrexix" title="'
				+ refinementTitle
				+ '"><td class="queryPrefixMainTD"><span class="queryPrefixRaw">'
				+ refinementRaw + '</span><span class="queryPrefixTitle">'
				+ refinementDescription + '</td></tr>');

		// add a button to remove the current selection
		var removeButton = $('<td title="Remove this refinement" ><span class="ui-icon ui-icon-closethick ui-icon-turnred"/></td>');
		removeButton
				.one(
						"click",
						function() {
							// remove the current plot
							if (settings["showRefinementNotification"] == "true"){
								title = "Removing a refinement from your dataset";
								message = "You have chosen to remove a filter from your dataset. <br/><br/>"
								message += "The listing in the top left corner will update to show the number of regions that fulfil the remaining conditions.<br/><br/>"								
								message += "All further visualizations will show updated information for your new set.<br/><br/>"
								showRefinementNotification(title,message);	
							}
							$('#rangeFeaturePlotMain').children().remove()
							// remove the current row form the list
							queryRefinementRow.remove();
							currentState["currentOverlaps"] = settings["defaultCurrentOverlaps"];
							currentState["currentOverlapsStat"] = settings["defaultCurrentOverlapStats"];
							currentState["currentNeighborhood"] = settings["defaultCurrentOverlaps"];
							// remove the link
							$('#currentLinkLocation').text("")

							// 22.10.10update the opene features,the results and
							// the number
							// 22.10.10 Remvoe updating of the open feature, but
							// update the general plot instead
							// updateOpenFeature(true,true,true);
							closeOpenFeatureBox();
							// alert(2);

							updateCurrentSelectionOverlapPlot(false);
							updateResultsAndDocuments(false, true, true);
						});

		// activate OR fucntionality on click
		var orButton = $('<td title="Add additional conditions for this refinement"><span class="ui-icon ui-icon-arrowthick-2-e-w ui-icon-turnred queryRefinementORButtonDeactive"/></td>');
		queryRefinementRow.append(orButton);
		queryRefinementRow.append(removeButton);
		// queryRefinementRow.append($('<br/>'));
		// add the remove button

		$('table.regionsListingTable').append(queryRefinementRow);
		if (currentState["referenceQuery"]["genome"] != ""
				&& currentState["referenceQuery"]["editable"]) {
			// alert("adding refinement to ref start")
			/* CHECK_FOR_MAJOR_REF_UPDATE */
			// update the reference listing
			currentState["referenceQuery"]["queryParts"].push(refinementRaw);
			referenceUpdate(false, false);
			// alert("adding refinement to ref end")
		}

		// if(doHighlight){
		// highlightElement(queryRefinementRow,1000,2);
		// }
	}
}
function activateORClause(orButton, refresh) {
	// alert("clicked the Or button activate start");
	if (settings["showRefinementNotification"] == "true"){
		title = "Activating an OR clause";
		message = "You have activated the possibility to add an <b>OR</b> statement to one of your refinements. <br/><br/>"
		message += "You can switch it off by pressing the same button.<br/><br/>"
		message += "The listing in the top left corner will update to show the number of regions, excluding the refinement you have activated. <br/><br/>"		
		message += "The next refinement you apply will be added as an OR clause to the active refinement.<br/><br/>"		
		showRefinementNotification(title,message);
	}
	// deactivate all other ORs
	$('.queryRefinementORButtonActive').each(function(index) {
		// alert("queryRefinementOr is active "+index);
		deactivateORClause($(this), false);
	});

	// alert("icon");
	// change the icon and the class of the button
	orButton.removeClass("ui-icon-arrowthick-2-e-w");
	orButton.removeClass("queryRefinementORButtonDeactive");
	orButton.addClass("ui-icon-cancel");
	orButton.addClass("queryRefinementORButtonActive");

	// alert("title");
	// change the title
	orButton.attr("title", "Cancel the OR selection");

	// alert("activate queryRaw class");
	// change the class of the queryPrefix sos that it is not included in a
	// query refresh
	var queryPrefixRowElement = orButton.parent().siblings(
			"td.queryPrefixMainTD").children("span.queryPrefixRaw");
	// alert(queryPrefixRowElement.length)
	queryPrefixRowElement.addClass("queryPrefixRawOR");
	queryPrefixRowElement.removeClass("queryPrefixRaw");

	// alert("activate refresh");
	// query refresh
	currentState["currentOverlaps"] = settings["defaultCurrentOverlaps"];
	currentState["currentOverlapsStat"] = settings["defaultCurrentOverlapStats"];
	currentState["currentNeighborhood"] = settings["defaultCurrentOverlaps"];
	// remove the link
	$('#currentLinkLocation').text("")
	if (refresh) {
		if ($('.featureBoxOpened').length > 0) {
			updateOpenFeature(false, true, true);
		} else {
			updateCurrentSelectionOverlapPlot(false);
			updateOpenFeature(false, false, true);
		}
	}

	// alert("clicked the Or button activate end");
}
function deactivateORClause(orButton, refresh) {
	// alert("clicked the Or button deactivate start");

	// change the icon
	orButton.removeClass("ui-icon-cancel");
	orButton.removeClass("queryRefinementORButtonActive");
	orButton.addClass("ui-icon-arrowthick-2-e-w");
	orButton.addClass("queryRefinementORButtonDeactive");
	// change the title
	orButton.attr("title", "Add additional conditions for this refinement");
	// change the class of the queryPrefix sos that it is not included in a
	// query refresh
	var queryPrefixRowElement = orButton.parent().siblings(
			"td.queryPrefixMainTD").children("span.queryPrefixRawOR");
	// alert(queryPrefixRowElement.length)
	queryPrefixRowElement.addClass("queryPrefixRaw");
	queryPrefixRowElement.removeClass("queryPrefixRawOR");
	// query refresh
	currentState["currentOverlaps"] = settings["defaultCurrentOverlaps"];
	currentState["currentOverlapsStat"] = settings["defaultCurrentOverlapStats"];
	currentState["currentNeighborhood"] = settings["defaultCurrentOverlaps"];
	// remove the link
	$('#currentLinkLocation').text("")
	if (refresh) {
		if ($('.featureBoxOpened').length > 0) {
			updateOpenFeature(false, true, true);
		} else {

			updateCurrentSelectionOverlapPlot(false);
			updateOpenFeature(false, false, true);
		}
	}
	// activate OR fucntionality on click
	// $(this).one('click',activateORClause);
	// alert("clicked the Or button deactivate end");
}
function addResultsRefinementAndUpdate(refinementTitle, refinementRaw,
		numberOfDocuments, update) {
	if (numberOfDocuments == 0 || numberOfDocuments == "0") {
		alert("This refinement will lead to 0 remaining results!");
	}

	// remvoe the current plot
	// $('#rangeFeaturePlot').remove();
	// $('#convertPlotToImage').remove();
	$('#rangeFeaturePlotMain').children().remove()
	// add to the query listing
	addRefinementToTheQueryListing(refinementTitle, refinementRaw, true);

	if (update) {
		// 21.10.10 KH: The functionality used to be that the current open
		// feature is again updated
		// but maybe it is better to refresh the general feature
		// updateOpenFeature(true,true,numberOfDocuments == -1);
		// alert(1);
		closeOpenFeatureBox();
		// alert(2);
		updateCurrentSelectionOverlapPlot(false);
		// alert(3);
	}

	// update the total number of documents
	if (numberOfDocuments != -1) {
		currentState["totalNumberOfRegions"] = parseInt(numberOfDocuments
				.replace(/,/g, ""));
		;
		$('#totalDocuments').text(
				numberWithCommas(currentState["totalNumberOfRegions"]));

	} else {
		updateResultsAndDocuments(false, true, true);
	}
	// alert("From within addResultsRefinementAndUpdate");
}

function updateNumberOfDocuments(result) {
	currentState["totalNumberOfRegions"] = parseInt(result[2]);
	$('#totalDocuments').text(
			numberWithCommas(currentState["totalNumberOfRegions"]));
}

// Given a query answers the query and executes the resultsMethod to process the
// results
// this is the most basic method
function answerQuery(regiontype, query, numberOfCompletions, numberOfHits,
		asynchronous, extraSettings, resultsMethod) {
	if (regiontype == "") {
		return;
	}
	// CONVERT_BASEQUERY_TO_JSON var fullQuery =
	// "type=basequery&regiontype="+regiontype+"&query="+query+"&ncompl="+numberOfCompletions+"&nhits="+numberOfHits;
	var fullQuery = "type=baseQueryPostJSON&regiontype=" + regiontype + "&query="
			+ query + "&ncompl=" + numberOfCompletions + "&nhits="
			+ numberOfHits + "&extraSettings=" + extraSettings;

	$.ajax({
		async : asynchronous,
		type : "POST",
		url : "relay.php",
		// CONVERT_BASEQUERY_TO_JSON dataType: "text",
		dataType : "json",
		data : fullQuery,
		success : function(result) {
			resultsMethod(result);
			// alert("Query complete");
		}
	});
}
/* ####----####---- Function ----####----#### */
// show infor for a feature
function showInfoPlot(plotType) {
	var plotDescription = getTextForPlotDescription(plotType);
	if (plotDescription != "") {
		$(".infoboxMain").show();
		$(".infoboxPlot").show();
		// $(".infoWelcome").remove();
		hideIframe();
		$(".infoboxPlot").html("")
		$(".infoboxPlot").append(
				"<p class=\"infoboxTitle\"><b>Chart description:</b> "
						+ plotDescription + "</p>")
		// highlightElement($(".infoboxPlot"),1000,1);
	} else {
		$(".infoboxPlot").html("")
	}
}
// show infor for a feature
function showInfoFeature(featureName, featureDescription) {
	if (featureDescription != "") {
		$(".infoboxMain").show();
		// $(".infoWelcome").remove();
		// $('div.content').show()
		// $('#contentFrameID').attr("src","")
		// $('div.contentFrame').hide();
		$(".infoboxFeature").html("")
		$(".infoboxFeature").append(featureDescription);
		// highlightElement($(".infoboxFeature"),700,2);
	}
	// $(".infoboxFeature").html(featureDescription);
}
function loadDatasetInfo(regionSetID, property, asynchronized) {	
	var datacall;
	if (property != ""){			
		datacall = "type=getDatasetInfo&datasetName=" + regionSetID+"properties="+property;
	}else{
		datacall = "type=getDatasetInfo&datasetName=" + regionSetID
	}
	$.ajax({
		type : "GET",
		url : "relay.php",
		dataType : "json",
		async : asynchronized,
		data : datacall,
		success : function(result) {
			if (currentState["datasetInfo"][regionSetID] == undefined){
				currentState["datasetInfo"][regionSetID] = {};				
			}
			featureGroupDescription[regionSetID] = result["description"];
			featureGroupNames[regionSetID] = result["officialName"];
			featureGroupCategories[regionSetID] = result["categories"];
			overlapMarks[regionSetID] = result["overlappingText"];
			
			$.each(result, function(index, value) {
				currentState["datasetInfo"][regionSetID][index] = value;
			});
			//currentState["datasetInfo"][regionSetID] = result;
		}
	});	
}
// show info for a region set
function showInfoRegionSet(regionSetID, showExploreRegionbutton) {
	currentState["exploreRegionSelected"] = regionSetID;
	// Load the current dataset info
	loadDatasetInfo(regionSetID,"", false)
	// this function ahs user input so here we put everything into text

	var infoBoxPar = $("<p class=\"infoboxTitle\"></p>");
	var header = $("<h3></h3>");
	// "Dataset name:"+
	header
			.text(currentState["datasetInfo"][regionSetID]['officialName']
					+ " ("
					+ numberWithCommas(currentState["datasetInfo"][regionSetID]['numberOfRegions'])
					+ " regions)");
	infoBoxPar.append(header);
	if (currentState["datasetInfo"][regionSetID]["isDefault"] == false) {
		var content = $('<p class="infoboxDescription">'
				+ currentState["datasetInfo"][regionSetID]['description']
				+ '</p><p class="tutorialMode">You may share this dataset using its unique ID ('
				+ regionSetID + ')</p>');
	} else {
		var content = $('<p class="infoboxDescription">'
				+ currentState["datasetInfo"][regionSetID]['description']
				+ '</p>');
	}
	infoBoxPar.append(content);
	if (currentState["datasetInfo"][regionSetID]['moreInfoLink']
			&& currentState["datasetInfo"][regionSetID]['moreInfoLink'] != "None") {
		var link = $("<a href=\""
				+ currentState["datasetInfo"][regionSetID]['moreInfoLink']
				+ "\" target=\"_blank\">Click here for more info</a>");
		infoBoxPar.append(link);
	}
	$(".infoboxMain").show();
	// $(".infoWelcome").remove();
	hideIframe();
	$('.infoboxRegions').html("");
	$('.infoboxRegions').show();
	$('.infoboxRegions').append(infoBoxPar);
	showExploreRegionbutton = false;
	if (showExploreRegionbutton) {
		var datasetButton = $('<p class="infoboxDescription regionSelectionLinkFromInfoBox"><img src="extras/media-playback-start.png" width="16px" height="16px" alt="Select dataset"/><a href="#" onclick="return false;">Explore this region set</a></p>');
		datasetButton
				.click(function() {
					$(this).remove();
					// alert(currentState["exploreRegionSelected"]+" --
					// "+regionSetID)
					// if (currentState["exploreRegionSelected"] !=
					// regionSetID){
					currentState["exploreRegionSelected"] = regionSetID;

					currentState["totalNumberOfRegions"] = currentState["datasetInfo"][currentState["exploreRegionSelected"]]['numberOfRegions']
					// alert(currentState["totalNumberOfRegions"])
					activateMode_ExploreRegionChosen(false);
					// }
				});
		$('.infoboxRegions').append(datasetButton);
	}
}

/* ####----####---- Function ----####----#### */
function featureOpenBox() {
	hideIframe();
	// alert("Open feature" + $(this).text());
	var header = $(this).children("h4")[0];
	// if there is an opened box feature, then close it
	closeOpenFeatureBox();
	// unbind the behavior of clickin on the current feature

	// $(".infoboxFeature").html("")
	if ($(header).children("input.featureBoxName").length > 0) {
		var featureDescription = getTextForFeatureDescription($(header)
				.children("input.featureBoxName").val());
		showInfoFeature($(header).text(), featureDescription);

	} else {
		var foundFirstBranchData = false;
		var currentElement = $(this).parent();
		while (!foundFirstBranchData
				&& currentElement.attr("id") != "featureListingTree") {
			// var parentDiv = featureBranchElement.parent();
			if ($(currentElement).children("h4").length > 0) {
				var currentElementBox = $(currentElement).children("h4")[0];
				if ($(currentElementBox).children("input.featureBranchName").length > 0) {
					var groupName = $(currentElementBox).children(
							"input.featureBranchName").val();
					
					descriptionData = getDatasetDescription(groupName);					
					var featureDescription =  buildDescription(descriptionData);
					
					//var featureDescription = getDescriptionForFeatureGroup(groupName);
					if (featureDescription != null) {
						if (featureDescription != "") {
							showInfoFeature($(currentElementBox).text(),
									featureDescription);
							foundFirstBranchData = true;
						}
					}
				}
			}
			var currentElement = $(currentElement).parent();
		}
	}

	$(this).unbind('click');
	// add to the current closed feature the opened tag
	$(this).addClass("featureBoxOpened");
	$(header).children(".ui-icon-search").addClass("ui-icon-circle-check");
	$(header).children(".ui-icon-search").removeClass("ui-icon-search");
	$(header)
			.append(
					$('<img name="progress_image_feature" src="extras/ajax-loader.gif" class="progress_image_feature" align="right" alt="Processing ..."></img>'));
	setCurrentStatus("Fetching data ...", true)
	// $("#currentStatus").append($('<img name="progress_image_feature_plot"
	// src="extras/ajax-loader-big.gif" class="progress_image_feature_plot"
	// align="center" alt="Processing..."></img>'));
	// $(".visualization").append($('<img name="progress_image_feature_plot"
	// src="extras/ajax-loader-big.gif" class="progress_image_feature_plot"
	// align="center" alt="Processing ..."></img>'));

	$(this)
			.append(
					$('<table id="openedFeatureResults" style="padding-left:'
							+ (parseInt($(header).css("padding-left").slice(0,
									-2), 10) + settings["standardIdentation"])
							+ 'px;" cellspacing="0"></table>'));
	updateOpenFeature(false, true, false);
}
/* ####----####---- Function ----####----#### */
function closeOpenFeatureBox() {
	hideIframe();
	// Clear the resources form previous charts
	clearCharts();
	// Updating the current visualization	
	updateCurrentVisualization(settings["genome"] + "summary",false);
	// any open feature box has an icon, chnage it to the default one
	$('.ui-icon-circle-check').not("#iconLegend .ui-icon-circle-check")
			.addClass("ui-icon-search");
	$('.ui-icon-circle-check').not("#iconLegend .ui-icon-circle-check")
			.removeClass("ui-icon-circle-check");
	// remove the highlighting
	// $('.ui-state-highlight').removeClass("ui-state-highlight");
	// hide the plot thing
	$('#rangeFeaturePlotMain').hide();
	// $('#convertPlotToImage').remove();
	// remove any table
	// remove the current list in the feature refinement
	$('#openedFeatureResults tr').remove();
	$('#openedFeatureResults div.featureRangeOrRatioResults').remove();
	$('#openedFeatureResults').remove();
	// associate its default click behaviour
	$('.featureBoxOpened').one("click", featureOpenBox);

	// remove its opened class
	$('.featureBoxOpened').removeClass("featureBoxOpened");
}
/* ####----####---- Function ----####----#### */
function featureOpenBranch(featureBranchElementDOM, updatePlots) {
	var featureBranchElement = $(featureBranchElementDOM);
	// alert("open branch "+$(this).text());
	var parentDiv = featureBranchElement.parent();

	featureBranchElement.children(".ui-icon").removeClass("ui-icon-plusthick");
	featureBranchElement.children(".ui-icon").addClass("ui-icon-minusthick");
	featureBranchElement.children(".ui-icon").addClass("ui-icon-turnred");

	// If this branch has a Sumary/Overlaps data to be displayed.
	var hasOverlaps = false;

	if (updatePlots
			&& featureBranchElement
					.siblings("input.featureBranchOverlapPrefixes").length > 0) {
		currentState["overlapSelection"] = featureBranchElement.siblings(
				"input.featureBranchOverlapPrefixes").val().split(",");
		hasOverlaps = true;
	}
	// Add the feature description
	if (updatePlots
			&& featureBranchElement.children("input.featureBranchName").length > 0) {
		var groupName = featureBranchElement
				.children("input.featureBranchName").val();

		if (hasOverlaps
				&& currentState["featuresElements"][groupName] !== undefined) {
			
			updateCurrentVisualization(groupName,true);
			$('#currentLinkLocation').text("")
			// $('.visualizationLinks').append('<a href="#"
			// class="visualizationDirectLink" onclick="return
			// false;">'+groupName+'</a><br/>')
		}

		// If is a box that is openned now... does not change the description.
		if (currentState["activeChart"].length == 0 || hasOverlaps) {
			$(".infoboxFeature").html("");
			descriptionData = getDatasetDescription(groupName);			
			text = "</BR>" + buildDescription(descriptionData);
			if (text != null) {
				showInfoFeature(featureBranchElement.text(), text);
			}
		}
	}
	if (hasOverlaps == true) {
		updateCurrentSelectionOverlapPlot(false);
	}

	// alert("icon changed");
	parentDiv.addClass("featureBranchOpened");
	parentDiv.children().show();
	// make sure if an opne branch is clicked it closes all its children
	// $(this).unbind('click');
	// $(this).one("click",featureCloseBranch);
	featureBranchElement.children(".ui-icon").one("click", featureCloseBranch);
}
/* ####----####---- Function ----####----#### */
function featureCloseBranch(event) {
	event.stopPropagation();
	// var parentDiv = $(this).parent();
	var parentDiv = $(this).parent().parent();
	parentDiv.removeClass("featureBranchOpened");
	parentDiv.children("div").hide();
	// $(this).children(".ui-icon").removeClass("ui-icon-minusthick");
	$(this).removeClass("ui-icon-minusthick");
	$(this).removeClass("ui-icon-turnred");
	// $(this).children(".ui-icon").addClass("ui-icon-plusthick");
	$(this).addClass("ui-icon-plusthick");
	// alert("icon changed");
	$(this).unbind('click');
	// $(this).one("click",featureOpenBranch);
}

/* ####----####---- Function ----####----#### */
// selects a region set
function activateMode_ExploreRegionChosen(reloadPlot) {
	initCurrentDatasetData();
	
	$(".features").show();
	$("tr.reloadUserDatasetTD").hide()
	$(".activateUserDatasetSpan").text("")
	$(".regionsSelection").hide();
	
	addRegionSelectionToTheQueryListing(
			currentState["datasetInfo"][currentState["exploreRegionSelected"]]["officialName"],
			currentState["exploreRegionSelected"], reloadPlot);

	$(".regionsSelected").show();
	$(".visualization").show();

	$(".menuSeparator").show();

	$("#rangeFeaturePlotMain").show();
	$(".infoboxMain").show();
	// $(".infoWelcome").remove();
	hideIframe();
	$("#exportMenu").show();
	if (reloadPlot) {
		updateCurrentSelectionOverlapPlot(false);
	}
}

function initCurrentDatasetData() {
	initDatasetCoverage(settings["genome"], currentState["exploreRegionSelected"]);
	initFeatures(true);
	currentState["isRegionSelected"] = true;
}

function visualizeMode_ExploreRegionSelection() {
	$(".queryRegions").remove();
	$(".queryPrexix").remove();
	$("table.regionsListingTable").remove();
	// $(".querySide").hide();
	// $(".queryResults").hide();
	$(".features").hide();
	$(".regionsSelection").show();
	$(".regionsSelected").hide();
	$('#currentLinkLocation').text("")

	$("#rangeFeaturePlotMain").show();
	// $('#convertPlotToImage').remove();
	$(".visualization").show();
	$(".menuSeparator").hide();

	$(".infoboxDetail").html("");
	$(".infoboxMain").hide();
	// $(".infoWelcome").show();
	$("#exportMenu").hide();

	closeOpenFeatureBox();
	// hide all branches
	// $(".featureBranchOpened").each(featureCloseBranch);
	// $(".featureBranchClosed").children("div").hide();

}
function activateMode_ExploreRegionSelection() {
	currentState["isRegionSelected"] = false;
	currentState["exploreRegionSelected"] = settings["defaultRegionSelected"];
	currentState["currentOverlaps"] = settings["defaultCurrentOverlaps"];
	currentState["currentOverlapsStat"] = settings["defaultCurrentOverlapStats"];
	currentState["currentNeighborhood"] = settings["defaultCurrentOverlaps"];
	// remove the link
	$('#currentLinkLocation').text("")
	currentState["overlapSelection"] = settings["overlapSelection"][settings["genome"]];
	
	updateCurrentVisualization(settings["genome"] + "summary",true);
	visualizeMode_ExploreRegionSelection();
}

/* ####----####---- Function ----####----#### */
// initializes the regionListing
function initRegionSets(asyncronous) {
	$("#regionsTable").html("");
	setCurrentStatus("Retrieving data for the available datasets ...", true);
	$.ajax({
		type : "GET",
		url : "relay.php",
		// dataType: "text",
		async : asyncronous,
		dataType : "json",
		error: function(jqXHR, textStatus, errorThrown) {
			alert(jqXHR);
			alert(textStatus);
			alert(errorThrown);
			setCurrentStatus("Error loading region types.", false);
		},				
		data : "type=regiontypes&sourceType=" + settings["sourceType"]
				+ "&genome=" + settings["genome"],
				
		success : function(result) { processRegionTypes(result) }
	});
}
				
function processRegionTypes(datasets) {
	setCurrentStatus("Loading default datasets ...", true);
	var sortedDatasetNames = [];
	$.each(datasets, function(index, dataset) {
		sortedDatasetNames.push(dataset["officialName"]);
		currentState["datasetInfo"] [dataset["simpleName"]] = dataset;
	});
	sortedDatasetNames.sort();
	sortedDatasetNames.reverse();
	$.each(datasets, function(index, value) {
		var i = jQuery.inArray(value["officialName"], sortedDatasetNames);
		sortedDatasetNames[i] = index;
	});
	
	// load the results in the regionsTable
	var regionTable = $("#regionsTable");
	var total = 0;

	$.each(sortedDatasetNames, function(index, value) {
		index = value;
		value = datasets[index];
		var regionRow = $('<tr class="regionsButton regionsButtonHover" title="See more information"></tr>');
		regionRow.append($('<td align="left" class="regionsetInfoButton hoverChangeIcon" title="Show information about this region set"><img src="extras/dialog-information.png" class="selectDatasetIcon" alt="Select dataset"></img><div class="selectDatasetText">Info</div><input type="hidden" value="'
				+ index + '"/></td>'));
						// var add as compariosn dataset button
		regionRow.append($('<td title="Add this dataset as comparison" class="compareDatasetButton hoverChangeIcon"><img src="extras/split.png" class="compareDatasetIcon" alt="Compare to dataset"/><div class="selectDatasetText">Compare</div><input type="hidden" value="'
				+ index + '"/></td>'));
		
		regionRow.append($('<td class="regionsetSelectButton" align="left" title="Explore this dataset">'
				+ value["officialName"] + '<input type="hidden" value="' + index + '"/></td>'));
		
		regionRow.append($('<td class="regionsetSelectButton" align="right" title="Explore this dataset">'
				+ numberWithCommas(value["numberOfRegions"]) + '<input type="hidden" value="'+ index + '"/></td>'));

		regionRow.append($('<td align="center" class="regionsetSelectButton hoverChangeIcon" title="Explore this dataset"><img src="extras/media-playback-start.png" class="selectDatasetIcon" alt="Select dataset"></img><div class="selectDatasetText">Select</div><input type="hidden" value="'
				+ index + '"/></td>'));

		regionTable.prepend(regionRow);

		total = total + parseInt(value["numberOfRegions"], 10);

	});
	setCurrentStatus("Loading user datasets ...", true);
	// the user datasets
	
	$.each(currentState["userDatasets"], function(index, userDataset) {
		// update the visualization, only if the
		// dataset was loaded from link
		var updateSpan = currentState["loadedUserDatasetFromLink"] == userDataset;
		setCurrentStatus("Loading user datasets " + (index + 1) + " out of "
						+ currentState["userDatasets"].length + " ...", true);					
		activateUserDatasetFunction(userDataset, updateSpan, false, true);
	});

	// update the total number of documents
	currentState["totalNumberOfRegions"] = total;
	// totalNumberOfDocuments = numberWithCommas(total);
	setCurrentStatus(null, false);
}

				
function genomeChanged(async) {
	setCurrentStatus("Changing the genome settings ...", true);
	// change the values
	$('#genomeSelectLabel div.menuicontext').text(
			"Genome (" + settings["genome"] + ")");
	$.cookie("cgs:settings:genome", settings["genome"], {
		expires : 14
	});
	// change the current default overlap
	currentState["overlapSelection"] = settings["overlapSelection"][settings["genome"]];	
	updateCurrentVisualization(settings["genome"] + "summary",true);
	// change the active user datasets
	if ($.cookie("cgs:settings:userdatasets:" + settings["genome"])) {
		var userDatasets = $.cookie(
				"cgs:settings:userdatasets:" + settings["genome"]).split(";");

		if (userDatasets[0].length > 0) {
			currentState["userDatasets"] = userDatasets;
		} else {
			currentState["userDatasets"] = [];
		}

	} else {
		currentState["userDatasets"] = [];
		$.cookie("cgs:settings:userdatasets:" + settings["genome"],
				currentState["userDatasets"].join(";"), {
					expires : 30
				});
	}
        currentState["datasetInfo"] = {};
	// initialize the default region set
	initRegionSets(async);
	// initialize the list of features
	// initFeatures();
	// default start
	activateMode_ExploreRegionSelection();
	setCurrentStatus(null, false);
}
function initSettings() {
	//
	// Hide the regions on the left by default
	$(".regionsSelection").hide();
	$(".regionsSelected").hide();
	// $('#genomeSelect').val(settings["genome"]);
	$('#genomeSelectLabel div.menuicontext').text(
			"Genome (" + settings["genome"] + ")");

	$("body").delegate('.genomeSelect', 'click', function() {
		settings["genome"] = $(this).text();
		// alert(settings["genome"])
		genomeChanged(false)
	});

	// $('#overlapSelect').val(settings["overlap"]);
	$("body")
			.delegate(
					'#overlapSelect',
					'change',
					function() {

						// $('#overlapSelect').change(function() {
						settings["overlap"] = $(
								'#overlapSelect option:selected').val();
						// alert(settings["overlap"])
						$.cookie("cgs:settings:overlap", settings["overlap"], {
							expires : 14
						});
						// var oldExploreRegionSelected =
						// currentState["exploreRegionSelected"];
						// currentState["exploreRegionSelected"] = regionName;
						// currentState["currentOverlaps"] =
						// settings["defaultCurrentOverlaps"]
						currentState["currentOverlapsStat"] = settings["defaultCurrentOverlapStats"];
						if (currentState["exploreRegionSelected"] != settings["defaultRegionSelected"]) {
							if ($('.featureBoxOpened').size() == 0) {
								updateCurrentSelectionOverlapPlot(true);								
							} else {
								// updateCurrentSelectionOverlapPlot(true);
								updateOpenFeature(false, true, false);
							}
						}
						// currentState["exploreRegionSelected"] =
						// oldExploreRegionSelected;

					});

	// $('#tissueSelect').val(settings["tissue"]);

	// $('#tissueSelect').change(function() {
	$("body").delegate('#tissueSelect', 'change', function() {
		settings["tissue"] = $('#tissueSelect option:selected').val();
		// alert(settings["tissue"])
		$.cookie("cgs:settings:tissue", settings["tissue"], {
			expires : 14
		});
		// update the plot
		if ($('.featureBoxOpened').size() == 0) {
			updateCurrentSelectionOverlapPlot(false);
		} else {
			updateOpenFeature(false, true, false);
		}
	});

}
function showExternalPageInIFrame(page) {
	$('div.content').hide();
	$('#contentFrameID').attr("src", page)
	$('div.contentFrame').show();
}
function hideIframe() {
	$('#contentFrameID').attr("src", '')
	$('div.contentFrame').hide()
	$('div.content').show();
}
function initStartingSettings() {
	// var currentState["analysisLinkData"]["param"] =
	// getParameterByName('analysisLink');
	// alert("default")
	// default start
	activateMode_ExploreRegionSelection();
	if (currentState["loadedUserDatasetFromLink"] == "") {
		showExternalPageInIFrame("welcome.php")
	}

	if (currentState["analysisLinkData"]["param"] != null) {
		/*
		 * //Moved the ajax call to the start of the index.php $.ajax({ type:
		 * 'GET', url: "relay.php", async:false, data: {'type':'getLinkData',
		 * 'analysisLink':analysisLinkParam}, dataType:"json", success:
		 * function(jsonResult){
		 */
		setCurrentStatus("Loading analysis data", true);
		var jsonResult = currentState["analysisLinkData"]["result"];
		// alert(jsonResult)
		// Check if we have currently selected the wrong geneome, change it
		if (jsonResult[0] != settings['genome']) {
			// alert("Genome is to be changed")
			settings['genome'] = jsonResult[0];
			setCurrentStatus("Changing the active genome ... ", true);
			genomeChanged(false)
		}
		if (jsonResult[1] != "") {
			// alert("Activate a region set")

			currentState["exploreRegionSelected"] = jsonResult[1];
			if (!hasDatasetInfo(currentState["exploreRegionSelected"],"isDefault")) {
				setCurrentStatus("Activating custom datasets ... ", true);
				loadDatasetInfo(currentState["exploreRegionSelected"],"", false)
			}
			if (currentState["datasetInfo"][currentState["exploreRegionSelected"]]["isDefault"] == false) {
				// Teh region is not a default region "+jsonResult[1])
				setCurrentStatus("Activating custom datasets ... ", true);
				if (jQuery.inArray(jsonResult[1], currentState["userDatasets"]) == -1) {
					// Reset the dataset info, to be reloaded in the following
					// showinfo
					currentState["datasetInfo"][currentState["exploreRegionSelected"]] = undefined

					activateUserDatasetFunction(jsonResult[1], false, false,
							true)
				} else {
					// currentState["datasetInfo"][currentState["exploreRegionSelected"]]
					// = undefined
					activateUserDatasetFunction(jsonResult[1], false, false,
							false)
				}
			}
			showInfoRegionSet(currentState["exploreRegionSelected"], false)
			// alert(currentState["datasetInfo"][currentState["exploreRegionSelected"]]['numberOfRegions'])

			currentState["totalNumberOfRegions"] = currentState["datasetInfo"][currentState["exploreRegionSelected"]]['numberOfRegions']
			activateMode_ExploreRegionChosen(false);
			
			if (jsonResult[2] != "") {
				setCurrentStatus("Loading refinements ... ", true);
				// $('#totalDocuments').text(numberWithCommas(currentState["totalNumberOfRegions"]));
				// Add each refinement
				$.each(jsonResult[2].split("::qq::"), function(index,
						refinement) {
					if (!refinement.startsWith("Eregion")) {
						addRefinementToTheQueryListing("", refinement, false);
					}
				})
			}
			updateResultsAndDocuments(false, true, false);

		}

		// Load the reference
		if (jsonResult[4] != "") {
			if (jsonResult[5] != "") {
				setCurrentStatus("Activating comparison mode ... ", true);
				if (!hasDatasetInfo(jsonResult[5],"officialName")) {
					loadDatasetInfo(jsonResult[5],"", false)
				}			
				if (currentState["datasetInfo"][jsonResult[5]]["isDefault"] == false) {
					setCurrentStatus("Activating comparison dataset ... ", true);
					if (jQuery.inArray(jsonResult[5],
							currentState["userDatasets"]) == -1) {
						// alert("Reference is user dataset not loaded")
						activateUserDatasetFunction(jsonResult[5], false,
								false, true)
					} else {
						// alert("Reference is user dataset already loaded")
						activateUserDatasetFunction(jsonResult[5], false,
								false, false)
					}
				}/* CHECK_FOR_MAJOR_REF_UPDATE */
				// alert("loading ref from link start")
								
				var refQueryParts = [];
				$.each(jsonResult[6].split("::qq::"), function(index,
						refQueryRefinementDescription) {
					setCurrentStatus("Activating comparison refinments ... ",
							true);
					// alert(refQueryRefinementDescription)
					if (refQueryRefinementDescription.startsWith("BASEREFQ")) {
					} else if (refQueryRefinementDescription
							.startsWith("Eregion")) {
						// alert("Skipped Eregion")
					} else {
						// refQueryDescriptions.push(getReadableFeatureText(refQueryRefinementDescription))
						// alert("Push "+refQueryRefinementDescription)
						refQueryParts.push(refQueryRefinementDescription)
					}
				})
				// alert(refQueryParts)
				// var refQuery = jsonResult[6].replace(/::qq::/g," ")
				// alert(refQuery)
				// referenceSelect(jsonResult[4],jsonResult[5],refQuery,refQueryDescriptions,false,false)
				referenceSelect(jsonResult[4], jsonResult[5], refQueryParts,
						false, false)
				// alert("loading ref from link end")

			}
		}
		setCurrentStatus("Fetching summary information ... ", true);
		// current view, currently not used
		if (jsonResult[3] != ""
				&& currentState["featuresElements"][jsonResult[3]] !== undefined) {
			loadVisualizationByID(jsonResult[3]);
		} else {
			updateCurrentSelectionOverlapPlot(true);
		}
		/*
		 * //Moved the ajax call to the start of the index.php } });
		 */
	}

}
/* ####----####---- Function ----####----#### */
function initExploreButtons() {
	/*
	 * //$('body').delegate(".visualizationDirectLink","click",function(){ //var
	 * query = $(this).text(); //loadVisualizationByID(query) //});
	 */

	// Converting the plots to PNG
	// $('#convertPlotToImage').button();
	// $('body').delegate("#convertPlotToImage","click",function(){
	// replaceCanvaswithImage(true);
	// });
	// the start default datasets slection
	$('body').delegate(".exploreDefaultDatasetsButton", "click",
			activateMode_ExploreRegionSelection);
	// The button that shows the input field for adding new dataset
	$('div.regions').delegate("td.showReloadUserDatasetButton", "click",
			function() {
				if ($("tr.reloadUserDatasetTD").is(":visible")) {
					$("tr.reloadUserDatasetTD").hide();
				} else {
					$("tr.reloadUserDatasetTD").show();
				}
				// $("#userDatasetID").focus();
			});
	// Load the upload page
	$("td.uploadNewDatasetButton").click(function() {
		// window.open('uploadManagement.php');
		showExternalPageInIFrame("upload.php")
	});
	// the export buttons
	$('body').delegate(
			".exportRegionsButton",
			"click",
			function() {
				var query = getQuery("::qq::", "Eregion", "main");
				// alert(query);
				var regiontype = currentState["exploreRegionSelected"];
				var w = window.open(
						"relay.php?type=exportRegionsAndSendBack&regiontype="
								+ regiontype + "&query=" + query, 'CGSExport',
						'');
				w.focus();
			});
	// use as reference button
	$('body').delegate(
			".useAsReferenceButton",
			"click",
			function() {
				// use the current query as reference
				$('#currentLinkLocation').text("")

				var refQueryRefinements = [];
				$.each($('span.queryPrefixRaw'), function(index, value) {
					refQueryRefinements.push($(value).text());
				});
				referenceSelect(settings["genome"],
						currentState["exploreRegionSelected"],
						refQueryRefinements, true, true)

			});
	$('body')
			.delegate(
					"td.toPNGButton",
					"click",
					function() {
						var width = 800;
						var height = 400
						var hiddenInputs = $(this).children('input:hidden');
						if (hiddenInputs.length == 3) {
							width = hiddenInputs[0].value;
							height = hiddenInputs[1].value;
							containerID = hiddenInputs[2].value;
						} else {
							alert("Error: wrong number of inputs")
							return;
						}
						var iframeBody = $('#' + containerID + ' iframe')
								.contents().find('body').html()
						if (iframeBody && iframeBody.length > 0) {
							var svgStart = iframeBody.indexOf("<svg");
							var svgEnd = iframeBody.indexOf("</svg>");
							var svgSource = iframeBody.substring(svgStart,
									svgEnd + 6);
							// alert(svgSource)
							// REPLACES THE SVG WITH CANVAS
							// $('#'+containerID).children().remove()
							// alert("removed")
							var hiddenCanvasElement = $('<canvas class="canvasChartElement" id="canvasPlot'
									+ containerID
									+ '" width="'
									+ width
									+ 'px" height="' + height + 'px"></canvas>');
							// REPLACES THE SVG WITH CANVAS //THE
							// canvasChartElement class defines it not to be
							// visible
							$('#' + containerID).append(hiddenCanvasElement)
							// alert("canvas added")
							canvg('canvasPlot' + containerID, svgSource)
							// alert("canvas converted")
							var canvasElement = document
									.getElementById('canvasPlot' + containerID);
							// alert(canvasElement)
							var canvasData = canvasElement
									.toDataURL("image/png");
							// alert("canvas data extracted")
							canvasData = canvasData.substr(
									canvasData.indexOf(',') + 1).toString();
							// alert("canvas data chnaged")

							var dataInput = document.createElement("input");
							dataInput.setAttribute("name", 'imgdata');
							dataInput.setAttribute("value", canvasData);
							// alert("input created")
							// var nameInput = document.createElement("input") ;
							// nameInput.setAttribute("name", 'name') ;
							// nameInput.setAttribute("value", fname + '.png');

							var myForm = document.createElement("form");
							myForm.method = 'post';
							myForm.action = "saveAsPNG.php";
							myForm.appendChild(dataInput);
							// myForm.appendChild(nameInput);
							// alert("form created")

							document.body.appendChild(myForm);
							myForm.submit();
							// alert("form submitted")
							document.body.removeChild(myForm);
							// alert("form deleted")
							hiddenCanvasElement.remove();
							// REPLACES THE SVG WITH CANVAS
							// $(this).children("a").hide();

						}
					});

	$('body').delegate("td.toCoverageBubbles", "click", function() {
		currentState["currentDefaultChart"] = "bubbles";
		updateCurrentSelectionOverlapPlot(false);
		$(this).remove();
	});
	
	$('body').delegate("td.toOverlapeBars", "click", function() {
		currentState["currentDefaultChart"] = "bars";
		updateCurrentSelectionOverlapPlot(false);
		$(this).remove();
	});
	$('body').delegate("div.editableNameBox","click",function(){
		var nameBox = $(this).parent(); 
		var referenceName = $(this).text();
		//alert(referenceName);
		nameBox.html("");
		var newInput = $('<input value="'+referenceName+'" size="25"/>');
		
		$(newInput).blur(function() {
			
  			var newReferenceName = $(newInput).val();  			
  			if (newReferenceName.length == 0){
  				newReferenceName = referenceName;
  			}
  			//alert(newReferenceName)
  			$(newInput).remove();
  			nameBox.html('<div class="editableNameBox">'+newReferenceName+'</div>')
		});
		nameBox.append(newInput)
		
	});
	$('body')
			.delegate(
					"td.toConfidenceIntervals",
					"click",
					function() {
						$('tr.showConfidenceIntervals').remove();

						if (!currentState["datasetInfo"][currentState["exploreRegionSelected"]]["hasBinning"]) {
							alert("Dataset does not support binning");
							return;
						}
						setCurrentStatus("Computing confidence data ...", true)
						// $("#currentStatus").append($('<img
						// name="progress_image_feature_plot"
						// src="extras/ajax-loader-big.gif"
						// class="progress_image_feature_plot" align="center"
						// alt="Processing..."></img>'));
						// $('#rangeFeaturePlot').html('<img
						// name="progress_image_feature_plot"
						// src="extras/ajax-loader-big.gif"
						// class="progress_image_feature_plot" align="center"
						// alt="Processing..."></img>');

						if (Object.keys(currentState["currentOverlapsStat"]).length == 0) {
							var regiontype = currentState["exploreRegionSelected"];
							// this relies on the fact that CS is started as
							// single threaded and hence the totla number query
							// will finish before the overlap query
							var query = getQuery(" ", settings["overlap"]
									+ ":*", "main");
							var overlapStatistics = {}
							var nQueryBins = 10;
							for ( var i = 1; i <= 10; i++) {
								var binRegions = "EregBin:" + i;
								var queryBin = query.replace(/Eregion/g,
										binRegions)
								answerQuery(
										regiontype,
										queryBin,
										settings['maxOverlapCompletions'],
										0,
										false,
										"",
										function(result) {
											totalNumber = parseInt(result[2],
													10);
											if (totalNumber == 0) {
												nQueryBins = nQueryBins - 1;
											}
											$
													.each(
															result[3],
															function(index,
																	value) {
																value = parseInt(
																		value,
																		10);
																if (overlapStatistics[index] === undefined) {
																	overlapStatistics[index] = [];
																}
																overlapStatistics[index]
																		.push(value
																				/ totalNumber);
															});

										});
							}

							if (nQueryBins == 0) {
								alert("No binning data available for this dataset");
								$('.progress_image_feature_plot').remove();
								setCurrentStatus(null, false);
								return;
							}
							currentState["currentOverlapsStat"] = {}
							$
									.each(
											overlapStatistics,
											function(index, value) {
												var osl = overlapStatistics[index].length;
												if (osl < nQueryBins) {
													for ( var j = 0; j < nQueryBins
															- osl; j++) {
														overlapStatistics[index]
																.push(0)
													}
												}
												currentState["currentOverlapsStat"][index] = getConfidenceStatistics(overlapStatistics[index]);
											});
						}

						// If there is reference update the reference data also
						if (currentState["referenceQuery"]["genome"] != "") {
							if (currentState["datasetInfo"][currentState["referenceQuery"]["dataset"]]["hasBinning"]) {
								if (Object
										.keys(currentState["referenceQuery"]["statvalues"]).length == 0) {
									// alert("Reference query values to be
									// retrieved");
									referenceQuery = currentState["referenceQuery"]["query"]
											.replace(/BASEREFQUERY/g,
													settings["overlap"] + ":*")

									var referenceOverlapStatistics = {}
									var nRefQueryBins = 10;
									for ( var i = 1; i <= 10; i++) {
										var binRegions = "EregBin:" + i;
										var refQueryBin = referenceQuery
												.replace(/Eregion/g, binRegions)
										answerQuery(
												currentState["referenceQuery"]["dataset"],
												refQueryBin,
												settings['maxOverlapCompletions'],
												0,
												false,
												"",
												function(result) {
													var totalNumber = parseInt(
															result[2], 10);
													if (totalNumber == 0) {
														nRefQueryBins = nRefQueryBins - 1;
													}
													$
															.each(
																	result[3],
																	function(
																			index,
																			value) {
																		value = parseInt(
																				value,
																				10);
																		if (referenceOverlapStatistics[index] === undefined) {
																			referenceOverlapStatistics[index] = [];
																		}
																		referenceOverlapStatistics[index]
																				.push(value
																						/ totalNumber);
																	});

												});
									}

									if (nRefQueryBins == 0) {
										alert("No binning data available for the reference dataset");
									} else {
										currentState["referenceQuery"]["statvalues"] = {}

										$
												.each(
														referenceOverlapStatistics,
														function(index, value) {
															var osl = referenceOverlapStatistics[index].length;
															if (osl < nRefQueryBins) {
																for ( var j = 0; j < nRefQueryBins
																		- osl; j++) {
																	referenceOverlapStatistics[index]
																			.push(0)
																}
															}
															currentState["referenceQuery"]["statvalues"][index] = getConfidenceStatistics(referenceOverlapStatistics[index]);
														});
									}
								}
							}
						}
						updateCurrentSelectionOverlapPlotOnlyColumnWithConfidenceGoogle()
						$('.progress_image_feature_plot').remove();
						setCurrentStatus(null, false);
						// updateCurrentSelectionOverlapPlotOnlyCandleStickGoogle();
					});

	// activate a user dataset
	$('body')
			.delegate(
					".activateUserDataset",
					"click",
					function() {
						var datasetID = $("#userDatasetID").val().trim();
						if (jQuery.inArray(datasetID,
								currentState["userDatasets"]) == -1) {
							activateUserDatasetFunction(datasetID, true, false,
									true);
						} else {
							$(".activateUserDatasetSpan").show();
							$(".activateUserDatasetSpan").text(
									"The dataset is already active").fadeOut(
									2000, function() {
										// $(".activateUserDatasetSpan").hide();
									});
						}
						$("#userDatasetID").val(
								"Paste here a dataset ID and press enter");
					});

	$('#toggleCheckBoxes').button().click(function() {
		// alert("Toggle");
		// $("#exportQueryDataForm").toggleCheckboxes(":not(#regionsCheckBox)");
		$("#exportQueryDataForm").toggleCheckboxes(":not(#regionsCheckBox)");
		// alert("Toggle");
	});
	$('#checkCheckBoxes').button().click(function() {
		// alert("Check");
		$("#exportQueryDataForm").checkCheckboxes(":not(#regionsCheckBox)");
		// alert("Check");
	});
	$('#uncheckCheckBoxes').button().click(function() {
		// alert("Uncheck");
		$("#exportQueryDataForm").unCheckCheckboxes(":not(#regionsCheckBox)");
		// alert("Uncheck");
	});

	// the OR clause delegations
	$('div.regions').delegate(".queryRefinementORButtonDeactive", "click",
			function() {
				activateORClause($(this), true);
			});
	$('div.regions').delegate(".queryRefinementORButtonActive", "click",
			function() {
				deactivateORClause($(this), true);
			});
	$('body').delegate(".showNext10Results", "click", function() {
		// add the progress image to the results
		// $('#resultsHitsListing > p').prepend($('<img
		// name="progress_image_hits" src="extras/ajax-loader.gif"
		// class="progress_image_hits" align="left" alt="Processing
		// ..."></img>'));
		// update the results
		// updateResultsAndDocuments(true,false);
	});

	$('body')
			.delegate(
					".selectGeneSymbol",
					"click",
					function() {
						var baseTerm = $("#exampleAutocomplete").val()
								.toUpperCase();
						// alert(baseTerm)
						var regex = /^[0-9A-Za-z]+$/;
						if (regex.test(baseTerm)) {
							// alert(goDescTerm);
							var refinement = '[Egn:*%23gS:' + baseTerm
									+ '*%20Egn:*]';
							var refinementDescription = "Overlapping with genes described by the symbol '"
									+ baseTerm + "*'"

							addResultsRefinementAndUpdate(
									refinementDescription, refinement, -1, true)
						} else {
							alert("This field must not be empty and must contain only letters and numbers");
						}
					});
	$('body').delegate(".referencelistingRefinementX", "click", function() {
		/* CHECK_FOR_MAJOR_REF_UPDATE */
		// alert("Refinment to be removed
		// "+currentState["referenceQuery"]["editable"])
		if (currentState["referenceQuery"]["editable"]) {
			currentState["referenceQuery"]["editable"] = false;
			$(this).parent().remove();
			var queryParts = [];
			$('span.referencePrefixRaw').each(function(index) {
				queryParts.push($(this).text())
			});
			currentState["referenceQuery"]["queryParts"] = queryParts;
			referenceUpdate(true, false);
			// currentState["referenceQuery"]["editable"] = true;
		}
		// alert("Finished with removing refinement")
	});
	// $('div.leftside').delegate("span.referencelistingRefinementX","hover",function(){
	// $(this).parent().toggleClass("pretty-hover");
	// });
	$('div.leftside').delegate("span.referencelistingRefinementX",
			"mouseenter", function() {
				$(this).parent().addClass("pretty-hover");
			});
	$('div.leftside').delegate("span.referencelistingRefinementX",
			"mouseleave", function() {
				$(this).parent().removeClass("pretty-hover");
			});
	
	$('body').delegate("td.opmenuTD","mouseenter",function(){
		var t = $(this).text();
		$('td div.opmenuTDText').text(t)
		$('td div.opmenuTDText').css("color","black");
	});	
	$('body').delegate("td.opmenuTD","mouseleave",function(){		
		$('td div.opmenuTDText').text("_")
		$('td div.opmenuTDText').css("color","#FFFFD0");
	});
	// $('#referenceListing').delegate("div.activeSearchBox
	// span.ui-icon-closethick","hover",function(){
	// $(this).parent().parent().toggleClass("pretty-hover");
	// });
	$('#referenceListing').delegate(
			"div.activeSearchBox span.ui-icon-closethick", "mouseenter",
			function() {
				$(this).parent().parent().addClass("pretty-hover");
			});
	$('#referenceListing').delegate(
			"div.activeSearchBox span.ui-icon-closethick", "mouseleave",
			function() {
				$(this).parent().parent().removeClass("pretty-hover");
			});
	// $('div.leftside').delegate("tr.queryRegions td
	// span.ui-icon-closethick","hover",function(){
	// $(this).parent().parent().parent().toggleClass("pretty-hover");
	// });
	$('div.leftside').delegate("tr.queryRegions td span.ui-icon-closethick",
			"mouseenter", function() {
				$(this).parent().parent().parent().addClass("pretty-hover");
			});
	$('div.leftside').delegate("tr.queryRegions td span.ui-icon-closethick",
			"mouseleave", function() {
				$(this).parent().parent().parent().removeClass("pretty-hover");
			});
	// $('div.leftside').delegate("tr.queryPrexix td
	// span.ui-icon-closethick","hover",function(){
	// $(this).parent().parent().toggleClass("pretty-hover");
	// });
	$('div.leftside').delegate("tr.queryPrexix td span.ui-icon-closethick",
			"mouseenter", function() {
				$(this).parent().parent().addClass("pretty-hover");
			});
	$('div.leftside').delegate("tr.queryPrexix td span.ui-icon-closethick",
			"mouseleave", function() {
				$(this).parent().parent().removeClass("pretty-hover");
			});
	$('body').delegate(
			".selectGeneName",
			"click",
			function() {
				var tdBase = $(this).parent().parent();
				// alert("Select this gene?");
				var trsublings = tdBase.children("td");
				// alert(trsublings.length);
				var geneID = $(trsublings[1]).text();
				var refinementDescription = "Overlapping with gene " + geneID
				// alert(refinementDescription);
				if ($(trsublings[2]).text().length > 0) {
					refinementDescription = refinementDescription + " ("
							+ $(trsublings[2]).text() + ")"
				}
				// alert(refinementDescription);
				addResultsRefinementAndUpdate(refinementDescription, "Egn:"
						+ geneID, -1, true)
			});
	$('body')
			.delegate(
					".selectGOName",
					"click",
					function() {
						var tdBase = $(this).parent().parent();
						// alert("Select this GO?");
						var trsublings = tdBase.children("td");
						// alert(trsublings.length);
						var goID = $(trsublings[1]).text();
						var refinementDescription = "Overlapping with genes annotated with "
								+ goID
						// alert(refinementDescription);
						if ($(trsublings[4]).text().length > 0) {
							refinementDescription = refinementDescription
									+ " (" + $(trsublings[4]).text() + ")"
						}
						// alert(refinementDescription);
						addResultsRefinementAndUpdate(refinementDescription,
								"gGO:" + goID, -1, true)
					});
	$('body')
			.delegate(
					".selectGOterm",
					"click",
					function() {

						// alert("Select this GO term?");
						var goDescTerm = $(this).find("input:hidden").val();
						// alert(goDescTerm);
						var refinement = '[gGO:*%23' + goDescTerm + '%20gGO:*]';
						// alert(refinement);
						var tdBase = $(this).parent().parent();
						var trsublings = tdBase.children("td");
						// alert(trsublings.length);
						var goterm = $(trsublings[1]).text();
						var refinementDescription = "Overlapping with genes annotated with GO described by '"
								+ goterm + "'"
						// alert(refinementDescription);
						// if ($(trsublings[4]).text().length > 0){
						// refinementDescription = refinementDescription + "
						// ("+$(trsublings[4]).text()+")"
						// }
						// alert(refinementDescription);
						addResultsRefinementAndUpdate(refinementDescription,
								refinement, -1, true)
					});
	$('body')
			.delegate(
					".selectOMIMName",
					"click",
					function() {
						var tdBase = $(this).parent().parent();
						// alert("Select this OMIM?");
						var trsublings = tdBase.children("td");
						// alert(trsublings.length);
						var omimID = $(trsublings[1]).text().split(":")[1];
						// alert(omimID)
						var refinementDescription = "Overlapping with genes annotated with "
								+ omimID
						// alert(refinementDescription);
						if ($(trsublings[4]).text().length > 0) {
							refinementDescription = refinementDescription
									+ " (" + $(trsublings[4]).text() + ")"
						}
						// alert(refinementDescription);
						addResultsRefinementAndUpdate(refinementDescription,
								"omimID:" + omimID, -1, true)
					});
	$('body')
			.delegate(
					".selectOMIMterm",
					"click",
					function() {

						// alert("Select this GO term?");
						var goDescTerm = $(this).find("input:hidden").val();
						// alert(goDescTerm);
						var refinement = '[omimID:*%23' + goDescTerm
								+ '%20omimID:*]';
						// alert(refinement);
						var tdBase = $(this).parent().parent();
						var trsublings = tdBase.children("td");
						// alert(trsublings.length);
						var goterm = $(trsublings[1]).text();
						var refinementDescription = "Overlapping with genes annotated with OMIM described by '"
								+ goterm + "'"
						// alert(refinementDescription);
						// if ($(trsublings[4]).text().length > 0){
						// refinementDescription = refinementDescription + "
						// ("+$(trsublings[4]).text()+")"
						// }
						// alert(refinementDescription);
						addResultsRefinementAndUpdate(refinementDescription,
								refinement, -1, true)
					});

	$('body')
			.delegate(
					".getLinkButton",
					"click",
					function() {
						// alert("About to get a link to the current selection")
						if (currentState["exploreRegionSelected"] == settings["defaultRegionSelected"]) {
							$('#currentLinkLocation').text(
									"No dataset selected")
							highlightElement($('#currentLinkLocation'), 700, 2);
							// $('#currentLinkLocation').text("")
							return;
						}
						var querySep = "::qq::";
						// var currentQuery = getQuery(querySep,"","main");
						var querySelector = 'span.queryPrefixRaw';
						var queryParts = [];
						$(querySelector).each(function(index) {
							queryParts.push($(this).text())
						});
						var currentQuery = queryParts.join(querySep)
						// There is an artificial Eregion before each query.
						// Remove it for the save mode
						while (currentQuery.startsWith("Eregion" + querySep)) {
							currentQuery = currentQuery
									.substr(("Eregion" + querySep).length)
						}
						var dataToBeSend = {
							"type" : "getLink",
							"genome" : settings["genome"],
							"currentSelection" : currentState["exploreRegionSelected"],
							"currentQuery" : currentQuery,
							"currentView" : currentState["featureCurrentVisualization"],
							"rGenome" : "",
							"rSelection" : "",
							"rQuery" : "",
							"rNORegions" : ""
						};
						if (currentState["referenceQuery"]["genome"] != "") {
							dataToBeSend["rGenome"] = currentState["referenceQuery"]["genome"];
							dataToBeSend["rSelection"] = currentState["referenceQuery"]["dataset"]
							dataToBeSend["rQuery"] = currentState["referenceQuery"]["query"]
									.replace(/ /g, querySep)
							dataToBeSend["rNORegions"] = currentState["referenceQuery"]["totalNumber"]
						}

						$
								.ajax({
									type : 'GET',
									url : "relay.php",
									data : dataToBeSend,
									dataType : "json",
									success : function(jsonResult) {
										if (jsonResult[0] == '0') {
											// success
											// url =
											// document.location.href+"?analysisLink="+jsonResult[1]
											var urlText = "http://epiexplorer.mpi-inf.mpg.de/index.php?analysisLink="
													+ jsonResult[1]
											$('#currentLinkLocation')
													.html(
															'<a href="'
																	+ urlText
																	+ '" target="_blank">'
																	+ urlText
																	+ '</a>')
										} else {
											$('#currentLinkLocation').text(
													jsonResult[1])
										}
									}
								});

					});
	$('#userDatasetID').keypress(function(e) {
		// e.preventDefault();
		if (e.which == 13) {
			$('.activateUserDataset').click();
		}
	});
	var loadUserDatasetText = "Paste here a dataset ID and press enter";
	$("#userDatasetID").attr("value", loadUserDatasetText);

	$("#userDatasetID").focus(function() {
		$(this).addClass("active");
		if ($(this).attr("value") == loadUserDatasetText)
			$(this).attr("value", "");
	});

	$("#userDatasetID").blur(function() {
		$(this).removeClass("active");
		if ($(this).attr("value") == "")
			$(this).attr("value", loadUserDatasetText);
	});

	$('#showWelcomePageInFrame').click(function() {
		showExternalPageInIFrame("welcome.php")
	})
	$('#showAboutPageInFrame').click(function() {
		showExternalPageInIFrame("about_epiexplorer.php")
	})
	$('#showCitePageInFrame').click(function() {
		showExternalPageInIFrame("cite.php")
	})
	$('#showUploadPageInFrame').click(function() {
		showExternalPageInIFrame("uploadManagement.php")
	})
	$('#showDownloadPageInFrame').click(function() {
		showExternalPageInIFrame("DownloadSourceCodeMain.php")
	})
	$('#presentationModeSwitch')
			.click(
					function() {
						if ($("div.leftside").is(":visible")) {
							$(
									'div.container span.ui-layout-resizer div.ui-layout-toggler')
									.click();
							// $("div.leftside").hide();
							$(this)
									.html(
											'<img src="extras/measure.png" class="menusubicon" alt="Presentation mode Off" />Presentation mode Off')
						} else {
							$(
									'div.container span.ui-layout-resizer div.ui-layout-toggler')
									.click();
							// $("div.leftside").show();
							$(this)
									.html(
											'<img src="extras/measure.png" class="menusubicon" alt="Presentation mode On"/>Presentation mode On')
						}
					})
	//upload dataset button		
	$(".exportToUCSCAsCustomTrack").click(function(){
		
		var ucscLink = "http://genome.ucsc.edu/cgi-bin/hgTracks?";
			ucscLink = ucscLink + "db=" + settings["genome"]			
			ucscLink = ucscLink
			+ "&hgt.customText="
			+ encodeURIComponent(getExportLink("UCSC"))
		window.open(ucscLink);		
	});
	$(".exportToEnsemblAsCustomTrack").click(function(){
		if (settings["genome"] == "hg18"){
			alert("Ensembl does not support custom tracks for hg18")
		}else{
			window.open(getExportLink("ENSEMBL"));	
		}
				
	});
	$(".exportToGalaxy").click(function(){
		window.open(getExportLink("GALAXY"));
	});
	$(".exportToHyperBrowser").click(function(){
		window.open(getExportLink("HYPERBROWSER"));
	});
	$(".gotoListingOfRegions").click(function(){
		$("div.featureRegionsList").click();
		//window.location.href = getExportLink("URL");
		
		//window.location.href = getExportLink("TEXTFILE");		
	});

}
function getExportLink(type){
	return "http://epiexplorer.mpi-inf.mpg.de/" +			
			"relay.php?type=exportRegionsAndSendBack&exportType="+type+"&regiontype="
					+ currentState["exploreRegionSelected"]
					+ "&query="
					+ getQuery("::qq::", "Eregion", "main")
					+ "&genome="
					+ settings["genome"]
}

function isDataset(datasetSimpleName) {
	var found = false;
	$.each(currentState["datasetInfo"], function(currentDatasetSimpleName, dataset) {
		if (datasetSimpleName == currentDatasetSimpleName) {
			found = true;
			return 0;
		}
	});
	
	return found;
}

function bubbleChartDefaultData()  {
	var data = new google.visualization.DataTable();

	data.addColumn('string', 'ID');
	data.addColumn('number', 'Genome coverage');
	data.addColumn('number', "Percent of overlapping regions");
	data.addColumn('string', 'Category');
	
	return data;
}

function bubbleChartDefaultDataComparison()  {
	var data = new google.visualization.DataTable();
	
	data.addColumn('string', 'ID');
	data.addColumn('number', "Percent of overlapping control set regions");
	data.addColumn('number', "Percent of overlapping regions");
	data.addColumn('string', 'Category');
	data.addColumn('number', 'Genome coverage');
	
	return data;
}

function bubbleChartDefaultOptions() {
	heightChart = 520;
	widthChart = 660;
	var options = {
		width : widthChart,
		height : heightChart,
		chartArea : {
			left : 60,
			right : 200,
			top:60,
			bottom:60,			
			width : widthChart - 60 - 200,
			height: heightChart - 60 - 60
		/* left */
		},
		legend : {position:"right",
				  textStyle: textStyles["legend"]},
		title : 'Association between dataset overlap and genome coverage of (epi)genomic annotations (tissue: '
				+ settings['tissue'] + ')',
		titleTextStyle:textStyles["mainTitle"],
		hAxis : {
			title : 'Genome coverage of (epi)genomic annotation',
			titleTextStyle:textStyles["axisTitle"],
			textStyle: textStyles["axisText"],
			format : '#,###%',
			minValue : 0,
			maxValue : 1
		},
		vAxis : {
			title : "Percent of regions overlapping with (epi)genomic annotation",
			titleTextStyle:textStyles["axisTitle"],
			textStyle: textStyles["axisText"],
			format : '#,###%',
			minValue : 0,
			maxValue : 1
		},
		bubble : {
			textStyle : {
				fontSize : 1,
				color : 'none'
			}
		},
		sizeAxis : {
			maxSize : 5,
			minSize : 5
		},
		forceIFrame: true
	};
	
	options['page'] = 'enable';
    options['pageSize'] = 25;
	
	return options;
}

function bubbleChartDefaultOptionsComparison() {
	heightChart = 520;
	widthChart = 660;
	var options = {
		width : widthChart,
		height : heightChart,
		chartArea : {
			left : 60,
			right : 200,
			top:60,
			bottom:60,			
			width : widthChart - 60 - 200,
			height: heightChart - 60 - 60
		/* left */
		},
		legend : {position:"right",
				  textStyle: textStyles["legend"]},
		title : 'Association between dataset overlap, control set overlap and genome coverage of (epi)genomic annotations',
		titleTextStyle:textStyles["mainTitle"],
		hAxis : {
			title : 'Percent of overlapping control set regions',
			titleTextStyle:textStyles["axisTitle"],
			textStyle: textStyles["axisText"],
			format : '#,###%',
			minValue : 0,
			maxValue : 1
		},
		vAxis : {
			title : "Percent of overlapping regions",
			titleTextStyle:textStyles["axisTitle"],
			textStyle: textStyles["axisText"],
			format : '#,###%',
			minValue : 0,
			maxValue : 1
		},
		sizeAxis : {
			title : 'Genome coverage of (epi)genomic annotation',			
			format : '#,###%',
			minValue : 0,
			maxValue : 5		
		},
		bubble : {
			textStyle : {
				fontSize : 1,
				color : 'none'
			}
		},
		forceIFrame: true
	};
	return options;
}

function bubbleChartCategoryPicker(categories) {
	
	var categoryNames = new Array();
	
	for (var key in categories)  {
		categoryNames.push(key);
	}
	
	var categoryPicker = new google.visualization.ControlWrapper({
		'controlType': 'CategoryFilter',
	    'containerId': 'categoryPickerClass',
	    'options': {
	    	'filterColumnLabel': 'Category',
	    	'ui': {
	    		'allowTyping': false,
	    		'allowMultiple': true,
	    		'selectedValuesLayout': 'aside'
	    	}
	    },
	    'state': {'selectedValues': categoryNames}
	});
	  
	return categoryPicker
}

function bubbleChartWrapper(data, options) {
	var chart = new google.visualization.ChartWrapper({
		'chartType' : 'BubbleChart',
		'containerId' : 'rangeFeaturePlot',
		'dataTable' : data,
		'options' : options
	});
	return chart;
}

function bubbleChartDashboard(categoryPicker, data, options) {
	var chart = bubbleChartWrapper(data, options);
	
	var categoryPickerBar = $('<tr ><td colspan="2" style="width:900px"><div id="categoryPickerClass"></div><br/></td></tr>')
	//$(categoryPickerBar).insertAfter('#rangeFeaturePlotTable tr:eq(0)');
	$(categoryPickerBar).insertAfter('#rangeFeaturePlot');
	
	var d = document.getElementById('rangeFeaturePlotMain');
	var dashboard = new google.visualization.Dashboard(d);
	
	dashboard.bind(categoryPicker, chart);
	dashboard.draw(data);

	currentState["activeChart"].push(chart);
	
	return chart;
}

function updateBubbleChart() {		
	if (currentState["referenceQuery"]["genome"] != "") {		
		if (isDataset(currentState["featureCurrentVisualization"]) == true) {
			chart = doDatasetBubbleChartComparison(currentState["featureCurrentVisualization"]);
		} else if ( isInSummary() ) {
			chart = doBubbleChartGenomeSummaryComparison();
		} else {
			chart = doCategoryBubbleChartComparison(currentState["featureCurrentVisualization"]);
		}
	} else {
		if (isDataset(currentState["featureCurrentVisualization"]) == true) {
			chart = doDatasetBubbleChart(currentState["featureCurrentVisualization"]);
		} else if ( isInSummary() ) {
			chart = doBubbleChartGenomeSummary();
		} else {
			chart = doCategoryBubbleChart(currentState["featureCurrentVisualization"]);
		}	
	}
	
		
	var difShow = $('<tr class="showTableLink"><td ><a href="#" onclick="return false">Show as table</a></td><td></td></tr>');
	difShow.click(function() {
		if (chart.getChartType() == "Table") {
			chart.setChartType('BubbleChart')
			chart.setOption("height", heightChart)
			$(".showTableLink a").text("Show as table");
			$('tr.toPNGRow').show()
		} else {
			chart.setChartType("Table");
			chart.setOption("height", null)
			$(".showTableLink a").text("Show as chart");
			$('tr.toPNGRow').hide()
		}
		chart.draw();
	});	
	$('.showTableLink').remove();
	$('#rangeFeaturePlotTable').append(difShow);
	// Image convertion
	$('tr.toPNGRow').remove();
	var toImageButton = $('<tr class="toPNGRow"><td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
			+ options["width"]
			+ '"/> <input type="hidden" value="'
			+ options["height"]
			+ '"/><input type="hidden" value="'
			+ chart.getContainerId() + '"/></td><td></td></tr>')
	$('#rangeFeaturePlotTable').append(toImageButton);	
}
function bubbleSortFunction(a,b){
	if(a[3] < b[3]){
		return -1;
	}else if(a[3] > b[3]){
		return 1;
	}else{
		return 0;
	}
}
function doBubbleChartGenomeSummary() {	
	count = 0;
	rows = new Array();
	categories = new Array();
			
	$.each(currentState["datasetInfo"], function(datasetSimpleName, dataset) {						
		if (dataset["coverage"] == undefined) {
			return 1;
		}
		
		tissuesCount = 0;
		$.each(dataset["coverage"], function(tissue, value) {
			tissuesCount += 1;
		});
		
		name = getTextForFeatureGroup(datasetSimpleName);		
		overlapMark = overlapMarks[datasetSimpleName];
		category = featureGroupCategories[datasetSimpleName];
		
		if (datasetSimpleName.search("repeat_masker") > 0) {
			category = new Array();
			category[0] = "Repeats";
		}
		
		if (category == undefined || category[0] == "") {
			category = new Array();
			category[0] = "Others";
		}
		
		if (category[0] == "Repeats" && settings["tissue"] == "any") {			
			$.each(dataset["coverage"], function(tissue, value) {		
				overlapKey = settings["overlap"] + ":" + overlapMark + ":" + tissue;
				overlapValue = currentState["currentOverlaps"][overlapKey];
					
				if (overlapValue == undefined) {
					return 1;
				}
					
				value = dataset["coverage"][tissue];
				percentageOverlap = overlapValue / currentState["totalNumberOfRegions"];
				var maxR = Math.round(1000 * percentageOverlap) / 10;
				overlap = {
					"v" : percentageOverlap,
					"f" : (maxR) + "%"
				};
				coverage = {
					"v" : value / 10000,
					"f" : (value / 100) + "%"
				};
				categoryText = getTextForFeatureGroup(overlapMark);
				if (overlapMark.indexOf(':') >= 0) {
					categoryText = overlapMark.split(":")[1];
				}
	            name = getOverlapLabels(overlapKey);
	            if (name == overlapKey) {
	                    name = datasetSimpleName;
	            }			
				rows[count] = [ name, coverage, overlap, categoryText];
				count++;
				categories[categoryText] = 1;
				});
		} 
		else {
		if (tissuesCount == 1) {
			value = dataset["coverage"]["any"];
			overlapKey = settings["overlap"] + ":" + overlapMark;
			overlapValue = currentState["currentOverlaps"][overlapKey];
						
			if (overlapValue == undefined) {
				return 1;
			}

			percentageOverlap = overlapValue / currentState["totalNumberOfRegions"];
			var maxR = Math.round(1000 * percentageOverlap) / 10;
			overlap = {
				"v" : percentageOverlap,
				"f" : (maxR) + "%"
			};
			coverage = {
				"v" : value / 10000,
				"f" : (value / 100) + "%"
			};				
						
			categoryText = getTextForFeatureGroup(category[0]);			
			rows[count] = [ name, coverage, overlap, categoryText ];
			count++;
			categories[categoryText] = 1;				
		} else {
			if (dataset["coverage"][settings["tissue"]] != undefined) {
				overlapKey = settings["overlap"] + ":" + overlapMark + ":" + settings["tissue"];
				overlapValue = currentState["currentOverlaps"][overlapKey];
				
				if (overlapValue == undefined) {
					return 1;
				}
			
				value = dataset["coverage"][settings["tissue"]];
				percentageOverlap = overlapValue / currentState["totalNumberOfRegions"];
				var maxR = Math.round(1000 * percentageOverlap) / 10;
				overlap = {
					"v" : percentageOverlap,
					"f" : (maxR) + "%"
				};
				coverage = {
					"v" : value / 10000,
					"f" : (value / 100) + "%"
				};
					
				categoryText = getTextForFeatureGroup(category[0]) ;
				rows[count] = [ name, coverage, overlap, categoryText];
				count++;
				categories[categoryText] = 1;
			}
		}
		}	
	});

	data = bubbleChartDefaultData();
	rows.sort(bubbleSortFunction)
	data.addRows(rows);	
	options = bubbleChartDefaultOptions();	
	var categoryPicker = bubbleChartCategoryPicker(categories);	
	var chart = bubbleChartDashboard(categoryPicker, data, options);

	return chart;
}
 
function doBubbleChartGenomeSummaryComparison() {	
	count = 0;
	rows = new Array();
	categories = new Array();
	
	count = 0;
	rows = new Array();
	categories = new Array();
		
	$.each(currentState["datasetInfo"], function(datasetSimpleName, dataset) {
		if (dataset["coverage"] == undefined) {
			return 1;
		}
				
		tissuesCount = 0;
		$.each(dataset["coverage"], function(tissue, value) {
			tissuesCount += 1;
		});
	
		overlapMark = overlapMarks[datasetSimpleName];
		category = featureGroupCategories[datasetSimpleName];
		
		if (datasetSimpleName.search("repeat_masker") > 0) {
			category = new Array();
			category[0] = "Repeats";
		}
		if (category == undefined || category[0] == "") {
			category = new Array();
			category[0] = "Others";
		}
		
		if (category[0] == "Repeats" && settings["tissue"] == "any") {			
			$.each(dataset["coverage"], function(tissue, value) {		
				overlapKey = settings["overlap"] + ":" + overlapMark + ":" + tissue;
				overlapValue = currentState["currentOverlaps"][overlapKey];
				overlapControlSetValue = currentState["referenceQuery"]["values"][overlapKey];
					
				if (overlapValue == undefined || overlapControlSetValue == undefined) {
					return 1;
				}
					
				value = dataset["coverage"][tissue];
				percentageOverlap = overlapValue / currentState["totalNumberOfRegions"];
				percentageOverlapControlSet = overlapControlSetValue / currentState["referenceQuery"]["totalNumber"];
				var maxR = Math.round(1000 * percentageOverlap) / 10;
				var maxS = Math.round(1000 * percentageOverlapControlSet) / 10;
				overlap = {
					"v" : percentageOverlap,
					"f" : (maxR) + "%"
				};
				overlapControlSet = {
						"v" : percentageOverlapControlSet,
						"f" : (maxS) + "%"
				};
				coverage = {
					"v" : value / 10000,
					"f" : (value / 100) + "%"
				};
				categoryText = getTextForFeatureGroup(overlapMark);
				if (overlapMark.indexOf(':') >= 0) {
					categoryText = overlapMark.split(":")[1];
				}
	            name = getOverlapLabels(overlapKey);
	            if (name == overlapKey) {
	            	name = datasetSimpleName;
	            }			
	            rows[count] = [ name, overlapControlSet,overlap, categoryText, coverage];
				count++;
				categories[categoryText] = 1;
				});
		} 
		else {
		if (tissuesCount == 1) {
			value = dataset["coverage"]["any"];
			overlapKey = settings["overlap"] + ":" + overlapMark;
			overlapValue = currentState["currentOverlaps"][overlapKey];
			overlapControlSetValue = currentState["referenceQuery"]["values"][overlapKey];
						
			if (overlapValue == undefined || overlapControlSetValue == undefined) {
				return 1;
			}
			
			percentageOverlap = overlapValue / currentState["totalNumberOfRegions"];
			percentageOverlapControlSet = overlapControlSetValue / currentState["referenceQuery"]["totalNumber"];							
			var maxR = Math.round(1000 * percentageOverlap) / 10;
			var maxS = Math.round(1000 * percentageOverlapControlSet) / 10;
				
			overlap = {
				"v" : percentageOverlap,
				"f" : (maxR) + "%"
			};
			overlapControlSet = {
				"v" : percentageOverlapControlSet,
				"f" : (maxS) + "%"
			};
			coverage = {
				"v" : value / 10000,
				"f" : (value / 100) + "%"
			};				
				
			name = getOverlapLabels(overlapKey);
			if (name == overlapKey) {
				name = datasetSimpleName;
			}
				
			categoryText = getTextForFeatureGroup(category[0]);			
			rows[count] = [ name, overlapControlSet,overlap, categoryText, coverage];
			count++;
			categories[categoryText] = 1;				
		} else {
			if (dataset["coverage"][settings["tissue"]] != undefined) {
				overlapKey = settings["overlap"] + ":" + overlapMark + ":" + settings["tissue"];
				overlapValue = currentState["currentOverlaps"][overlapKey];
				overlapControlSetValue = currentState["referenceQuery"]["values"][overlapKey];							
				
				if (overlapValue == undefined || overlapControlSetValue == undefined) {
					return 1;
				}
				
				value = dataset["coverage"][settings["tissue"]];
				percentageOverlap = overlapValue / currentState["totalNumberOfRegions"];
				percentageOverlapControlSet = overlapControlSetValue / currentState["referenceQuery"]["totalNumber"];
				var maxR = Math.round(1000 * percentageOverlap) / 10;
				var maxS = Math.round(1000 * percentageOverlapControlSet) / 10;
									
				overlap = {
					"v" : percentageOverlap,
					"f" : (maxR) + "%"
				};
				overlapControlSet = {
						"v" : percentageOverlapControlSet,
						"f" : (maxS) + "%"
				};
				coverage = {
						"v" : value / 10000,
						"f" : (value / 100) + "%"
				};
                
				name = getOverlapLabels(overlapKey);
                if (name == overlapKey) {
                        name = datasetSimpleName;
                }  
								
				categoryText = getTextForFeatureGroup(category[0]) ;
				rows[count] = [name, overlapControlSet, overlap, categoryText, coverage];
				count++;
				categories[categoryText] = 1;
			}
		}
		}
	});

	data = bubbleChartDefaultDataComparison();
	rows.sort(bubbleSortFunction)
	data.addRows(rows);	
	options = bubbleChartDefaultOptionsComparison();		
	var categoryPicker = bubbleChartCategoryPicker(categories);	
	var chart = bubbleChartDashboard(categoryPicker, data, options);

	return chart;
}

function doCategoryBubbleChart(currentCategory)  {
	count = 0;
	rows = new Array();
	categories = new Array();

	others = ["uw_DNaseI", "repeat_masker"];
	$.each(others, function(c, d) {
		if (currentCategory.indexOf(d) != -1) {
			currentCategory = "Others";
			return 0;
		} 
	});	
		
	$.each(currentState["datasetInfo"], function(datasetSimpleName, dataset) {		
		overlapMark = overlapMarks[datasetSimpleName];

		category = featureGroupCategories[datasetSimpleName];
		if (category == undefined || category[0] == "") {
			category = new Array();
			category[0] = "Others";
		}		

		if (currentCategory !== category[0]) {
			return 1;
		}		
		if (dataset["coverage"][settings["tissue"]] != undefined){
			tissue = settings["tissue"]
		//$.each(dataset["coverage"], function(tissue, value) {		
			overlapKey = settings["overlap"] + ":" + overlapMark + ":" + tissue;
			overlapValue = currentState["currentOverlaps"][overlapKey];
				
			if (overlapValue == undefined) {
				return 1;
			}
				
			value = dataset["coverage"][tissue];
			percentageOverlap = overlapValue / currentState["totalNumberOfRegions"];
			var maxR = Math.round(1000 * percentageOverlap) / 10;
			overlap = {
				"v" : percentageOverlap,
				"f" : (maxR) + "%"
			};
			coverage = {
				"v" : value / 10000,
				"f" : (value / 100) + "%"
			};
			categoryText = getTextForFeatureGroup(overlapMark);
			if (overlapMark.indexOf(':') >= 0) {
				categoryText = overlapMark.split(":")[1];
			}
            name = getOverlapLabels(overlapKey);
            if (name == overlapKey) {
                    name = getTextForFeatureGroup(datasetSimpleName);
            }			
			rows[count] = [ name, coverage, overlap, categoryText];
			count++;
			categories[categoryText] = 1;
			//});
		}			
	});

	data = bubbleChartDefaultData();
	rows.sort(bubbleSortFunction)
	data.addRows(rows);	
	options = bubbleChartDefaultOptions();	
	options["title"] = 'Association between dataset overlap with ' + getTextForFeatureGroup(currentCategory)+ ' and genome coverage of ' + getTextForFeatureGroup(currentCategory);
	var categoryPicker = bubbleChartCategoryPicker(categories);	
	var chart = bubbleChartDashboard(categoryPicker, data, options);

	return chart;
}

function doCategoryBubbleChartComparison(currentCategory)  {
	count = 0;
	rows = new Array();
	categories = new Array();

	others = ["uw_DNaseI", "repeat_masker"];
	$.each(others, function(c, d) {
		if (currentCategory.indexOf(d) != -1) {
			currentCategory = "Others";
			return 0;
		} 
	});	
	
	$.each(currentState["datasetInfo"], function(datasetSimpleName, dataset) {		
		//name = getTextForFeatureGroup(datasetSimpleName);
		
		overlapMark = overlapMarks[datasetSimpleName];
		category = featureGroupCategories[datasetSimpleName];
		if (category == undefined || category[0] == "") {
			category = new Array();
			category[0] = "Others";
		}
		
		if (currentCategory !== category[0]) {
			return 1;
		}		
		if (dataset["coverage"][settings["tissue"]] != undefined){
			tissue = settings["tissue"]
		//$.each(dataset["coverage"], function(tissue, value) {		
			overlapKey = settings["overlap"] + ":" + overlapMark + ":" + tissue;
			overlapValue = currentState["currentOverlaps"][overlapKey];
			overlapControlSetValue = currentState["referenceQuery"]["values"][overlapKey];	
			
			if (overlapValue == undefined || overlapControlSetValue == undefined) {
				return 1;
			}
			
			value = dataset["coverage"][tissue];
			percentageOverlap = overlapValue / currentState["totalNumberOfRegions"];
			percentageOverlapControlSet = overlapControlSetValue / currentState["referenceQuery"]["totalNumber"];
				
			var maxR = Math.round(1000 * percentageOverlap) / 10;
			var maxS = Math.round(1000 * percentageOverlapControlSet) / 10;
				
			overlap = {
				"v" : percentageOverlap,
				"f" : (maxR) + "%"
			};
			overlapControlSet = {
				"v" : percentageOverlapControlSet,
				"f" : (maxS) + "%"
			};
			coverage = {
				"v" : value / 10000,
				"f" : (value / 100) + "%"
			};
								
			categoryText = getTextForFeatureGroup(overlapMark);
			if (overlapMark.indexOf(':') >= 0) {
				categoryText = overlapMark.split(":")[1];
			}
			name = getOverlapLabels(overlapKey);
            if (name == overlapKey) {
                    name = getTextForFeatureGroup(datasetSimpleName);
            }
			
			rows[count] = [name, overlapControlSet, overlap, categoryText, coverage];
			count++;
			categories[categoryText] = 1;
			//});
			}		
	});

	data = bubbleChartDefaultDataComparison();
	rows.sort(bubbleSortFunction)
	data.addRows(rows);	
	options = bubbleChartDefaultOptionsComparison();		
	options["title"] = 'Association between main and control datasets overlap with ' + getTextForFeatureGroup(currentCategory)+ ' and genome coverage of ' + getTextForFeatureGroup(currentCategory);
	var categoryPicker = bubbleChartCategoryPicker(categories);	
	var chart = bubbleChartDashboard(categoryPicker, data, options);

	return chart;	
}

function doDatasetBubbleChart(datasetName) {
	count = 0;
	rows = new Array();
	categories = new Array();
		
	dataset = currentState["datasetInfo"][datasetName];		

	overlapMark = overlapMarks[datasetName];
	if (overlapMark == undefined) {
		overlapMark = datasetSimpleName;
	}

	$.each(dataset["coverage"], function(tissue, value) {		
		if (dataset["coverage"][tissue] != undefined) {
			overlapKey = settings["overlap"] + ":" + overlapMark + ":" + tissue;
			overlapValue = currentState["currentOverlaps"][overlapKey];
					
			if (overlapValue == undefined) {
				return 1;
			}
				
			if (overlapMark == "" || overlapValue == undefined || overlapValue == 'undefined') {
				alert(datasetSimpleName);
				alert(overlapKey);
				alert(overlapValue);
			} else {
				value = dataset["coverage"][tissue];
				percentageOverlap = overlapValue / currentState["totalNumberOfRegions"];
				var maxR = Math.round(1000 * percentageOverlap) / 10;
				overlap = {
					"v" : percentageOverlap,
					"f" : (maxR) + "%"
				};
				coverage = {
					"v" : value / 10000,
					"f" : (value / 100) + "%"
					};						
				categoryText = tissue ;
				name = getOverlapLabels(overlapKey);
				if (name == overlapKey) {
					name = datasetSimpleName;
				}				
				rows[count] = [name, coverage, overlap, categoryText];
				count++;
				categories[categoryText] = 1;				
			}
		}
	});

	data = bubbleChartDefaultData();
	rows.sort(bubbleSortFunction)
	data.addRows(rows);	
	options = bubbleChartDefaultOptions();		
	options["title"] = 'Association between dataset overlap with ' + getTextForFeatureGroup(datasetName) + ' and genome coverage of ' + getTextForFeatureGroup(datasetName);
	var categoryPicker = bubbleChartCategoryPicker(categories);	
	var chart = bubbleChartDashboard(categoryPicker, data, options);

	return chart;
}

function doDatasetBubbleChartComparison(datasetName) {
	count = 0;
	rows = new Array();
	categories = new Array();
		
	dataset = currentState["datasetInfo"][datasetName];		

	overlapMark = overlapMarks[datasetName];
	if (overlapMark == undefined) {
		overlapMark = datasetSimpleName;
	}
			
	$.each(dataset["coverage"], function(tissue, value) {		
		if (dataset["coverage"][tissue] != undefined) {
			overlapKey = settings["overlap"] + ":" + overlapMark + ":" + tissue;
			overlapValue = currentState["currentOverlaps"][overlapKey];
			overlapControlSetValue = currentState["referenceQuery"]["values"][overlapKey];			
			
			// Workarround to show values for Eoverlaps50p.  && overlapKey == "Eoverlaps50p:repeats:any"
			if (overlapValue == undefined) {
				return 1;
			}
			
			if (overlapControlSetValue == undefined) {
				return 1;
			}			
				
			if (overlapMark == "" || overlapValue == undefined || overlapValue == 'undefined') {
				alert(datasetSimpleName);
				alert(overlapKey);
				alert(overlapValue);
			} else {
				value = dataset["coverage"][tissue];
				percentageOverlap = overlapValue / currentState["totalNumberOfRegions"];
				percentageOverlapControlSet = overlapControlSetValue / currentState["referenceQuery"]["totalNumber"];
				
				var maxR = Math.round(1000 * percentageOverlap) / 10;
				var maxS = Math.round(1000 * percentageOverlapControlSet) / 10;
				
				overlap = {
					"v" : percentageOverlap,
					"f" : (maxR) + "%"
				};				
				overlapControlSet = {
						"v" : percentageOverlapControlSet,
						"f" : (maxS) + "%"
				};
				coverage = {
					"v" : value / 10000,
					"f" : (value / 100) + "%"
					};						
				categoryText = tissue;
				name = getOverlapLabels(overlapKey);
				if (name == overlapKey) {
					name = datasetSimpleName;
				}
				rows[count] = [name, overlapControlSet, overlap, categoryText, coverage];
				count++;
				categories[categoryText] = 1;				
			}
		}
	});

	data = bubbleChartDefaultDataComparison();
	rows.sort(bubbleSortFunction)
	data.addRows(rows);	
	options = bubbleChartDefaultOptionsComparison();
	options["title"] = 'Association between main and control dataset overlap with ' + getTextForFeatureGroup(datasetName) + 'and genome coverage of ' + getTextForFeatureGroup(datasetName);
	var categoryPicker = bubbleChartCategoryPicker(categories);	
	var chart = bubbleChartDashboard(categoryPicker, data, options);

	return chart;
}

/* ####----####---- Function ----####----#### */
function initEventDelegationRegionsTable() {
	// add visual support for hovering over a region element
	// $('.regions').delegate(".regionsButtonHover",'hover',function(){
	// $(this).toggleClass("pretty-hover");
	// });
	$('.regions').delegate(".regionsButtonHover", 'mouseenter', function() {
		$(this).addClass("pretty-hover");
	});
	$('.regions').delegate(".regionsButtonHover", 'mouseleave', function() {
		$(this).removeClass("pretty-hover");
	});
	// $('div.visualization').delegate("td
	// div.ui-icon-play",'hover',function(event){
	// $(this).parent().parent().removeClass("google-visualization-table-tr-over")
	// $(this).parent().parent().toggleClass("pretty-hover");
	// });
	$('div.visualization').delegate(
			"td div.ui-icon-play",
			'mouseenter',
			function(event) {
				$(this).parent().parent().removeClass(
						"google-visualization-table-tr-over")
				$(this).parent().parent().addClass("pretty-hover");
			});
	$('div.visualization').delegate("td div.ui-icon-play", 'mouseleave',
			function(event) {
				// $(this).parent().parent().removeClass("google-visualization-table-tr-over")
				$(this).parent().parent().removeClass("pretty-hover");
			});

	// Check if the user uses iPad
	// var ua = navigator.userAgent,event = (ua.match(/iPad/i)) ? "touchstart" :
	// "click";
	// add the functionality if a region button is clicked
	$('.regions')
			.delegate(
					".regionsetInfoButton",
					"click",
					function() {
						var regionName = $(this).children("input:hidden")[0].value;
						currentState["exploreRegionSelected"] = regionName;
						currentState["currentOverlaps"] = settings["defaultCurrentOverlaps"];
						currentState["currentOverlapsStat"] = settings["defaultCurrentOverlapStats"];
						currentState["currentNeighborhood"] = settings["defaultCurrentOverlaps"];
						$('#currentLinkLocation').text("")
						showInfoRegionSet(regionName, currentState["exploreRegionSelected"] != regionName);
						currentState["totalNumberOfRegions"] = currentState["datasetInfo"][currentState["exploreRegionSelected"]]["numberOfRegions"];
						initCurrentDatasetData();
						updateCurrentSelectionOverlapPlot(false);																	
						// remove the link
						$('#currentLinkLocation').text("")						
					});
	// Here the shortcut key activates both the info box and the
	// selection fo the region set
	$('.regions').delegate(
			".regionsetSelectButton",
			"mouseenter",
			function() {
				$(this).parent().children("td.regionsetSelectButton").css(
						"background-color", "#F7E7D7");
				// $(this).parent().find("td.regionsetSelectButton
				// div.selectDatasetText").css("color","#000000");
			});
	$('.regions').delegate(
			".regionsetSelectButton",
			"mouseleave",
			function() {
				$(this).parent().children("td.regionsetSelectButton").css(
						"background-color", "transparent");
				// $(this).parent().find("td.regionsetSelectButton
				// div.selectDatasetText").css("color","#FFFFD0");
			});

	$('.regions')
			.delegate(
					".regionsetSelectButton",
					"click",
					function() {
						if (settings["showRefinementNotification"] == "true"){
							title = "Exploring a dataset"
							message = "You have chosen to epiexplore the properties of a dataset.<br/><br/>"
							message += "The left panel will be updated with genetic and epigenetic annotations for which you can visualize and refine the properties of your dataset.<br/><br/>"
							message += "At any point you can go back to the dataset selection menu by choosing the back button in the top-left corner or pressing the X on the right of the dataset.<br/><br/>"							
							showRefinementNotification(title,message);
						}
						var regionName = $(this).children("input:hidden")[0].value;						
						currentState["exploreRegionSelected"] = regionName;
						currentState["currentOverlaps"] = settings["defaultCurrentOverlaps"];
						currentState["currentOverlapsStat"] = settings["defaultCurrentOverlapStats"];
						currentState["currentNeighborhood"] = settings["defaultCurrentOverlaps"];
						// remove the link
						$('#currentLinkLocation').text("")
						currentState["totalNumberOfRegions"] = currentState["datasetInfo"][currentState["exploreRegionSelected"]]["numberOfRegions"];

						activateMode_ExploreRegionChosen(false);
						showInfoRegionSet(
								regionName,
								currentState["exploreRegionSelected"] != regionName);
						updateCurrentSelectionOverlapPlot(false);
						$('.regionSelectionLinkFromInfoBox').remove();
					});
	$('.regions')
			.delegate(
					".compareDatasetButton",
					"click",
					function() {						
						var regionName = $(this).children("input:hidden")[0].value;
						//alert("select "+regionName+" for comparison")
						referenceSelect(settings["genome"], regionName, [], false, false);
					});
	/*
	 * $('.regions').delegate(".removeUserDataset","click",function(event){
	 * event.stopPropagation(); alert("Remove custom dataset") });
	 */
	$('body').delegate(".hoverChangeIcon", "mouseenter", function(event) {
		var cimg = $(this).children("img")[0];
		$(cimg).attr("src", $(cimg).attr("src").split(".").join("-hover."));
	});
	$('body').delegate(".hoverChangeIcon", "mouseleave", function(event) {
		var cimg = $(this).children("img")[0];
		$(cimg).attr("src", $(cimg).attr("src").split("-hover.").join("."));
	});

}
/* ####----####---- Function ----####----#### */
function initEventDelegationFeatureListing() {
	// add visual support for hovering over a region element
	$('.features').delegate(".featureHover", 'hover', function() {
		// alert("Feature hovering");
		$(this).toggleClass("pretty-hover");
	});
	$('body').delegate('#openedFeatureResults tr.listResults', 'hover',
			function() {
				$(this).toggleClass("pretty-hover");//
				$(this).toggleClass("ui-corner-all");
			});
	// make sure there is always maximum one box open
	// $('.features').delegate(".featureBoxClosed","click",openBox);

	// make sure that if an closed branch is clicked, it opened all its children
	// $('.features').delegate(".featureBranchClosed > h4","click",openBranch);

}

function addFeatureGroupsToParentElement(groupName, groupData, parentElement,
		level) {
	// alert("START group initialization "+groupName);
	var featureContainer = $('<div></div>');
	var featureClass = "featureBranch";
	featureContainer.addClass(featureClass);
	featureContainer.addClass(featureClass + "Closed");
	// alert(1)
	var groupNameOfficial = getTextForFeatureGroup(groupName);
	var header = $('<h4 class="featureBox ui-corner-all" style="padding-left:'
			+ settings["standardIdentation"] * level + 'px;">'
			+ groupNameOfficial + '</h4>');
	header.addClass("featureHover");
	featureContainer.append(header);
	header
			.prepend($('<div class="ui-icon ui-icon-plusthick" style="float:left;"></div>'));
	var newDivHiddenValueGroupName = $('<input type="hidden" class="'
			+ featureClass + 'Name" value="' + groupName + '"></input>');
	header.append(newDivHiddenValueGroupName);
	// alert(2)
	var groupNameOverlap = getOverlapSummaryForGroup(groupName);
	if (groupNameOverlap != "") {
		var newDivHiddenValueQueryPrefix = $('<input type="hidden" class="'
				+ featureClass + 'OverlapPrefixes" value="' + groupNameOverlap
				+ '"></input>');
		featureContainer.append(newDivHiddenValueQueryPrefix);
	}
	parentElement.append(featureContainer);
	currentState["featuresElements"][groupName] = header
	// alert("START group children "+groupName);
	// alert(3)
	var featureOrder = [];
	$.each(groupData, function(gName, gData) {
		featureOrder.push([ getGroupOrderElem(gName), gName ])
	});
	featureOrder.sort()

	$.each(featureOrder, function(index, gNameOrder) {
		var gName = gNameOrder[1];
		var gData = groupData[gName];
		// $.each(groupData,function( gName, gData ){
		if (gName != "featureBox") {
			addFeatureGroupsToParentElement(gName, gData, featureContainer,
					level + 1)
		} else {
			addFeatureBoxesToParentElement(gName, gData, featureContainer,
					level + 1)
		}
	});

	// alert("END group initialization "+groupName);
}
function addFeatureBoxesToParentElement(featureName, featureData,
		parentElement, level) {
	// alert("START featureBox ");
	var featureOrder = [];
	$.each(featureData, function(index, featureBoxData) {
		featureOrder.push([ getGroupOrderElem(featureBoxData[0]), index ])
	});
	featureOrder.sort()
	// alert(featureOrder)

	$
			.each(
					featureOrder,
					function(index, gNameOrder) {
						var index = gNameOrder[1];
						var featureBoxData = featureData[index];
						// $.each(featureData,function( index, featureBoxData ){
						// alert("START " +featureBoxData);
						var featureContainer = $('<div></div>');
						var featureClass = "featureBox";
						featureContainer.addClass(featureClass);
						featureContainer.addClass(featureClass + "Closed");
						var featureNameOfficial = getTextForFeaturePrefix(featureBoxData[0]);
						var header = $('<h4 class="featureBox ui-corner-all" style="padding-left:'
								+ settings["standardIdentation"]
								* level
								+ 'px;">' + featureNameOfficial + '</h4>');
						header.addClass("featureHover");
						if (level == 0) {
							var newDivHiddenValueGroupName = $('<input type="hidden" class="'
									+ featureClass
									+ 'Name" value="'
									+ featureBoxData[0] + '"></input>');
							header.append(newDivHiddenValueGroupName);
						}
						featureContainer.append(header);
						header
								.prepend($('<div class="ui-icon ui-icon-search" style="float:left;"></div>'));
						var featureType = getTypeForFeaturePrefix(featureBoxData[0]);
						// if (featureType == "featureText"){
						// header.append($('<div class="ui-icon ui-icon-play"
						// style="float:right;"></div>'));
						// }
						featureContainer.addClass(featureType);
						if (featureType == "featureText"
								|| featureType == "featureRange"
								|| featureType == "featureRatio"
								|| featureType == "featureNeighborhood") {
							var newDivHiddenValueQueryPrefix = $('<input type="hidden" value="'
									+ featureBoxData[0] + '"></input>');
							var newDivHiddenValueBoxType = $('<input type="hidden" value="'
									+ featureType + '"></input>');
							featureContainer
									.append(newDivHiddenValueQueryPrefix);
							featureContainer.append(newDivHiddenValueBoxType);
							if (featureType == "featureText"
									&& featureBoxData.length > 1) {
								var inDepthFeatureType = getTypeForFeaturePrefix(featureBoxData[1]);
								var newDivHiddenRefValueQuery = $('<input type="hidden" value="'
										+ featureBoxData[1] + '"></input>');
								var newDivHiddenRefValueBoxType = $('<input type="hidden" value="'
										+ inDepthFeatureType + '"></input>');
								featureContainer
										.append(newDivHiddenRefValueQuery);
								featureContainer
										.append(newDivHiddenRefValueBoxType);
							} else if (featureType == "featureRange"
									&& featureBoxData.length == 3) {
								var newDivHiddenRefNumberOfDigits = $('<input type="hidden" value="'
										+ featureBoxData[1] + '"></input>');
								var newDivHiddenRefValueBase = $('<input type="hidden" value="'
										+ featureBoxData[2] + '"></input>');
								featureContainer
										.append(newDivHiddenRefNumberOfDigits);
								featureContainer
										.append(newDivHiddenRefValueBase);
							} else if (featureType == "featureRatio"
									&& featureBoxData.length == 3) {
								var newDivHiddenRefNumberOfDigits = $('<input type="hidden" value="'
										+ featureBoxData[1] + '"></input>');
								var newDivHiddenRefValueBase = $('<input type="hidden" value="'
										+ featureBoxData[2] + '"></input>');
								featureContainer
										.append(newDivHiddenRefNumberOfDigits);
								featureContainer
										.append(newDivHiddenRefValueBase);
							} else if (featureType == "featureNeighborhood"
									&& featureBoxData.length == 3) {
								var newDivHiddenRefBeforeStart = $('<input type="hidden" value="'
										+ featureBoxData[1] + '"></input>');
								var newDivHiddenRefAfterEnd = $('<input type="hidden" value="'
										+ featureBoxData[2] + '"></input>');
								featureContainer
										.append(newDivHiddenRefBeforeStart);
								featureContainer
										.append(newDivHiddenRefAfterEnd);
							}
						} else if (featureType == "featureTable") {
							var parts = [];
							if (featureBoxData[0]
									.startsWith("GENENAME:ENSEMBL")) {
								// http://infao3806:9130/?q=[Eregion%20Egn:*%23gene%20Egn:*]
								// gene&c=200&h=0
								parts = [ "gene", "Egn:*", "gene" ];
							} else if (featureBoxData[0].startsWith("GO:ALL")) {
								// http://infao3806:9130/?q=[gGO:*%23GOterm%20gGO:*]%20GOterm&c=0&h=100
								// parts = ["gGO:*","gGO:*","GOterm"];
								parts = [ "", "gGO:*",
										"GOterm gGONG:000--gGONG:999" ];
							} else if (featureBoxData[0].startsWith("GO:TERMS")) {
								// http://infao3806:9130/?q=[Eregion%20gGO:*%23GOterm%20gGO:*]%20gGO:*&c=200&h=0
								parts = [ "gGOd:*", "gGO:*", "GOterm" ];
							} else if (featureBoxData[0].startsWith("OMIM:ALL")) {
								// http://infao3806:9130/?q=[gGO:*%23GOterm%20gGO:*]%20GOterm&c=0&h=100
								// parts = ["omimID:*","omimID:*","omim"];
								parts = [ "", "omimID:*",
										"omim gOMIMNG:00--gOMIMNG:99" ];
							} else if (featureBoxData[0]
									.startsWith("OMIM:TERMS")) {
								// http://infao3806:9130/?q=[Eregion%20omimID:*%23omim%20omimID:*]%20omimD:*&c=200&h=0
								parts = [ "omimD:*", "omimID:*", "omim" ];
							}
							var newDivHiddenValueQueryPrefix = $('<input type="hidden" value="'
									+ featureBoxData[0] + '"></input>');
							var newDivHiddenValueBoxType = $('<input type="hidden" value="'
									+ featureType + '"></input>');
							var newDivHiddenRefMainQuery = $('<input type="hidden" value="'
									+ parts[0] + '"></input>');
							var newDivHiddenRefJoinField = $('<input type="hidden" value="'
									+ parts[1] + '"></input>');
							var newDivHiddenRefJoinPart = $('<input type="hidden" value="'
									+ parts[2] + '"></input>');
							featureContainer
									.append(newDivHiddenValueQueryPrefix);
							featureContainer.append(newDivHiddenValueBoxType);
							featureContainer.append(newDivHiddenRefMainQuery);
							featureContainer.append(newDivHiddenRefJoinField);
							featureContainer.append(newDivHiddenRefJoinPart);
						} else if (featureType == "featureRegionsList") {
							var newDivHiddenValueQueryPrefix = $('<input type="hidden" value="Eregion"></input>');
							var newDivHiddenValueBoxType = $('<input type="hidden" value="'
									+ featureType + '"></input>');
							featureContainer
									.append(newDivHiddenValueQueryPrefix);
							featureContainer.append(newDivHiddenValueBoxType);
						}
						parentElement.append(featureContainer);
						currentState["featuresElements"][featureBoxData[0]] = featureContainer

					});
	// alert("END featureBox");
}
function processFeatureArray(featuresArray) {

	currentState["featuresElements"] = {};	
	updateCurrentVisualization(settings["genome"] + "summary",false);
	$('.features').children().remove()
	var featureListingRoot = $('<div id="featureListingTree"></div>');
	$('.features').append(featureListingRoot);
	var featureOrder = [];
	$.each(featuresArray, function(gName, gData) {
		featureOrder.push([ getGroupOrderElem(gName), gName ])
	});
	featureOrder.sort()
	// alert(featureOrder);
	var horizontalline = true;
	$
			.each(
					featureOrder,
					function(index, gNameOrder) {
						var gName = gNameOrder[1];
						var gData = featuresArray[gName];
						// $.each(featuresArray,function( gName, gData ){
						// alert("START processing "+gName);
						if ((horizontalline && gNameOrder[0] >= 40)
								|| gNameOrder[0] == 99) {
							featureListingRoot
									.append($('<hr class="dottedlineTransparent"></hr>'));
							horizontalline = false;
						}
						if (gName != "featureBox") {
							addFeatureGroupsToParentElement(gName, gData,
									featureListingRoot, 0)
						} else {
							addFeatureBoxesToParentElement(gName, gData,
									featureListingRoot, 0)
						}
						// alert("END processing "+gName);
					});
	// alert("END feature array initialization");
	// hide all branches
	$(".featureBranchClosed").children("div").hide();
	// closeOpenFeatureBox();
	// make sure that if an closed branch is clicked, it opened all its children
	// $(".featureBranchClosed > h4").one("click",featureOpenBranch);
	$(".featureBranchClosed > h4").click(function() {
		featureOpenBranch(this, true);
	});
	// make sure there is always maximum one box open
	$(".featureBoxClosed").one("click", featureOpenBox);

}

function initFeatures(refresh) {
	// alert("InitFeatures default");
	// $('.features').html('<h2 class="boxheader">Explore the dataset
	// properties</h2>');
	if (currentState["datasetFeatures"][currentState["exploreRegionSelected"]] !== undefined) {
		if (refresh) {
			// alert("START Refreshing local")
			processFeatureArray(currentState["datasetFeatures"][currentState["exploreRegionSelected"]]);
			// alert("END Refreshing local")
		}
	} else {
		$
				.ajax({
					type : "GET",
					url : "relay.php",
					async : false,
					dataType : "json",
					data : "type=getfeatures&regiontype="
							+ currentState["exploreRegionSelected"]
							+ "&genome=" + settings["genome"],
					success : function(featureArray) {
						currentState["datasetFeatures"][currentState["exploreRegionSelected"]] = featureArray;
						if (refresh) {
							// alert("START Refreshing remote")
							processFeatureArray(featureArray);
							// alert("END Refreshing remote")
						}
					}
				});
	}
}

function autoCompleteCallbackGOterm(response, callback) {
	// alert("autocomplete GO term");
	var baseTerm = response.term.toUpperCase();
	var regex = /^[0-9A-Za-z]*$/;
	if (regex.test(baseTerm)) {
		var otherParameters = [ "GO:TERMS:", "gGOd:" + baseTerm + "*", "gGO:*",
				"GOterm", false ]
		var query = getQueryComplexJoin(" ", "Eregion", otherParameters[1],
				otherParameters[2], otherParameters[3])
		updateOpenedFeatureCore("featureTable",
				currentState["exploreRegionSelected"], query, 200, 0, "",
				otherParameters);
	} else {
		alert("This field allows only letters and numbers")
	}
}
function autoCompleteCallbackOMIMterm(response, callback) {
	// alert("autocomplete GO term");
	var baseTerm = response.term.toUpperCase();
	var regex = /^[0-9A-Za-z]*$/;
	if (regex.test(baseTerm)) {
		var otherParameters = [ "OMIM:TERMS:", "omimD:" + baseTerm + "*",
				"omimID:*", "omim", false ]
		var query = getQueryComplexJoin(" ", "Eregion", otherParameters[1],
				otherParameters[2], otherParameters[3])
		updateOpenedFeatureCore("featureTable",
				currentState["exploreRegionSelected"], query, 200, 0, "",
				otherParameters);
	} else {
		alert("This field allows only letters and numbers")
	}

}
function autoCompleteCallbackGene(response, callback) {
	parts = [ "gene", "Egn:*", "gene" ];
	// alert("autocomplete GO term");
	var baseTerm = response.term.toUpperCase();
	var regex = /^[0-9A-Za-z]*$/;
	if (regex.test(baseTerm)) {
		var otherParameters = [ "GENENAME:ENSEMBL:",
				"gS:" + baseTerm + "* gene", "Egn:*", "gene", false ]
		var query = getQueryComplexJoin(" ", "Eregion", otherParameters[1],
				otherParameters[2], otherParameters[3])
		updateOpenedFeatureCore("featureTable",
				currentState["exploreRegionSelected"], query, 0, 200, "",
				otherParameters);
	} else {
		alert("This field allows only letters and numbers")
	}

}
function autoCompleteCallbackGOcategory(response, callback) {
	// alert("autocomplete GO term");
	var baseTerm = response.term.toUpperCase();
	var baseTerms = baseTerm.split(" ")
	var par3 = [];
	var regex = /^[0-9A-Za-z]*$/;
	$.each(baseTerms, function(index, baseTerm) {
		if (regex.test(baseTerm)) {
			par3.push("gGOd:" + baseTerm + "*")
		} else {
			alert("This field allows only letters and numbers")
			return;
		}
	});
	par3.push("GOterm")
	// var sliderMinValueAny = $('#termSlider
	// .ui-slider').slider("values",0)+"";
	// var sliderMaxValueAny = $('#termSlider
	// .ui-slider').slider("values",1)+"";
	// var complexTerm =
	// "gGONG:"+"0".repeat(3-sliderMinValueAny.length)+sliderMinValueAny+"--gGONG:"+"0".repeat(3-sliderMaxValueAny.length)+sliderMaxValueAny;
	var minValue = $('select.minGenesOFGO option:selected').val();
	var maxValue = $('select.maxGenesOFGO option:selected').val();
	var complexTerm = "GOterm gGONG:" + minValue + "--gGONG:" + maxValue;
	// par3.push("gGONG:000--gGONG:999")
	par3.push(complexTerm)
	// var otherParameters = ["GO:ALL:","gGO:*","gGO:*",par3.join(" "),false]
	var otherParameters = [ "GO:ALL:", "", "gGO:*", par3.join(" "), false ]
	var query = getQueryComplexJoin(" ", "Eregion", otherParameters[1],
			otherParameters[2], otherParameters[3])
	updateOpenedFeatureCore("featureTable",
			currentState["exploreRegionSelected"], query, 100, 0, "rw=1d",// "rw=0d%26s=MMMS",
			otherParameters);
}
function autoCompleteCallbackOMIMcategory(response, callback) {
	// alert("autocomplete GO term");
	var baseTerm = response.term.toUpperCase();
	var baseTerms = baseTerm.split(" ")
	var par3 = [];
	var regex = /^[0-9A-Za-z]*$/;
	$.each(baseTerms, function(index, baseTerm) {
		if (regex.test(baseTerm)) {
			par3.push("omimD:" + baseTerm + "*")
		} else {
			alert("This field allows only letters and numbers")
			return;
		}
	});
	par3.push("omim")
	par3.push("gOMIMNG:00--gOMIMNG:99")
	// var otherParameters = ["OMIM:ALL:","omimID:*","omimID:*",par3.join("
	// "),false]
	var otherParameters = [ "OMIM:ALL:", "", "omimID:*", par3.join(" "), false ]
	var query = getQueryComplexJoin(" ", "Eregion", otherParameters[1],
			otherParameters[2], otherParameters[3])
	updateOpenedFeatureCore("featureTable",
			currentState["exploreRegionSelected"], query, 100, 0, "rw=1d",// "rw=0d%26s=MMMS",
			otherParameters);
}

function loadVisualizationByID(visualizationID) {
	//
	if (currentState["featuresElements"][visualizationID] !== undefined) {
		// check the parent elements
		var parentElem = currentState["featuresElements"][visualizationID]
				.parent();
		// here we store all parents 'featureBranch' that needs to be opened
		var parentsList = [];
		while (parentElem.hasClass('featureBranch')) {
			if (parentElem.hasClass('featureBranchOpened')) {
			} else {
				parentsList.push(parentElem)
			}
			parentElem = parentElem.parent();
		}

		// open them reversed, from top to bottom
		$.each(parentsList.reverse(), function(index, parentEl) {
			featureOpenBranch(parentEl.children("h4.featureBox"), false);
		})
		// And finally, load the visualization
		$(currentState["featuresElements"][visualizationID]).click()
	}
}
function updateCurrentSelectionOverlapPlotOnlyCandleStickGoogle() {
	// alert(1)
	var l;
	var visualizationData = {
		'cols' : [ {
			'label' : 'Annotation',
			'type' : 'string'
		} ],
		'rows' : []
	};
	var widthChart = 800;
	var heightChart = 350;
	var fontSizeChart = 10;
	var slantedTextAngleChart = 10;
	var slantedTextChart = false;
	if (currentState["overlapSelection"].length > 12) {
		fontSizeChart = 9;
		widthChart = 1000;
		// slantedTextChart = true;
	}
	var plotTitle;
	if ( isInSummary() ) {
		plotTitle = 'Summary of '
				+ numberWithCommas(currentState["totalNumberOfRegions"])
				+ " "
				+ currentState["datasetInfo"][currentState["exploreRegionSelected"]]['officialName'];
	} else {
		plotTitle = getTextForFeatureGroup(currentState["featureCurrentVisualization"])
				+ " summary of "
				+ numberWithCommas(currentState["totalNumberOfRegions"])
				+ " "
				+ currentState["datasetInfo"][currentState["exploreRegionSelected"]]['officialName'];
	}
	// alert(2)
	var options = {
		width : widthChart,
		height : heightChart,
		focusTarget : 'category',
		//bar:{groupWidth:"80%"},
		title : plotTitle,
		legend : {position:'top',
				  textStyle : textStyles["legend"]},
		hAxis : {
			maxAlternation : 1,
			textStyle : textStyles["axisText"],
			slantedText : slantedTextChart,
			slantedTextAngle : slantedTextAngleChart,
			showTextEvery : 1
		},
		vAxis : {
			title : "Percent of overlapping regions",
			titleTextStyle : textStyles["axisTitle"],
			textStyle : textStyles["axisText"],
			format : '#,###%',
			minValue : 0,
			maxValue : 1
		},
		chartArea : {
			left : 60,
			// top:26,
			width : (widthChart - 60)
		},
		forceIFrame: true
	}
	// alert(3)
	if (currentState["referenceQuery"]["genome"] != "") {
		// alert("TO BE UPDATED");
		visualizationData['cols'].push({
			'label' : 'Current selection ('
					+ numberWithCommas(currentState["totalNumberOfRegions"])
					+ ')',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'label' : 'Current selection 25percentile',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'label' : 'Current selection 75percentile',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'label' : 'Current selection maximum',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'role' : 'tooltip',
			'type' : 'string',
			"p" : {
				"role" : "tooltip"
			}
		})
		visualizationData['cols']
				.push({
					'label' : 'Control set ('
							+ numberWithCommas(currentState["referenceQuery"]["totalNumber"])
							+ ')',
					'type' : 'number'
				})
		visualizationData['cols'].push({
			'label' : 'Control set 25percentile',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'label' : 'Control set 75percentile',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'label' : 'Control set maximum',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'role' : 'tooltip',
			'type' : 'string',
			"p" : {
				"role" : "tooltip"
			}
		})

		options['colors'] = [ '#FA9627', '#999999' ]
	} else {
		// alert("1.2")
		visualizationData['cols'].push({
			'label' : 'Current selection',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'label' : 'Current selection 25percentile',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'label' : 'Current selection 75percentile',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'label' : 'Current selection maximum',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			'role' : 'tooltip',
			'type' : 'string',
			"p" : {
				"role" : "tooltip"
			}
		})
		options['legend'] = 'none'
		options['colors'] = [ '#FA9627' ]
	}
	var overlapKeyIndeces = [];
	// alert(4)
	// visualizationData['rows'].push({'c':[{'v':"Test1"},{'v':0.1},{'v':0.3},{'v':0.5},{'v':0.7},{'v':"tooltip1"}]})
	// visualizationData['rows'].push({'c':[{'v':"Test2"},{'v':0.1},{'v':0.5},{'v':0.6},{'v':1},{'v':"tooltip2"}]})

	$
			.each(
					currentState["overlapSelection"],
					function(index, key) {
						overlapKeyIndeces.push(key);
						var updatedKey = key.replace(/OVERLAP/g,
								settings["overlap"]).replace(/TISSUE/g,
								settings["tissue"]);
						label = getOverlapLabels(updatedKey);
						row = []
						row.push({
							'v' : label
						});
						if (currentState["currentOverlaps"][updatedKey] !== undefined
								&& currentState["currentOverlapsStat"][updatedKey] !== undefined) {
							var ratio = currentState["currentOverlaps"][updatedKey]
									/ currentState["totalNumberOfRegions"];
							var minR = Math
									.round(1000 * currentState["currentOverlapsStat"][updatedKey][0]) / 1000;
							var p25R = Math
									.round(1000 * currentState["currentOverlapsStat"][updatedKey][1]) / 1000;
							var p75R = Math
									.round(1000 * currentState["currentOverlapsStat"][updatedKey][2]) / 1000;
							var maxR = Math
									.round(1000 * currentState["currentOverlapsStat"][updatedKey][3]) / 1000;

							row.push({
								'v' : minR
							});
							row.push({
								'v' : p25R
							});
							row.push({
								'v' : p75R
							});
							row.push({
								'v' : maxR
							});
							row.push({
								'v' : "Mean " + Math.round(ratio * 1000) / 10
										+ "% (Min=" + Math.round(minR * 10000)
										/ 100 + "%, 25perc="
										+ Math.round(p25R * 10000) / 100
										+ "%, 75perc="
										+ Math.round(p75R * 10000) / 100
										+ "%, Max=" + Math.round(maxR * 10000)
										/ 100 + "%)"
							});
							// row.push({'v':ratio,
							// 'f':numberWithCommas(currentState["currentOverlaps"][updatedKey])+"
							// ("+Math.round(ratio*1000)/10+"%)"});

						} else {
							row.push({
								'v' : 0,
								'f' : "0"
							});
							row.push({
								'v' : 0,
								'f' : "0"
							});
							row.push({
								'v' : 0,
								'f' : "0"
							});
							row.push({
								'v' : 0,
								'f' : "0"
							});
							row.push({
								'v' : "All at 0%"
							});

						}

						if (currentState["referenceQuery"]["genome"] != "") {
							// alert("TO BE UPDATED");
							// alert(currentState["referenceQuery"]["values"][updatedKey])
							// alert(currentState["referenceQuery"]["statvalues"][updatedKey])
							if (currentState["referenceQuery"]["values"][updatedKey] !== undefined) {
								var ratio = currentState["referenceQuery"]["values"][updatedKey]
										/ currentState["referenceQuery"]["totalNumber"];

								if (currentState["referenceQuery"]["statvalues"][updatedKey] !== undefined) {
									var minR = Math
											.round(1000 * currentState["referenceQuery"]["statvalues"][updatedKey][0]) / 1000;
									var p25R = Math
											.round(1000 * currentState["referenceQuery"]["statvalues"][updatedKey][1]) / 1000;
									var p75R = Math
											.round(1000 * currentState["referenceQuery"]["statvalues"][updatedKey][2]) / 1000;
									var maxR = Math
											.round(1000 * currentState["referenceQuery"]["statvalues"][updatedKey][3]) / 1000;
								} else {
									var minR = ratio;
									var p25R = ratio;
									var p75R = ratio;
									var maxR = ratio;
								}
								// row.push({'v':ratio});
								row.push({
									'v' : minR
								});
								row.push({
									'v' : p25R
								});
								row.push({
									'v' : p75R
								});
								row.push({
									'v' : maxR
								});
								row.push({
									'v' : " Control set: Mean "
											+ Math.round(ratio * 1000) / 10
											+ "% (Min="
											+ Math.round(minR * 10000) / 100
											+ "%, 25perc="
											+ Math.round(p25R * 10000) / 100
											+ "%, 75perc="
											+ Math.round(p75R * 10000) / 100
											+ "%, Max="
											+ Math.round(maxR * 10000) / 100
											+ "%)"
								});

								// row.push({'v':ratio,
								// 'f':numberWithCommas(currentState["referenceQuery"]["values"][updatedKey])+"
								// ("+Math.round(ratio*1000)/10+"%)"});
								// refValues.push(currentState["referenceQuery"]["values"][updatedKey]);
								// refRatios.push(currentState["referenceQuery"]["values"][updatedKey]/currentState["referenceQuery"]["totalNumber"]);
							} else {
								// row.push({'v':0,'f':"0"});
								row.push({
									'v' : 0,
									'f' : "0"
								});
								row.push({
									'v' : 0,
									'f' : "0"
								});
								row.push({
									'v' : 0,
									'f' : "0"
								});
								row.push({
									'v' : 0,
									'f' : "0"
								});
								row.push({
									'v' : "All at 0%"
								});
							}
						}
						visualizationData['rows'].push({
							'c' : row
						})
					});
	// alert(5)
	var dt = new google.visualization.DataTable(visualizationData, 0.6);
	// alert(6)
	// var chart = new
	// google.visualization.ColumnChart(document.getElementById('rangeFeaturePlot'));
	var chart = new google.visualization.ChartWrapper({
		'chartType' : 'CandlestickChart',
		'containerId' : 'rangeFeaturePlot',
		'dataTable' : dt,
		'options' : options
	});
	currentState["activeChart"].push(chart);
	// alert(7)
	// chart.draw(dt, options);
	chart.draw();
	// alert(8)
	function chartSelectHandler() {
		if (currentState["isRegionSelected"] == false) {
			// alert("region selection mode")
			return;
		}
		var selection = chart.getChart().getSelection();
		for ( var i = 0; i < selection.length; i++) {
			if (selection[i].row != null) {
				var currentVisualization = currentState["featureCurrentVisualization"];
				var currentItem = overlapKeyIndeces[selection[i].row];
				// alert(currentState["featureCurrentVisualization"])
				// alert(selection[i].row)
				// alert(overlapKeyIndeces[selection[i].row])//The overlap id of
				// the
				// alert(visualizationData['rows'][selection[i].row]["c"][0]["v"])//
				// The overlap name
				var newVisualizationItem = getForwardVisualizationID(
						currentVisualization, currentItem);
				// alert(newVisualizationItem)
				loadVisualizationByID(newVisualizationItem)
			}
		}
	}
	;
	google.visualization.events
			.addListener(chart, 'select', chartSelectHandler);
	var difShow = $('<tr class="showTableLink"><td colspan="2"><a href="#" onclick="return false">Show as table</a></td></tr>');
	difShow.click(function() {
		if (chart.getChartType() == "Table") {
			chart.setChartType('CandlestickChart')
			chart.setOption("height", heightChart)
			$(".showTableLink a").text("Show as table");
			$('tr.toPNGRow').show()
		} else {
			chart.setChartType("Table")
			chart.setOption("height", null)
			$(".showTableLink a").text("Show as chart");
			$('tr.toPNGRow').hide()
		}
		chart.draw()
	});

	$('.showTableLink').remove();
	$('#rangeFeaturePlotTable').append(difShow);
	// Image convertion
	$('tr.toPNGRow').remove();
	var toImageButton = $('<tr class="toPNGRow"><td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
			+ options["width"]
			+ '"/> <input type="hidden" value="'
			+ options["height"]
			+ '"/><input type="hidden" value="'
			+ chart.getContainerId() + '"/></td></tr>')
	$('#rangeFeaturePlotTable').append(toImageButton)
	// alert(9)
}
function updateCurrentSelectionOverlapPlotOnlyColumnWithConfidenceGoogle() {
	showInfoPlot("summaryWithConfidence")
	var l;
	var visualizationData = {
		'cols' : [ {
			'label' : 'Annotation',
			'type' : 'string'
		} ],
		'rows' : []
	};
	var widthChart = 800;
	var heightChart = 350;
	var fontSizeChart = 10;
	var slantedTextAngleChart = 10;
	var slantedTextChart = false;
	if (currentState["overlapSelection"].length > 12) {
		fontSizeChart = 9;
		widthChart = 1000;
		// slantedTextChart = true;
	}
	var plotTitle;
	if (isInSummary()) {
		plotTitle = 'Summary of '
				+ numberWithCommas(currentState["totalNumberOfRegions"])
				+ " "
				+ currentState["datasetInfo"][currentState["exploreRegionSelected"]]['officialName'];
	} else {
		plotTitle = getTextForFeatureGroup(currentState["featureCurrentVisualization"])
				+ " summary of "
				+ numberWithCommas(currentState["totalNumberOfRegions"])
				+ " "
				+ currentState["datasetInfo"][currentState["exploreRegionSelected"]]['officialName'];
	}
	var options = {
		width : widthChart,
		height : heightChart,
		focusTarget : 'category',
		title : plotTitle,
		legend : 'top',
		hAxis : {
			maxAlternation : 1,
			textStyle : {
				fontName : 'Tahoma',
				fontSize : fontSizeChart
			},
			slantedText : slantedTextChart,
			slantedTextAngle : slantedTextAngleChart,
			showTextEvery : 1
		},
		vAxis : {
			title : "Percent of overlapping regions",
			titleTextStyle : {
				italic : false
			},
			format : '#,###%',
			minValue : 0,
			maxValue : 1
		},
		chartArea : {
			left : 60,
			// top:26,
			width : (widthChart - 60)
		},
		forceIFrame: true
	}
	if (currentState["referenceQuery"]["genome"] != "") {
		// alert("TO BE UPDATED");
		visualizationData['cols'].push({
			'label' : 'Current selection ('
					+ numberWithCommas(currentState["totalNumberOfRegions"])
					+ ')',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			"type" : "number",
			"role" : "interval",
			"p" : {
				"role" : "interval"
			}
		})
		visualizationData['cols'].push({
			"type" : "number",
			"role" : "interval",
			"p" : {
				"role" : "interval"
			}
		})
		visualizationData['cols'].push({
			"type" : "number",
			"role" : "interval",
			"p" : {
				"role" : "interval"
			}
		})
		visualizationData['cols'].push({
			"type" : "number",
			"role" : "interval",
			"p" : {
				"role" : "interval"
			}
		})
		visualizationData['cols'].push({
			'role' : 'tooltip',
			'type' : 'string',
			"p" : {
				"role" : "tooltip"
			}
		})

		visualizationData['cols']
				.push({
					'label' : 'Control set ('
							+ numberWithCommas(currentState["referenceQuery"]["totalNumber"])
							+ ')',
					'type' : 'number'
				})
		if (currentState["datasetInfo"][currentState["referenceQuery"]["dataset"]]["hasBinning"]) {
			visualizationData['cols'].push({
				"type" : "number",
				"role" : "interval",
				"p" : {
					"role" : "interval"
				}
			})
			visualizationData['cols'].push({
				"type" : "number",
				"role" : "interval",
				"p" : {
					"role" : "interval"
				}
			})
			visualizationData['cols'].push({
				"type" : "number",
				"role" : "interval",
				"p" : {
					"role" : "interval"
				}
			})
			visualizationData['cols'].push({
				"type" : "number",
				"role" : "interval",
				"p" : {
					"role" : "interval"
				}
			})
		}
		visualizationData['cols'].push({
			'role' : 'tooltip',
			'type' : 'string',
			"p" : {
				"role" : "tooltip"
			}
		})

		options['colors'] = [ '#FA9627', '#999999' ]
	} else {
		// alert("1.2")
		// visualizationData['cols'].push({'label':'Current
		// selection','type':'number'})
		visualizationData['cols'].push({
			'label' : 'Current selection',
			'type' : 'number'
		})
		visualizationData['cols'].push({
			"type" : "number",
			"role" : "interval",
			"p" : {
				"role" : "interval"
			}
		})
		visualizationData['cols'].push({
			"type" : "number",
			"role" : "interval",
			"p" : {
				"role" : "interval"
			}
		})
		visualizationData['cols'].push({
			"type" : "number",
			"role" : "interval",
			"p" : {
				"role" : "interval"
			}
		})
		visualizationData['cols'].push({
			"type" : "number",
			"role" : "interval",
			"p" : {
				"role" : "interval"
			}
		})
		visualizationData['cols'].push({
			'role' : 'tooltip',
			'type' : 'string',
			"p" : {
				"role" : "tooltip"
			}
		})
		// visualizationData['rows'] = [
		// {c:[{v: 'Test1cs'}, {v: 1.0, f: 'One'}]},
		// {c:[{v: 'Test2cs'}, {v: 2.0, f: 'Two'}]}]
		options['legend'] = 'none'
		options['colors'] = [ '#FA9627' ]
	}
	var overlapKeyIndeces = [];
	$
			.each(
					currentState["overlapSelection"],
					function(index, key) {
						overlapKeyIndeces.push(key);
						var updatedKey = key.replace(/OVERLAP/g,
								settings["overlap"]).replace(/TISSUE/g,
								settings["tissue"]);
						label = getOverlapLabels(updatedKey);
						row = []
						row.push({
							'v' : label
						});
						if (currentState["currentOverlaps"][updatedKey] !== undefined) {
							var ratio = currentState["currentOverlaps"][updatedKey]
									/ currentState["totalNumberOfRegions"];

							if (currentState["currentOverlapsStat"][updatedKey] !== undefined) {
								var minR = Math
										.round(1000 * currentState["currentOverlapsStat"][updatedKey][0]) / 1000;
								var p25R = Math
										.round(1000 * currentState["currentOverlapsStat"][updatedKey][1]) / 1000;
								var p75R = Math
										.round(1000 * currentState["currentOverlapsStat"][updatedKey][2]) / 1000;
								var maxR = Math
										.round(1000 * currentState["currentOverlapsStat"][updatedKey][3]) / 1000;
							} else {
								var minR = ratio;
								var p25R = ratio;
								var p75R = ratio;
								var maxR = ratio;
							}
							row.push({
								'v' : ratio
							});
							row.push({
								'v' : minR
							});
							row.push({
								'v' : p25R
							});
							row.push({
								'v' : p75R
							});
							row.push({
								'v' : maxR
							});
							row.push({
								'v' : "Current selection: "
										+ Math.round(ratio * 1000) / 10
										+ "% (Min=" + Math.round(minR * 10000)
										/ 100 + "%, 25perc="
										+ Math.round(p25R * 10000) / 100
										+ "%, 75perc="
										+ Math.round(p75R * 10000) / 100
										+ "%, Max=" + Math.round(maxR * 10000)
										/ 100 + "%)"
							});
							// row.push({'v':ratio,
							// 'f':numberWithCommas(currentState["currentOverlaps"][updatedKey])+"
							// ("+Math.round(ratio*1000)/10+"%)"});

						} else {
							row.push({
								'v' : 0,
								'f' : "0"
							});
							row.push({
								'v' : 0,
								'f' : "0"
							});
							row.push({
								'v' : 0,
								'f' : "0"
							});
							row.push({
								'v' : 0,
								'f' : "0"
							});
							row.push({
								'v' : 0,
								'f' : "0"
							});
							row.push({
								'v' : "Current selection: 0%"
							});

						}

						if (currentState["referenceQuery"]["genome"] != "") {
							// alert("TO BE UPDATED");
							// alert(currentState["referenceQuery"]["values"][updatedKey])
							// alert(currentState["referenceQuery"]["statvalues"][updatedKey])
							if (currentState["referenceQuery"]["values"][updatedKey] !== undefined) {
								var ratio = currentState["referenceQuery"]["values"][updatedKey]
										/ currentState["referenceQuery"]["totalNumber"];
								row.push({
									'v' : ratio
								});
								if (currentState["datasetInfo"][currentState["referenceQuery"]["dataset"]]["hasBinning"]) {
									if (currentState["referenceQuery"]["statvalues"][updatedKey] !== undefined) {
										var minR = Math
												.round(1000 * currentState["referenceQuery"]["statvalues"][updatedKey][0]) / 1000;
										var p25R = Math
												.round(1000 * currentState["referenceQuery"]["statvalues"][updatedKey][1]) / 1000;
										var p75R = Math
												.round(1000 * currentState["referenceQuery"]["statvalues"][updatedKey][2]) / 1000;
										var maxR = Math
												.round(1000 * currentState["referenceQuery"]["statvalues"][updatedKey][3]) / 1000;
									} else {
										var minR = ratio;
										var p25R = ratio;
										var p75R = ratio;
										var maxR = ratio;
									}
									row.push({
										'v' : minR
									});
									row.push({
										'v' : p25R
									});
									row.push({
										'v' : p75R
									});
									row.push({
										'v' : maxR
									});
									row.push({
										'v' : " Control set: "
												+ Math.round(ratio * 1000) / 10
												+ "% (Min="
												+ Math.round(minR * 10000)
												/ 100 + "%, 25perc="
												+ Math.round(p25R * 10000)
												/ 100 + "%, 75perc="
												+ Math.round(p75R * 10000)
												/ 100 + "%, Max="
												+ Math.round(maxR * 10000)
												/ 100 + "%)"
									});
								} else {
									row.push({
										'v' : " Control set: "
												+ Math.round(ratio * 1000) / 10
												+ "%"
									});
								}

								// row.push({'v':ratio,
								// 'f':numberWithCommas(currentState["referenceQuery"]["values"][updatedKey])+"
								// ("+Math.round(ratio*1000)/10+"%)"});
								// refValues.push(currentState["referenceQuery"]["values"][updatedKey]);
								// refRatios.push(currentState["referenceQuery"]["values"][updatedKey]/currentState["referenceQuery"]["totalNumber"]);
							} else {
								row.push({
									'v' : 0,
									'f' : "0"
								});
								if (currentState["datasetInfo"][currentState["referenceQuery"]["dataset"]]["hasBinning"]) {
									row.push({
										'v' : 0,
										'f' : "0"
									});
									row.push({
										'v' : 0,
										'f' : "0"
									});
									row.push({
										'v' : 0,
										'f' : "0"
									});
									row.push({
										'v' : 0,
										'f' : "0"
									});
								}
								row.push({
									'v' : "Control set: 0%"
								});

							}
						}
						visualizationData['rows'].push({
							'c' : row
						})
					});

	var dt = new google.visualization.DataTable(visualizationData, 0.6);

	// var chart = new
	// google.visualization.ColumnChart(document.getElementById('rangeFeaturePlot'));
	var chart = new google.visualization.ChartWrapper({
		'chartType' : 'ColumnChart',
		'containerId' : 'rangeFeaturePlot',
		'dataTable' : dt,
		'options' : options
	});
	currentState["activeChart"].push(chart);

	// chart.draw(dt, options);
	chart.draw();
	function chartSelectHandler() {
		if (currentState["isRegionSelected"] == false) {
			// alert("region selection mode")
			return;
		}
		var selection = chart.getChart().getSelection();
		for ( var i = 0; i < selection.length; i++) {
			if (selection[i].row != null) {
				var currentVisualization = currentState["featureCurrentVisualization"];
				var currentItem = overlapKeyIndeces[selection[i].row];
				// alert(currentState["featureCurrentVisualization"])
				// alert(selection[i].row)
				// alert(overlapKeyIndeces[selection[i].row])//The overlap id of
				// the
				// alert(visualizationData['rows'][selection[i].row]["c"][0]["v"])//
				// The overlap name
				var newVisualizationItem = getForwardVisualizationID(
						currentVisualization, currentItem);
				// alert(newVisualizationItem)
				loadVisualizationByID(newVisualizationItem)
			}
		}
	}
	;
	google.visualization.events
			.addListener(chart, 'select', chartSelectHandler);
	var difShow = $('<tr class="showTableLink"><td colspan="2"><a href="#" onclick="return false">Show as table</a></td></tr>');
	difShow.click(function() {
		if (chart.getChartType() == "Table") {
			chart.setChartType('ColumnChart')
			chart.setOption("height", heightChart)
			$(".showTableLink a").text("Show as table");
			$('tr.toPNGRow').show()
		} else {
			chart.setChartType("Table")
			chart.setOption("height", null)
			$(".showTableLink a").text("Show as chart");
			$('tr.toPNGRow').hide()
		}
		chart.draw()
	});

	$('.showTableLink').remove();
	$('#rangeFeaturePlotTable').append(difShow);
	// Image convertion
	$('tr.toPNGRow').remove();
	var toImageButton = $('<tr class="toPNGRow"><td class="toPNGButton"><a href="#" onclick="return false">To PNG</a><input type="hidden" value="'
			+ options["width"]
			+ '"/> <input type="hidden" value="'
			+ options["height"]
			+ '"/><input type="hidden" value="'
			+ chart.getContainerId() + '"/></td></tr>')
	$('#rangeFeaturePlotTable').append(toImageButton)

}
function getConfidenceStatistics(listOfValues) {
	var l = listOfValues.length;
	if (l == 0) {
		return [ 0, 0, 0, 0 ];
	}
	listOfValues.sort()
	var p25 = listOfValues[Math.floor(l * 0.25)];
	var p75 = listOfValues[Math.floor(l * 0.75)];

	return [ listOfValues.min(), p25, p75, listOfValues.max() ];
}

function clearCharts() {
	// alert("About to clear the "+currentState["activeChart"].length+" charts
	// data ")
	// clears the resources for active charts
	// as documented here:
	// http://code.google.com/apis/chart/interactive/docs/gallery/linechart.html#Methods
	for ( var i = 0; i < currentState["activeChart"].length; i++) {
		currentState["activeChart"][i].getChart().clearChart();
	}
	currentState["activeChart"] = [];
	// alert("Cleared!");
}
function setCurrentStatus(text, showProcessing) {
	if (text == null) {
		$('#currentStatus').children().remove();
	} else {
		if (showProcessing) {
			$("#currentStatus").children('p').remove();
		} else {
			$('#currentStatus').children().remove();
		}
		$("#currentStatus").prepend($('<p>' + text + '</p>'))
		if (showProcessing && $('#currentStatus').children("img").length == 0) {
			$("#currentStatus")
					.append(
							$('<img name="progress_image_feature_plot" src="extras/ajax-loader-big.gif" class="progress_image_feature_plot" align="center" alt="Processing..."></img>'));
		}

	}
}
function showRefinementNotification(title,message){
	//alert(type)
	//alert(message)
	$('#notificationTitle').html("<p><b>"+title+"</b></p>")
	$('#notificationParagraph').html("<p>"+message+"</b>")
	$("#dialog-notification" ).dialog({							
			resizable: true,
			height:350,
			width:450,
			modal: true,
			buttons: {								
				"Keep announcing me": function() {
					$( this ).dialog( "close" );
					$('#notificationTitle').html("");
					$('#notificationParagraph').html("");
				},
				"Stop all notifications": function() {
					$( this ).dialog( "close" );
					$('#notificationTitle').html("");
					$('#notificationParagraph').html("");
					settings["showRefinementNotification"] = "false";
					$.cookie("cgs:settings:showRefinementNotification", settings["showRefinementNotification"], { expires: 60});
				}
			}
	});
}

function updateCurrentVisualization(newVisualization,log){
	currentState["featureCurrentVisualization"] = newVisualization;	
	if (log && currentState["exploreRegionSelected"] != ""){
		$.ajax({
			type : "GET",
			url : "relay.php",
			async : true,		
			data : "type=logPageView"
				   + "&regionType=" + currentState["exploreRegionSelected"]
				   + "&genome=" + settings["genome"]
				   + "&visType=" + currentState["featureCurrentVisualization"]					
				   + "&tissueType=" + settings["tissue"]
				   + "&overlapType=" + settings["overlap"]
				   + "&summaryChartType=" + currentState["currentDefaultChart"] 
		});
	}
}
	