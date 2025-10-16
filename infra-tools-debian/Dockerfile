FROM debian:12-slim as release

ARG BUILD_BRANCH
ARG BUILD_HASH

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

LABEL build.stage="release"
LABEL build.branch="${BUILD_BRANCH}"
LABEL build.hash="${BUILD_HASH}"
RUN set -x \
    && apt-get -y update \
    && apt-get -y dist-upgrade \
    && apt-get -y install curl wget gnupg \
    && wget https://dl.k8s.io/release/v1.32.8/bin/linux/amd64/kubectl \
    && chmod +x kubectl \
    && mv ./kubectl /usr/local/bin/kubectl \
    && curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
        gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
        --dearmor \
    && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list \
    && echo "deb https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc > /etc/apt/trusted.gpg.d/postgres.asc \
    && apt-get -y update \
    && apt-get -y install \
        git \
        make \
        bash \
        openssh-client \
        openssl \
        python3 \
        unzip \
        netcat-openbsd \
        traceroute \
        dnsutils \
        redis-tools \
        mongodb-mongosh \
        mongodb-org-database-tools-extra \
        vim-nox \
        mc \
        gpg \
        duply \
        python3-boto3 \
        postgresql-client-15 \
        procps \
        screen \
        tmux \
        mtr-tiny \
        tcpdump \
        gettext-base \
        gettext \
        librsync-dev \
        python3-pip \
        ldap-utils \
        jq \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    # https://stackoverflow.com/questions/75602063/pip-install-r-requirements-txt-is-failing-this-environment-is-externally-mana
    && pip install duplicity==0.8.23 --break-system-packages
