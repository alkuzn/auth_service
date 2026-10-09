PYTHON_RUN_M := PYTHONDONTWRITEBYTECODE=1 python3 -B -m 
UV_RUN_M := $(PYTHON_RUN_M) uv run -m

run: 
	$(UV_RUN_M) auth_service

migrate:
	$(UV_RUN_M) alembic -q check || $(UV_RUN_M) alembic revision --autogenerate && $(UV_RUN_M) alembic upgrade head

check:
	$(UV_RUN_M) black src
	
sync:
	$(PYTHON_RUN_M) uv sync

before_commit:
	$(UV_RUN_M) isort .
	$(UV_RUN_M) black .
	$(PYTHON_RUN_M) uv check
	$(UV_RUN_M) pytest -s tests/test.py