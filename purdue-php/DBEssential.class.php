<?php

ini_set('memory_limit','3072M');

class DBEssential {
  public $oriDocIDs, $nonColModDocIDs, $nonModDocIDs, $nonModOriDocIDs, $dupDocIDs;
  public $docTitle;
  public $allDocDocMap, $modDocDocMap;
  public $docAmount;
  public $full;
  public $authorIDs, $personName, $authorMap, $dupAuthorIDs, $excludedPersonIDs,$eliminatedPersonIDs;
  public $yearDocIDs;
  public $docAuthors, $authorDocs, $docPOs, $poDocs;
  public $docDDP, $ddpDocs;
  public $idPgmname, $idDivname, $idDirname, $idDirabbr, $ddp_ddpIDs, $groupStatus, $conceptPC;
  public $ddpExists, $groupStatusExists, $conceptExists, $docDocMapExists;
  public $orgPersons, $orgName;
  public $stateInfo;

  public function __construct($docIDs) {
	  $this->oriDocIDs = $docIDs;
	  $this->ddpExists = file_exists("widgetcache/ddp_name.json");
	  $this->groupStatusExists = file_exists("widgetcache/group_status.json");
	  $this->conceptExists = file_exists("widgetcache/concept.json");
	  $this->stateInfoExists = file_exists("widgetcache/stateInfo.json");
	  $this->excludedPersonIDsExists = file_exists("widgetcache/excludedPersonIDs.json");
	  $this->docDocMapExists = file_exists("widgetcache/ddMap.json");
  }

  public function run() {
	$this->authorshipID = getIDFromLookup("documentPersonRelationship", "authorship");

	if ($this->full)
	  $this->oriDocIDs = $this->getAllDocIDs();

	if ($this->docDocMapExists) {
	  $string   = file_get_contents("widgetcache/ddMap.json");
	  $json   = json_decode($string,true);
	  $this->allDocDocMap = $json["allDocDocMap"];
	  $this->modDocDocMap = $json["modDocDocMap"];
	}
	$this->computeDupDocumentIDs($this->oriDocIDs);

	if (!$this->full) {
	  $this->loadDocumentAuthor();
	}
	$this->computePrimaryDocumentIDs($this->oriDocIDs);
	$this->computeNonModOriDocumentIDs($this->oriDocIDs);

	if (!$this->full)
	  $this->loadDocTitle();
	$this->loadDocAward();

	if (!$this->ddpExists) {
	  $this->loadPgmName();
	  $this->loadDivName();
	  $this->loadDirName();
	  $this->loadDDP();
	}
	$this->loadDDPDoc();

	if (!$this->conceptExists) 
	  $this->loadConceptPC();
	$this->loadStatusGroups();
	$this->loadDocAmount();

	if (!$this->excludedPersonIDsExists)
	  $this->loadExcludedPersonIDs();
	
	if (!$this->full)
	  $this->loadPersonIDNameMap();
	$this->loadYearDocIDs();

	if (!$this->full) {
	  $this->loadOrgPersonMap(); //Sanjeev
	  $this->loadStateOrg();
	  $this->loadOrgDocs();
	}
	$this->loadStateInfo();
	
	//print_r($this);
  }

  public function getAllDocIDs() {
	  $res = executeSQLSequence(array(), array("select id from document"));
	  foreach ($res as $r) {
	      $all[] = $r["id"];
	  }
	  return $all;
  }

