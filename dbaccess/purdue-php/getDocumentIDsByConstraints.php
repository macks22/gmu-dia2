<?php

require_once("service_basic.php");
$full = true;

function getDocumentIDsByParams($params) {
    global $full;
    $op = $params->{"logicalOp"};
    $docIDs = array();
    $first = true;

    $paramFuncMap = array(
        "authorID"=>'getDocumentIDsByAuthorID',
        "author"=>'getDocumentIDsByAuthor',
        "personID"=>'getDocumentIDsByPersonID',
        "POID"=>'getDocumentIDsByPOID',
        "poID"=>'getDocumentIDsByPOID',
        "PIID"=>'getDocumentIDsByPIID',
        "coPIID"=>'getDocumentIDsByCoPIID',
        "publicationID"=>'getDocumentIDsByPublicationID',
        "organization"=>'getDocumentIDsByOrganization',
        "organizationID"=>'getDocumentIDsByOrganizationID',
        "NSFProgram"=>'getDocumentIDsByNSFProgram',
        "program"=>'getDocumentIDsByNSFProgram',
        "directorateID"=>'getDocumentIDsByDirID',
        "NSFDirectorate"=>'getDocumentIDsByNSFDirectorate',
        "directorate"=>'getDocumentIDsByNSFDirectorate',
        "dirID"=>'getDocumentIDsByDirID',
        "divisionID"=>'getDocumentIDsByDivID',
        "divID"=>'getDocumentIDsByDivID',
        "division"=>'getDocumentIDsByNSFDivision',
        "NSFDivision"=>'getDocumentIDsByNSFDivision',
        "programID"=>'getDocumentIDsByNSFProgramID',
        "pgmID"=>'getDocumentIDsByNSFProgramID',
        "documentGenreID"=>'getDocumentIDsByDocumentGenreID',
        "publicationGenreID"=>'getDocumentIDsByPublicationGenreID',
        "title"=>'getDocumentIDsByDocumentTitle',
        "documentTitle"=>'getDocumentIDsByDocumentTitle',
        "abstract"=>'getDocumentIDsByAbstract',
        "awardID"=>'getDocumentIDsByAwardIDArray',
        //"MachineGeneratedTerm"=>'getDocumentIDsByMachineGeneratedTerm',
        "conceptID"=>'getDocumentIDsByConceptID',
        "statusGroupID"=>'getDocumentIDsByStatusGroupID',
        "q"=>'getDocumentIDsByFullText',
        "stateID"=>'getDocumentIDsByStateID',
        "year"=>'getDocumentIDsByPublicationYear',
    );

    $ddpDone = false;
    if (isset($params->{"directorateID"})
        && isset($params->{"divisionID"})
        && isset($params->{"programID"}))
    {
    	$docIDs = getDocumentIDsByDirDivPgm($params->{"directorateID"}, $params->{"divisionID"}, $params->{"programID"});
        $first = false;
        $ddpDone = true;
        $full = false;
    }

    foreach ($paramFuncMap as $attr=>$func) {
        if ($ddpDone && in_array($attr, array(
            "NSFProgram", "program", "directorateID",
            "NSFDirectorate", "directorate", "dirID",
            "divisionID", "divID", "division",
            "NSFDivision", "programID", "pgmID")))
        {
            continue;
        }

        if (isset($params->{$attr})) {
            $newIDs = array();
            $ids = getArray($params->{$attr});
            foreach ($ids as $id) {
                array_splice($newIDs, 0, 0, $func($id));
            }

            $newIDs = array_values(array_unique($newIDs));
            if ($op == "and") {
                if ($first) {
                    $docIDs = $newIDs;
                    $first = false;
                } else {
                    $docIDs = array_intersect($docIDs, $newIDs);
                }
            } else {
                array_splice($docIDs, 0, 0, $newIDs);
            }
            $full = false;
        }
    }

    if (isset($params->{"documentID"})) {
        $full = false;
        $first = false;
        $docIDs = getArray($params->{"documentID"});
    }

    if (isset($params->{"yearRange"})) {
        $yr = getArray($params->{"yearRange"});
        $bgnYear = $yr[0];
        $endYear = $yr[1];
        $newIDs = getDocumentIDsByYearRange($bgnYear, $endYear);

        if ($op == "and") {
            if ($first) {
                $docIDs = $newIDs;
            } else {
                $docIDs = array_intersect($docIDs, $newIDs);
            }
        } else {
            array_splice($docIDs, 0, 0, $newIDs);
        }

        $first = false;
        $full = false;
    }

    if ($full) {
        $docIDs = getAllDocumentIDs();
        return $docIDs;
    } else {
        return array_values($docIDs);
    }
}

