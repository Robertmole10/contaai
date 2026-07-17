.PHONY: up down logs ps migrate shell-api clean
up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

migrate:
	docker compose exec api alembic upgrade head

shell-api:
	docker compose exec api bash

clean:
	docker compose down -v --remove-orphans