  public function save($fileName) {
	$dir = "widgetcache";
	$open = opendir($dir);
	$pattern = "/\b".$fileName."\./";
	while (($file = readdir($open)) !== false){
	    if (preg_match($pattern, $file)){
	        unlink($file);
	    }
	}
	closedir($open);
	
	$fileName = "widgetcache/".$fileName;
	if (!$this->stateInfoExists) {
	    file_put_contents("widgetcache/stateInfo.json", json_encode($this->stateInfo));
	}

	if (!$this->ddpExists) {
	    $json = array();
	    $json["idPgmname"] = $this->idPgmname;
	    $json["idDivname"] = $this->idDivname;
	    $json["idDivabbr"] = $this->idDivabbr;
	    $json["idDirname"] = $this->idDirname;
	    $json["idDirabbr"] = $this->idDirabbr;
	    $json["ddp_ddpIDs"] = $this->ddp_ddpIDs;
	    $json["ddpID_ddp"] = $this->ddpID_ddp;
	    file_put_contents("widgetcache/ddp_name.json", json_encode($json));
	}

	if (!$this->docDocMapExists) {
	    $json = array();
	    $json["allDocDocMap"] = $this->allDocDocMap;
	    $json["modDocDocMap"] = $this->modDocDocMap;
	    file_put_contents("widgetcache/ddMap.json", json_encode($json));
	}

	if (!$this->excludedPersonIDsExists) {
	    file_put_contents("widgetcache/excludedPersonIDs.json", json_encode($this->excludedPersonIDs));
	}

	if (!$this->groupStatusExists) {
	    file_put_contents("widgetcache/group_status.json", json_encode($this->groupStatus));
	}

	if (!$this->conceptExists) {
	    file_put_contents("widgetcache/concept.json", json_encode($this->conceptPC));
	}
	
	// getting the unique and duplicate documents
    $fields = array(
        "full", "docTitle", "docAward",
        "oriDocIDs", "nonColModDocIDs", "nonModDocIDs",
        "nonModOriDocIDs", "dupDocIDs", "eliminatedPersonIDs",
        "docAmount", "authorIDs", "dupAuthorIDs",
        "authorMap", "docAuthors", "authorDocs",
        "ddpDocs", "docDDP", "poIDs",
        "docPOs", "poDocs", "personName",
        "yearDocIDs", "orgPersons", "orgName",
        "stateOrg", "orgDocs"
    );

    // Save certain fields to the cache files.
	foreach ($fields as $f) {
        if (($f == "docTitle"
            || $f == "personName"
            || $f == "docAuthors"
            || $f == "orgName"
            || $f == "stateOrg"
            || $f=="orgDocs"
            || $f == "poIDs")
            && $this->full)
        {
		    continue;
        }
	    $this->saveToFile($fileName, $f);
	}
  }

  function saveToFile($prefix, $name) {
      file_put_contents($prefix.".".$name.".json", json_encode($this->$name));
  }

  public function load($params, $attrs=null) {
    if ($attrs == null || in_array("ddp", $attrs)) {
	  $string = file_get_contents("widgetcache/ddp_name.json");
	  $json   = json_decode($string,true);
	  $this->idPgmname = $json["idPgmname"];
	  $this->idDivname = $json["idDivname"];
	  $this->idDivabbr = $json["idDivabbr"];
	  $this->idDirname = $json["idDirname"];
	  $this->idDirabbr = $json["idDirabbr"];
	  $this->ddp_ddpIDs= $json["ddp_ddpIDs"];
	  $this->ddpID_ddp = $json["ddpID_ddp"];
	}

	if ($attrs == null || in_array("stateInfo", $attrs)) {
	  $string = file_get_contents("widgetcache/stateInfo.json");
	  $this->stateInfo = json_decode($string, true);
	}

	if ($attrs == null || in_array("status", $attrs)) {
	  $string   = file_get_contents("widgetcache/group_status.json");
	  $this->groupStatus   = json_decode($string,true);
	}

	if ($attrs == null || in_array("excludedPersonIDs", $attrs)) {
	  $string = file_get_contents("widgetcache/excludedPersonIDs.json");
	  $this->excludedPersonIDs = json_decode($string, true);
	}

	if ($attrs == null || in_array("conceptPC", $attrs)) {
	  $string   = file_get_contents("widgetcache/concept.json");
	  $this->conceptPC   = json_decode($string,true);
	}

	if ($this->docDocMapExists) {
	  $string   = file_get_contents("widgetcache/ddMap.json");
	  $json   = json_decode($string,true);
	  $this->allDocDocMap = $json["allDocDocMap"];
	  $this->modDocDocMap = $json["modDocDocMap"];
	}
	

    $caseAttrs = array(
        "full","docTitle","docAward",
        "oriDocIDs","nonColModDocIDs","nonModDocIDs",
        "nonModOriDocIDs","dupDocIDs","eliminatedPersonIDs",
        "docAmount","authorIDs", "dupAuthorIDs",
        "docAuthors","authorDocs","authorMap",
        "ddpDocs","docDDP","poIDs",
        "docPOs","poDocs","personName",
        "yearDocIDs","orgPersons", "stateOrg",
        "orgDocs", "orgName"
    );

	if ($attrs==null) {
	    $items = $caseAttrs;
	} else {
	    $items = array_intersect($attrs, $caseAttrs);
    }
	
	if (isset($params) && $params != null) {
	    $fileName = "widgetcache/".DBEssential::getFileName($params);
	    foreach ($items as $item) {
	        $string = file_get_contents($fileName.".".$item.".json");
	        $json = json_decode($string,true);
	        $this->$item =$json;
	    }
	}
  }

