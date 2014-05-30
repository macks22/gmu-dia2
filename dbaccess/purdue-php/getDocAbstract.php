<?php

//require_once("../dbconn.php");
function getDocAbstract($params){
    $docID = $params->{"documentID"};
    $sql = "select title, abstract from document where ID = $docID";
    $r = mysql_query($sql);
    $data = mysql_fetch_row($r);

    $result["data"]["title"] = $data[0];
    if ($data[1]=="") {
        $result["data"]["abstract"] = "No abstract is provided.";
    } else {
        $result["data"]["abstract"] = $data[1];
    }

    $QueryPIs = "select `firstName`, `lastName` from person left join document_person on person.ID = document_person.`personID` where documentID = $docID and relationshipID = 26";
    $PIs = mysql_query($QueryPIs);
    while ($row = mysql_fetch_array($PIs)) {
        $piList[] = $row["firstName"]." ".$row["lastName"];
    }

    $result["data"]["pi"] = implode(", " , $piList);
    $result["status"] = "OK";
    return $result;
}

?>
