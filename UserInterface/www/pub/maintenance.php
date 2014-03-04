<?php
  // php initialization of XML-RPC variables
  require_once("grab_globals.lib.php");
  include("xmlrpc_submit.php");
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<link rel="SHORTCUT ICON" href="extras/new_logo_symbol_16.ico"/>
	<link href="menu/menu.css" rel="stylesheet" type="text/css" />
	<!--script type="text/javascript" src="jQuery/js/jquery-1.4.2.min.js"></script-->
	<script type="text/javascript" src="http://code.jquery.com/jquery-1.7.1.min.js"/>
	
	<script type="text/javascript" src="commonCGS.js"></script>
	<script type="text/javascript" src="CGSTexts.js"></script>
	<script type="text/javascript" src="commonExploreCGS.js"></script>	
	<link href="testIndex.css" rel="stylesheet" type="text/css" />
    <!-- The purpose of the jQuery UI is to use the slider, remove them if the slider is removed -->
  	<!--script type="text/javascript" src="jQuery/js/jquery-ui-1.8.5.custom.min.js"></script-->		
	<!--link type="text/css" href="jQuery/css/custom-theme/jquery-ui-1.8.5.custom.css" rel="stylesheet"/-->
	
	
	
	<script type="text/javascript" src="twitterPlugin/jquery.jtweetsanywhere-1.3.1.min.js"></script>
	<script type="text/javascript" src="twitterPlugin/jtweetsanywhere-de-1.3.1.min.js"></script>
	<script type="text/javascript" src="http://platform.twitter.com/anywhere.js?id=9cD1uPaPf5BdtVuXbePpjQ&v=1"></script>
	<link rel="stylesheet" type="text/css" href="twitterPlugin/jquery.jtweetsanywhere-1.3.1.css" />
    
    <style type="text/css"></style>

	<link href="jQueryUI-mine/jquery-ui-mine.css" rel="stylesheet" type="text/css" />
	
  
  
  <!-- jQuery checkboxes -->
  <!-- script type="text/javascript" src="jCheckbox/jquery.checkboxes.pack.js"></script-->
  <!-- jQuery cookies -->	
  <!-- script type="text/javascript" src="jquery.cookie/jquery.cookie.js"></script-->
  
  <!-- jquery simple drop-won menu -->
  <link rel="stylesheet" type="text/css" href="jsddm/jsddm.css"/>
  <script type="text/javascript" src="jsddm/jsddm.js"></script>
  
  

<title>EpiExplorer</title>

<style type="text/css"></style>
<script type="text/javascript">		
	




	/*####----####---- Start if jQuery onReady ----####----####*/
$(function() {
	$('#jTweetsAnywhereSample').jTweetsAnywhere({
	    username: 'hEpiExplorer',
	    count: 5,
	    showFollowButton: true,
	    showTweetFeed: {
    		autoConformToTwitterStyleguide: true,
        	showTimestamp: {
            	refreshInterval: 120
        	},
        	autorefresh: {
            	mode: 'trigger-insert',
            	interval: 120
        	},
        	paging: { mode: 'prev-next' }
    	},
    	onDataRequestHandler: function(stats, options) {
        	if (stats.dataRequestCount < 51) {
            	return true;
        	}
        	else {
            	stopAutorefresh(options);
            	alert("To avoid struggling with Twitter's rate limit, we stop loading data after 50 API calls.");
        	}
    	}
	});	
});
</script>		
</head>

<body>

<div class="container">
    <div class="leftside">
        <div class="logo">
        	<!--a href="index.php"><img src="extras/logo_tes.PNG" width="242px" height="90px" align="bottom" style="border-width:0px"></a-->
        	<a href="index.php"><img src="extras/new_logo.png" width="100%" align="bottom" style="border-width:0px" alt="EpiExplorer logo"/></a>
        	
        </div>
        
        <div class="regions">
	        
        </div>
        
        <div class="features activeSearchBox">
        	            
        </div>        
        
    </div>

	<div class="rightside">
		<div class="header">
			<ul class="jsddm" align="right">
				<li><a href="#">Help</a>
					<ul>
						<li><!--a onmouseover="UE.Popin.preload();" href="#" onclick="UE.Popin.show(); return false;">Questions, problems, ideas?</a-->
						<a href="http://epiexplorer.userecho.com/forum/5999-feedback/" target="_blank">Questions, problems, ideas?</a>						
						</li>
						<!--li><a href="http://epiexplorer.userecho.com/forum/5999-feedback/filter-17845/order-top/">Quesions?</a></li-->
						<!--li><a href="http://epiexplorer.userecho.com/forum/5999-feedback/filter-17845/order-top/">Bugs?</a></li-->
						<!--li><a href="http://epiexplorer.userecho.com/forum/5999-feedback/filter-17845/order-top/">Ideas?</a></li-->
						<!--a href="feedback.php">Feedback</a-->
					</ul>
				</li>				
					
				
			</ul>
			<div class="clear"> </div>
			<br/>
						           
	    </div>

		<div class="content">
					
            <div class="visualization">
	          	<h3 style="color:red;">The EpiExplorer is currently unavailable due to maintenance or technical problems. We are aware of the situation and are working on it. You can try reloading the main page by clicking on the logo on the left.
	          	<br/><br/>
	          	Below are the latest announcements on our twitter account<br/></h3>	
				<div id="jTweetsAnywhereSample"></div>
			</div><!-- End of visualization-->
			
            <div class="infoboxMain">   
            				  	              
			</div><!-- End of infoboxMain-->
			
						
	    </div>		
	    
	</div><!-- End of rightside-->
	</div><!-- End of container-->
	   
    
    <div> <!-- userfeedbacktest -->						

		<!-- userecho -->
		<script type='text/javascript'>
		
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
		
		</script>
	</div><!-- userfeedbacktest -->
</body>
</html>