  public static function getFileName($params){

	// getting the name of the file with params
	$filename = "";
	$paramsArr = (array) $params;
	foreach ($paramsArr as $k=>$v) {
	  unset($paramsArr[$k]);
	  $paramsArr[strtolower($k)] = $v;
	}

	ksort($paramsArr);
	//print_r($paramsArr);
	foreach ($paramsArr as $k=>$v) {
        if ($k == "userid"
            || $k == "mode"
            || $k == "overviewmode"
            || $k == "depth"
            ||(gettype($v) != "string"
            && gettype($v) != "array"
            && gettype($v) != "integer"))
        {
		    continue;
        }

	    if (gettype($v)=="array") {
	        $filename.= $k."=";
	        foreach ($v as $t) {
	          $filename.=$t;
	        }
	        $filename.="_";
	    }
	    else {
	        $filename .= $k."=".$v."_";
	    }
	}

	$filename = substr($filename, 0, -1);  
	$filename = str_replace("?", "_", $filename);
	$filename = str_replace("/", "^", $filename);
	$filename = str_replace("&", "+", $filename);
	$filename = str_replace("%20", "_", $filename);
	$filename = str_replace(" ", "_", $filename);
	$filename = str_replace('"', '+qt', $filename);
	$filename = strtolower($filename);
	//echo $filename;
	
	return $filename;
  }


  function loadExcludedPersonIDs() {
	  $this->excludedPersonIDs = array();
	  //Name Not Available
      $res = executeSQLSequence(array(),
          array('select id from person where lastname="" or lastname in ("None","Available","DATA NOT AVAILABLE")'));
	  foreach ($res as $r) {
	      $this->excludedPersonIDs[] = $r["id"];
	  }
  }
  
  function getDocumentAliasMapByCollab($docIDs) {
      // Check function in service_basic.php the two parameters are $type and $name
	  $dupID = getIDFromLookup("documentRelationship", "collaborative");
      $res = executeSQLSequence($docIDs, 
          array("select documentID1 as id, documentID2 as aliasID from document_document where (documentID1 in (#) or documentID2 in (#)) and relationshipID=$dupID"));
	  foreach ($res as $r) {
	      $map[$r["id"]] = $r["aliasID"];
	  }
	  return $map;
  }

  public static function getPersonAliasMap($pids) {
      $res = executeSQLSequence($pids,
          array("select id, aliasID from person_person where id in (#) or aliasID in (#)"));
	  foreach ($res as $r) {
	      $map[$r["id"]] = $r["aliasID"];
	  }
	  return $map;
  }

  function loadStateInfo() {
      $res = executeSQLSequence(array(),
          array('select id, name, abbreviation as abbr from state'));
	  foreach ($res as $r) {
	      $this->stateInfo[$r["id"]] = array("name"=>$r["name"],
	  									 "abbr"=>$r["abbr"]);
	  }
  }
  
  function loadOrgPersonMap(){
	  $pIDs = $this->dupAuthorIDs;
	  $res = executeSQLSequence($pIDs, array("select affiliationID as id from person where id in (#)",
	  									   "select organizationID as id from affiliation where id in (#)",
	  									   "select name, id from organization where id in (#)"));
	  foreach ($res as $r) {
	      $this->orgName[$r["id"]] = $r["name"];
	  }
  }

