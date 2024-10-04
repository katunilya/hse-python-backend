# Build the image
build:
	@echo "Building the image"
	      docker build -t my-fastapi-app -f lecture_2/hw/Dockerfile .

# Run the container
run:
	@echo "Running the container"
	docker run -it my-fastapi-app

# Stop the container
stop:
	@echo "Stopping the container"
	      docker stop my-fastapi-app

# Build docker-compose
build-dc:
	@echo "Building the docker-compose"
	docker-compose -f lecture_3/docker-compose.yml up --build
