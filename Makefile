COMPOSE = docker compose -f docker/docker-compose.yml --env-file .env

.PHONY: up down logs rebuild shell

up:
\t$(COMPOSE) up -d minio

up-all:
\t$(COMPOSE) --profile ingest --profile db --profile api up -d

down:
\t$(COMPOSE) down

logs:
\t$(COMPOSE) logs -f --tail=200

ingest:
\t$(COMPOSE) run --rm ingestion

rebuild:
\t$(COMPOSE) build --no-cache

shell:
\t$(COMPOSE) exec ingestion bash