  function loadOrgDocs() {
	  $this->orgDocs = array();
	  $authorshipID = $this->authorshipID;
	  // person-doc
	  
	  $res = executeSQLSequence($this->dupDocIDs,
	  			array("select documentID as docID, personID as id from document_person where documentID in (#) and relationshipID in ($authorshipID)",
	  								));

	  $persons = array();
	  foreach ($res as $r) {
	      $persons[] = $r["id"];
	      if (!isset($pd[$r["id"]])) {
	    	$pd[$r["id"]] = array();
          }
	      $pd[$r["id"]][] = $r["docID"];
	  }

	  // aff-person
	  $persons = array_values(array_unique($persons));
      $res = executeSQLSequence($persons,
          array("select id, affiliationID from person where id in (#)"));
	  $affs = array();

	  foreach ($res as $r) {
	      $affs[] = $r["affiliationID"];
	      if (!isset($aff_persons[$r["affiliationID"]])) {
	          $aff_persons[$r["affiliationID"]] = array();
          }
	      $aff_persons[$r["affiliationID"]][] = $r["id"];
	  }

	  // org-aff
	  $affs = array_values(array_unique($affs));
      $res = executeSQLSequence($affs,
          array('select id, organizationID from affiliation where id in (#)'));

	  foreach ($res as $r) {
	      $affID = $r["id"];
	      $orgID = $r["organizationID"];
	      if (!isset($this->orgDocs[$orgID])) {
	    	$this->orgDocs[$orgID] = array();
          }

	      $persons = $aff_persons[$affID];
	      foreach ($persons as $p) {
	    	$docs = $pd[$p];
	    	array_splice($this->orgDocs[$orgID], 0, 0, $docs);
	      }

	      $this->orgDocs[$orgID] = array_values(array_unique($this->orgDocs[$orgID]));
	      if (count($this->orgDocs[$orgID]) == 0) {
	    	unset($this->orgDocs[$orgID]);
          }
	  }
  }
  
  function loadStateOrg() {
	  $authorshipID = $this->authorshipID;
	  // all available affiliation IDs
	  $res = executeSQLSequence($this->dupDocIDs,
              array("select personID as id from document_person where documentID in (#) and relationshipID in ($authorshipID)",
                    "select affiliationID as id from person where id in (#)",
                    "select id, addressID, organizationID from affiliation where id in (#)"
                    ));

	  $affs = array();
	  $addrs = array();
	  $orgs = array();
	  //print_r($res);

	  foreach ($res as $r) {
	      $affs[] = $r["id"];
	      // aff-addr
	      $aff_addr[$r["id"]] = $r["addressID"];
	      $addr_aff[$r["addressID"]] = $r["id"];
	      $addrs[] = $r["addressID"];
	      // aff-org
	      $aff_org[$r["id"]] = $r["organizationID"];
	  }

	  $addrs = array_values(array_unique($addrs));
	  //print_r($addrs);
	  // addr-state and state-org
	  $res = executeSQLSequence($addrs, array("select id, stateID from address where id in (#)"));
	  foreach ($res as $r) {
	      $addr_state[$r["id"]] = $r["stateID"];
	      if (!isset($state_org[$r["stateID"]])) {
	          $state_org[$r["stateID"]] = array();
          }
	      $state_org[$r["stateID"]][] = $aff_org[$addr_aff[$r["id"]]];
	  }
	  $this->stateOrg = $state_org;
  }
  
  function loadPgmName() {
  	  $res = executeSQLSequence(array(), array("select id, name from nsfprogram"));
  	  foreach ($res as $r) {
  	      $this->idPgmname[$r["id"]] = $r["name"];
  	  }
  }

  function loadDivName() {
	  $res = executeSQLSequence(array(), array("select id, name, abbreviation from nsfdivision"));
	  foreach ($res as $r) {
	      $this->idDivname[$r["id"]] = $r["name"];
	      $this->idDivabbr[$r["id"]] = $r["abbreviation"];
	  }
  }

  function loadDirName() {
	  $res = executeSQLSequence(array(), array("select id, name, abbreviation as abbr from nsfdirectorate"));
	  foreach ($res as $r) {
	      $this->idDirname[$r["id"]] = $r["name"];
	      $this->idDirabbr[$r["id"]] = $r["abbr"];
	  }
  }

