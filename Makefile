modules = app/ src/ tests/


.PHONY: init
init:
	poetry install

.PHONY: format
format:
	poetry run black $(modules)
	poetry run isort $(modules)

.PHONY: mypy
mypy:
	poetry run mypy $(modules)

.PHONY: flake8
flake8:
	poetry run flake8 $(modules)

.PHONY: format-check
format-check:
	poetry run black --check --diff $(modules)
	poetry run isort --check-only --diff $(modules)
	poetry run lint-imports

.PHONY: check
check: format-check flake8 mypy

nice: format check

.PHONY: test
test:
	poetry run pytest # --cov-fail-under=95

migrate:
	poetry run alembic upgrade head

futlog:
	poetry run uvicorn app.api.app:app --reload --port 6001

task-worker:
	poetry run celery -A app.tasks.app:celery_app worker --beat --loglevel=info