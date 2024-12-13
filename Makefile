# Variables
CONTAINER_NAME = dev-container
IMAGE_NAME = dev-env
WORKSPACE_DIR ?= $(PWD)
DOCKER_COMMAND = /bin/bash

build: buildx-check
	docker buildx build -t $(IMAGE_NAME) .

# Targets
buildx-check:
	@if ! docker buildx version > /dev/null 2>&1; then \
		echo "buildx is not installed. Installing buildx..."; \
		mkdir -p ~/.docker/cli-plugins/; \
		curl -SL https://github.com/docker/buildx/releases/latest/download/buildx-$(uname -s)-$(uname -m) -o ~/.docker/cli-plugins/docker-buildx; \
		chmod +x ~/.docker/cli-plugins/docker-buildx; \
		echo "buildx installed successfully."; \
	else \
		echo "buildx is already installed."; \
	fi

run: build
	@if [ $$(docker ps -a -q -f name=$(CONTAINER_NAME)) ]; then \
		if [ $$(docker ps -q -f name=$(CONTAINER_NAME)) ]; then \
			echo "Container already running!"; \
		else \
			echo "Starting existing stopped container..."; \
			docker start $(CONTAINER_NAME); \
		fi \
	else \
		echo "Creating and running new container..."; \
		docker run --detach -it --name $(CONTAINER_NAME) \
			-v $(WORKSPACE_DIR):/workspace $(IMAGE_NAME); \
	fi

attach: run
	docker attach $(CONTAINER_NAME);

install_lib: compile
	docker exec $(CONTAINER_NAME) pip install -e c_src;

compile:
	@if [ ! $$(docker ps -q -f name=$(CONTAINER_NAME)) ]; then \
		echo "The container is not running. Run 'make run' first."; \
		exit 1; \
	fi
	docker exec $(CONTAINER_NAME) bash -c "cd c_src && python setup.py build_ext --inplace"

test: run
	docker exec $(CONTAINER_NAME) pytest

stop:
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true

remove:
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true
	@if [ -w ./files ] && [ -w ./objects ]; then \
		rm -rf ./files ./objects; \
	else \
		sudo rm -rf ./files ./objects; \
	fi

clean:
	docker container prune -f
	docker image prune -f
	docker volume prune -f
	sudo rm -rf ./files ./objects c_src/libcaf.egg-info c_src/*.so

help:
	@echo "Available targets:"
	@echo "  build       - Build the Docker image"
	@echo "  run         - Run the Docker container"
	@echo "  attach      - Attach to the running Docker container"
	@echo "  compile     - Compile the shared library in c_src"
	@echo "  install_lib - Install the library using pip"
	@echo "  stop        - Stop the Docker container"
	@echo "  remove      - Remove the Docker container and clean up files"
	@echo "  clean       - Clean up Docker resources and generated files"

.PHONY: build buildx-check run install_lib compile stop remove clean help
