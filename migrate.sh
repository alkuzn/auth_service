uv run alembic -q check ||  uv run alembic revision --autogenerate && uv run alembic upgrade head
