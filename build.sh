#!/bin/bash

# Check if the version parameter is provided
if [ -z "$1" ]; then
    echo "Version not specified."
    exit 1
fi

VERSION=$1
IMAGE_NAME="lux4rd0/unifi-timelapse"  # Replace with your Docker Hub username and image name

# Create a new builder instance
docker buildx create --name mybuilder --use

# Start up the builder instance
docker buildx inspect --bootstrap

# Build and push the Docker image
docker buildx build --platform linux/amd64,linux/arm64 -t ${IMAGE_NAME}:${VERSION} --push .

# Check if "latest" tag is required
if [ "$2" == "latest" ]; then
    docker buildx build --platform linux/amd64,linux/arm64 -t ${IMAGE_NAME}:latest --push .
fi

echo "Docker image build and push complete."
