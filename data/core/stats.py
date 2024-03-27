import docker
import time
import json
from MySQLClient import Client
from _thread import *

# docker API
client = docker.from_env()



# set of currently running container names
container_list = set()

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
    db = Client("db", "user", "test", "database")
    container = client.containers.get(container_name)
    for stats in container.stats(decode=None, stream=True):
        #print(f"Collecting stats for {container_name}")
        stats = json.loads(stats)

        # Memory Usage subtracted with inactive_files to mirror behavior of 'docker stats' and linux ram calculation, ignoring buffer/cache
        memory_b = stats["memory_stats"]["usage"] - stats["memory_stats"]["stats"]["inactive_file"]
        cpu = calculate_cpu_percent(stats)
        tx_b = stats["networks"]["eth0"]["tx_bytes"]
        rx_b = stats["networks"]["eth0"]["rx_bytes"]

        db.track(container_name, cpu, memory_b, tx_b, rx_b)

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


start_new_thread(find_containers, ())

while True:
    db = Client("db", "user", "test", "database")
    db.cleanup()
    time.sleep(3)

# todo loop checking for new containers
# todo thread exiting, remove container_name from set
