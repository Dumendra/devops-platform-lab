SERVICE ?= gateway
TAG ?= local

.PHONY: help install lint test compose-up compose-down image helm-lint helm-template tf-init tf-validate

help:
	@echo "install       Install development dependencies"
	@echo "lint          Run flake8"
	@echo "test          Run pytest"
	@echo "compose-up    Start the full local stack"
	@echo "compose-down  Stop the local stack"
	@echo "image         Build one image: make image SERVICE=orders TAG=v1"
	@echo "helm-lint     Lint the Helm chart"
	@echo "helm-template Render the Helm chart"
	@echo "tf-init       Initialize Terraform"
	@echo "tf-validate   Validate Terraform"

install:
	pip install -r requirements-dev.txt

lint:
	flake8 common apps tests

test:
	python -m pytest -q

compose-up:
	docker compose up --build

compose-down:
	docker compose down

image:
	docker build --build-arg SERVICE=$(SERVICE) --build-arg APP_VERSION=$(TAG) -t devops-platform-$(SERVICE):$(TAG) .

helm-lint:
	helm lint charts/platform

helm-template:
	helm template platform charts/platform -f charts/platform/values.yaml

tf-init:
	terraform -chdir=terraform init

tf-validate:
	terraform -chdir=terraform validate
