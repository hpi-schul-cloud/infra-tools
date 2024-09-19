FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

RUN set -x \
    && apt-get -y update \
    && apt-get -y install wget python3-pip \
    && wget https://dl.k8s.io/release/v1.28.7/bin/linux/amd64/kubectl \
    && chmod +x kubectl \
    && mv ./kubectl /usr/local/bin/kubectl \
    && wget -qO /usr/share/keyrings/postgres.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    && echo "deb [signed-by=/usr/share/keyrings/postgres.asc] https://apt.postgresql.org/pub/repos/apt jammy-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && pip install boto \
    && apt-get -y update \
    && apt-get -y install \
        duply \
        ca-certificates \
        gnupg \
        apt-transport-https \
        postgresql-client-14 \
        mariadb-client \
    && apt-get clean -y