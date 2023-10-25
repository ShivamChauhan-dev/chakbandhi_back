.PHONY: install
install:
	poetry install

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: lint
lint:
	poetry run pre-commit run

.PHONY: migrate
migrate:
	poetry run python3.11 backend/manage.py migrate

.PHONY: migrations
migrations:
	poetry run python3.11 backend/manage.py makemigrations

.PHONY: run-server
run-server:
	poetry run python3.11 backend/manage.py runserver

.PHONY: shell
shell:
	poetry run python3.11 backend/manage.py shell

.PHONY: superuser
superuser:
	poetry run python3.11 backend/manage.py createsuperuser

.PHONY: test
test:
	poetry run pytest backend

.PHONY: update
update: install migrate install-pre-commit ;

.PHONY: docker-project
docker-project:
	docker-compose up -d --build; docker ps