function getDocumentIDsByParamsWithin($params, $docs) {
	$newIDs = getDocumentIDsByParams($params);
	$docIDs = array_intersect($newIDs, $docs);
	return array_values($docIDs);
}

function filterDocuments($ids) {
    $res = executeSQLSequence($ids, array(
        "select id from document where year(publicationDate)>1970 and title!='' and id in (#)"
    ));

    $retIDs = array();
    foreach ($res as $r) {
        $retIDs[] = $r["id"];
    }
    return $retIDs;
}

function hasCondition($params) {
    return (isset($params->{"authorID"})
         || isset($params->{"personID"})
         || isset($params->{"keywordID"})
         || isset($params->{"publicationID"})
         || isset($params->{"organizationName"})
         || isset($params->{"organizationID"})
         || isset($params->{"publicationGenreID"})
         || isset($params->{"yearRange"})
         || isset($params->{"dirID"})
         || isset($params->{"POID"})
    );
}

function getAllDocumentIDs() {
    $retArray = array();
    $SQLs = array("select max(id) as mx from document");
    $res = executeSQLSequence(array(), $SQLs);
    $maxID = $res[0]["mx"];

    //will this leave the maxID out? should we use $i< $maxID+1 or <=$maxID? Xin added +1
    for ($i = 1; $i < $maxID+1; $i++) {
        $retArray[] = $i;
    }
    return $retArray;
}

function getDocumentIDsByStatusGroupID($id) {
  //$lk = getIDFromLookup("statusGroup", $id);
    $res = executeSQLSequence(array(), array(
        "select statusID as id from group_status where groupID=$id",
        "select documentID as id from documentStatusUpdate where statusID in (#)"
    ));

    $retArr = array();
    foreach ($res as $r) {
        $retArr[] = $r["id"];
    }
    return $retArr;
}

function getDocumentIDsByFullText($q, $adv = false) {
    $groups = array(
        array("phet", "physics and chemistry education technology"),
		array("pogil", "process oriented guided inquiry learning"),
		array("pltl", "peer-led team learning")
    );

    $lq = strtolower($q);
    $special = false;
    $adv = false;
    if (stripos($lq, " and ") !== false || stripos($lq, " or ") !== false) {
        $adv = true;
    }

    foreach ($groups as $g) {
        if (in_array($lq, $g)) {
            foreach ($g as $e) {
              	$qnarr[] = 'name:"'.$e.'"';
              	$qtarr[] = 'title:"'.$e.'"';
            }

            $qn = implode(" OR ", $qnarr);
            $qt = implode(" OR ", $qtarr);
            $special = true;
            break;
        }
    }

    require_once('./SolrPhpClient/Apache/Solr/Service.php');
    // $solr = new Apache_Solr_Service('128.150.141.103', '8983', '/solr');
    $solr = new Apache_Solr_Service('ci4ene09.ecn.purdue.edu', '8983', '/solr');
    if (!$solr->ping()) {
        exit('Solr service not responding.');
    }

    $offset = 0;
    $limit = 9999999;
    if (!$special) {
        // if there is 'and' 'or', leave it as it is,
        // otherwise wrap the whole string with quotes
        if ($adv) {
            $q = str_ireplace(" and ", " AND ", $q);
            $q = str_ireplace(" or ", " OR ", $q);
            $qn = "name:($q)";
            $qt = "title:($q)";
        } else {
            $qn = 'name:"'.$q.'"';
            $qt = 'title:"'.$q.'"';
        }
    }

    $res = $solr->search($qn, $offset, $limit, array("fl"=>"id"));
    $docIDs = array();
    foreach ($res->response->docs as $doc) {
        foreach ($doc as $k=>$v) {
            if ($k == "id") {
                $docIDs[] = intval(trim($v));
            }
        }
    }

    $res = $solr->search($qt, $offset, $limit, array("fl"=>"id"));
    foreach ($res->response->docs as $doc) {
        foreach ($doc as $k=>$v) {
          if ($k == "id") {
        	  $docIDs[] = intval(trim($v));
          }
        }
    }
    return array_values(array_unique($docIDs));
}

