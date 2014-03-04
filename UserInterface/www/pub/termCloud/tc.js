/*

A list of terms, where the size and color of each term is determined
by a number (typically numebr of times it appears in some text).
Uses the Google Visalization API.

Data Format
  First column is the text (string)
  Second column is the weight (positive number)
  Third optional column ia a link (string)

Configuration options:
  target Target for link: '_top' (default) '_blank'

Methods
  getSelection

Events
  select
  * 
10.05.2011 Modified by Konstantin Halachev

*/
String.prototype.startsWith = function(str){
	return (this.match("^"+str)==str)
}
TermCloud = function(container) {
  this.container = container;
}

TermCloud.MIN_UNIT_SIZE = 1;
TermCloud.MAX_UNIT_SIZE = 7;
TermCloud.RANGE_UNIT_SIZE = TermCloud.MAX_UNIT_SIZE - TermCloud.MIN_UNIT_SIZE;

TermCloud.nextId = 0;

TermCloud.prototype.draw = function(data, options) {  
  options = options || {};
  // Start KH 05.10.11 chnages. Commented lines are old version
  // I added options to specify indexes to allow creating termCloud from more flexible data tables
  // The following 3 variables are new  
  var wordColumnIndex = (options["wordColumnIndex"] !== undefined)?options["wordColumnIndex"]:0;
  var numberColumnIndex = (options["numberColumnIndex"] !== undefined)?options["numberColumnIndex"]:1;
  var linkColumnIndex = (options["linkColumnIndex"] !== undefined)?options["linkColumnIndex"]:undefined;
  //check if the column types are correct
  var cols = data.getNumberOfColumns();
  //var valid = (cols >= 2 && cols <= 3 && data.getColumnType(0) == 'string' && data.getColumnType(1) == 'number');
  var valid = (cols >= 2 && data.getColumnType(wordColumnIndex) == 'string' && data.getColumnType(numberColumnIndex) == 'number'); 
      
  //if (valid && cols == 3) {
  if (valid && linkColumnIndex !== undefined) {
    valid = data.getColumnType(linkColumnIndex) == 'string';
  }
  // End KH 05.10.11 chnages  
  if (!valid) {
    this.container.innerHTML = '<span class="term-cloud-error">TermCloud Error: Invalid data format. First column must be a string, second a number, and optional third column a string</span>';
    return;
  }

  
  var linkTarget = options.target || '_top';

  // Compute frequency range
  var minFreq = 999999;
  var maxFreq = 0;
  for (var rowInd = 0; rowInd < data.getNumberOfRows(); rowInd++) {    
    var f = data.getValue(rowInd, numberColumnIndex);    
    if (f > 0) {
      minFreq = Math.min(minFreq, f);
      maxFreq = Math.max(maxFreq, f);
    }
  }

  if (minFreq > maxFreq) {
    minFreq = maxFreq;
  }
  if (minFreq == maxFreq) {
    maxFreq++;
  }
  var range = maxFreq - minFreq;
  //range = Math.max(range, 4);
  //range = Math.max(range, 2);

  var html = [];
  var id = TermCloud.nextId++;
  html.push('<div class="term-cloud">');
  //alert("tc3")
  for (var rowInd = 0; rowInd < data.getNumberOfRows(); rowInd++) {
    var f = data.getValue(rowInd, numberColumnIndex);
    if (f > 0) {
      var text = data.getValue(rowInd, wordColumnIndex);
      var link = linkColumnIndex !== undefined ? data.getValue(rowInd, linkColumnIndex) : null;
      
      if (linkColumnIndex !== undefined){
      	if (link.startsWith("<a")){
	      	var ls = link.indexOf("href=")+6;
	      	//alert(ls)
	      	var lc = link.charAt(ls-1);
	      	//alert(lc)
	      	var le = link.indexOf(lc,ls+1);
	      	//alert(le)
	      	link = link.substring(ls,le);
	      	//alert(link)
	      	//return;
      	}
      }
      var freq = data.getValue(rowInd, numberColumnIndex);
      var size = TermCloud.MIN_UNIT_SIZE +
           Math.round((freq - minFreq) / range * TermCloud.RANGE_UNIT_SIZE);
      //alert("tc4")
      if (linkColumnIndex !== undefined) {
      	html.push('<a class="term-cloud-link" href="', (link || '#'), '" id="_tc_', id, '_', rowInd , '"');
      	if (link) {
        	html.push(' target="', linkTarget, '"');      	
        }
        html.push('>');
      }
      
      //alert("tc5")
      html.push('<span class="term-cloud-', size, '">');
      html.push(this.escapeHtml(text));
      html.push('</span>');
      if (linkColumnIndex !== undefined) {
      	html.push('</a>');
      }
      html.push(' ');
      //alert("tc6")
    }
  }
  html.push('</div>');

  this.container.innerHTML = html.join('');
  //alert("tc7")
  // Add event listeners
  var self = this;
  if (linkColumnIndex !== undefined){
	  for (var rowInd = 0; rowInd < data.getNumberOfRows(); rowInd++) {
	    var f = data.getValue(rowInd, numberColumnIndex);
	    if (f > 0) {
	      var text = data.getValue(rowInd, wordColumnIndex);
	      var link = linkColumnIndex !== undefined ? data.getValue(rowInd, linkColumnIndex) : null;
	      var anchor = document.getElementById('_tc_' + id + '_' + rowInd);
	      anchor.onclick = this.createListener(rowInd, !!link);
	    }
	  }
  }
  //alert("tc8")
};

TermCloud.prototype.createListener = function(row, hasLink) {
  var self = this;
  return function() { 
    self.selection = [{row: row}];
    google.visualization.events.trigger(self, 'select', {});
    return hasLink;
  }
};

TermCloud.prototype.selection = [];

TermCloud.prototype.getSelection = function() {
  return this.selection;
};

TermCloud.prototype.escapeHtml = function(text) {
  if (text == null) {
    return '';
  }
  return text.replace(/&/g, '&amp;').
      replace(/</g, '&lt;').
      replace(/>/g, '&gt;').
      replace(/"/g, '&quot;');
};
