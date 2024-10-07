#!/bin/bash

# Set Docker BuildKit
export DOCKER_BUILDKIT=1

# You can add other Docker-related environment variables here
# For example:
# export DOCKER_CLI_EXPERIMENTAL=enabled

echo "Docker BuildKit has been enabled."

# Check if docker-compose.yml exists in the current directory
if [ -f "docker-compose.yml" ]; then
    echo "docker-compose.yml found. Building containers..."
    docker-compose build
else
    echo "Error: docker-compose.yml not found in the current directory."
    exit 1
fi

# If you want this script to affect the current shell session, 
# you should source it instead of executing it:
# source /path/to/this/script.sh