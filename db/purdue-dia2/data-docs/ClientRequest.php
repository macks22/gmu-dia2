<?php

ini_set('memory_limit','3072M');

$url = 'http://ci4ene01.ecn.purdue.edu/GMU_DIA2/DIA2/site/JSONRPC/query.php';

$triggerRequest = array(
    'method' => 'Trigger',
    'params'=>array(
        "logicalOp" => 'and',
        'yearMonth' => '2011-01',
        "directorateID" =>'05'
    )
);

$mainRequest = array(
    'method' => 'GMUDataTransfer',
    'params'=>array(
        "logicalOp" => 'and',
        "mode" => 'current',
        'yearMonth' => '2011-01',
        "directorateID" =>'05'
    )
);

$triggerResponse = JSONRPCRequest($url, $triggerRequest);
$mainResponse = JSONRPCRequest($url, $mainRequest);
print_r($mainResponse);
$data = $mainResponse["result"]["data"];

foreach($data as $docID=>$valueArr) {
    $abstractRequest = array(
        'method' => 'getOneTitleAbstract',
        'params'=>array("docID" => $docID)
    );

    $abstractResponse = JSONRPCRequest($url, $abstractRequest); 
    $title = $abstractResponse["result"]["data"]["title"];
    $abstract = $abstractResponse["result"]["data"]["abstract"];

    echo $docID."\n";
    echo $title." ".$abstract."\n"; 
}

function JSONRPCRequest($url, $request){
    $options = array(
        'http' => array(
        'method'  => 'POST',
        'content' => json_encode( $request ),
        'header'=>  "Content-Type: application/json\r\n" .
                    "Accept: application/json\r\n"
        )
    );

    $context  = stream_context_create( $options );
    $result = file_get_contents( $url, false, $context );

    $response = json_decode($result, true);
    return $response;
}

?>
