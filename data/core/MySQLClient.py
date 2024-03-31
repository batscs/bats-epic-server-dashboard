import platform
import mysql.connector

class Client:
    def __init__(self, host, user, password, database):
        self.client = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            ssl_disabled=True
        )

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
          #print("Creating table 'hosts'")
          cursor.execute("CREATE TABLE `database`.`hosts` (`ID` INT NOT NULL AUTO_INCREMENT , `HOST_NAME` VARCHAR(255) NULL , `CPU_MAX` DOUBLE NULL , `MEMORY_MAX` BIGINT NULL , `TX_MAX` BIGINT NULL , `RX_MAX` BIGINT NULL , `CPU_NAME` VARCHAR(255) NULL , `OS_NAME` VARCHAR(255) NULL , `UPTIME` BIGINT NULL , `STORAGE_MAX` INT NULL , `CPU_CORES` INT NULL , `STORAGE_USED` INT NULL , PRIMARY KEY (`ID`)) ENGINE = InnoDB;")
          self.client.commit()

      machine_name = platform.node()
      cursor.execute(f"SELECT ID FROM hosts WHERE HOST_NAME = '{machine_name}'") 
      result = cursor.fetchall()
      
      if len(result) == 0:
          cursor.execute(f"INSERT INTO hosts (HOST_NAME) VALUES ('{machine_name}')")
          cursor.execute(f"SELECT ID FROM hosts WHERE HOST_NAME = '{machine_name}'") 
          result = cursor.fetchall()

      self.machine_id = result[0][0]

      # -------------------------------- METRICS TABLE
      cursor.execute("SHOW TABLES LIKE 'metrics'")
      result = cursor.fetchall()

      if len(result) == 0:
        cursor.execute("CREATE TABLE `database`.`metrics` (`ID` BIGINT NOT NULL AUTO_INCREMENT , `TIMESTAMP` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , `CONTAINER` VARCHAR(255) NOT NULL , `CPU` DOUBLE NOT NULL , `MEMORY` BIGINT NOT NULL , `TX` BIGINT NOT NULL , `RX` BIGINT NOT NULL , `HOST_ID` INT NOT NULL , PRIMARY KEY (`ID`)) ENGINE = InnoDB;")


    def cleanup(self):
        cursor = self.client.cursor()
        cursor.execute("DELETE FROM metrics WHERE TIMESTAMP < NOW() - INTERVAL 15 MINUTE;")
        self.client.commit()

    def track(self, name, cpu, mem, tx, rx):
        cursor = self.client.cursor()
        cursor.execute(f"INSERT INTO metrics (CONTAINER, CPU, MEMORY, TX, RX, HOST_ID) VALUES ('{name}', {cpu}, {mem}, {tx}, {rx}, {self.machine_id})")
        self.client.commit()
