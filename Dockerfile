FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

# Data directory for TinyDB persistence
RUN mkdir -p /app/data
VOLUME /app/data

ENV BENCH_DB_PATH=/app/data/bench_sales.json

EXPOSE 8000

CMD ["bench-agent-web", "--host", "0.0.0.0", "--no-browser"]
