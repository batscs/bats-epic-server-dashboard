import docker
import time
import json
from _thread import *
import os

from MySQLClient import Client
from DeviceManager import Device

# ------------------------------------------------------------------------------------------

# docker API
client = docker.from_env()

# set of currently running container names
container_list = set()

# host_name, used as identifier of this cloudwatch instance
host_name = os.environ.get('CW_SERVER_NAME')

# auth key, empty string if no auth
auth_key = os.environ.get("CW_AUTH_KEY")

# mysql connection
mysql_host = os.environ.get("MYSQL_HOST")
mysql_user = os.environ.get("MYSQL_USER")
mysql_password = os.environ.get("MYSQL_PASSWORD")
mysql_database = os.environ.get("MYSQL_DATABASE")

# ------------------------------------------------------------------------------------------

def main():
    connected = False

    while not connected:
        try:
            db = Client(mysql_host, mysql_user, mysql_password, mysql_database)
            connected = True
        except:
            print(f"Error: Could not connect to MySQL Database at {mysql_host}:3306")
            time.sleep(5)
        
    print(f"Connected to MySQL Database at {mysql_host}:3306")
    device = Device()

    cpu_max = device.cpu_max()
    memory_max = device.memory_max()
    storage_max = device.storage_max()
    tx_max = device.tx_max()
    rx_max = device.rx_max()
    cpu_name = device.cpu_name()
    os_name = device.os_name()
    uptime = device.uptime()
    cpu_cores = device.cpu_cores()

    db.setup_host(host_name, cpu_max, memory_max, storage_max, tx_max, rx_max, cpu_name, os_name, uptime, cpu_cores)

    db.update_auth(auth_key)

    db.identify(host_name)

    # This 'parent' Thread continuously searches for new containers and tracks them
    # in each their own new thread simultaneously
    start_new_thread(find_containers, ())

    while True:
        db.cleanup()
        db.track_storage(device.storage_used())
        time.sleep(60)

# ------------------------------------------------------------------------------------------

# this is taken directly from docker client:
# https://github.com/docker/docker/blob/28a7577a029780e4533faf3d057ec9f6c7a10948/api/client/stats.go#L309
def calculate_cpu_percent(status):
    try:
        cpuDelta = status["cpu_stats"]["cpu_usage"]["total_usage"] - status["precpu_stats"]["cpu_usage"]["total_usage"]
        systemDelta = status["cpu_stats"]["system_cpu_usage"] - status["precpu_stats"]["system_cpu_usage"]
        # print("systemDelta: "+str(systemDelta)+" cpuDelta: "+str(cpuDelta))
        cpuPercent = (cpuDelta / systemDelta) * (status["cpu_stats"]["online_cpus"]) * 100
        cpuPercent = round(cpuPercent, 2)
    except:
        cpuPercent = 0.0
    return cpuPercent

def collect_stats(container_name):
    db = Client(mysql_host, mysql_user, mysql_password, mysql_database)
    db.identify(host_name)
    container = client.containers.get(container_name)
    for stats in container.stats(decode=None, stream=True):
        #print(f"Collecting stats for {container_name}")
        stats = json.loads(stats)

        # Memory Usage subtracted with inactive_files to mirror behavior of 'docker stats' and linux ram calculation, ignoring buffer/cache
        memory_b = stats["memory_stats"]["usage"] - stats["memory_stats"]["stats"]["inactive_file"]
        cpu = calculate_cpu_percent(stats)
        tx_b = stats["networks"]["eth0"]["tx_bytes"]
        rx_b = stats["networks"]["eth0"]["rx_bytes"]

        db.track_container(container_name, cpu, memory_b, tx_b, rx_b)

    print(f"Container {container_name} has been stopped.")
    container_list.remove(container_name)

def find_containers():
    while True:
        for container in client.containers.list():
            about = container.stats(decode=None, stream=False)
            name = about["name"]
            #name = "ark-server"
            if name not in container_list:
                container_list.add(name)
                start_new_thread(collect_stats, (name, ))
                print(f"Starting to track container {name}")

        time.sleep(5)

# ----------------- main function -------------------
if __name__ == "__main__":
    main()