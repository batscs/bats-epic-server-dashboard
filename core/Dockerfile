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

# Create directory for cron script
RUN mkdir -p /app/data
