# Define variables
.PHONY: build run stop rebuild clean

# Define variables for Docker
IMAGE_NAME := dev-env
CONTAINER_NAME := dev-container
WORKDIR := /workspace
HOST_DIR := $(PWD)

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run the Docker container with bind mount to ./workspace dir
run:
	docker run -it --name $(CONTAINER_NAME) \
		-v $(HOST_DIR):$(WORKDIR) \
		$(IMAGE_NAME) /bin/bash

# Stop and remove the Docker container
stop:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

# Rebuild the image and run the container
rebuild: stop build run

# Clean up the image
clean:
	docker rmi $(IMAGE_NAME)
