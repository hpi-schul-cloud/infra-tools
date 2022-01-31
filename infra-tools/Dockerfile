FROM debian:bullseye as release

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
        python3-boto3 \
        postgresql-client \
        procps \
        screen \
        tmux \
        mtr-tiny \
        tcpdump \
        gettext-base \
    && apt-get clean -y

run curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.23.3/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl

# Install nvm with node and npm
RUN curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash \
    && . /root/.nvm/nvm.sh \
    && nvm install --lts

ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/v$NODE_VERSION/bin:$PATH
