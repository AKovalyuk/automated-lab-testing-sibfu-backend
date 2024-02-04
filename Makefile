build_compilers:
	docker build -t runner-compilers ./runner/compilers

build_service:
	docker build -t runner-service ./runner/service

dev:
	docker compose -f docker-compose.dev.yaml up

api-only:
	docker compose -f docker-compose.dev.yaml up app app-db app-redis --no-deps

prod:
	docker compose -f docker-compose.prod.yaml up

stop:
	docker compose down

env:
	cp .env.sample .env

test:
	docker compose exec -it app poetry run python -m pytest -vv --showlocals --log-level=DEBUG --full-trace

connect-db:
	docker compose exec -it app-db psql -U user -d db
