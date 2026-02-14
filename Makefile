IMAGE_NAME = clickuperbot
CONTAINER_NAME = clickuperbot

.PHONY: up down logs

up:
	docker build -t $(IMAGE_NAME) .
	-docker rm -f $(CONTAINER_NAME)
	docker run -d --name $(CONTAINER_NAME) -v $$(pwd)/data.db:/app/data.db --restart unless-stopped $(IMAGE_NAME)

down:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

logs:
	docker logs -f $(CONTAINER_NAME)
