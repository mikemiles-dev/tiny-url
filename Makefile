VERSION=0.0.1
HOST?=0.0.0.0
REDIS_HOST?=redis://127.0.0.1:7001

export PYTHONPATH=$(PWD)
export REDIS_HOST
export VERSION
export FLASK_APP=src/tiny.py
export DOMAIN_NAME=http://localhost:5000

redis-dev:
	docker run --rm --name tiny-redis -p 7001:6379 -d redis

redis-test-start:
	docker run --rm --name tiny-redis-test -p 7002:6379 -d redis

redis-test-stop:
	docker stop tiny-redis-test

build-dev: build-shortener
	pip install -r requirements_dev.txt
	flake8

build: build-shortener
	pip install -r requirements.txt

build-shortener:
	cd rust_shortener;cargo b --release
	cp rust_shortener/target/release/libmyrust_shortener.so myrust_shortener.so

run-dev: build-dev
	export FLASK_ENV=development
	@echo Running Version ${VERSION}
	flask run --host=$(HOST)

run-prod: build
	@echo Todo UWGI or something here

test:
	$(MAKE) redis-test-stop || true
	@echo Starting Redis test service
	$(MAKE) redis-test-start
	REDIS_HOST=redis://127.0.0.1:7002;pytest -v || true
	$(MAKE) redis-test-stop
