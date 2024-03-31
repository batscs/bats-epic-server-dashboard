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

    public function hostIdByName($host) {
	    $stmt = $this->client->prepare("SELECT ID FROM hosts WHERE HOST_NAME = :name");
	    $stmt->bindParam("name", $host);
	    $stmt->execute();
	    $data = $stmt->fetch(PDO::FETCH_ASSOC);
	    return $data["ID"];
	}

    public function list_hosts() {
	    $stmt = $this->client->prepare("SELECT HOST_NAME FROM hosts");
	    $stmt->execute();
	    $data = $stmt->fetchAll(PDO::FETCH_ASSOC);

	    $result = array();

	    foreach($data as $item) {
		    if (isset($item["HOST_NAME"])) {
			    $result[] = $item["HOST_NAME"];
		    }
	    }

	    return $result; 
	    //return ["host01_dev", "host02_qa", "host03_prod"];
    }

    public function host_stats($host) {
	    $stmt = $this->client->prepare("SELECT 0 as storage, ROUND(SUM(CPU), 2) as cpu, SUM(MEMORY) as memory, SUM(TX) as tx, SUM(RX) as rx FROM ( SELECT *, ROW_NUMBER() OVER(PARTITION BY CONTAINER ORDER BY TIMESTAMP DESC) rn FROM metrics WHERE HOST_ID = :id AND TIMESTAMP >= DATE_SUB(NOW(), INTERVAL 5 SECOND)) a WHERE rn = 1;"); 
 	    $id = $this->hostIdByName($host);
	    $stmt->bindParam("id", $id);
	    $stmt->execute();
	    $data = $stmt->fetch(PDO::FETCH_ASSOC);
	    return $data;   
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