function getDocumentIDsByConceptID($id) {

    // get all the sub-concepts
    $ids = array($id);
    $ids = getSubConceptIDs($ids);

    // get document ids associated with all these concepts
    $res = executeSQLSequence($ids, array("select distinct docID as id from concept_document where conceptID in (#)"));
    $docIDs = array();
    $dExist = array();

    foreach ($res as $r) {
        if (!isset($dExist[$r["id"]])) {
            $dExist[$r["id"]] = true;
            $docIDs[] = $r["id"];
        }
    }
    return array_values(array_unique($docIDs));
}

function getDocumentIDsByAbstract($name) {
    $retArray = array();
    $SQLs = array("select id from document where abstract regexp \"$name\"");
    $ids = executeSQLSequence(array(), $SQLs);

    $docIDs = array();
    foreach ($ids as $id) {
        array_splice($docIDs, 0, 0, getDocumentIDsByAuthorID($item["id"]));
    }
    return $docIDs;
}

function getDocumentIDsByOrganization($name) {
    $retArray = array();
    $SQLs = array(
        "select id from organization where name like '".$name."%' or name like '% ".$name."%'",
      	"select id from affiliation where organizationID in (#)",
        "select id from Person where affiliationID in (#)"
    );

    $personIDs = executeSQLSequence(array(), $SQLs);
    $docIDs = array();
    foreach ($personIDs as $item) {
        array_splice($docIDs, 0, 0, getDocumentIDsByAuthorID($item["id"]));
    }
    return $docIDs;
}

function getDocumentIDsByOrganizationArray($arr) {
    $name = implode(" ", $arr);
    $retArray = array();
    $SQLs = array(
        "select id from organization where name like '".$name."%' or name like '% ".$name."%'",
      	"select id from affiliation where organizationID in (#)",
        "select id from Person where affiliationID in (#)"
    );

    $personIDs = executeSQLSequence(array(), $SQLs);
    $docIDs = array();
    foreach ($personIDs as $item) {
        array_splice($docIDs, 0, 0, getDocumentIDsByAuthorID($item["id"]));
    }
    return $docIDs;
}

