#!/bin/bash

# Stop and remove currently running container
docker stop telegram-bot-container || true
docker rm telegram-bot-container || true

# Build and start new container
docker build -t telegram-bot-image .
docker run -d --name telegram-bot-container telegram-bot-image