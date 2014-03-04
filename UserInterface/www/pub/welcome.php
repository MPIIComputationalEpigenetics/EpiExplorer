<?php
	if (strlen(strstr($_SERVER['SERVER_NAME'],'cosgen.bioinf')) == 0){
?>
<html>
<head>
	<script type="text/javascript" src="jQuery/js/jquery-1.4.2.min.js"></script>
	<link href="testIndex.css" rel="stylesheet" type="text/css" />	
	<script type="text/javascript" src="jQuery/js/jquery-ui-1.8.5.custom.min.js"></script>		
	<link type="text/css" href="jQuery/css/custom-theme/jquery-ui-1.8.5.custom.css" rel="stylesheet" />
	<script type="text/javascript">
	$(function() {
		/*function selectCast(){
			//Hide other Bs
			$('td.castItem b').hide();
			$('td.castItem a').show();
			//switch the current one to visible more
			$(this).hide()
			$(this).siblings("b").show()
			//Chage the cast source
			$('#castFrame').attr("src",$(this).siblings("input:hidden")[0].value)			
		}
		$('li.castItem').each(function(){			
			var castItemText = $(this).children("div.castdescription").text();
			var toselectCast = $('<a href="#" onclick="return false;">'+castItemText+'</a>')
			$(this).append(toselectCast);
			toselectCast.click(selectCast);
			var selectedCast = $('<b>'+castItemText+'</b>');			
			$(this).append(selectedCast);
			$(this).children("div.castdescription").hide();
			$(this).children("b").hide();			
		});		
		//$('table tr:first td:eq(1) a').click()
		*/
		function selectCast(){			
			if ($(this).children('.castFrame').is(":visible")){
				//close it
				$(this).children('.castFrame').attr("src",'')
				$(this).children('.castFrame').hide();
				$(this).children('.ui-icon-minusthick').addClass("ui-icon-plusthick")
				$(this).children('.ui-icon-minusthick').removeClass("ui-icon-minusthick")					
			}else{
				//close all others
				//$('.castFrame').attr("src",'')
				$('.castFrame').hide();
				$(".ui-icon-minusthick").addClass("ui-icon-plusthick")
				$(".ui-icon-minusthick").removeClass("ui-icon-minusthick")
				//open the current one
				$(this).children('.castFrame').show();				
				$(this).children('.castFrame').attr("src",$(this).children("input:hidden")[0].value);							
				$(this).children('.ui-icon-plusthick').addClass("ui-icon-minusthick")
				$(this).children('.ui-icon-plusthick').removeClass("ui-icon-plusthick")				
				//alert("end")
			}
		}
		function openSlideshowNewWindow(event){
			event.stopPropagation();
			//alert($(this).parent().children("input:hidden")[0].value)
			window.open($(this).parent().children("input:hidden")[0].value)
		}
		$('div.castItem').click(selectCast);
		$('div.castItem div.ui-icon-newwin').click(openSlideshowNewWindow);
		$('div.castItem:first').click();
		
		
	});
	</script>
	<style type="text/css">
  	body {
    	width:100%;
    	height:100%;
    	overflow:auto;
    	//padding-left:20px;
    }
    div.headerStyle {
    	margin-top:26px;
    	margin-bottom:0px;
    	font-size:16;
    	font-weight:700;
    	padding-left:20px;
    	
    }
    p.paragraphStyle {
    	padding-left:20px;    	
    	
    }
    .paragraphStyle{
    	margin-top:7px;
    }
    ul.paragraphStyle li{
    	margin-top:0px;
    	margin-bottom:7px;
    }
    a.castdescription{
    	float:left;    	
    }
    div.iconCast{
    	float:left;
    }
    #topWelcomPargraph{
    	font-weight:700;
    	//font-size:14;
    	width:700px;
    	margin-top:26px;
    	padding-left:20px;
    	margin-bottom:7px;
    }
    div.castItem {
    	cursor:pointer;
    	padding-left:20px;
    	width:580px;
    	margin-bottom:7px;
    }
    iframe.castFrame {
    	display:none;
    	margin-top:13px;
    	margin-bottom:13px;
    }
    div.castItem div.ui-icon-newwin {
    	float:right;
    }
  </style>
