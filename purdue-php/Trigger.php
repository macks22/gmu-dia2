<?php

ini_set('memory_limit','3072M');

function Trigger($params) {
    // Check if file with param attribute exists or not
    $res = checkFile($params);

    // if not exists create one in widgetCache folder
    if (!$res["exist"]) {
        $docIDs = getDocumentIDsByParams($params);
        if (count($docIDs) > 0) {
            global $full;

            //echo "list of documents"."\n";
            if (!$full) {
                $dbe = new DBEssential($docIDs);
            } else {
                $dbe = new DBEssential(null);
            }

            $dbe->full = $full;
            $dbe->run();
            $dbe->save($res["data"]);
        }
        $result["exist"] = false;
    } else {
        $result["exist"] = true;
    }

    $result["status"] = "OK";
    return $result;
}

function checkFile($params){
    $filename = DBEssential::getFileName($params);
    $dir = "widgetcache";
    $open = opendir($dir);
    $pattern = "/\b".$filename."\./";

    while (($file = readdir($open)) !== false ) {
        if (preg_match($pattern,$file)) {
            $result["exist"] = true;
            $result["status"] = "OK";
            $result["data"] = $filename;
            return $result;
        }
    }

    closedir($open);
    $result = array(
        "exist"=>0,
        "status"=>"OK",
        "data"=>$filename
    );

    return $result;
}

?>

