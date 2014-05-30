<?php

function getPOInfo($params) {
    ini_set('memory_limit','3072M');

    $attrs = array("oriDocIDs", "nonColModDocIDs", "nonModOriDocIDs","poDocs", "personName","eliminatedPersonIDs");
    $dbe = new DBEssential(null);
    $dbe->load($params);

    //$excludedPO["numProposals"] = 0;
    //$excludedPO["name"] = "Info Unavailable";
    //$excludedPO["personID"] = 0;

    if (!isset($dbe->oriDocIDs) || count($dbe->oriDocIDs) == 0) {
        $result["data"] = null;
    } else {
        $uniqueDocIDs = $dbe->getDocIDsByMode($params);
        foreach ($uniqueDocIDs as $ud) {
            $ude[$ud] = true;
        }

        $poDocs = $dbe->poDocs;
        $personName = $dbe->personName;
        $eliminatedPersonIDs = $dbe->excludedPersonIDs;

        foreach ($eliminatedPersonIDs as $p) {
            $eliP[$p] = true;
        }

        foreach ($poDocs as $po=>$doc) {
            $item["personID"] = $po;
            $udocs = array();

            foreach ($doc as $d) {
          	    if (isset($ude[$d])) {
          	        $udocs[] = $d;
                }
          	}

            if (!isset($eliP[$po])) {
                $item["numProposals"] = count($udocs);
                $item["name"] = $personName[$po];

                // if there are any proposals
                if ($item["numProposals"]) {
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
    if ($a["numProposals"] == $b["numProposals"]) {
        return 0;
    }
    return $a["numProposals"] < $b["numProposals"];
}

?>
