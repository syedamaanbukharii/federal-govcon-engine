.PHONY: up down logs rebuild shell-backend shell-frontend

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

rebuild:
	docker compose up -d --build

shell-backend:
	docker compose exec backend bash

shell-frontend:
	docker compose exec frontend sh
