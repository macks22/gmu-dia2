<?php
require_once("../importData/common.php");
date_default_timezone_set('America/New_York');

$conn = mysql_connect("XXX", "XXX", "XXX") or die("Cannot connect to DB");
mysql_select_db("XXX");

calibrateData();

function calibrateData() {
  ini_set('memory_limit','3072M');
  gc_enable();
  authorNameDisambiguation();
  //renamePublicationNames();
  //correctUnknownDocumentGenre();
  groupSimilarProposals();
  //groupSimilarDocuments();
}

function renamePublicationNames() {
  mysql_query("update publication set name='Education Engineering (EDUCON), IEEE' where name like '%(educon)%'");
  mysql_query("update publication set name='Education, IEEE Transactions On' where name='Education, Ieee Transactions On'");
}

function correctUnknownDocumentGenre() {
  mysql_query("update document set documentGenreID=2 where publicationID in (14, 15, 17)");
  mysql_query("update document set documentGenreID=5 where publicationID in (13, 16)");
}

function groupSimilarDocuments() {
  $similarityThreshold = 0.75;
  $r = mysql_query("select id, title from document");
  while($row = mysql_fetch_array($r, MYSQL_ASSOC)) {
	$docs[] = $row;
  }
  for($i = 0; $i < count($docs); $i++) {
	for($n = $i + 1, $j = 0; $n < count($docs); $n++, $j++) {
	  $t1 = $docs[$i]["title"];
	  $t2 = $docs[$n]["title"];
	  $titleSimilarity = getSimilarity($t1, $t2, null);
	  if($titleSimilarity > $similarityThreshold) {
		$titleSimilarityMatrix[$i][$n] = 1;
	  }
	}
  }
  
 
}

function shouldFilter($t) {
  //return false;
  if(preg_match('/research\s+fellowship/i', $t) == 1)
	return true;
  else
	return false;
}

function groupCollabProposals($sql, $docRelationshipID, $samePI, $primaryRule) {
  // create a doc-value map based on the primary selection rule
  if($primaryRule == "amount") {
	$res = executeSQLSequence(array(), array('select documentID as id, obligatedToDate as amt from awardamount'));
	foreach($res as $r) {
	  $map[$r["id"]] = floatval($r["amt"]);
	}
  } else if($primaryRule == "date") {
	$res = executeSQLSequence(array(), array('select id, publicationDate as dt from document'));
	foreach($res as $r) {
	  $map[$r["id"]] = strtotime($r["dt"]);
	}
  }
  $similarityThreshold = 0.8;
  // store all proposal info into an array and remove the collab... heading
  // ******************************************************************
  $r = mysql_query($sql);
  $proposals = array();
  while(($row = mysql_fetch_array($r, MYSQL_ASSOC))) {
	if(shouldFilter($row["title"]))
	  continue;
	$row["title"] = preg_replace("/^collab([a-zA-Z]|\s)+(:|\-)+/", "", strtolower($row["title"]));
	array_push($proposals, $row);
  }
  //echo count($proposals);
  //exit();
  // sort the array by title
  // ******************************************************************
  usort($proposals, function($a, $b) { return $a["title"] > $b["title"]; });
  $count = 0;
  // compute the similarity matrix -------------------------------------------
  $lookAheadDist = 9;
  for($i = 0; $i < count($proposals); $i++) {
	for($n = $i + 1, $j = 0; $n < count($proposals) && $j < $lookAheadDist; $n++, $j++) {
	  $t1 = $proposals[$i]["title"];
	  $t2 = $proposals[$n]["title"];
	  $titleSimilarity = getSimilarity($t1, $t2, null);
	  if($titleSimilarity > $similarityThreshold) {
		$titleSimilarityMatrix[$i][$n] = 1;
	  }
	}
  }
  //print_r($titleSimilarityMatrix);
  // Group proposals if they are collaborative proposals, randomly select one
  // proposal in the group and direct other proposals to it
  // ******************************************************************
  if(isset($titleSimilarityMatrix)) {
	$groups = formDupGroups($titleSimilarityMatrix, $proposals, $samePI);
	//echo "Identify ".count($groups)." groups of proposals including ".count(array_values(array_unique($groupedIDs)))." awards\n";
	//print_r($groups);
	//exit();
	insertDupDocsIntoDB($groups, $docRelationshipID, $map);
  }
  // set <ID, aliasID> pairs in document_document table
  
}

