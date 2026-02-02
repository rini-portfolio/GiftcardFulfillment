# Top-level Makefile to orchestrate builds and tests across Java (Maven) and Python services
SHELL := /bin/bash
.PHONY: all java python test build-java build-python docker-build compose-up compose-down clean

all: java python

java: build-java

build-java:
	@echo "Building Java modules..."
	cd order-service && mvn -DskipTests package
	cd payment-service && mvn -DskipTests package
	@echo "Java builds complete."

python: build-python

build-python:
	@echo "Installing Python deps and running tests for Python services..."
	cd giftcard-service && python3 -m pip install --user -r requirements.txt || true
	cd giftcard-service && pytest || true
	cd notification-service && python3 -m pip install --user -r requirements.txt || true
	cd notification-service && pytest || true
	@echo "Python tasks complete."

test:
	@echo "Running full test suite..."
	cd order-service && mvn test
	cd payment-service && mvn test
	cd giftcard-service && pytest
	cd notification-service && pytest
	@echo "All tests complete."

docker-build:
	@echo "Building Docker images for all services..."
	docker build -t order-service:local ./order-service
	docker build -t payment-service:local ./payment-service
	docker build -t giftcard-service:local ./giftcard-service
	docker build -t notification-service:local ./notification-service
	@echo "Docker images built."

compose-up:
	docker-compose up --build

compose-down:
	docker-compose down

clean:
	@echo "Cleaning build artifacts..."
	cd order-service && mvn -q clean || true
	cd payment-service && mvn -q clean || true
	@echo "Clean complete."