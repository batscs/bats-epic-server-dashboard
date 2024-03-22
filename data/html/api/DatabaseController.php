<?php

class Client {

    private $client;

    function __construct($sql) {
        $this->client = $sql;
    }

    public function requiresAuthentication() {
        return true;
    }

    public function authenticate($key) {
        if (!$this->requiresAuthentication()) {
            return true;
        }

        // Password Check
        return $key == "111";
    }

    public function list_hosts() {
        return ["host01_dev", "host02_qa", "host03_prod"];
    }

    public function host_stats($host) {
        return [
            "host" => $host,
            "cpu" => rand(1, 600),
            "memory" => rand(1.0,32.0),
            "storage" => rand(200,1000),
            "tx" => rand(1,7),
            "rx" => rand(1,7)
        ];
    }

    public function host_stats_max($host) {
        return [
            "host" => $host,
            "cpu" => 600,
            "memory" => 32,
            "storage" => 1000,
            "tx" => 7,
            "rx" => 7
        ];
    }

    public function test() {

        $stmt = $this->client->prepare("SELECT CURRENT_TIMESTAMP();");
        $stmt->execute();
        $result = $stmt->fetch();
        echo $result;
    }
}