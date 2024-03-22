from tqdm import tqdm
from time import sleep
import psutil
import platform

from MySQLClient import Client

client = Client("db", "user", "test", "database")