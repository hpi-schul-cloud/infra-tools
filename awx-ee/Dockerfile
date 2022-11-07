ARG EE_BASE_IMAGE=quay.io/ansible/ansible-runner:stable-2.12-latest
ARG EE_BUILDER_IMAGE=quay.io/ansible/ansible-builder:latest

FROM $EE_BASE_IMAGE as galaxy
ARG ANSIBLE_GALAXY_CLI_COLLECTION_OPTS=
USER root

ADD _build /build
WORKDIR /build

RUN ansible-galaxy role install -r requirements.yml --roles-path "/usr/share/ansible/roles"
RUN ANSIBLE_GALAXY_DISABLE_GPG_VERIFY=1 ansible-galaxy collection install $ANSIBLE_GALAXY_CLI_COLLECTION_OPTS -r requirements.yml --collections-path "/usr/share/ansible/collections"

FROM $EE_BUILDER_IMAGE as builder

COPY --from=galaxy /usr/share/ansible /usr/share/ansible

ADD _build/requirements.txt requirements.txt
ADD _build/bindep.txt bindep.txt
RUN ansible-builder introspect --sanitize --user-pip=requirements.txt --user-bindep=bindep.txt --write-bindep=/tmp/src/bindep.txt --write-pip=/tmp/src/requirements.txt
RUN assemble

FROM $EE_BASE_IMAGE
USER root
ARG HELM_VERSION=3.10.1
ARG TERRAFORM_VERSION=1.3.4
ARG KUBECTL_VERSION=1.21.4
ARG OP_VERSION=2.7.3
RUN whoami
RUN cat /etc/os-release
RUN pip3 install --upgrade pip setuptools
RUN dnf install -y unzip
RUN cd /tmp && curl -LO https://releases.hashicorp.com/terraform/$TERRAFORM_VERSION/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && install -o root -g root -m 0755 terraform /usr/local/bin/terraform
RUN curl -LO https://dl.k8s.io/release/$KUBECTL_VERSION/bin/linux/amd64/kubectl
RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
RUN cd /tmp && curl -LO https://get.helm.sh/helm-v$HELM_VERSION-linux-amd64.tar.gz &&  tar -xf helm-v$HELM_VERSION-linux-amd64.tar.gz && install -o root -g root -m 0755 linux-amd64/helm /usr/local/bin/helm
RUN cd /tmp && curl -LO https://cache.agilebits.com/dist/1P/op2/pkg/v$OP_VERSION/op_linux_amd64_v$OP_VERSION.zip && unzip op_linux_amd64_v$OP_VERSION.zip && install -o root -g root -m 0755 op /usr/local/bin/op

COPY --from=galaxy /usr/share/ansible /usr/share/ansible

COPY --from=builder /output/ /output/
RUN /output/install-from-bindep && rm -rf /output/wheels
RUN alternatives --set python /usr/bin/python3