function getDocumentIDsByOrganizationID($id) {
    $retArray = array();
    $SQLs = array(
        "select id from affiliation where organizationID=$id",
        "select id from Person where affiliationID in (#)"
    );

    $personIDs = executeSQLSequence(array(), $SQLs);
    $pIDs = array();
    foreach ($personIDs as $pID) {
        $pIDs[] = $pID['id'];
    }
    //$allPersonIDs = getDupPersonIDsByPersonIDs($pIDs);

    $res = executeSQLSequence($pIDs, array(
        "select distinct documentID as id from document_person where personID in (#)"
    ));

    foreach ($res as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByStateID($id) {
    $retArray = array();
    $SQLs = array(
        "select id from address where stateID = $id","select id from affiliation where addressID in (#)",
        "select id from Person where affiliationID in (#)"
    );

    $personIDs = executeSQLSequence(array(), $SQLs);
    $pIDs = array();
    foreach ($personIDs as $pID) {
        $pIDs[] = $pID['id'];
    }
    //$allPersonIDs = getDupPersonIDsByPersonIDs($pIDs);

    $res = executeSQLSequence($pIDs, array(
        "select distinct documentID as id from document_person where personID in (#)"
    ));

    foreach ($res as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByKeyword($name) {
    $retArray = array();
    $SQLs = array(
        "select id from keyword where keyword='".$name."' or keyword like '".$name." %' or keyword like '% ".$name."' or keyword like '% ".$name." %'",
        "select documentID as id from document_keyword where keywordID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByKeywordArray($arr) {
    $name = implode(" ", $arr);
    $retArray = array();
    $SQLs = array(
        "select id from keyword where keyword='".$name."'",
        "select documentID as id from document_keyword where keywordID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }

    $SQLs = array(
        "select id from keyword where keyword='".$name."'",
        "select documentID as id from document_machineGeneratedTerm where machineGeneratedTermID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    $retArray = array_values(array_unique($retArray));
    return $retArray;
}

function getDocumentIDsByKeywordID($id) {
    $retArray = array();
    $SQLs = array("select documentID as id from document_keyword where keywordID=$id");

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByMachineGeneratedTermID($id) {
    $retArray = array();
    $SQLs = array("select documentID as id from document_machineGeneratedTerm where machineGeneratedTermID=$id");

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByMachineGeneratedTerm($name) {
    $retArray = array();
    $SQLs = array(
        "select id from keyword where keyword='".$name."' or keyword like '".$name." %' or keyword like '% ".$name."' or keyword like '% ".$name." %'",
        "select documentID as id from document_machineGeneratedTerm where machineGeneratedTermID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByPublicationID($id) {
    $retArray = array();
    $SQLs = array("select id from document where publicationID=$id");

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByPublicationGenreID($id) {
    $retArray = array();
    $docIDs = executeSQLSequence(array(), array(
        "select id from publication where publicationGenreID=$id",
        "select id from document where publicationID in (#)"
    ));

    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByPublicationYear($yr) {
    $retArray = array();
    $SQLs = array("select id from document where year(publicationDate)=$yr");

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByYearRange($bgnYear, $endYear) {
    $retArray = array();

    // Get publicationID for NSF
    $nsfPubID = returnID("", "select ID from publication where name='NSF'");

    // For non-NSF documents
    $SQLs = array(
        "select id from document where year(publicationDate)>=$bgnYear AND year(publicationDate)<=$endYear AND publicationID!=$nsfPubID"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }

    // For NSF documents
    $SQLs = array(
        "select documentID as id from awardactiveperiod where year(startDate)<=$endYear AND year(expirationDate)>=$bgnYear"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByDocumentTitle($name) {
    $retArray = array();
    $SQLs = array("select id from document where title like '".$name." %' OR title like '% ".$name." %' OR title like '%(".$name.")%' OR title like '% ".$name.":%' OR title like '".$name.":%'");
    $docIDs = executeSQLSequence(array(), $SQLs);

    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByDocumentTitleArray($arr) {
    $name = implode(" ", $arr);
    $retArray = array();
    $SQLs = array("select id from document where title like '".$name." %' OR title like '% ".$name." %' OR title like '%(".$name.")%' OR title like '% ".$name.":%' OR title like '".$name.":%'");

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $item) {
        $retArray[] = $item["id"];
    }
    return $retArray;
}

function getDocumentIDsByAuthor($name) {
    $retArray = array();
    $SQLs = array(
        "select id from person where firstName='".$name."' OR lastName='".$name."'",
        "select documentID as id from document_person where personID in (#) AND relationshipID=25"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        $retArray[] = $docIDs[$n]["id"];
    }
    return $retArray;
}

function getDocumentIDsByAuthorArray($arr) {
    if (count($arr) == 0) {
        return array();
    } else if (count($arr) == 1) {
        return getDocumentIDsByAuthor($arr[0]);
    } else if (count($arr) == 2) {
        $str = "(firstName='".$arr[0]."' AND lastName='".$arr[1]."') OR (firstName='".$arr[1]."' AND lastName='".$arr[0]."')";
    } else if (count($arr) >= 3) {
        $first = $arr[0];
        $last = $arr[count($arr)-1];
        $mid = array_splice($arr, 1, -1);
        $str = "(firstName='".$first."' AND lastName='".$last."' AND middleInitial='".implode(" ", $mid)."') OR (firstName='".$arr[count($arr)-1]."' AND lastName='".$arr[0]."' AND middleInitial='".implode(" ", $mid)."')";
    }

    $retArray = array();
    $SQLs = array(
        "select id from person where $str",
        "select documentID as id from document_person where personID in (#) AND relationshipID=2"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByProgramOfficer($name) {
    $retArray = array();
    $SQLs = array("select id from person where firstName='".$name."' OR lastName='".$name."'", "select documentID as id from document_person where personID in (#) AND relationshipID=3");
    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++)
      array_push($retArray, $docIDs[$n]["id"]);
    return $retArray;
}

function getDocumentIDsByProgramOfficerArray($arr) {
    if (count($arr) == 0) {
        return array();
    } else if (count($arr) == 1) {
        return getDocumentIDsByProgramOfficer($arr[0]);
    } else if (count($arr) == 2) {
        $str = "(firstName='".$arr[0]."' AND lastName='".$arr[1]."') OR (firstName='".$arr[1]."' AND lastName='".$arr[0]."')";
    } else if (count($arr) >= 3) {
        $first = $arr[0];
        $last = $arr[count($arr)-1];
        $mid = array_splice($arr, 1, -1);
        $str = "(firstName='".$first."' AND lastName='".$last."' AND middleInitial='".implode(" ", $mid)."') OR (firstName='".$arr[count($arr)-1]."' AND lastName='".$arr[0]."' AND middleInitial='".implode(" ", $mid)."')";
    }

    $retArray = array();
    $SQLs = array(
        "select id from person where $str",
        "select documentID as id from document_person where personID in (#) AND relationshipID=3"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByPI($name) {
    $retArray = array();
    $SQLs = array("select awardID as id from AwardID_PIInfo where (first_name='".$name."' OR last_name='".$name."')");

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsBycoPI($name) {
    $retArray = array();
    $SQLs = array("select awardID as id from COPIID_AwardID where first_name='".$name."' OR last_name='".$name."'");

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByAuthorID($id) {
    $ids = getDupPersonIDsByPersonID($id);
    $retArray = array();
    $authorshipID = getIDFromLookup("documentPersonRelationship", "authorship");
    $res = executeSQLSequence($ids, array("select distinct documentID as id from document_person where personID in (#) AND relationshipID=$authorshipID"));

    foreach ($res as $r) {
        $retArray[] = $r["id"];
    }
    return $retArray;
}

function getDocumentIDsByPIID($id) {
    $ids = getDupPersonIDsByPersonID($id);
    $retArray = array();
    $res = executeSQLSequence($ids, array("select documentID as id from document_person where personID in (#) AND ordering=1 AND relationshipID=2"));

    $dIDs[] = -1;
    foreach ($res as $r) {
        $dIDs[] = $r["id"];
    }

    $SQLs = array(
        "select id from documentGenre where name='Grant Proposal'",
        "select id from document where id in (".implode(",", $dIDs).") AND documentGenreID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByCoPIID($id) {
    $ids = getDupPersonIDsByPersonID($id);
    $retArray = array();
    $res = executeSQLSequence($ids, array(
        "select documentID as id from document_person where personID in (#) AND ordering>1 AND relationshipID=2"
    ));

    $dIDs[] = -1;
    foreach ($res as $r) {
        $dIDs[] = $r["id"];
    }

    $SQLs = array(
        "select id from documentGenre where name='Grant Proposal'",
        "select id from document where id in (".implode(",", $dIDs).") AND documentGenreID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByDocumentGenreID($id) {
    $retArray = array();
    $res = executeSQLSequence(array(), array("select id from document where documentGenreID=$id"));

    foreach ($res as $r) {
        $retArray[] = $r["id"];
    }
    return $retArray;
}

function getDocumentIDsByPOID($id) {
    $ids = getDupPersonIDsByPersonID($id);
    $retArray = array();
    $poID = getIDFromLookup("documentPersonRelationship", "program officer");
    $res = executeSQLSequence($ids, array(
        "select documentID as id from document_person where relationshipID=$poID AND personID in (#)"
    ));

    foreach ($res as $r) {
        $retArray[] = $r["id"];
    }
    return $retArray;
}


function getDocumentIDsByPersonID($id) {
    $ids = getDupPersonIDsByPersonID($id);
    $retArray = array();
    $dIDs = executeSQLSequence($ids, array(
        "select documentID as id from document_person where personID in (#)"
    ));

    for ($n = 0; $n < count($dIDs); $n++) {
        array_push($retArray, $dIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByDirID($dirID) {
    $retArray = array();
    $SQLs = array(
        "select id from dir_div_pgm where nsfdirectorateID='$dirID'",
        "select documentID as id from document_ddp where ddpID in (#)"
    );
    $docIDs = executeSQLSequence(array(), $SQLs);

    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByDivID($divID) {
    $retArray = array();
    $SQLs = array(
        "select id from dir_div_pgm where nsfdivisionID='$divID'",
        "select documentID as id from document_ddp where ddpID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByNSFDirectorate($name) {
    $retArray = array();
    $SQLs = array(
        "select id from nsfdirectorate where name='".$name."' OR abbreviation='".$name."'",
        "select id from dir_div_pgm where nsfdirectorateID in (#)",
        "select documentID as id from document_ddp where ddpID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    foreach ($docIDs as $d) {
        $retArray[] = $d["id"];
    }
    $retArray = array_values(array_unique($retArray));
    return $retArray;
}

function getDocumentIDsByNSFDivision($name) {
    $retArray = array();
    $SQLs = array(
        "select id from nsfdivision where name='".$name."' OR abbreviation='".$name."'",
        "select id from dir_div_pgm where nsfdivisionID in (#)",
        "select documentID as id from document_ddp where ddpID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

/*
  function getDocumentIDsByAgencyOrganizationArray($arr) {
  $name = implode(" ", $arr);
  $retArray = array();
  $SQLs = array("select id from agencyOrganization where name='".$name."' OR abbreviation='".$name."'", "select documentID as id from document_agencyOrganization where agencyOrganizationID in (#)");
  $docIDs = executeSQLSequence(array(), $SQLs);
  for ($n = 0; $n < count($docIDs); $n++)
  array_push($retArray, $docIDs[$n]["id"]);
  return $retArray;
  }
*/

function getDocumentIDsByNSFProgram($name) {
    $retArray = array();
    $SQLs = array(
        "select id from NSFProgram where name like '$name%' OR name like '$name %' OR name like '% $name %' OR name like '% $name'",
        "select id from dir_div_pgm where nsfprogramID in (#)",
        "select documentID as id from document_ddp where ddpID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByNSFProgramID($id) {
    $retArray = array();
    $SQLs = array(
        "select id from dir_div_pgm where nsfProgramID='$id'",
        "select documentID as id from document_ddp where ddpID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByDirDivPgm($dir, $div, $pgm) {
    $retArray = array();
    $SQLs = array(
        "select id from dir_div_pgm where nsfProgramID='$pgm' and nsfdivisionID='$div' and nsfdirectorateID='$dir'",
        "select documentID as id from document_ddp where ddpID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByEmail($email) {
    $retArray = array();

    // PI's email
    $SQLs = array(
        "select id from Person where email='".$email."'", 
        "select federal_award_id as id from Proposal where PI_ID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }

    // Program officer's email
    $SQLs = array(
        "select id from Person where email='".$email."'",
      	"select id from ProgramInfo where officer_ID in (#)",
        "select federal_award_id as id from Proposal where programInfo_ID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByPhone($phone) {
    $retArray = array();

    // PI's phone
    $SQLs = array(
        "select id from Person where phone='".$phone."'",
        "select documentID from document_person where personID in (#)"
    );

    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByAwardID($awardID) {
    $retArray = array();
    $SQLs = array("select documentID as id from Document_Award where awardID='$awardID'");
    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByAwardIDArray($str) {
    $retArray = array();
    $SQLs = array("select documentID as id from document_source_mapper where originalID REGEXP '^$str'");
    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByAmountRange($range) {
    $retArray = array();

    // find the upper bound and lower bound
    $min = '';
    $max = '';
    if ($range->{"min"}) {
        $min = " AND actualAmount>=".$range->{"min"};
    }
    if ($range->{"max"}) {
        $max = " AND actualAmount<=".$range->{"max"};
    }

    // query
    $SQLs = array("select documentID as id from awardAmount where 1=1".$min.$max);
    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function getDocumentIDsByDateRange($range) {
    $retArray = array();

    // find the upper bound and lower bound
    $min = '';
    $max = '';
    if ($range->{"min"}) {
        $min = " AND expirationDate>='".$range->{"min"}."'";
    }
    if ($range->{"max"}) {
        $max = " AND startDate<='".$range->{"max"}."'";
    }

    // query
    $SQLs = array("select documentID as id from awardActivePeriod where 1=1".$min.$max);
    $docIDs = executeSQLSequence(array(), $SQLs);
    for ($n = 0; $n < count($docIDs); $n++) {
        array_push($retArray, $docIDs[$n]["id"]);
    }
    return $retArray;
}

function includePersonAlias($pIDs) {
    for ($n = 0; $n < 2; $n++) {
        $sql = "select id, aliasID from person where ID in (".implode(",", $pIDs).") OR aliasID in (".implode(",", $pIDs).")";
        $r = mysql_query($sql);
        while(($row = mysql_fetch_array($r))) {
            $id = $row["id"];
            $aliasID = $row["aliasID"];
            if (!in_array($id, $pIDs) && $id != 1) {
          	    $pIDs[] = $id;
            }
            if (!in_array($aliasID, $pIDs) && $aliasID != 1) {
          	    $pIDs[] = $aliasID;
            }
        }
    }
    return $pIDs;
}

?>
