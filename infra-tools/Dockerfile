ARG DEBIAN_IMAGE_TAG="stable-20200607"
FROM debian:${DEBIAN_IMAGE_TAG} as release

ARG BUILD_BRANCH
ARG BUILD_HASH

LABEL build.stage="release"
LABEL build.branch="${BUILD_BRANCH}"
LABEL build.hash="${BUILD_HASH}"
RUN set -x \
    && apt-get -y update \
    && apt-get -y install wget gnupg \
    && wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add - \
    && echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.2 main" | tee /etc/apt/sources.list.d/mongodb-org-4.2.list \
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
        mongodb-org-shell \
        mongodb-org-tools \
        vim-nox \
        mc \
        gpg \
        duply \
        python-boto \
        postgresql-client \
        procps \
        screen \
        tmux \
        mtr-tiny \
        tcpdump \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

