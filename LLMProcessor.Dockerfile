FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.13 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY . .

EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "--no-sync", "--env-file", ".env.production", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
