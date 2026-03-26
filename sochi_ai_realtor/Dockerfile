FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       build-essential \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock* /app/

RUN poetry run playwright install --with-deps chromium
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY src /app/src

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
