FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

RUN set -x \
    && apt-get -y update \
    && apt-get -y install wget \
    && apt-get -y install bsdextrautils \
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
        jq \
    && apt-get clean -y
CMD ["mongosh", "--nodb", "--eval", "disableTelemetry()"]