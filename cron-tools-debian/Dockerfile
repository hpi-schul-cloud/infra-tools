FROM debian:13-slim

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

RUN set -x \
    && apt-get -y update \
    && apt-get -y dist-upgrade \
    && apt-get -y install bsdextrautils \
    && apt-get -y install curl wget gnupg \
#    && wget https://dl.k8s.io/release/v1.32.8/bin/linux/amd64/kubectl \
#    && chmod +x kubectl \
#    && mv ./kubectl /usr/local/bin/kubectl \
#    && curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
#        gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
#        --dearmor \
#    && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list \
    && echo "deb https://apt.postgresql.org/pub/repos/apt trixie-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc > /etc/apt/trusted.gpg.d/postgres.asc \
    && apt-get -y update \
    && apt-get -y install \
#        mongodb-mongosh \
        postgresql-client-15 \
        mariadb-client \
        jq \
        openssl \
        python3-boto3 \
        duply \
        duplicity \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

    
    # https://stackoverflow.com/questions/75602063/pip-install-r-requirements-txt-is-failing-this-environment-is-externally-mana
#RUN pip install duplicity==3.0.6 boto3 --break-system-packages
