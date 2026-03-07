DC = docker compose
APP_SERVICE = app
DB_SERVICE = db

.PHONY: run
run:
	${DC} up -d --build

.PHONY: down
down:
	${DC} down

.PHONY: stor
stor:
	${DC} up -d ${DB_SERVICE}
