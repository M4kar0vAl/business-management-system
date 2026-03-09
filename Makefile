DC = docker compose
APP_SERVICE = app
DB_SERVICE = db
name =

.PHONY: run
run:
	${DC} up -d --build

.PHONY: down
down:
	${DC} down

.PHONY: stor
stor:
	${DC} up -d ${DB_SERVICE}

.PHONY: migration
migration:
ifndef name
	$(error migration_name must be defined)
endif
	alembic revision --autogenerate -m "${name}"

.PHONY: migrate
migrate:
	alembic upgrade head