  function loadDDP() {
      $res = executeSQLSequence(array(),
          array("select id, nsfdirectorateID as dirID, nsfdivisionId as divID, nsfprogramID as pgmID from dir_div_pgm"));

	  foreach ($res as $r) {
  	      $id    = $r["id"];
  	      $dirID = $r["dirID"];
  	      $divID = $r["divID"];
  	      $pgmID = $r["pgmID"];

  	      if (!isset($this->ddp_ddpIDs[$dirID][$divID][$pgmID])) {
  	  	      $this->ddp_ddpIDs[$dirID][$divID][$pgmID] = array();
          }
  	      $this->ddp_ddpIDs[$dirID][$divID][$pgmID][] = $id;
          $this->ddpID_ddp[$id] = array(
              "dir"=>$dirID,
              "div"=>$divID,
              "pgm"=>$pgmID);
	  }
  }

  function loadDDPDoc() {
	  $res = executeSQLSequence($this->oriDocIDs, array("select ddpID, documentID from document_ddp where documentID in (#)"));
	  foreach ($res as $r) {
	      if (!isset($this->ddpDocs[$r["ddpID"]])) {
	    	  $this->ddpDocs[$r["ddpID"]] = array();
          }
	      $this->ddpDocs[$r["ddpID"]][] = $r["documentID"];
	      $this->docDDP[$r["documentID"]] = $r["ddpID"];
	  }
  }
  
  function loadStatusGroups() {
	/*
	$res = executeSQLSequence(array(), array("select groupID, statusID from group_status"));
	foreach ($res as $r) {
	  if (!isset($this->groupStatus[$r["groupID"]]))
		$this->groupStatus[$r["groupID"]] = array();
	  $this->groupStatus[$r["groupID"]][] = $r["statusID"];
	}
	*/
  }

  function loadConceptPC() {
      $res = executeSQLSequence(array(),
          array("select parentid as pid, childid as cid from conceptidrelation"));

	  foreach ($res as $r) {
	      if (!isset($this->conceptPC[$r["pid"]])) {
	          $this->conceptPC[$r["pid"]] = array();
          }
	      $this->conceptPC[$r["pid"]][] = $r["cid"];
	  }
  }

  public static function getDocumentAliasMap($docIDs) {
	$modID = getIDFromLookup("documentRelationship", "modified");
	$colID = getIDFromLookup("documentRelationship", "collaborative");
	$res = executeSQLSequence($docIDs, array("select documentID2 as id from document_document where documentID1 in (#) and relationshipID in ($modID, $colID)"));
	$ids = array();
	array_splice($ids, 0, 0, $docIDs);
	foreach ($res as $r) {
	  $ids[] = $r["id"];
	}
	$res = executeSQLSequence($ids, array("select documentID1 as id, documentID2 as aliasID from document_document where (documentID1 in (#) or documentID2 in (#)) and relationshipID in ($modID, $colID)"));
	foreach ($res as $r) {
	  $map[$r["id"]] = $r["aliasID"];
	}
	if (isset($map))
	  return $map;
	else
	  return array();
	/*
	$res = executeSQLSequence($docIDs, array("select documentID1 as id, documentID2 as aliasID from document_document where documentID1 in (#) or documentID2 in (#)"));
	foreach ($res as $r) {
	  $map[$r["id"]] = $r["aliasID"];
	}
	*/
	return $map;
  }

  public static function getDocumentAliasMapByModByDocs($docIDs) {
	$dupID = getIDFromLookup("documentRelationship", "modified");
	if ($docIDs == null) {
	  $res = executeSQLSequence(array(), array("select documentID1 as id, documentID2 as aliasID from document_document where relationshipID=$dupID"));
	} else {
	  $res = executeSQLSequence($docIDs, array("select documentID2 as id from document_document where documentID1 in (#) and relationshipID=$dupID"));
	  $ids = array();
	  array_splice($ids, 0, 0, $docIDs);
	  foreach ($res as $r) {
		$ids[] = $r["id"];
	  }
	  $res = executeSQLSequence($ids, array("select documentID1 as id, documentID2 as aliasID from document_document where (documentID1 in (#) or documentID2 in (#)) and relationshipID=$dupID"));
	  
	}
	foreach ($res as $r) {
	  $map[$r["id"]] = $r["aliasID"];
	}
	if (isset($map))
	  return $map;
	else
	  return array();
  }
  
