# Use the PostGIS image as the base
FROM postgis/postgis:15-3.4

# Install necessary packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       wget \
       git \
       postgresql-server-dev-15 \
    && rm -rf /var/lib/apt/lists/* \
    && git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && cd /tmp/pgvector \
    && make \
    && make install \
    && cd - \
    && apt-get purge -y --auto-remove build-essential postgresql-server-dev-15 libpq-dev wget git \
    && rm -rf /tmp/pgvector

# Copy initialization scripts
COPY ./init-db.sh/ /docker-entrypoint-initdb.sh/