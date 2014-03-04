<?php
if (strlen(strstr($_SERVER['SERVER_NAME'],'mpiat3502'))>0 || strlen(strstr($_SERVER['SERVER_NAME'],'moebius'))>0){
	
ini_set('memory_limit', '512M');
//ini_set("display_errors", 1); 

define(LOG_DIR, "/TL/www/epiexplorer/");
define(MAIN_LOG_FILE, "CGS.log");
define(OLD_LOG_FILE, "/CGS_upto(\d{2})\.(\d{4}).log/");


define(SEND_QUERY, "/^.*sends a query.*$/");
define(PROCESS_DATASET, "/^.*uploads a dataset named.*$/");
define(PAGE_VIEW, "/^.*vislogged VISTYPE.*$/");

$ip_geo_cache = array();

function get_ip_geo($ip){
    if (isset($ip_geo_cache[$ip])) {
        return $ip_geo_cache[$ip];
    }

   $address = "http://api.hostip.info/get_html.php?ip=$ip";
   $content = file_get_contents($address, FILE_TEXT);

   $lines = split("\n", $content);

   if (count($lines) < 3) {
      return array();
   }

   $country = split(":", $lines[0]);
   $city = split(":", $lines[1]);

   $g = array($country[1], $city[1]);

   $ip_geo_cache[$ip] = $g;

   return $g;
}

function maskIp($ip) {
   list($a,$b,$c,$d) = split("\.", $ip);
   return $a."."."$b".".".$c.".xxx";
}

function compareData($a, $b) {
   if (intval($a[2]) > intval($b[2])) {
      return 1;
   } else if (intval($a[2]) < intval($b[2])) {
      return -1;
   }
   return intval($a[1]) - intval($b[1]);
}

function compare_entries_date($a, $b) {
   $a = strcmp($b["date_pretty"], $a["date_pretty"]);
   if ($a == 0) {
      return 0;
   }
   if ($a < 0) {
      return -1;
   } else {
      return 1;
   }
}

function get_file_logs_entries($directory, $file, $default_year) {
   $lines = file($directory.$file);

   $accesses = array();
   foreach ($lines as $line_num => $line) {
      if (preg_match("/^.*log_me.*$/", $line) == 0) {
         continue;
      }
      $date_str = "|(\d{2}\.\d{2}[\.\d{4}]?) (\d{2}:\d{2}:\d{2} CFS) log_me: (\d{1,3}\.\d{1,3}\.\d{1,3}\..{1,3}) .*|U";
      preg_match_all($date_str, $line, $out, PREG_PATTERN_ORDER);
      $date = $out[1][0];

      list($day,$month,$year) = split("\.", $date);
      if (strlen($year) == 0) {
          $year = $default_year;
      }
      $date = "new Date($year,$month,$day)";
      $date_pretty = "$year-$month-$day";
      $hour = $out[2][0];
      $address = $out[3][0];

      if (preg_match(SEND_QUERY, $line) > 0) {
         $category = "SEND_QUERY";
      } else if (preg_match(PROCESS_DATASET, $line) > 0) {
         $category = "PROCESS_DATASET";
      } else if (preg_match(PAGE_VIEW, $line) > 0) {
         $category = "PAGE_VIEW";
      } else {
         continue;
      }

      $access_info = array("date" => $date,
                           "date_pretty" => $date_pretty,
                           "hour" => $hour,
                           "address" => $address,
                           "category" => $category);
      array_push($accesses, $access_info);
   }
   return $accesses;
}

function get_all_logs_entries() {
   $handle = opendir(LOG_DIR);

   $files = array();
   while (false !== ($entry = readdir($handle))) {
      if (preg_match(OLD_LOG_FILE, $entry, $matches) > 0) {
         //array_push($files, $matches);
      }
   }
   uasort($files, 'compareData');

   array_push($files, array(MAIN_LOG_FILE, "07", "2012"));

   $FILTER_YEAR = "2000";

   $all_entries = array();

   foreach($files as $file) {
      if ($file[0] == "CGS_upto01.2012.log") {
         $default_year = "2011";
      } else {
         $default_year = $file[2];
      }
      $entries = get_file_logs_entries(LOG_DIR, $file[0], $default_year);
      foreach($entries as $entry) {
         array_push($all_entries, $entry);
      }
   }
   uasort($all_entries, 'compare_entries_date');
   return $all_entries;
}

function get_google_chart_data() {
    $all = get_all_logs_entries();
    $a = aggregate_by_day($all);
    return aggregate_to_google_charts($a);
}

function aggregate_to_google_charts($aggs) {
   $r = "google.visualization.Query.setResponse({version:'0.6', reqId:'0', status:'ok', \n";
   $r = $r . "table: { cols:[{id:'access_date', label:'Access date', type:'date'}, \n";
   $r = $r . "{id:'compute_dataset', label:'Compute Dataset Count', type:'number'},\n";
   $r = $r . "{id:'count', label:'Unique Visitors', type:'number'},";
   $r = $r . "{id:'visualization', label:'Page Views', type:'number'}],";
   $r = $r . " rows:[\n";

   foreach ($aggs as $entry) {
      //$r = $r . "{c:[{v:".$entry['date'].",f:'".$entry['date_pretty']."'},{v:".$entry['send_query']."},{v:".$entry['process_dataset']."},{v:".$entry["count"]."},{v:".$entry['page_view']."}]},";
      $r = $r . "{c:[{v:".$entry['date'].",f:'".$entry['date_pretty']."'},{v:".$entry['process_dataset']."},{v:".$entry["count"]."},{v:".$entry['page_view']."}]},";
   }
   $r = $r . "]}})";

   return $r;
}

function aggregate_by_day($all_entries) {
   $actual_date = NULL;
   $actual_date_pretty = NULL;
   $actual_itens = NULL;
   $aggs = array();

   foreach ($all_entries as $entry) {
      if ($entry["date"] != $actual_date) {
         if ($actual_date != NULL) {
            $actual = array("date" => $actual_date,
                           "date_pretty" => $actual_date_pretty,
                           "send_query" => $send_query,
                           "process_dataset" => $process_dataset,
                           "count" => count($actual_itens),
                           "page_view" => $page_view);
            array_push($aggs, $actual);
         }
         $send_query = 0;
         $process_dataset = 0;
         $page_view = 0;
         $actual_itens = array();
         $actual_date = $entry["date"];
         $actual_date_pretty = $entry["date_pretty"];
      }

      switch ($entry["category"]) {
      case "SEND_QUERY": $send_query++; break;
      case "PROCESS_DATASET": $process_dataset++; break;
      case "PAGE_VIEW": $page_view++; break;
      }

      if (!array_key_exists($entry["address"], $actual_itens)) {
         $actual_itens[$entry["address"]] = 1;
      }
   }
   return $aggs;
}

function all_ip_entries() {
    $all_entries = get_all_logs_entries();
    $result = "";
    foreach($all_entries as $e) {
        $result = $result . maskIp($e['address']) . "\t" . $e['address'] . "\t" . $e['hour'] . "\t" . $e['date_pretty'] . "\t" . $e['category'] . "\n";
    }
   return $result;
}

if ($_GET['type'] == "get_chart_data") {
    print get_google_chart_data();
}
}else{
		echo "To be done";
}
?>
