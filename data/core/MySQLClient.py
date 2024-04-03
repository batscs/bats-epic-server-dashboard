import mysql.connector

class Client:
    def __init__(self, host, user, password, database):
        self.client = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        self.machine_id = -1

        if not self.client.is_connected():
           print("error")
           exit(1)

        self.init()

    def init(self):
      cursor = self.client.cursor()

      # -------------------------------- HOSTS   TABLE
      cursor.execute("SHOW TABLES LIKE 'hosts'")
      result = cursor.fetchall()
      
      if not len(result) == 1:
          cursor.execute("CREATE TABLE `database`.`hosts` (`ID` INT NOT NULL AUTO_INCREMENT , `HOST_NAME` VARCHAR(255) NULL , `CPU_MAX` DECIMAL(10,2) NULL , `MEMORY_MAX` DECIMAL(10,2) NULL , `TX_MAX` BIGINT NULL , `RX_MAX` BIGINT NULL , `CPU_NAME` VARCHAR(255) NULL , `OS_NAME` VARCHAR(255) NULL , `UPTIME` BIGINT NULL , `STORAGE_MAX` DECIMAL(10,2) NULL , `CPU_CORES` INT NULL , `STORAGE_USED` DECIMAL(10,2) NULL , PRIMARY KEY (`ID`)) ENGINE = InnoDB;")
          self.client.commit()

      # -------------------------------- METRICS TABLE
      cursor.execute("SHOW TABLES LIKE 'metrics'")
      result = cursor.fetchall()

      if len(result) == 0:
        cursor.execute("CREATE TABLE `database`.`metrics` (`ID` BIGINT NOT NULL AUTO_INCREMENT , `TIMESTAMP` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , `CONTAINER` VARCHAR(255) NOT NULL , `CPU` DECIMAL(10,3) NOT NULL , `MEMORY` DECIMAL(16,2) NOT NULL , `TX` BIGINT NOT NULL , `RX` BIGINT NOT NULL , `HOST_ID` INT NOT NULL , PRIMARY KEY (`ID`)) ENGINE = InnoDB;")


    def cleanup(self):
        cursor = self.client.cursor()
        cursor.execute("DELETE FROM metrics WHERE TIMESTAMP < NOW() - INTERVAL 15 MINUTE;")
        self.client.commit()

    def track_container(self, name, cpu, mem, tx, rx):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting")
            exit(3)

        cursor = self.client.cursor()
        cursor.execute(f"INSERT INTO metrics (CONTAINER, CPU, MEMORY, TX, RX, HOST_ID) VALUES ('{name}', {cpu}, {mem}, {tx}, {rx}, {self.machine_id})")
        self.client.commit()

    def track_storage(self, used_storage):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting")
            exit(4)

        cursor = self.client.cursor()
        cursor.execute(f"UPDATE hosts SET STORAGE_USED = {used_storage} WHERE ID = {self.machine_id}")
        self.client.commit()

    def identify(self, host_name):
        cursor = self.client.cursor()
        # TODO hier machine_name modularisieren
        cursor.execute(f"SELECT ID FROM hosts WHERE HOST_NAME = '{host_name}'") 
        result = cursor.fetchall()
        try:
            self.machine_id = result[0][0]
        except:
            print(f"ERROR: This host '{host_name}' has not been setup in the 'host' Table! Please setup first.")
            exit(2)

    def setup_host(self, host_name, cpu_max, memory_max, storage_max, tx_max, rx_max, cpu_name, os_name, uptime, cpu_cores):
        cursor = self.client.cursor()
        print(f"setup host_name={host_name}")
        cursor.execute(f"SELECT ID FROM hosts WHERE HOST_NAME = '{host_name}'") 
        result = cursor.fetchall()

        if len(result) == 0:
            cursor.execute(f"INSERT INTO hosts (HOST_NAME, CPU_MAX, MEMORY_MAX, STORAGE_MAX, TX_MAX, RX_MAX, CPU_NAME, OS_NAME, UPTIME, CPU_CORES) VALUES ('{host_name}', {cpu_max}, {memory_max}, {storage_max}, {tx_max}, {rx_max}, '{cpu_name}', '{os_name}', {uptime}, {cpu_cores})")
        else:
            cursor.execute(f"UPDATE hosts SET CPU_MAX = {cpu_max}, MEMORY_MAX = {memory_max}, STORAGE_MAX = {storage_max}, TX_MAX = {tx_max}, RX_MAX = {rx_max}, CPU_NAME = '{cpu_name}', OS_NAME = '{os_name}', UPTIME = {uptime}, CPU_CORES = {cpu_cores} WHERE HOST_NAME = '{host_name}'")

