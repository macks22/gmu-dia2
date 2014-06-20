<?php

function computeAliasMap(&$documentAliasMap, &$authorAliasMap) {
    // *********************************************************************
    // Construct the alias map
    // *********************************************************************

    $sql = "select id, aliasID from person where id!=aliasID AND aliasID!=1";
    $r = mysql_query($sql);
    while($row = mysql_fetch_array($r, MYSQL_ASSOC)) {
        $authorAliasMap[$row["id"]] = $row["aliasID"];
    }

    $sql = "select documentID, aliasID from document_document";
    $r = mysql_query($sql);
    while($row = mysql_fetch_array($r, MYSQL_ASSOC)) {
        $documentAliasMap[$row["documentID"]] = $row["aliasID"];
    }
}

?>
