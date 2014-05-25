<?php
function getAuthorInfo($params) {
  ini_set('memory_limit','3072M');
  $attrs = array("oriDocIDs", "dupDocIDs", "nonModDocIDs","nonColModDocIDs","nonModOriDocIDs","authorDocs", "personName", "modDocDocMap","eliminatedPersonIDs");
  $dbe = new DBEssential(null);
  $dbe->load($params, $attrs);
  //$excludedPI["numProposals"] = 0;
  //$excludedPI["name"] = "Info Unavailable";
  //$excludedPI["personID"] = 0;
  $testcnt = 0;
  if(!isset($dbe->oriDocIDs) || count($dbe->oriDocIDs) == 0)
	$result["data"] = null;
  else {
	$uniqueDocIDs = $dbe->getDocIDsByMode($params);
	foreach($uniqueDocIDs as $ud) {
	  $ude[$ud] = true;
	}
	
	
	$ad = $dbe->authorDocs;
	$personName = $dbe->personName;
	$eliminatedPersonIDs = $dbe->eliminatedPersonIDs;
	
	foreach($eliminatedPersonIDs as $p)
	{
	  $eliP[$p] = true;
	}
	
	foreach($ad as $authorID=>$docIDs) {
	  $item["personID"] = $authorID;
	
	    $pDocIDs = array();
	    foreach($docIDs as $d) {
		if(isset($ude[$d]))
		  $pDocIDs[] = $d;
		 }
		 
	  if(!isset($eliP[$authorID]))
	  {
	   
	    $item["numProposals"] = count($pDocIDs);
	    $item["name"] = $personName[$authorID];
	    if($item["numProposals"])
	    {
	    $personCntArr[] = $item;
	    }
	  }
	 
	}
	
	usort($personCntArr, "cmp");
	$result["data"] = $personCntArr;
  }
  $result["status"] = "OK";

  return $result;
}

function cmp($a, $b) {
  if($a["numProposals"] == $b["numProposals"])
	return 0;
  return $a["numProposals"] < $b["numProposals"];
}

?>
