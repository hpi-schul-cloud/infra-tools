FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

RUN set -x \
    && apt-get -y update \
    && apt-get -y install wget \
    && wget https://dl.k8s.io/release/v1.28.7/bin/linux/amd64/kubectl \
    && chmod +x kubectl \
    && mv ./kubectl /usr/local/bin/kubectl \
    && wget -qO /usr/share/keyrings/mongodb.asc https://www.mongodb.org/static/pgp/server-6.0.asc \
    && echo "deb [signed-by=/usr/share/keyrings/mongodb.asc] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" > /etc/apt/sources.list.d/mongodb-org-6.0.list \
    && wget -qO /usr/share/keyrings/postgres.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    && echo "deb [signed-by=/usr/share/keyrings/postgres.asc] https://apt.postgresql.org/pub/repos/apt jammy-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get -y update \
    && apt-get -y install \
        mongodb-mongosh \
        postgresql-client-15 \
        mariadb-client \
        jq \
        openssl \
        duply \
        python3 \
        python3-pip \
        python3-boto3 \
        gpg \
        gettext \
        librsync-dev \
    && apt-get clean -y

RUN pip install duplicity==0.8.23