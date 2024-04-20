import mysql.connector

class Client:
    def __init__(self, host, user, password, database):
        self.database = database

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

      # -------------------------------- AUTH    TABLE
      cursor.execute("SHOW TABLES LIKE 'settings'")
      result = cursor.fetchall()
      
      if not len(result) == 1:
        cursor.execute(f"CREATE TABLE `{self.database}`.`settings` (`AUTH_REQUIRED` BOOLEAN NOT NULL , `AUTH_KEY` VARCHAR(255) NOT NULL , `VERSION` DECIMAL(10,1) NULL ) ENGINE = InnoDB;")
        cursor.execute("INSERT INTO settings (AUTH_REQUIRED, AUTH_KEY) VALUES (False, '')")

      # -------------------------------- HOSTS   TABLE
      cursor.execute("SHOW TABLES LIKE 'hosts'")
      result = cursor.fetchall()
      
      if not len(result) == 1:
          cursor.execute(f"CREATE TABLE `{self.database}`.`hosts` (`ID` INT NOT NULL AUTO_INCREMENT , `HOST_NAME` VARCHAR(255) NULL , `CPU_MAX` DECIMAL(10,3) NULL , `CPU_NOW` DECIMAL(10,3) NULL , `CPU_TEMP` VARCHAR(255) NULL ,  `CPU_POWER` DECIMAL(10,2) NULL , `MEMORY_MAX` DECIMAL(10,3) NULL , `MEMORY_NOW` DECIMAL(10,3) NULL , `TX_MAX` BIGINT NULL , `TX_NOW` BIGINT NULL , `RX_MAX` BIGINT NULL , `RX_NOW` BIGINT NULL , `CPU_NAME` VARCHAR(255) NULL , `OS_NAME` VARCHAR(255) NULL , `OS_TIME` TIMESTAMP NULL , `OS_TIMEZONE` VARCHAR(255) NULL , `UPTIME` BIGINT NULL , `STORAGE_MAX` DECIMAL(10,2) NULL , `CPU_CORES` INT NULL , `STORAGE_USED` DECIMAL(10,2) NULL , PRIMARY KEY (`ID`)) ENGINE = InnoDB;")
          self.client.commit()

      # -------------------------------- METRICS TABLE
      cursor.execute("SHOW TABLES LIKE 'metrics'")
      result = cursor.fetchall()

      if len(result) == 0:
        cursor.execute(f"CREATE TABLE `{self.database}`.`metrics` (`ID` BIGINT NOT NULL AUTO_INCREMENT , `TIMESTAMP` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , `CONTAINER` VARCHAR(255) NOT NULL , `CPU` DECIMAL(10,3) NOT NULL , `MEMORY` DECIMAL(10,4) NOT NULL , `TX` BIGINT NOT NULL , `RX` BIGINT NOT NULL , `HOST_ID` INT NOT NULL , PRIMARY KEY (`ID`)) ENGINE = InnoDB;")


    def cleanup(self):
        cursor = self.client.cursor()
        cursor.execute("DELETE FROM metrics WHERE TIMESTAMP < NOW() - INTERVAL 15 MINUTE;")
        self.client.commit()

    def track_container(self, name, cpu, mem, tx, rx):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting from track_container: ", name)
            exit(3)

        cursor = self.client.cursor()
        cursor.execute(f"INSERT INTO metrics (CONTAINER, CPU, MEMORY, TX, RX, HOST_ID) VALUES ('{name}', {cpu}, {mem}, {tx}, {rx}, {self.machine_id})")
        self.client.commit()

    def track_storage(self, used_storage):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting from track_storage")
            exit(4)

        cursor = self.client.cursor()
        cursor.execute(f"UPDATE hosts SET STORAGE_USED = {used_storage} WHERE ID = {self.machine_id}")
        self.client.commit()

    def track_uptime(self, uptime):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting from track_uptime")
            exit(5)

        cursor = self.client.cursor()
        cursor.execute(f"UPDATE hosts SET UPTIME = {uptime} WHERE ID = {self.machine_id}")
        self.client.commit()

    def track_time(self, time, timezone):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting from track_time")
            exit(6)

        cursor = self.client.cursor()
        cursor.execute(f"UPDATE hosts SET OS_TIME = '{time}', OS_TIMEZONE = '{timezone}' WHERE ID = {self.machine_id}")
        self.client.commit()

    def track_cpu(self, cpu_usage):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting from track_cpu")
            exit(7)

        cursor = self.client.cursor()
        cursor.execute(f"UPDATE hosts SET CPU_NOW = {cpu_usage} WHERE ID = {self.machine_id}")
        self.client.commit()

    def track_netio(self, tx, rx):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting from track_netio")
            exit(8)

        cursor = self.client.cursor()
        cursor.execute(f"UPDATE hosts SET TX_NOW = {tx}, RX_NOW = {rx} WHERE ID = {self.machine_id}")
        self.client.commit()

    def track_memory(self, memory):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting from track_memory")
            exit(9)

        cursor = self.client.cursor()
        cursor.execute(f"UPDATE hosts SET MEMORY_NOW = {memory} WHERE ID = {self.machine_id}")
        self.client.commit()

    def track_cpu_temp(self, temp):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting from track_memory")
            exit(10)

        cursor = self.client.cursor()
        cursor.execute(f"UPDATE hosts SET CPU_TEMP = '{temp}' WHERE ID = {self.machine_id}")
        self.client.commit()

    def track_cpu_power(self, power):
        if self.machine_id == -1:
            print("ERROR: Instance has not been identified. Exiting from track_memory")
            exit(10)

        cursor = self.client.cursor()
        cursor.execute(f"UPDATE hosts SET CPU_POWER = {power} WHERE ID = {self.machine_id}")
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
        cursor.execute(f"SELECT ID FROM hosts WHERE HOST_NAME = '{host_name}'") 
        result = cursor.fetchall()

        if len(result) == 0:
            cursor.execute(f"INSERT INTO hosts (HOST_NAME, CPU_MAX, MEMORY_MAX, STORAGE_MAX, TX_MAX, RX_MAX, CPU_NAME, OS_NAME, UPTIME, CPU_CORES) VALUES ('{host_name}', {cpu_max}, {memory_max}, {storage_max}, {tx_max}, {rx_max}, '{cpu_name}', '{os_name}', {uptime}, {cpu_cores})")
        else:
            cursor.execute(f"UPDATE hosts SET CPU_MAX = {cpu_max}, MEMORY_MAX = {memory_max}, STORAGE_MAX = {storage_max}, TX_MAX = {tx_max}, RX_MAX = {rx_max}, CPU_NAME = '{cpu_name}', OS_NAME = '{os_name}', UPTIME = {uptime}, CPU_CORES = {cpu_cores} WHERE HOST_NAME = '{host_name}'")

    def update_auth(self, auth_key):
        cursor = self.client.cursor()
        if auth_key == "" or auth_key == None:
            cursor.execute("UPDATE settings SET AUTH_REQUIRED=False")
        else:
            cursor.execute(f"UPDATE settings SET AUTH_REQUIRED=True, AUTH_KEY='{auth_key}'")
