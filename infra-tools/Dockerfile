FROM ubuntu:22.04 as release

ARG BUILD_BRANCH
ARG BUILD_HASH

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

LABEL build.stage="release"
LABEL build.branch="${BUILD_BRANCH}"
LABEL build.hash="${BUILD_HASH}"
RUN set -x \
    && apt-get -y update \
    && apt-get -y install wget gnupg \
    && wget -qO - https://pgp.mongodb.com/server-6.0.asc | gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor \
    && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list \
    && echo "deb https://apt.postgresql.org/pub/repos/apt jammy-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc > /etc/apt/trusted.gpg.d/postgres.asc \
    && apt-get -y update \
    && apt-get -y install \
        curl \
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
        mongodb-database-tools \
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
    && pip install duplicity==0.8.23
