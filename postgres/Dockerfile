# Используем официальный образ PostgreSQL
FROM postgres:15

# Установка необходимых пакетов и pgvector
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    make \
    gcc \
    libpq-dev \
    git \
    postgresql-server-dev-15 \
    ca-certificates && \
    git clone https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    cd .. && \
    rm -rf pgvector && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