  function getDocumentAliasMapByMod() {
	$dupID = getIDFromLookup("documentRelationship", "modified");
	$res = executeSQLSequence($this->dupDocIDs, array("select documentID2 as id from document_document where documentID1 in (#) and relationshipID=$dupID"));
	$ids = array();
	array_splice($ids, 0, 0, $docIDs);
	foreach ($res as $r) {
	  $ids[] = $r["id"];
	}
	$res = executeSQLSequence($ids, array("select documentID1 as id, documentID2 as aliasID from document_document where (documentID1 in (#) or documentID2 in (#)) and relationshipID=$dupID"));
	foreach ($res as $r) {
	  $map[$r["id"]] = $r["aliasID"];
	}
	if (isset($map))
	  return $map;
	else
	  return array();
  }

  function loadPersonIDNameMap() {
	  if (count($this->authorIDs) == 0) {
	      $allPersonIDs = $this->poIDs;
      } else if (count($this->poIDs) == 0) {
	      $allPersonIDs = $this->authorIDs;
      } else {
          $allPersonIDs = array_merge($this->poIDs, $this->authorIDs);
      }

  	  $SQLs = array("select firstName, lastName, middleInitial, id from person where id in (#)");
	  $res = executeSQLSequence($allPersonIDs, $SQLs);

	  foreach ($res as $r) {
	      $lastName = strtolower($r["lastName"]);
          if ($lastName == "" || $lastName == "none"
              || $lastName=="available" || $lastName=="data not available")
          {
	          $this->eliminatedPersonIDs[] = $r["id"];
          } else {
	          $this->personName[$r["id"]] = name2String($r);
          }
	  }
  }

  function computePrimaryDocumentIDs() {
	  $ids = $this->dupDocIDs;
	  if (!$this->docDocMapExists) {
	      $collab = getIDFromLookup("documentRelationship", "Collaborative");
	      $mod = getIDFromLookup("documentRelationship", "Modified");
	      $relationshipIDs = array($collab, $mod);

	      // Build the doc-doc map for disambiguation
          $res = executeSQLSequence($ids,
              array("select documentID1 as id, documentID2 as doc2, relationshipID from document_document where relationshipID in (".implode(",", $relationshipIDs).")"));

	      foreach ($res as $r) {

	  	      // build the doc-doc map for all relationship (modified and collaborative)
	  	      $this->allDocDocMap[$r["id"]] = $r["doc2"];

	  	      // build the doc-doc map for only modified relationship
	  	      if ($r["relationshipID"] == $mod) {
	  	        $this->modDocDocMap[$r["id"]] = $r["doc2"];
              }
	      }
	  }

	  // Find the primary IDs
	  $this->nonColModDocIDs = DBEssential::disambiguateDocuments($ids, $this->allDocDocMap);
	  $this->nonModDocIDs = DBEssential::disambiguateDocuments($ids, $this->modDocDocMap);
  }
  
   function computeNonModOriDocumentIDs (){
      $ids = $this->oriDocIDs;
      if (!$this->docDocMapExists) {
          $collab = getIDFromLookup("documentRelationship", "Collaborative");
          $mod = getIDFromLookup("documentRelationship", "Modified");
          $relationshipIDs = array($collab, $mod);

          // Build the doc-doc map for disambiguation
          $res = executeSQLSequence($ids, array("select documentID1 as id, documentID2 as doc2, relationshipID from document_document where relationshipID in (".implode(",", $relationshipIDs).")"));

          foreach ($res as $r) {
        	  // build the doc-doc map for all relationship (modified and collaborative)
        	  $this->allDocDocMap[$r["id"]] = $r["doc2"];

        	  // build the doc-doc map for only modified relationship
        	  if ($r["relationshipID"] == $mod)
        	    $this->modDocDocMap[$r["id"]] = $r["doc2"];
            }
      }
      $this->computeCurrentDocIDs($ids, $this->modDocDocMap);
  }

