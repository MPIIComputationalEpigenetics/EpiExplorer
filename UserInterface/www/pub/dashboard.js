google.load('visualization', '1.0', {'packages':['corechart', 'orgchart', 'table', 'annotatedtimeline']});
google.setOnLoadCallback(drawVisualization);


function drawVisualization() {
   var query = new google.visualization.Query('http://moebius.ag3.mpi-sb.mpg.de/epiexplorer/epiexplorer_logs.php?type=get_chart_data');
   query.send(handleQueryResponse);
}

function handleQueryResponse(response) {
   var dt = response.getDataTable();
   var annotatedtimeline = new google.visualization.AnnotatedTimeLine(document.getElementById('table'));
   annotatedtimeline.draw(dt, {'displayAnnotations': true});



   var grouped_table = new google.visualization.Table(document.getElementById('infos'));
   grouped_table.draw(dt, null);
}
