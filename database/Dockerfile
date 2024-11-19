# Use the PostGIS image as the base
FROM postgis/postgis:15-3.4

# Install necessary packages
RUN apt-get update

RUN apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       wget \
       git \
       postgresql-server-dev-15

RUN apt-get install -y clang-13

RUN rm -rf /var/lib/apt/lists/*
RUN git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git /tmp/pgvector
WORKDIR /tmp/pgvector
RUN make
RUN make install
RUN cd -
RUN apt-get purge -y --auto-remove build-essential postgresql-server-dev-15 libpq-dev wget git
WORKDIR /
RUN rm -rf /tmp/pgvector

# Copy initialization scripts
COPY init-db.sh /docker-entrypoint-initdb.sh/
