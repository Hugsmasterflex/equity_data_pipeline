COMPOSE = docker compose -f docker/docker-compose.yml --env-file .env

.PHONY: up down logs rebuild shell

up:
	$(COMPOSE) up -d minio

up-all:
	$(COMPOSE) --profile ingest --profile db --profile api up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

ingest:
	$(COMPOSE) run --rm ingestion

rebuild:
	$(COMPOSE) build --no-cache

shell:
	$(COMPOSE) exec ingestion bash

s3ls:
	aws --profile minio --endpoint-url http://localhost:9000 s3 ls

activate:
	. ~/projects/equity_data_pipeline/.venv/bin/activate