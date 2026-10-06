PYTHON_RUN_M := PYTHONDONTWRITEBYTECODE=1 python3 -B -m 
UV_RUN_M := $(PYTHON_RUN_M) uv run -m

run: 
	$(UV_RUN_M) registration_service

migrate:
	$(UV_RUN_M) alembic revision --autogenerate

upgrade:
	$(UV_RUN_M) alembic upgrade head

check:
	$(UV_RUN_M) black src