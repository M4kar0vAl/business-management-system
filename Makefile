DC = docker compose
APP_SERVICE = app

.PHONY: run
run:
	${DC} up -d --build

.PHONY: down
down:
	${DC} down
