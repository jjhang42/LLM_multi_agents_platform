# ------------------------------------------------------------------------------
# 🛠️ Dockerfile 생성 및 관리
# ------------------------------------------------------------------------------

dockerfiles:
	@echo "[make] Generating Dockerfiles..."
	python3 scripts/generate_dockerfile.py create

cleandockerfiles:
	@echo "[make] Cleaning Dockerfiles..."
	python3 scripts/generate_dockerfile.py clean

# ------------------------------------------------------------------------------
# 🧱 Docker Compose Lifecycle
# ------------------------------------------------------------------------------

build:
	docker-compose build --no-cache

up:
	docker-compose up

down:
	docker-compose down

logs:
	docker-compose logs --follow

ps:
	docker-compose ps

restart:
	make down && make up

# ------------------------------------------------------------------------------
# 🔁 Full Rebuild Cycle
# ------------------------------------------------------------------------------

rebuild:
	make cleandockerfiles
	make dockerfiles
	make build
	make up

go:
	make rebuild