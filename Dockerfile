FROM python:3.12-slim as first
WORKDIR /app
COPY ./ ./
RUN pip install uv &&  uv sync --frozen --no-dev

FROM python:3.12-slim
WORKDIR /app
COPY --from=first /app ./
CMD . .venv/bin/activate && python -m registration_service