</head>
<body >
				<!--div class="headerStyle">
					Welcome to EpiExplorer
					 class="paragraphStyle"
				</div-->
	<p id="topWelcomPargraph">
	EpiExplorer is a web tool that allows you to use large reference epigenome datasets for your own analysis without complex scripting or laborous preprocessing. 
	</p>

	<div class="headerStyle">Getting started</div>
		<p class="paragraphStyle" style="margin-bottom:7px;">
		If this is your first time using EpiExplorer, please have a quick look at the introductory slide-show tutorials:
		</p>
			<div class="castItem">
				<div class="ui-icon ui-icon-plusthick iconCast"></div>
				<a href="#" onclick="return false;" class="castdescription">Getting started with EpiExplorer</a> <div class="ui-icon ui-icon-newwin"></div>
				<br/>
				<!--input type="hidden" value="http://goo.gl/Hqbr0"/-->
				<input type="hidden" value="http://goo.gl/ZD9tZ"/>
				<!--input type="hidden" value="https://docs.google.com/presentation/embed?id=1p0ueg6ndnTGBsULlljB9rs6nwmoOPiOEmkxl9jauQlk&start=false&loop=false&delayms=3000"/-->				
				<iframe class="castFrame" src="" frameborder="0" width="555" height="451"></iframe>
			</div>
			
			<div class="castItem">
				<div class="ui-icon ui-icon-plusthick iconCast"></div>
				<a href="#" onclick="return false;" class="castLink">Adding your dataset(s) in 5 steps</a><div class="ui-icon ui-icon-newwin"></div>
				<br/>
				<!--input type="hidden" value="http://goo.gl/33xwL"/-->
				<input type="hidden" value="http://goo.gl/RQRBm"/>
				<!--input type="hidden" value="https://docs.google.com/presentation/embed?id=1E-Sp3LxAPP65lxl4wmHvgBMbzEevmJcZwLZZ_nm6pSw&start=false&loop=false&delayms=3000"/-->
				<iframe class="castFrame" src="" frameborder="0" width="555" height="451"></iframe>
			</div>	
			
			<div class="castItem">
				<div class="ui-icon ui-icon-plusthick iconCast"></div>
				<a href="#" onclick="return false;" class="castLink">Comparing two datasets side-by-side</a><div class="ui-icon ui-icon-newwin"></div>
				<br/>
				<input type="hidden" value="http://goo.gl/ckAYV"/>
				<!--input type="hidden" value="https://docs.google.com/presentation/embed?id=1B8XwiPPqm-uj5PczXHn43Q1qCN8yLWNpUO0XeXV3R08&start=false&loop=false&delayms=3000"/-->
				<iframe class="castFrame" src="" frameborder="0" width="555" height="451"></iframe>
			</div>	
			<div class="castItem">
				<div class="ui-icon ui-icon-plusthick iconCast"></div>
				<a href="#" onclick="return false;" class="castLink">Saving, exporting and sharing EpiExplorer results</a><div class="ui-icon ui-icon-newwin"></div>
				<br/>
				<input type="hidden" value="http://goo.gl/Qc1re"/>
				<!--input type="hidden" value="https://docs.google.com/presentation/embed?id=1KrDId6d8PzWuUuUfgSHDyTycfq3JE3yidZvRhfyy4I4&start=false&loop=false&delayms=3000"/-->
				<iframe class="castFrame" src="" frameborder="0" width="555" height="451"></iframe>
			</div>
			<div class="castItem">
				<div class="ui-icon ui-icon-plusthick iconCast"></div>
				<a href="#" onclick="return false;" class="castLink">Privacy and confidentiality or what happens with your data when you upload it?</a><div class="ui-icon ui-icon-newwin"></div>
				<br/>
				<input type="hidden" value="http://goo.gl/IWEqJ"/>
				<!--input type="hidden" value="https://docs.google.com/presentation/embed?id=19zNekmU604AAwPG0b-cNJOVAp9O-mrhO19b7RSR3AFk&start=false&loop=false&delayms=3000"/-->
				<iframe class="castFrame" src="" frameborder="0" width="555" height="451"></iframe>
			</div>	
			<div class="castItem">
				<div class="ui-icon ui-icon-plusthick iconCast"></div>
				<a href="#" onclick="return false;" class="castLink">How to test an EpiExplorer overlap for significance using the Genomic HyperBrowser?</a><div class="ui-icon ui-icon-newwin"></div>
				<br/>
				<input type="hidden" value="http://goo.gl/4qDI4"/>
				<!--input type="hidden" value="https://docs.google.com/presentation/embed?id=1-EEgRlqbXZ8cRgaOx4pEis_Mhj1S03hESDaumpTtqpk&start=false&loop=false&delayms=3000"/-->
				<iframe class="castFrame" src="" frameborder="0" width="555" height="451"></iframe>
			</div>
			<div class="castItem">
				<div class="ui-icon ui-icon-plusthick iconCast"></div>
				<a href="#" onclick="return false;" class="castLink">Full listing of the genomic and epigenomic annotations currently available in EpiExplorer</a><div class="ui-icon ui-icon-newwin"></div>
				<br/>
				<input type="hidden" value="http://goo.gl/xOiZv"/>
				<!--input type="hidden" value="https://docs.google.com/spreadsheet/pub?key=0AmGLN6XZ0HmydGNoSi1pVDRmQkg3OERURkh5N09NX1E&output=html&widget=true"/-->
				<iframe class="castFrame" src="" frameborder="0" width="555" height="451"></iframe>
			</div>
			<div class="castItem">
				<div class="ui-icon ui-icon-plusthick iconCast"></div>
				<a href="#" onclick="return false;" class="castLink">(NEW!) Utilizing epigenome annotations base genome coverage as alternative control (or introducing the bubble chart)</a><div class="ui-icon ui-icon-newwin"></div>
				<br/>
				<input type="hidden" value="http://goo.gl/sHuqj"/>
				<!--input type="hidden" value="https://docs.google.com/presentation/embed?id=1xHCFf_R6KAeMkXGlwRZmq70ymGLK486yIffJRFQ8WRk&start=false&loop=false&delayms=3000"/-->
				<iframe class="castFrame" src="" frameborder="0" width="555" height="451"></iframe>
			</div>		
										
		</ol>
				
	<div class="headerStyle tutorialMode">News</div>
		<ul class="tutorialMode paragraphStyle">
			<li><b>3 Oct 2012: EpiExplorer was published at Genome Biology <a href="http://genomebiology.com/2012/13/10/R96">http://genomebiology.com/2012/13/10/R96</a></b>
			<br/>
			<li><b>20 Aug 2012: EpiExplorer now supports the <a href="http://genomebiology.com/2012/13/8/418" target="_blank">mouse ENCODE</a> histone and TFBS data within a week of its publication</b>
			<br/>  
			</li>
			<li>10 July 2012: We added base genome coverage for all supported annotations. Learn more by inspecting the bubble chart and the new slideshow above
			<br/>  
			</li>
			<li>12 Apr 2012: All default datasets are annotated with transcription factor binding sites for dozens of transcription factors
			<br/>  
			</li>
			<li>1 Feb 2012: EpiExplorer now supports annotations for mouse and the latest human genome assembly
			<br/>  
			</li>			
			<li>4 Nov 2011: EpiExplorer is presented at the 2011 CSHL Genome Informatics meeting
			<br/>  
			</li>
			<li>27 Oct 2011: All datasets are now annotated with chromatin state segmentation data by <a href="http://www.nature.com/nature/journal/v473/n7345/full/nature09906.html" target="_blank">Ernst et al. 2011</a>
			<br/>  
			</li>
				
		</ul>
	
	<div class="headerStyle tutorialMode">About EpiExplorer</div>
		<p class="paragraphStyle tutorialMode">EpiExplorer was developed in the <a href="http://www.computational-epigenetics.de/" target="_blank">Computational Epigenetics Group</a> at the <a href="http://www.mpi-inf.mpg.de/" target="_blank">Max-Planck Institute for Informatics</a>.
		EpiExplorer was published at Genome Biology <a href="http://genomebiology.com/2012/13/10/R96">http://genomebiology.com/2012/13/10/R96</a>. Please, cite as
		<br/> <br/>
		<cite>Halachev K, Bast H, Albrecht F, Lengauer T, Bock C: <b>EpiExplorer: live exploration and global analysis of large epigenomic datasets.</b> Genome Biol (2012), 13:R96</cite>
		</p>
				
</body>
</html>
<?php
	}else{
		echo "The EpiExplorer server moved to a nicer domain: <a href='http://epiexplorer.mpi-inf.mpg.de'>http://epiexplorer.mpi-inf.mpg.de</a>";
	}
?>