function insertDupDocsIntoDB($groups, $docRelationshipID, $map) {
  // get the date and amount for each document
  
  $numAffected = 0;
  foreach($groups as $g) {
	if(count($g) == 1) // ignore groups with only one member
	  continue;
	if(isset($members))
	  unset($members);
	//print_r($groups);
	//print_r($g);
	foreach($g as $d) {
	  $members = array();
	  foreach($g as $d)
		$members[] = $d["documentID"];
	}
	$i = 0;
	// sort members based on map values
	arsort($members);
	foreach($members as $m) {
	  if($i == 0)
		$aliasID = $m;
	  else {
		if($m != $aliasID) {
		  mysql_query("insert into document_document (documentID1, documentID2, relationshipID) values ($m, $aliasID, $docRelationshipID)");
		  //echo "insert into document_document (documentID1, documentID2, relationshipID) values ($m, $aliasID, $docRelationshipID)\n";
		}
	  }
	  $i++;
	}	
	// identify the primary author in the group (highest amount as primary)
	/*
	  if(isset($g[0]["actualAmount"])) {
	  $maxAmount = $g[0]["actualAmount"];
	  $aliasID = $g[0]["documentID"];
	  for($i = 1; $i < count($g); $i++) {
	  $d = $g[$i]["actualAmount"];
	  if($maxAmount < $d) {
	  $maxAmount = $d;
	  $aliasID = $g[$i]["documentID"];
	  $aliasTitle = $g[$i]["title"];
	  }
	  }

	  // check existing doc duplicate groups before insertion
	  $members = array();
	  foreach($g as $d)
	  $members[] = $d["documentID"];
	  //if(in_array($aliasID, array(119932,123740,119930,119924)))
	  //print_r($members);
	  foreach($members as $x) {
	  // insert X,Z when exists
	  //   (1) X,Y - compare Y and Z to determine the primary, then update X,primary{Y,Z}.
	  $res = executeSQLSequence(array(), array("select documentid as id, aliasID from document_document where documentid=$x"));
	  if(count($res) > 0) {
	  $y = $res[0]["aliasID"];
	  $res2 = executeSQLSequence(array($aliasID, $y), array("select documentID as id, max(actualAmount) from awardAmount where documentID in (#)"));
	  $aliasID = $res2[0]["id"];
	  if($y != $aliasID)
	  mysql_query("update document_document set aliasID=$aliasID where aliasID=$y");
	  continue;
	  }
	  //   (2) Y,X - update it to Y,Z instead and insert X,Z
	  $res = executeSQLSequence(array(), array("select documentid as id from document_document where aliasID=$x"));
	  if(count($res) > 0) {
	  foreach($res as $r) {
	  mysql_query("update document_document set aliasID=$aliasID where id=".$r["id"]);
	  }
	  mysql_query("insert into document_document (documentID, aliasID, relationshipID) values ($x, $aliasID, $docRelationshipID)");
	  continue;
	  }
	  // insert X,Z when exists
	  //   (1) Z,Y - insert X,Y instead
	  $res = executeSQLSequence(array(), array("select documentID as id, aliasID from document_document where documentid=$aliasID"));
	  if(count($res) > 1) {
	  $y = $res[0]["aliasID"];
	  mysql_query("insert into document_document (documentID, aliasID, relationshipID) values ($x, $y, $docRelationshipID)");
	  continue;
	  }
	  //   (2) Y,Z - insert X,Z as planned
	  mysql_query("insert into document_document (documentID, aliasID, relationshipID) values ($x, $aliasID, $docRelationshipID)");
	  }
	  }
	*/
  }
}

function formDupGroups($titleSimilarityMatrix, $proposals, $samePI) {
  $groupedIDs = array();
  $groups = array();
  foreach($titleSimilarityMatrix as $rowIndex=>$row) {
	$g = array();
	if(in_array($rowIndex, $groupedIDs))	// the award has been grouped, skip
	  continue;
		
	foreach($row as $key=>$value) {
	  if($samePI) {
		if(getPrimaryPersonID($proposals[$rowIndex]["PI_ID"]) == getPrimaryPersonID($proposals[$key]["PI_ID"])) {
		  array_push($g, $proposals[$key]);	// push proposals in this row (over threshold)
		  array_push($groupedIDs, $key);
		}
	  } else {
		if(getPrimaryPersonID($proposals[$rowIndex]["PI_ID"]) != getPrimaryPersonID($proposals[$key]["PI_ID"])) {
		  array_push($g, $proposals[$key]);	// push proposals in this row (over threshold)
		  array_push($groupedIDs, $key);
		}
	  }
	}
	if(count($g) > 0) {
	  array_push($g, $proposals[$rowIndex]);	// push the proposal corresponding to this row
	  array_push($groups, $g);
	}
  }
  //print_r($groups);
  return $groups;
}

