import os
import speedtest
import datetime
import time
import subprocess

class Device:

    def cpu_cores(self):
        cpu_cores = 0

        # Open and read the /proc/cpuinfo file
        with open('/proc/cpuinfo', 'r') as file:
            # Read each line in the file
            for line in file:
                # Check if the line contains 'processor' which indicates a CPU core
                if line.startswith('processor'):
                    cpu_cores += 1

        return cpu_cores

    def uptime(self):
        uptime_seconds = None

        # Open and read the /proc/uptime file
        with open('/proc/uptime', 'r') as file:
            # Read the first line in the file
            uptime_line = file.readline().strip()
            # Split the line to get the uptime in seconds
            uptime_seconds = float(uptime_line.split()[0])

        return uptime_seconds

    def os_name(self):
        with open('/proc/version', 'r') as file:
            version_info = file.readline().strip()

        # Extracting kernel version
        kernel_version = " ".join(version_info.split()[:3])
        return kernel_version
    
    def cpu_power_stream(self):
        file_path = '/sys/class/powercap/intel-rapl:0/energy_uj'
        try:
            with open(file_path, 'r') as file:
                prev_energy_uj = float(file.read().strip())
            while True:
                time.sleep(1)
                with open(file_path, 'r') as file:
                    curr_energy_uj = float(file.read().strip())
                energy_diff_uj = curr_energy_uj - prev_energy_uj
                prev_energy_uj = curr_energy_uj
                yield round(energy_diff_uj / 1000000, 2)
        except FileNotFoundError:
            print("File not found. Make sure the path is correct.")
            yield 0
        except Exception as e:
            print("An error occurred:", e)
            yield 0

    def cpu_name(self):
        result = None

        # Open and read the /proc/cpuinfo file
        with open('/proc/cpuinfo', 'r') as file:
            # Read each line in the file
            for line in file:
                # Check if the line contains 'model name' which indicates the processor name
                if 'model name' in line:
                    # Split the line by ':' and get the second part which contains the processor name
                    result = line.split(':')[1].strip()
                    break  # No need to continue once we've found the processor name

        return result if result else "Unknown"

    def cpu_max(self):
        return 100 * 6 # self.cpu_cores()
    
    def cpu_temp(self):
        # Execute the 'sensors' command to get temperature information
        result = subprocess.run(['sensors'], capture_output=True, text=True)

        # Check if the command executed successfully
        if result.returncode == 0:
            # Split the output by lines
            output_lines = result.stdout.split('\n')

            # Search for lines containing CPU temperature information
            for line in output_lines:
                if "Core 0" in line:
                    # Extract temperature value from the line
                    cpu_temp = line.split("+")[1].split()[0]
                    return cpu_temp

        # Return None if temperature couldn't be retrieved
        return "Unknown"
    
    def memory_max(self):
        total_memory_kb = 0

        # Open and read the /proc/meminfo file
        with open('/proc/meminfo', 'r') as file:
            # Read each line in the file
            for line in file:
                # Check if the line contains 'MemTotal' which indicates total memory
                if line.startswith('MemTotal'):
                    # Extract the memory value from the line
                    total_memory_kb = int(line.split()[1])
                    break  # No need to continue once we've found the total memory

        # Convert kilobytes to gigabytes
        total_memory_gb = total_memory_kb / (1024 ** 2)

        return total_memory_gb
    
    def storage_max(self):
        # Get filesystem statistics for the specified directory
        stats = os.statvfs("/")
        
        # Calculate total capacity in bytes
        total_capacity = stats.f_frsize * stats.f_blocks
        
        # Convert bytes to gigabytes
        total_capacity_gb = total_capacity / (1024 ** 3)
        
        return total_capacity_gb
    
    def storage_used(self):
        # Get filesystem statistics for the specified directory
        stats = os.statvfs("/")
        
        # Calculate total capacity in bytes
        total_capacity = stats.f_frsize * stats.f_blocks
        
        # Calculate available space in bytes
        available_space = stats.f_frsize * stats.f_bavail
        
        # Calculate used space in bytes
        used_space = total_capacity - available_space
        
        # Convert bytes to gigabytes
        used_space_gb = used_space / (1024 ** 3)
        
        return used_space_gb
    
    def tx_max(self):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            max_tx_bandwidth = st.upload()
            return max_tx_bandwidth
        except:
            return 10_000_000
    
    def rx_max(self):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            max_rx_bandwidth = st.download()
            return max_rx_bandwidth
        except:
            return 50_000_000
        
    def rx_now(self):
        return -1
    
    def tx_now(self):
        return -1
    
    def memory_now(self):
        meminfo_file = '/proc/meminfo'
        with open(meminfo_file, 'r') as f:
            meminfo = f.readlines()

            # Parsing /proc/meminfo
            meminfo_dict = {}
            for line in meminfo:
                key, value = line.split(':', 1)
                meminfo_dict[key.strip()] = int(value.split()[0])  # Extracting numeric value

            # Extracting relevant memory information and converting to GB
            total_memory_gb = meminfo_dict['MemTotal'] / (1024 ** 2)  # Convert from KB to GB
            free_memory_gb = (meminfo_dict['MemAvailable']) / (1024 ** 2)
            used_memory_gb = total_memory_gb - free_memory_gb  # Used memory in GB

            return used_memory_gb
        
        return -1

    def cpu_usage_stream(self):
        # Initial measurement
        prev_idle_time = 0
        prev_total_time = 0

        while True:
            # Read CPU times
            with open('/proc/stat', 'r') as file:
                lines = file.readlines()

            cpu_times = [int(time) for time in lines[0].strip().split()[1:]]
            idle_time = cpu_times[3]  # idle time

            # Total CPU time
            total_time = sum(cpu_times)

            # Calculate the difference
            idle_time_delta = idle_time - prev_idle_time
            total_time_delta = total_time - prev_total_time

            # Calculate CPU usage percentage
            cpu_usage = 100.0 - ((idle_time_delta / total_time_delta) * 100.0)

            # Update previous values for next iteration
            prev_idle_time = idle_time
            prev_total_time = total_time

            yield cpu_usage * 6

            time.sleep(1)  # Sleep for 1 second before checking again
    
    def local_time(self):
        return datetime.datetime.now()
    
    def local_timezone(self):
        return datetime.datetime.now().astimezone().tzinfo