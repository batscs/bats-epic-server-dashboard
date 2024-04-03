FROM ubuntu:22.04

# Installing requirements
RUN apt-get update

# cron to schedule the script
RUN apt-get install -y cron

RUN apt-get install -y python3.6

RUN apt-get install -y python3-mysql.connector

RUN apt-get install -y python3-docker

RUN apt-get install -y python3-psutil

# Create directory for script
RUN mkdir -p /app; 

# TODO cp 3 python files to /app-Directory

ENTRYPOINT ["python3 /app/CloudwatchStats.py"]
