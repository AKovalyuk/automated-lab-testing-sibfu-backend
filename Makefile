

build_compilers:
	docker build -t runner-compilers ./runner/compilers

build_service:
	docker build -t runner-service ./runner/service

run:
	make build_compilers
	make build_service
	docker compose up -d

stop:
	docker compose down

env:
	cp .env.sample .env