function groupSimilarProposals() {
  $authorshipID = returnID("", "select ID from lookup where type='documentPersonRelationship' AND name='authorship'");
  $collabID = returnID("", "select ID from lookup where type='documentRelationship' and name='Collaborative'");
  $modID = returnID("", "select ID from lookup where type='documentRelationship' and name='Modified'");
  // start
  
  echo "Start grouping collaborative proposals ...\n";
  groupCollabProposals("SELECT document.id as documentID, title, year(publicationDate) as year, personID as PI_ID FROM document LEFT JOIN document_person ON document.id=document_person.documentID LEFT JOIN document_ddp ON document.id=document_ddp.documentID WHERE title like 'collab%' AND ordering=1 AND document_person.relationshipID=$authorshipID", $collabID, false, "amount");
  
  echo "Start grouping duplicate proposals ...\n";
  groupCollabProposals("SELECT document.id as documentID, title, year(publicationDate) as year, personID as PI_ID FROM document LEFT JOIN document_person ON document.id=document_person.documentID LEFT JOIN document_ddp ON document.id=document_ddp.documentID WHERE ordering=1 AND document_person.relationshipID=$authorshipID", $modID, true, "date");
  
}

function authorNameDisambiguation() {
  // get the current disambiguation result
  $res = executeSQLSequence(array(), array("select id, aliasID from person_person"));
  foreach($res as $r) {
	$idAlias[$r["id"]] = $r["aliasID"];
  }

  // detect possible duplicates
  for($lastL = 97; $lastL < 97+26; $lastL++) {
	$leadingLast = chr($lastL);
	for($firstL = 97; $firstL < 97+26; $firstL++) {
	  $leadingFirst = chr($firstL);
	  //$leadingLast = "M";
	  //$leadingFirst = "A";
	  $res = executeSQLSequence(array(), array("select id, firstname, lastname, middleinitial from person where lastname like '".$leadingLast."%' and firstname like '".$leadingFirst."%' order by lastname, firstname, middleinitial, id desc"));
	  //echo "***".count($res)."\n";
	  $preL = $preF = $preM = "";
	  $preID = 0;
	  $n = 0;
	  foreach($res as $r) {
		$l = $r["lastname"];
		$f = $r["firstname"];
		$m = $r["middleinitial"];
		$length = strlen($l.$f.$m);
		$id = $r["id"];
		//echo $preID."=".$preL.",".$preF." - ".$preM."\n";
		//echo $id."=".$l.",".$f." - ".$m."\n";
		//echo "=======\n";
		if(($l == $preL && $f == $preF) 
		   || ($l == $preL && substr($f,0,1) == substr($preF,0,1) && (strlen($preF) <= 2 || strlen($f) <= 2))
		   || ($l == $preL && strlen($f) > 2 && strlen($preF) > 2 && (strpos($f, $preF) === 0 || strpos($preF, $f) === 0)))  {
		  if($preLength < $length) {
			$matrix[$preID] = $id;
			$preL = $l;
			$preF = $f;
			$preM = $m;
			$preLength = $length;
			$preID = $id;
		  } else
			$matrix[$id] = $preID;
		} else {
		  $preL = $l;
		  $preF = $f;
		  $preM = $m;
		  $preLength = $length;
		  $preID = $id;
		}
	  }
	  //print_r($matrix);

	  // resolve the matrix
	  foreach($matrix as $id1=>$id2) {
		$endID = $id2;
		while(isset($matrix[$endID]))
		  $endID = $matrix[$endID];
		mysql_query("insert into person_person (id, aliasID) values ($id1, $endID)");
		//echo "$id1, $endID \n";
		$n++;
	  }
	  echo $n." author duplicates identified with lastname $leadingLast $leadingFirst \n";
	  if(isset($matrix))
		unset($matrix);
	  //break;
	}
	//break;
  }
  //removeAuthorNameDisambiguationPath();
}



function removeAuthorNameDisambiguationPath() {
  $res = executeSQLSequence(array(), array("SELECT id, aliasID FROM person_person where id!=aliasID AND aliasID in (select id from person_person where id!=aliasID) "));
  $aliasID = array();
  foreach($res as $r) {
	$map[$r["id"]] = $r["aliasID"];
	$aliasID[] = $r["aliasID"];
	
  }
  print_r($aliasID);
  $res = executeSQLSequence($aliasID, array("select id, aliasID from person_person where id!=aliasID and id in (#)"));
  foreach($res as $r) {
	mysql_query("update person_person set aliasID=".$r["aliasID"]." where aliasID=".$r["id"]);
  }
}

function getSimilarity($a, $b, $maxLenDiff) {
  if($a == $b)
	return 1;
  if($maxLenDiff)	
	if(abs(strlen($a) - strlen($b)) > $maxLenDiff)
	  return 0;
  $dist = levenshtein($a, $b);
  $longerStr = (strlen($a)>strlen($b))?strlen($a):strlen($b);
  return ($longerStr - $dist)/$longerStr;
}

function getPrimaryPersonID($id) {
  $SQLs = array("select aliasID as id from person_person where id=$id AND aliasID!=1");
  $res = executeSQLSequence(array(), $SQLs);
  if(count($res) > 0)
	return $res[0]["id"];
  else
	return $id;
}
