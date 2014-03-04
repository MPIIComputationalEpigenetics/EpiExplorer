/*####----####---- Function ----####----####*/
function numberWithCommas(x) {
    	return x.toString().replace(/\B(?=(?:\d{3})+(?!\d))/g, ",");
}
/*####----####---- Function ----####----####*/
String.prototype.startsWith = function(str){
	return (this.match("^"+str)==str)
}
Array.prototype.sum = function(start,end) {
  return (! this.length) ? 0 : this.slice(1).sum(start-1,end-1) +
      ((typeof this[0] == 'number' & start<=0 & end>=0) ? this[0] : 0);
}
Array.prototype.max = function(){
    return Math.max.apply( Math, this );
};

Array.prototype.min = function(){
    return Math.min.apply( Math, this );
};

Array.prototype.binarySearchLE = function(find) {
  var low = 0, high = this.length - 1,
      i, comparison;
  while (low <= high) {
    i = Math.floor((low + high) / 2);
    comparison = this[i] <= find;
    if (comparison) { low = i + 1; continue; }
    else{ high = i - 1; continue; };
    //return i;
  }
  return high;
};
Array.prototype.searchSE = function(find) {
	for (var i=find;i>=0;i--){
		if(this[i] !== undefined){
			return i
		}
	}
	return 0;
};
Array.prototype.searchLE = function(find) {
	for (var i=find;i<this.length;i++){
		if(this[i] !== undefined){
			return i
		}
	}
	return this.length-1;
};

if(typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function() 
    {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}
String.prototype.repeat = function( num )
{
    return new Array( num + 1 ).join( this );
}
if(!Object.keys) Object.keys = function(o){
	 if (o !== Object(o))
	      throw new TypeError('Object.keys called on non-object');
	 var ret=[],p;
	 for(var p in o) if(Object.prototype.hasOwnProperty.call(o,p)) ret.push(p);
	 return ret;
}
/* REFERENCE UPDATE */
function getDefaultReferenceState(){
	return {"genome":"",
			"dataset":"",
			"query":"",
			"queryParts":[],
			"editable":false,
			"values":{},
			"statvalues":{},
			"totalNumber":0
			};
}

function getParameterByName(name) {

    var match = RegExp('[?&]' + name + '=([^&]*)')
                    .exec(window.location.search);

    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));

}

/*function getParameterByName( parName )
{
  parName = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+parName+"=([^&#]*)";
  var regex = new RegExp( regexS );
  alert(window.location.href)
  var results = regex.exec( window.location.href );
  alert(results)
  if( results == null )
    return "";
  else
    return decodeURIComponent(results[1].replace(/\+/g, " "));
}*/

function emailvalidate(email) {
	//alert('Javascript email check');
	var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;  
  if(reg.test(email) == false) {
      //alert('Invalid Email Address');	      
      return false;
  }
  return true;
}

function convertRangeToNumber(number,numberOfDigits,rangeBase){
	// The number x was computed from y 
	// log(y,10)+y[:numberOfDigits-1]
	// this is the method that converts itback to something similar(rounded) to y 
	if (number < Math.pow(10,numberOfDigits-1)){
		return number;
	}else{
		var ns = number.toString();				
		var powL = Math.pow(10,ns[0] - rangeBase - numberOfDigits + 2);
		if (numberOfDigits > 1){
			if (ns[1] == "0"){
				var ns1 = ns[0]+"1";
				if (numberOfDigits > 2){
					ns1 = ns1+"0"					
				}
				ns = ns1;
				//alert(ns)
			} 
		}
		var sec = parseInt(ns.slice(1), 10);
		return (sec == 0)? powL : sec*powL;
	}
}
function convertRatioToNumber(number,ratioBase){
	return number/Math.pow(10,ratioBase);	
}

function highlightElement(element,time,pulsTimes){		
	//var time = 1000;		
	var oldColor = element.css("background-color");		
	//element.css("background-color","#ffffc8").effect("pulsate", { times:3 }, time).css("background-color",oldColor);//#FA9627
	element.css("background-color","#ffffc8").show("pulsate", { times:pulsTimes }, time ,function(){
		//alert("about to put the old color back")
		element.css("background-color",oldColor);
		//alert("old color is back")
		}
	);//#FA9627
	// //		
  	//element.effect("highlight", {}, time).effect("highlight", {}, time).effect("highlight", {}, time);
}

function initBasicButtons(){
	
	//all not implemented
	$('body').delegate(".notimplementedButton","click",function(){
		alert("This functionality is not yet implemented!");
	});
	
	//The explore new dataset
	$("#exploreDefaultDatasetsLink").click(function(){
		window.location.href = 'index.php';
	});
	//The explore new dataset
	$("#exploreII27Button").click(function(){
		window.location.href = 'exploreII27.php';
	});
	//upload dataset button		
	$("#uploadUserDatasetsButton").click(function(){
		window.location.href = 'uploadManagement.php';
	});
	//search button
	
	$("#searchButton").click(function(){
		window.location.href = 'search.php';
	});
	// the about box
	$("#aboutButton").click(function(){
		window.location.href = 'about.php';
	});	
	// Give feedback
	$("#giveFeedbackButton").click(function(){
		window.location.href = 'feedback.php';
	});
	
}
