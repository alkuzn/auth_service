FROM python:3.12-slim as first
WORKDIR /app
COPY ./ ./
RUN \
--mount=type=cache,target=/root/.cache/uv \
--mount=type=cache,target=/root/.cache/pip \
pip install uv &&  uv sync --frozen --no-dev

FROM python:3.12-slim
WORKDIR /app
COPY --from=first /app ./
CMD . .venv/bin/activate && python -m auth_service