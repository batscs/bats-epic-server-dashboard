<?php
header('Content-Type: application/json');

require_once("DatabaseController.php");
require_once("mysql.php");

global $mysql;

$client = new Client($mysql);

$response = [];

if ($client->authenticate($_GET["auth"])) {
    $response["auth"] = true;
} else {
    $response["auth"] = false;
    $response["key"] = $_GET["auth"];
}

if ($response["auth"] == true) {
    if (isset($_GET["get"])) {
        if ($_GET["get"] == "hosts") {
            $response["hosts"] = $client->list_hosts();
        }
    }

    if (isset($_GET["host"]) && isset($_GET["stat"])) {
        if ($_GET["stat"] == "stats") {
            $response["stats"] = $client->host_stats($_GET["host"]);
        } else if ($_GET["stat"] == "max") {
            $response["max"] = $client->host_stats_max($_GET["host"]);
        }
    }
   
    //$client->test();
}

$json = json_encode($response);
echo $json;

// TODO: getHosts()
// TODO: getCPU("host")