import docker
import time
import json
from _thread import *
import platform
import os

from MySQLClient import Client

# ------------------------------------------------------------------------------------------

# docker API
client = docker.from_env()

# set of currently running container names
container_list = set()

# host_name, used as identifier of this cloudwatch instance
host_name = os.environ.get('CW_SERVER_NAME')

# ------------------------------------------------------------------------------------------

def main():
    db = Client("db", "user", "test", "database")

    db.setup_host(host_name, 600, 32, 1000, 7, 7, "M1", "OSX", 500, 6)

    db.identify(host_name)

    # This 'parent' Thread continuously searches for new containers and tracks them
    # in each their own new thread simultaneously
    start_new_thread(find_containers, ())

    while True:
        db.cleanup()
        db.track_storage(300)
        time.sleep(3)

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
    db = Client("db", "user", "test", "database")
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