  public static function getDupDocumentIDs($ids, $map) {
	$rmap = array();
	$newids = array();
	
	foreach ($ids as $id) {
	  $newids[$id] = true;
	}

	foreach ($map as $k=>$v) {
	  $rmap[$v][]=$k; 
	}

	foreach ($ids as $id) {
	  if (isset($map[$id])) {
		$newids[$map[$id]] = true;
      }
	}

	foreach (array_keys($newids) as $id) {
	    if (isset($rmap[$id])) {
	        foreach ($rmap[$id] as $index=>$ID) {
                $newids[$ID] = true;
            }
	    }
	}
	
	unset($rmap);
	return array_keys($newids);
  }
  
  public static function disambiguateDocuments($ids, $map) {
	foreach ($ids as $i) {
	  $ie[$i] = true;
	}

	if ($map != null) {
	  foreach ($ids as $id) {
		if (isset($map[$id])) {
		  unset($ie[$id]);
		  $ie[$map[$id]] = true;
		}
	  }
	}
	return array_keys($ie);
  }

  public function computeCurrentDocIDs($ids, $map) {
	foreach ($ids as $i) {
	  $ie[$i] = true;
	}

	if ($map != null) {
	  foreach ($ids as $id) {
		if (isset($map[$id])) {
		   unset($ie[$id]);
		
		}
	  }
	}
	$this->nonModOriDocIDs = array_keys($ie);
  }

  function computeDupDocumentIDs($ids) {
	  $newids = array();
	  foreach ($ids as $id) {
	      $newids[$id] = true;
	  }

	  //array_splice($newids, 0, 0, $ids);
	  // create an alias map
	  if ($this->full) {
	  	  $this->dupDocIDs = $this->oriDocIDs;
      } else {
	      $this->dupDocIDs = DBEssential::getDupDocumentIDs($ids, $this->allDocDocMap);
	  }
  }

  function loadDocumentAuthor() {
	$authorshipID = $this->authorshipID;
	$poRelationshipID = getIDFromLookup("documentPersonRelationship", "program officer");
	// document-author and document-po
	//echo implode(",",$this->dupDocIDs);
	if ($this->full)
		$res = executeSQLSequence(array(), array("select personID as id, documentID, relationshipID from document_person where relationshipID in ($authorshipID, $poRelationshipID)"));
	else
		$res = executeSQLSequence($this->dupDocIDs, array("select personID as id, documentID, relationshipID from document_person where documentID in (#) and relationshipID in ($authorshipID, $poRelationshipID)"));
	$i = 0;
	$aExist = array();
	foreach ($res as $r) {
	  $pID = $r["id"];
	  $dID = $r["documentID"];
	  if ($r["relationshipID"] == $authorshipID) {
		if (!isset($aExist[$pID])) {
		  $aExist[$pID] = true;
		  $aIDs[] = $pID;
		}
		$this->docAuthors[$dID][$pID] = true;
		$authorDocs[$pID][$dID] = true;
	  } else if ($r["relationshipID"] == $poRelationshipID) {
		$poIDs[] = $pID;
		$this->docPOs[$dID][$pID] = true;
		$poDocs[$pID][$dID] = true;
	  }
	}
	unset($aExist);
	$this->dupAuthorIDs = $aIDs;
	// person name disambiguation
	// -- author IDs
	if ($this->full)
		$res = executeSQLSequence(array(), array("select id, aliasID from person_person"));
	else
		$res = executeSQLSequence($aIDs, array("select id, aliasID from person_person where id in (#)"));
	$src = array();
	$alias = array();
	foreach ($res as $r) {
	    $this->authorMap[$r["id"]] = $r["aliasID"];
	    $alias[] = $r["aliasID"];
	    $src[] = $r["id"];
	}
	$primary = array_diff($aIDs, $src);
	
	array_splice($primary, 0, 0, $alias);
	$this->authorIDs = array_values(array_unique($primary));

	// -- PO IDs
	$poIDs = array_values(array_unique($poIDs));
	$res = executeSQLSequence($poIDs, array("select id, aliasID from person_person where id in (#)"));
	$src = array();
	$alias = array();
	foreach ($res as $r) {
	    $this->poMap[$r["id"]] = $r["aliasID"];
	    $alias[] = $r["aliasID"];
	    $src[] = $r["id"];
	}
	$primary = array_diff($poIDs, $src);
	array_splice($primary, 0, 0, $alias);
	$this->poIDs = array_values(array_unique($primary));

	// Refine doc-authors and doc-POs with disambiguated authors
	foreach ($this->docAuthors as $docID=>$authorIDs) {
	  $newAuthorIDs = array();
	  foreach ($authorIDs as $aID=>$temp) {
		if (isset($this->authorMap[$aID]))
		  $aID = $this->authorMap[$aID];
		$newAuthorIDs[] = $aID;
	  }
	  $this->docAuthors[$docID] = $newAuthorIDs;
	}

	foreach ($this->docPOs as $docID=>$poIDs) {
	  $newPOIDs = array();
	  foreach ($poIDs as $poID=>$temp) {
		if (isset($this->poMap[$poID]))
		  $poID = $this->poMap[$poID];
		$newPOIDs[] = $poID;
	  }
	  $this->docPOs[$docID] = $newPOIDs;
	}

	// Refine author-docs and po-docs with disambiguated authors
	foreach ($authorDocs as $aID=>$docIDs) {
	  if (isset($this->authorMap[$aID]))
		$aID = $this->authorMap[$aID];
	  if (!isset($this->authorDocs[$aID]))
		$this->authorDocs[$aID] = array();
	  $dIDs = array_keys($docIDs);
	  array_splice($this->authorDocs[$aID], 0, 0, $dIDs);
	}

	foreach ($poDocs as $poID=>$docIDs) {
	  if (isset($this->poMap[$poID]))
		$poID = $this->poMap[$poID];
	  if (!isset($this->poDocs[$poID]))
		$this->poDocs[$poID] = array();
	  $dIDs = array_keys($docIDs);
	  array_splice($this->poDocs[$poID], 0, 0, $dIDs);
	}

	// clean up
	unset($authorDocs);
	unset($poDocs);
  }

