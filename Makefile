# Variables
CONTAINER_NAME = dev-container
IMAGE_NAME = dev-env
WORKSPACE_DIR ?= $(PWD)
DOCKER_COMMAND = /bin/bash

# Targets
build_container:
	docker build -t $(IMAGE_NAME) .

build_lib:
	# Compiles the shared library
	gcc -shared -o $(WORKSPACE_DIR)/libcaf.so -fPIC $(WORKSPACE_DIR)/c_src/*.c -lcrypto

run: stop remove build_container build_lib
	docker run -it --name $(CONTAINER_NAME) \
		-v $(WORKSPACE_DIR):/workspace \
		$(IMAGE_NAME) $(DOCKER_COMMAND)

stop:
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true

remove:
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true

clean:
	docker container prune -f
	docker image prune -f
	docker volume prune -f

.PHONY: build_container build_lib run stop remove clean
