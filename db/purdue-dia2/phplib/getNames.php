<?php

function getNames($params) {
    $ids = $params->{"personIDs"};
    $res = executeSQLSequence($ids, array(
        "select ID, firstName, middleInitial, lastName from person where ID in (#)"
    ));

    $retNames = array();
    foreach ($res as $r) {
        $name = $r["firstName"];
        if (isset($r["middleInitial"]) {
            $name .= " ".$r["middleInitial"].".";
        }
        $name .= " ".$r["lastName"];
        $retNames[$r["ID"]] = $name;
    }

    $result["data"] = $retNames;
    $result["status"] = "OK";
    return $result;

}

?>
