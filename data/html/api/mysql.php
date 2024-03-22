<?php
$servername = "db:3306";
$username = "user";
$password = "test";

// Create connection
$mysql = new mysqli($servername, $username, $password);

// Check connection
if ($mysql->connect_error) {
  die("Connection failed: " . $mysql->connect_error);
}
// echo "Connected successfully";