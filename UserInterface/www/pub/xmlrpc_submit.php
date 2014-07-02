<?php
/*****
 * First off we'll be making a function, to send our request to the
 * server.
 * This is where the feared socket programming makes it appearence,
 * take a notice at the default value for port, some people have
 * (for reasons only god may know).
 *****/
function sendRequest($host, $url, $request, $port = 80)
{
    // First off we open a connection to the server.
    if ( !$sock = fsockopen($host, $port, $errNo, $errString) ) {
        echo 'Error: '. $errNo . ' - '. $errString;
        return FALSE;
    }

    /*****
     * We prepare the HTTP header, in our request.
     * Notice we set the Content-Type to text/xml (just notice...).
     *****/
    $httpQuery = "POST ". $url ." HTTP/1.0\n";
    $httpQuery .= "User-Agent: xmlrpc\n";
    $httpQuery .= "Host: ". $host ."\n";
    $httpQuery .= "Content-Type: text/xml\n";
    $httpQuery .= "Content-Length: ". strlen($request) ."\n\n";
    $httpQuery .= $request ."\n";

    // Here we send the request to the server
    if ( !fwrite($sock, $httpQuery, strlen($httpQuery)) ) {
        echo 'Error while trying to send request';
        return FALSE;
    }
	$xmlResponse = "";
    // We get the response from the server
    while ( !feof($sock) ) {
        $xmlResponse .= fgets($sock);
    }

    // Closing the connection
    fclose($sock);

    // We strip the response from it's HTTP header
    $xmlResponse = substr($xmlResponse, strpos($xmlResponse, "\r\n\r\n") +4);

    /*****
     * To decode the XML into PHP, we use the (finaly a short function)
     * xmlrpc_decode function. And that should've done the trick.
     * We now have what ever the server function made in our $xmlRespnse
     * variable.
     *****/
    $xmlResponse = xmlrpc_decode($xmlResponse);

    // Returns the result.
    return  $xmlResponse;
}

?>