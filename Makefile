

build_compilers:
	docker build -t runner-compilers ./runner/compilers

build_service:
	docker build -t runner-service ./runner/service

dev:
	docker compose -f docker-compose.dev.yaml up

api_only:
	docker compose -f docker-compose.dev.yaml up app app-db app-redis --no-deps

prod:
	docker compose -f docker-compose.prod.yaml up

stop:
	docker compose down

env:
	cp .env.sample .env