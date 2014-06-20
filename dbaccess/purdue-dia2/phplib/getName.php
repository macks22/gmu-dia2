<?php

function getName($params) {
    $attrs = array("ddp", "yearDocIDs", "personName", "poIDs", "authorIDs");
    $dbe = new DBEssential(null);
    $dbe->load($params, $attrs);

    $data = array();

    // If given a directorateID, use it to filter?
    if (isset($params->{"directorateID"})) {
  	    $dir = $dbe->idDirname;
  	    if (isset($dir[$params->{"directorateID"}])) {
            $data[] = array(
                "role"=>"directorate",
                "value"=>$dir[$params->{"directorateID"}]
            );
        }
    } else {  // otherwise search all directorates
  	    $data[] = array("role"=>"directorate","value"=>"All");
    }

    // Same idea here? Filter on directorate if passed.
    // NSFDirectorate appears to be an alternative to directorateID
    // (Perhaps change to else if logic?)
    if (isset($params->{"NSFDirectorate"})) {
        $data[] = array(
            "role"=>"directorate",
            "value"=>$params->{"NSFDirectorate"});
    }

    // Filter by division?
    if (isset($params->{"divisionID"})) {
  	    $div = $dbe->idDivname;
  	    if (isset($div[$params->{"divisionID"}])) {
            $data[] = array(
                "role"=>"division",
                "value"=>$div[$params->{"divisionID"}]
            );
        }
    } else {  // otherwise search all divisions
  	    $data[] = array("role"=>"division", "value"=>"All");
    }

    // NSFDivision
    if (isset($params->{"NSFDivision"})) {
        $data[] = array(
            "role"=>"division",
            "value"=>$params->{"NSFDivision"}
        );
    }

    // Filter by program ID?
    if (isset($params->{"programID"})) {
  	    $pgm = $dbe->idPgmname;
  	    if (isset($pgm[$params->{"programID"}])) {
            $data[] = array(
                "role"=>"program",
                "value"=>$pgm[$params->{"programID"}]
            );
        }
    } else {  // otherwise search through all
  	    $data[] = array("role"=>"program","value"=>"All");
    }

    if (isset($params->{"NSFProgram"})) {
        $data[] = array(
            "role"=>"program",
            "value"=>$params->{"NSFProgram"}
        );
    }

    if (isset($params->{"author"})) {
  	    $data[] = array("role"=>"PI","value"=>$params->{"author"});
    }

    if (isset($params->{"documentTitle"})) {
        $data[] = array(
            "role"=>"proposal title",
            "value"=>$params->{"documentTitle"}
        );
    }

    if (!isset($params->{"yearRange"})) {
  	    $yearDocIDs = $dbe->yearDocIDs;
  	    $years = array_keys($yearDocIDs);
  	    $yearRange = array();
  	    $yearRange[0] = intval($years[0]);
  	    $yearRange[1] = intval($years[count($years)-1]);
  	    $data[] = array("role"=>"yearRange","value"=>$yearRange);
    }

    // -----------------------------
    // Handler for personID requests
    // -----------------------------
    if (isset($params->{"personID"})) {
  	    $id = $params->{"personID"};
  	    $personName = $dbe->personName[$id];
  	    $poIDs = $dbe->poIDs;
  	    $authorIDs = $dbe->authorIDs;
  	    $role = array();
  	    $affiliations = array();

        // If the person is a PO:
  	    if (in_array($id, $poIDs)) {
  	        $role[] = "program officer";
            array_push($affiliations, array(
                "id"=>-1,
                "name"=>"NSF")
            );
  	    }

        // If the person is a PI/coPI:
  	    if (in_array($id, $authorIDs)) {
  	        $role[] = "PI/coPI";
  	        $aMap = DBEssential::getPersonAliasMap(array($id));
  	        $dupIDs = array($id);
  	        $nonPrimIDs = array_keys($aMap);

            // Put together an array of the disambiguated IDs
  	        foreach ($nonPrimIDs as $np) {
  	            $dupIDs[] = $np;
  	        }

            // First, query for all affiliation IDs for this PI/coPI
            $affiliationIds = executeSQLSequence($dupIDs, array(
                "select affiliationID as id from person where id in (#)")
            );

            // For each affiliation, get the organization info and address
            $orgRecords = array();
            foreach ($affiliationIds as $aid) {
                $orgInfo = executeSQLSequence(array(), array(
                    "select organizationID as id from affiliation where id=$id",
                    "select id, name, abbreviation from organization where id in (#)")
                );
                $address = executeSQLSequence(array(), array(
                    "select addressID as id from affiliation where id=$id",
                    "select street, cityID, stateID, nationID, zipCode from address where id in (#)")
                );

                // Get actual names of address components
                $addressInfo = array(
                    "street" => $address["street"],
                    "zipCode" => $address["zipCode"]
                );
                $cityId = $address["cityID"];
                $addressInfo["city"] = executeSQLSequence(array(),
                    "select name from city where id=$cityId");
                $stateId = $address["stateID"];
                $addressInfo["state"] = executeSQLSequence(array(),
                    "select name, abbreviation from state where id=$stateId");
                $nationId = $address["nationID"];
                $addressInfo["nation"] = executeSQLSequence(array(),
                    "select code, name, abbreviation from nation where id=$nationId");

                // Add entry to affiliation records to be returned
                array_push($affiliations, array(
                    "id"=>$aid,
                    "organization" => $orgInfo,
                    "address" => $addressInfo)
                );

            }

            //// Query for all organizations associated with this PI/coPI
            //$res = executeSQLSequence($dupIDs, array(
            //    "select affiliationID as id from person where id in (#)",
  	        //    "select organizationID as id from affiliation where id in (#)",
            //    "select id, name, abbreviation from organization where id in (#)")
            //);

            //// Set the name to the ID if no name is set
            //$orgNameID = array();
  	        //foreach ($res as $r) {
  	        //    if (!isset($orgNameID[$r["name"]])) {
  	        //        $orgNameID[$r["name"]] = $r["id"];
            //    }
  	        //}

            //// Add each organization found to the array of affiliations
  	        //foreach ($orgNameID as $name=>$id) {
            //    array_push($affiliations, array(
            //        "id"=>$id,
            //        "name"=>$name)
            //    );
            //}
  	    }

        // Return roles in comma-delimited list (string)
        $data[] = array(
            "role"=> implode(",", $role),
            "value"=> $personName,
            "affiliation"=>$affiliations
        );

  	    if (isset($role))
  	        unset($role);
        }

        if (isset($params->{"POID"})) {
  	        $id = $params->{"POID"};
            $res = executeSQLSequence(array(), array(
                "select id, firstName, lastName from person where id=$id"));
  	        $v = $res[0]["firstName"]." ".$res[0]["lastName"];
  	        $data[] = array("role"=>"program officer","value"=>$v);
        }

        // Get information about a particular author
        if (isset($params->{"authorID"})) {
            $authorAffiliations = array();
  	        $id = $params->{"authorID"};
            $res = executeSQLSequence(array(), array(
                "select id, firstName, lastName from person where id=$id"));

  	        $authorName = $res[0]["firstName"]." ".$res[0]["lastName"];
  	        $aMap = DBEssential::getPersonAliasMap(array($id));
  	        $dupIDs = array_keys($aMap);

            $res = executeSQLSequence($dupIDs, array(
                "select affiliationID as id from person where id in (#)",
  	            "select organizationID as id from affiliation where id in (#)",
                "select id, name from organization where id in (#)")
            );

  	        foreach ($res as $r) {
  	            if (!isset($orgNameIDAu[$r["name"]])) {
  	                $orgNameIDAu[$r["name"]] = $r["id"];
                }
  	        }
  	        foreach ($orgNameIDAu as $name=>$id) {
  	            array_push($authorAffiliations, array("id"=>$id, "name"=>$name));
            }

            $data[] = array(
                "role"=>"PI/coPI",
                "value"=>$authorName,
                "affiliation" => $authorAffiliations
            );
        }

    if (isset($params->{"organizationID"})) {
  	    $id = $params->{"organizationID"};
        $res = executeSQLSequence(array(), array(
            "select id, name from organization where id=$id"));

        $data[] = array(
            "role"=>"organization",
            "value"=>$res[0]["name"]
        );
    }

    if (isset($params->{"conceptID"})) {
  	    $id = $params->{"conceptID"};
        $res = executeSQLSequence(array(), array(
            "select id, concept from concept where id=$id"));

        $data[] = array(
            "role"=>"concept",
            "value"=>$res[0]["concept"]
        );
    }

    if (isset($params->{"q"})) {
  	    $q = $params->{"q"};
  	    $data[] = array("role"=>"text", "value"=>$q);
    }

    // Added if statement to account for awardID queries.
    if (isset($params->{"awardID"})) {
  	    $q = $params->{"awardID"};
  	    $data[] = array("role"=>"text", "value"=>$q);
    }

    if (isset($params->{"stateID"})) {
        $id = $params->{"stateID"};
        $res = executeSQLSequence(array(), array(
            "select ID, name from state where ID=$id"));

        $data[] = array(
            "role"=>"state",
            "value"=>$res[0]["name"]
        );
    }

    $result["data"] = $data;
    $result["status"] = "OK";
    return $result;
}

?>
