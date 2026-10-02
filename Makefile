run: 
	PYTHONDONTWRITEBYTECODE=1 python3 -B -m uv run  -m registration_service

migrate:
	PYTHONDONTWRITEBYTECODE=1 python3 -B -m uv run  -m alembic check