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

compile: run
	docker exec $(CONTAINER_NAME) bash -c "cd libcaf && python setup.py develop"

deploy_libcaf: compile
	docker exec $(CONTAINER_NAME) pip install -e libcaf;

deploy_caf:
	docker exec $(CONTAINER_NAME) pip install -e caf;

deploy: deploy_libcaf deploy_caf;

test: deploy
	docker exec $(CONTAINER_NAME) pytest tests

test_libcaf: deploy_libcaf
	docker exec $(CONTAINER_NAME) pytest tests/libcaf

test_caf: deploy_caf
	docker exec $(CONTAINER_NAME) pytest tests/caf

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
	sudo rm -rf libcaf/libcaf.egg-info libcaf/*.so libcaf/build
	sudo rm -rf caf.egg-info

help:
	@echo "Available targets:"
	@echo "  build                  - Build the Docker image"
	@echo "  run                    - Run the Docker container"
	@echo "  attach                 - Attach to the running Docker container"
	@echo "  compile                - Compile the shared library in libcaf"
	@echo "  test                   - Run all tests inside the Docker container"
	@echo "  test_caf               - Run tests for the CLI app inside the Docker container"
	@echo "  test_libcaf            - Run tests for the library inside the Docker container"
	@echo "  stop                   - Stop the Docker container"
	@echo "  remove                 - Remove the Docker container and clean up files"
	@echo "  clean                  - Clean up Docker resources and generated files"
	@echo "  deploy_libcaf          - Run, compile, and install the library"
	@echo "  deploy_caf             - Install the CLI application"

.PHONY: build buildx-check run attach compile test test_caf test_libcaf stop remove clean deploy_libcaf deploy_caf help
