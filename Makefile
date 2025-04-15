.PHONY: build up down logs restart \
        dockerfiles gen clean-dockerfiles

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down --rmi all --volumes --remove-orphans

logs:
	docker-compose logs -f

restart:
	docker-compose down --rmi all --volumes --remove-orphans
	docker-compose up

# 👇 Dockerfile 자동화 관리
dockerfiles:
	python3 scripts/generate_dockerfile.py create

clean-dockerfiles:
	python3 scripts/generate_dockerfile.py clean

build-fe:
	docker-compose build frontend

up-fe:
	docker-compose up -d frontend

gen: dockerfiles  # alias
