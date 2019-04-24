<?php
$db_connection = pg_connect("host=localhost dbname=<DATABASENAME. user=<USERNAME> password=<PASSWORD>"");
if ($_SERVER['REQUEST_METHOD'] == 'POST'){
        if ($_POST['type'] == 'startSession'){
                $location = $_POST['location'];
                $startSessionQuery = "INSERT INTO phonesetup_statsession (location) VALUES ('$location')RETURNING session_id";
                $sessionInfo = pg_query($db_connection, $startSessionQuery);
                $sessionID = pg_fetch_result($sessionInfo, 0, 0);
                $myObj->sessionid = $sessionID;
        }
        elseif ( $_POST['type'] == 'addTo'){
                $sessionID = $_POST['session'];
                $fileName = $_POST['file'];
                $buttonID = $_POST['button'];
                $addToQuery = "INSERT INTO phonesetup_statactivity (button_file_name, button_name_id, session_id_id) VALUES ('$fileName', '$buttonID', '$sessionID') RETURNING activity_id";
                $addToInfo = pg_query($db_connection, $addToQuery);
                $myObj->activityID = pg_fetch_result($addToInfo, 0, 0);
        }
        elseif ($_POST['type'] == 'closeSession'){
                $sessionID = $_POST['session'];
                $closeQuery = "UPDATE phonesetup_statsession SET end_time = NOW() WHERE session_id = '$sessionID'";
                $closeInfo = pg_query($db_connection, $closeQuery);
                $myObj->activityID = pg_fetch_result($closeInfo, 0, 0);
        }

        $myJSON = json_encode($myObj);
        echo $myJSON;
}
?>