  function loadDocAmount() {
      $res = executeSQLSequence($this->dupDocIDs,
          array("select documentID as docID, obligatedToDate as amt from awardamount where documentID in (#)"));
	  foreach ($res as $r) {
	      $this->docAmount[$r["docID"]] = floatval($r["amt"]);
	  }
  }

  function loadDocTitle() {
	  $res = executeSQLSequence($this->dupDocIDs, array("select id, title from document where id in (#)"));
	  foreach ($res as $r) {
	      $this->docTitle[$r["id"]] = $r["title"];
	  }
  }

  function loadDocAward() {
      $res = executeSQLSequence($this->dupDocIDs,
          array("select documentID as id, originalID from document_source_mapper where documentID in (#)"));
	  foreach ($res as $r) {
	      $this->docAward[$r["id"]] = $r["originalID"];
	  }
  }

  function loadYearDocIDs() {
	$res = executeSQLSequence($this->dupDocIDs, array("select id, year(publicationDate) as yr from document where id in (#)"));
	foreach ($res as $r) {
	  if (!isset($this->yearDocIDs[$r["yr"]]))
		$this->yearDocIDs[$r["yr"]] = array();
	  $this->yearDocIDs[$r["yr"]][] = $r["id"];
	}
  }

  public static function isFull($params) {
    foreach ($params as $k=>$v) {
        if ($k != "logicalOp") {
            return false;
        }
    }
    return true;
  }

  public static function isFullAwarded($params) {
    foreach ($params as $k=>$v) {
	    if (($k != "logicalOp" && $k != "statusGroupID" && $k != "mode") || ($k == "statusGroupID" && $v != 32)) {
	    	return false;
        }
    }
    return true;
  }

  public function getDocIDsByMode($params) {
	if (isset($params->{"mode"})) {
	    $mode = $params->{"mode"};
    } else {
	    $mode = "disambiguated";
    }

	if ($mode == "disambiguated") {
	    return $this->nonColModDocIDs;
    } else if ($mode == "all") {
	    return $this->dupDocIDs;
    } else if ($mode == "current") {
	    return $this->nonModOriDocIDs;
    } else if ($mode == "collab") {
	    return $this->nonModDocIDs;
    } else if ($mode == "ori" || $mode == "original") {
	    return $this->oriDocIDs;
    }
  }

}

?>
