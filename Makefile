# Variables
CONTAINER_NAME = dev-container
IMAGE_NAME = dev-env
WORKSPACE_DIR ?= $(PWD)
DOCKER_COMMAND = /bin/bash

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

build: buildx-check
	docker buildx build -t $(IMAGE_NAME) .

run: build
	@if [ $$(docker ps -a -q -f name=$(CONTAINER_NAME)) ]; then \
		if [ $$(docker ps -q -f name=$(CONTAINER_NAME)) ]; then \
			echo "Attaching to existing running container..."; \
			docker exec -it $(CONTAINER_NAME) $(DOCKER_COMMAND); \
		else \
			echo "Starting existing stopped container..."; \
			docker start $(CONTAINER_NAME); \
			docker exec -it $(CONTAINER_NAME) $(DOCKER_COMMAND); \
		fi \
	else \
		echo "Creating and running new container..."; \
		docker run -it --name $(CONTAINER_NAME) \
			-v $(WORKSPACE_DIR):/workspace \
			$(IMAGE_NAME) $(DOCKER_COMMAND) -c "gcc -shared -o /workspace/libcaf.so -fPIC /workspace/c_src/*.c -lcrypto && $(DOCKER_COMMAND)"; \
	fi

compile:
	gcc -shared -o /workspace/libcaf.so -fPIC /workspace/c_src/*.c -lcrypto

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
	sudo rm -rf ./files ./objects ./workspace/libcaf.so

help:
	@echo "Available targets:"
	@echo "  build   - Build the Docker image"
	@echo "  run     - Run the Docker container"
	@echo "  compile - Compile the shared library"
	@echo "  stop    - Stop the Docker container"
	@echo "  remove  - Remove the Docker container and clean up files"
	@echo "  clean   - Clean up Docker resources and generated files"

.PHONY: build buildx-check run compile stop remove clean help