### Web application for automatic testing of programming tasks

### Requirements

- Docker and docker-compose plugin
- python 3.11 and poetry (for local development)
- make
- Plantuml (only to view `.puml` documentation files)

### Run

1. Install dependencies with poetry:
```shell
poetry install
```
2. Install or build custom compilers for Judge0:
```shell
make build-compilers
make buibuild-service
```
or
```shell
docker pull judge0:latest
```
Note: Judge0 image is heavy (12GiB)
3. Configure `.env`:
```shell
cp .env.sample .env
nano .env
```
- `M_*` - confirmation email configuration
- `POSTGRES_*` - database configuration
- `REDIS_*` - KV-storage configuration
- `JUDGE0_*` - connection to execution service
- `CALLBACK_URL` - url of callback service
4. Run all services
```shell
docker compose up
```
On production server:
```shell
docker compose -f docker-compose.prod.yaml up -d
```

You also can service without pulling Judge0 image:
```shell
make api-only
```

### Dependencies

- [Judge0](https://judge0.com/)

