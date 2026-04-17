FROM python:3.13-slim

ARG SECRET_KEY
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV DEBUG=true
ENV SECRET_KEY=$SECRET_KEY

WORKDIR /app

ENV PYTHONPATH=/app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic
COPY static ./static

RUN uv lock
RUN uv sync --frozen --no-install-project
RUN uv sync --frozen
RUN uv run alembic upgrade head

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]