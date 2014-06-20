<?php

ini_set('memory_limit','3072M');
$url = 'http://ci4ene01.ecn.purdue.edu/GMU_DIA2/DIA2/site/JSONRPC/query.php';

$triggerRequest = array(
    'method' => 'Trigger',
    'params'=> array(
        "logicalOp" => 'and',
        'personID' => '13545'
    )
);

$mainRequest = array(
    'method' => 'getName',
    'params'=> array(
        "logicalOp" => 'and',
        "personID" => '13545'
    )
);

$triggerResponse = JSONRPCRequest($url, $triggerRequest);
$mainResponse = JSONRPCRequest($url, $mainRequest);
$data = $mainResponse["result"]["data"];
print_r($data);

foreach($data as $docID=>$valueArr){
    $abstractRequest = array(
        'method' => 'getOneTitleAbstract',
        'params'=>array("docID" => $docID)
    );

    $abstractResponse = JSONRPCRequest($url, $abstractRequest);
    $title = $abstractResponse["result"]["data"]["title"];
    $abstract = $abstractResponse["result"]["data"]["abstract"];
}

function JSONRPCRequest($url, $request){
    $options = array(
        'http' => array(
        'method'  => 'POST',
        'content' => json_encode($request),
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
