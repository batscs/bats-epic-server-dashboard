import mysql.connector

class Client:
    def __init__(self, host, user, password, database):
        self.client = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if self.client.is_connected():
          print(f"Sucessfully connected to MySQL at host={host}:3306")
        else:
           print(f"Error: Could not connect to MySQL Database for host={host}:3306")
           exit(1)

        self.init()

    def init(self):
      cursor = self.client.cursor()

      cursor.execute("SHOW TABLES LIKE 'hosts'")

      result = cursor.fetchall()

      if len(result) == 1:
        print("Table 'hosts' exists already in the database, skipping creation.")
      else:
        print("Creating table 'hosts'")
