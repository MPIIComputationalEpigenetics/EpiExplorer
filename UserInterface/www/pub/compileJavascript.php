<!-- Todo: need to replace hardcoded epiexplorer.mpi-inf.mpg.de values with elements written by javascript/jQuery -->

<html>
  <head>
  	<script type="text/javascript" src="jQuery/js/jquery-1.4.2.min.js"></script>
  	<script type="text/javascript">

	// Global var for commonExploreCGS.js
	//var contact_email = <?php echo json_encode($contact_email); ?>
	//This value is not needed here, but contact_email var name will need to be preserved by compiler/minifier
	var escaped_server_host = $.text(window.location.origin)

  	$(function() {	
	  	$('#optimizeJquery').click(function(){	  		
	  		$.ajax({
				type: "POST",
				url: "http://closure-compiler.appspot.com/compile",
				dataType: "json",
				data: "output_format=json&output_info=errors&output_info=warnings&output_info=statistics&compilation_level=SIMPLE_OPTIMIZATIONS&warning_level=default&output_file_name=EpiExplorer.pack.YYMMDD.js&code_url=" +
					escaped_server_host + "%2FcommonCGS.js&code_url=" + escaped_server_host + "%2FCGSTexts.js&code_url=" +
					escaped_server_host + "%2FcommonExploreCGS.js&js_code=",
				//data: "output_format=json&output_info=errors&output_info=warnings&output_info=statistics&compilation_level=SIMPLE_OPTIMIZATIONS&warning_level=default&output_file_name=EpiExplorer.pack.YYMMDD.js&code_url=http%3A%2F%2Fepiexplorer.mpi-inf.mpg.de%2FcommonCGS.js&code_url=http%3A%2F%2Fepiexplorer.mpi-inf.mpg.de%2FCGSTexts.js&code_url=http%3A%2F%2Fepiexplorer.mpi-inf.mpg.de%2FcommonExploreCGS.js&js_code=",
				success: function (result){
					//alert(Object.keys(result))
					//alert(Object.keys(result["statistics"]))
					if (result["errors"] !== undefined){
						$('#optimizeJQueryResult').text("errors" +result["errors"])
					}else if (result["warnings"] !== undefined){
						$('#optimizeJQueryResult').text("warnings" +result["warnings"])
					}else{
						$('#optimizeJQueryResult').html('Success! No errors and warnings!<br><a href="http://closure-compiler.appspot.com'+result["outputFilePath"]+'">compiled output here</a>')
						//<br><textarea>'+result["compiledCode"]+'</textarea>
					}		
				}
			});	
	  	});
  	});
  	</script>
  </head>
  <body>
  	<p>
  		<h4>Automatic with jQuery</h4>    		
    	<form action="http://closure-compiler.appspot.com/compile" method="POST" target="_blank" onsubmit="javascript:return false;">
    		<!--table>   
    		<tr><td><label>output_format</label></td><td><input type="text" name="output_format" value="json"></td></tr>
		    <tr><td><label>output_info</label></td><td><input type="text" name="output_info" value="compiled_code"></td></tr>
		    <tr><td><label>output_info</label></td><td><input type="text" name="output_info" value="warnings"></td></tr>
		    <tr><td><label>output_info</label></td><td><input type="text" name="output_info" value="errors"></td></tr>
		    <tr><td><label>output_info</label></td><td><input type="text" name="output_info" value="statistics"></td></tr>
		    <tr><td><label>compilation_level</label></td><td><input type="text" name="compilation_level" value="SIMPLE_OPTIMIZATIONS"></td></tr>
		    <tr><td><label>warning_level</label></td><td><input type="text" name="warning_level" value="default"></td></tr>
		    <tr><td><label>output_file_name</label></td><td><input type="text" size="100" name="output_file_name" value="EpiExplorer.pack.YYMMDD.js"></td></tr>



    		<tr><td><label>code_url</label></td><td><input type="text" size="100" name="code_url" value="http://epiexplorer.mpi-inf.mpg.de/commonCGS.js"></td></tr>
    		<tr><td><label>code_url</label></td><td><input type="text" size="100" name="code_url" value="http://epiexplorer.mpi-inf.mpg.de/CGSTexts.js"></td></tr>
    		<tr><td><label>code_url</label></td><td><input type="text" size="100" name="code_url" value="http://epiexplorer.mpi-inf.mpg.de/commonExploreCGS.js"></td></tr>
    		<tr><td><label>js_code</label></td><td><input type="text" size="100" name="js_code" value="">
    		</table-->
    		<input id="optimizeJquery" type="submit" value="Optimize">
    	</form>
    	<p id="optimizeJQueryResult">
    	</p>
    </p>
  	<p>
  		<h4>Manual compilation</h4>
    	<input size="100" type="text" value='http://closure-compiler.appspot.com/home'></input><br>
	    <textarea name="compilation code" cols="100" rows="10" >    
// ==ClosureCompiler==
// @output_file_name EpiExplorer.pack.111124.js
// @compilation_level SIMPLE_OPTIMIZATIONS
// @code_url http://epiexplorer.mpi-inf.mpg.de/commonCGS.js
// @code_url http://epiexplorer.mpi-inf.mpg.de/CGSTexts.js
// @code_url http://epiexplorer.mpi-inf.mpg.de/commonExploreCGS.js
// ==/ClosureCompiler==
	    </textarea><br>
	</p>
	<p>
  		<h4>Automatic with table</h4>    		
    	<form action="http://closure-compiler.appspot.com/compile" method="POST" target="_blank">
    		<table>   
    		<tr><td><label>output_format</label></td><td><input type="text" name="output_format" value="json" disabled="disabled" ></td></tr>
		    <tr><td><label>output_info</label></td><td><input type="text" name="output_info" value="compiled_code" disabled="disabled" ></td></tr>
		    <tr><td><label>output_info</label></td><td><input type="text" name="output_info" value="warnings" disabled="disabled" ></td></tr>
		    <tr><td><label>output_info</label></td><td><input type="text" name="output_info" value="errors" disabled="disabled" ></td></tr>
		    <tr><td><label>output_info</label></td><td><input type="text" name="output_info" value="statistics" disabled="disabled" ></td></tr>
		    <tr><td><label>compilation_level</label></td><td><input type="text" name="compilation_level" value="SIMPLE_OPTIMIZATIONS" disabled="disabled" ></td></tr>
		    <tr><td><label>warning_level</label></td><td><input type="text" name="warning_level" value="default" disabled="disabled" ></td></tr>
		    <tr><td><label>output_file_name</label></td><td><input type="text" size="100" name="output_file_name" value="EpiExplorer.pack.YYMMDD.js" disabled="disabled" ></td></tr>
    		<tr><td><label>code_url</label></td><td><input type="text" size="100" name="code_url" value="http://epiexplorer.mpi-inf.mpg.de/commonCGS.js" disabled="disabled" ></td></tr>
    		<tr><td><label>code_url</label></td><td><input type="text" size="100" name="code_url" value="http://epiexplorer.mpi-inf.mpg.de/CGSTexts.js" disabled="disabled" ></td></tr>
    		<tr><td><label>code_url</label></td><td><input type="text" size="100" name="code_url" value="http://epiexplorer.mpi-inf.mpg.de/commonExploreCGS.js" disabled="disabled" ></td></tr>
    		<tr><td><label>js_code</label></td><td><input type="text" size="100" name="js_code" value="">
    		</table>
    		<input type="submit" value="Optimize">
    	</form>
    </p>
    
    
  </body>
</html>