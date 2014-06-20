<?php

function query($params) {
  $docIDs = getDocumentIDsByParams($params);
  // person alias
  $res = executeSQLSequence($docIDs, array("select personID as id from document_person where documentID in (#) AND relationshipID=26", "select ID, aliasID from person_person where id in (#) or aliasID in (#)"));
  foreach($res as $r) {
	$personAlias[$r["ID"]] = $r["aliasID"];
  }
  // document alias
  $res = executeSQLSequence($docIDs, array("select documentID1, documentID2 from document_document where documentID1 in (#) or documentID2 in (#)"));
  foreach($res as $r) {
	//echo "###";
	$docAlias[$r["documentID1"]] = $r["documentID2"];
  }
  // not limit to doc
  $limitToDoc = $params->{"limitToDoc"};
  if(!isset($limitToDoc) || $limitToDoc == false)
	$res = executeSQLSequence($docIDs, array("select personID as id from document_person where documentID in (#) AND relationshipID=2", "select documentID, personID from document_person where relationshipID=26 AND personID in (#) and documentID!=1"));
  else
	$res = executeSQLSequence($docIDs, array("select documentID, personID from document_person where documentID in (#) AND documentID!=1 AND relationshipID=26"));
  foreach($res as $r) {
	if(isset($docAlias[$r["documentID"]]))
	  $docID = $docAlias[$r["documentID"]];
	else
	  $docID = $r["documentID"];
	if(isset($personAlias[$r["personID"]]))
	  $authorID = $personAlias[$r["personID"]];
	else
	  $authorID = $r["personID"];
	if(!isset($docAuthors[$docID]))
	  $docAuthors[$docID] = array();
	$docAuthors[$docID][] = $authorID;
  }
  
  $result["data"] = $docAuthors;
  $result["status"] = "OK";
  return $result;

}

?>
