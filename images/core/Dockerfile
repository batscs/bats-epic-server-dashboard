FROM ubuntu:22.04

# Installing requirements
RUN apt-get update

# cron to schedule the script
RUN apt-get install -y cron

RUN apt-get install -y python3.6

RUN apt-get install -y python3-mysql.connector

RUN apt-get install -y python3-docker

RUN apt-get install -y python3-psutil

RUN apt install -y python3-pip

RUN apt install -y lm-sensors

# Create directory for script
RUN mkdir -p /app
RUN mkdir -p /app_package

# app_package to avoid volume mounting issues of /app
COPY app/ /app_package/
COPY entrypoint /

RUN chmod +x /entrypoint

CMD /entrypoint
