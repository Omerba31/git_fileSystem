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
		$(IMAGE_NAME) $(DOCKER_COMMAND) -c "gcc -shared -o /workspace/libopenfile.so -fPIC /workspace/c_src/*.c -lcrypto && $(DOCKER_COMMAND)"

stop:
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true

remove:
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true

clean:
	docker container prune -f
	docker image prune -f
	docker volume prune -f

.PHONY: build run stop remove clean