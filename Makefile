# Variables
CONTAINER_NAME = dev-container
IMAGE_NAME = dev-env
WORKSPACE_DIR ?= $(PWD)
DOCKER_COMMAND = /bin/bash

# Targets
build:
	docker build -t $(IMAGE_NAME) .

run: stop remove build
	docker run -it --name $(CONTAINER_NAME) \
		-v $(WORKSPACE_DIR):/workspace \
		$(IMAGE_NAME) $(DOCKER_COMMAND) -c "gcc -shared -o /workspace/libcaf.so -fPIC /workspace/c_src/*.c -lcrypto && $(DOCKER_COMMAND)"

compile:
	gcc -shared -o /workspace/libcaf.so -fPIC /workspace/c_src/*.c -lcrypto

stop:
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true

remove:
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true
	sudo rm -rf ./files ./objects

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

.PHONY: build run compile stop remove clean help