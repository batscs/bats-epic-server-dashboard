<?php

class Client {

    private $client;

    function __construct($sql) {
        $this->client = $sql;
    }

    public function requiresAuthentication() {
        $stmt = $this->client->prepare("SELECT AUTH_REQUIRED FROM settings");
        $stmt->execute();
        $data = $stmt->fetch(PDO::FETCH_ASSOC);
        return $data["AUTH_REQUIRED"] == 0 ? False : True;
    }

    public function authenticate($key) {
        if (!$this->requiresAuthentication()) {
            return true;
        }

        $stmt = $this->client->prepare("SELECT AUTH_KEY FROM settings");
        $stmt->execute();
        $data = $stmt->fetch(PDO::FETCH_ASSOC);
        return $data["AUTH_KEY"] == $key ? True : False;
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
    }

    public function host_about($host) {
        $id = $this->hostIdByName($host);

        $stmt = $this->client->prepare("SELECT OS_NAME as os_name, CPU_NAME as cpu_name, CPU_TEMP as cpu_temp, CPU_CORES as cpu_cores, UPTIME as uptime, STORAGE_MAX as storage_max, MEMORY_MAX as memory_max, OS_TIME as os_time, OS_TIMEZONE as os_timezone FROM hosts WHERE ID = :id");
        $stmt->bindParam("id", $id);
        $stmt->execute();
        $data = $stmt->fetch(PDO::FETCH_ASSOC);

        $stmt = $this->client->prepare("SELECT COUNT(distinct CONTAINER) as amount FROM metrics WHERE HOST_ID = :id");
        $stmt->bindParam("id", $id);
        $stmt->execute();
        $result = $stmt->fetch(PDO::FETCH_ASSOC);

        $data["os_containers"] = $result["amount"];

        return $data;
    }

    public function host_stats($host) {
 	    $id = $this->hostIdByName($host);
        
        $stmt = $this->client->prepare("SELECT STORAGE_USED as storage, ROUND(CPU_NOW) as cpu, MEMORY_NOW as memory, TX_NOW as tx, RX_NOW as rx FROM hosts WHERE ID = :id");
	    $stmt->bindParam("id", $id);
        $stmt->execute();
        $result = $stmt->fetch(PDO::FETCH_ASSOC);

        $result["host_name"] = $host;
        $result["host_id"] = $id;

        // RX/TX Not working from host table currently, using sum from containers
        $stmt = $this->client->prepare("SELECT SUM(TX) as tx, SUM(RX) as rx FROM ( SELECT *, ROW_NUMBER() OVER(PARTITION BY CONTAINER ORDER BY TIMESTAMP DESC) rn FROM metrics WHERE HOST_ID = :id AND TIMESTAMP >= DATE_SUB(NOW(), INTERVAL 5 SECOND)) a WHERE rn = 1;");
        $stmt->bindParam("id", $id);
        $stmt->execute();
        $data = $stmt->fetch(PDO::FETCH_ASSOC);
        $result["tx"] = $data["tx"];
        $result["rx"] = $data["rx"];

	    return $result;   
    }

    public function host_stats_max($host) {

        $id = $this->hostIdByName($host);

        $stmt = $this->client->prepare("SELECT CPU_MAX as cpu, MEMORY_MAX as memory, STORAGE_MAX as storage, TX_MAX as tx, RX_MAX as rx FROM hosts WHERE ID = :id");
        $stmt->bindParam("id", $id);
        $stmt->execute();
        $data = $stmt->fetch(PDO::FETCH_ASSOC);

        return $data;
    }

    public function container_chart($host) {
        $id = $this->hostIdByName($host);
        
        $stmt = $this->client->prepare("SELECT * FROM metrics WHERE HOST_ID = :id");
	    $stmt->bindParam("id", $id);
        $stmt->execute();
        $result = $stmt->fetchAll(PDO::FETCH_ASSOC);

        return $result;
    }

    public function container_stats($host) {

    }

    public function container_start_chart($host) {

    }

    public function test() {

        $stmt = $this->client->prepare("SELECT CURRENT_TIMESTAMP();");
        $stmt->execute();
        $result = $stmt->fetch();
        echo $result;
    }
}
