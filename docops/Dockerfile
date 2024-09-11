FROM quay.io/ansible/awx-ee:24.1.0

USER root

RUN \
    # Add non-privileged user
    adduser docops --uid 1000 --gid 0 && \
    # Install drawio
    dnf install -y wget && \
    mkdir /home/docops/drawio && \
    cd /home/docops/drawio && \
    curl -s https://api.github.com/repos/jgraph/drawio-desktop/releases/latest | grep browser_download_url | grep '.*drawio-x86_64-.*\.rpm' | cut -d '"' -f 4 | wget -i -  && \
    dnf install -y ./drawio-x86_64-*.rpm && \
    dnf remove -y wget && \
    rm -rf /home/docops/drawio && \
    # Install X Virtual Framebuffer as an X server because it's needed to execute drawio in a headless mode
    # Later execute drawio with xvfb as the following.
    # Remember to append the options '--disable-gpu --headless --no-sandbox' as the last options of the command.
    # Examples:
    # xvfb-run -a drawio --version --disable-gpu --headless --no-sandbox
    # xvfb-run -a drawio --export --format png --output ./test.png ./test.drawio --disable-gpu --headless --no-sandbox
    dnf install -y xorg-x11-server-Xvfb;

USER docops

RUN \
    # Install doctoolchain
    cd /home/docops && \
    curl -Lo dtcw https://doctoolchain.org/dtcw && \
    chmod +x ./dtcw && \
    # trying to force V to 3.4.1 cause of hardcoded version in dtcw install script
    export DTC_VERSION="3.4.1" && \
    sed -i '15s/DTC_VERSION:=3.4.0/DTC_VERSION:=3.4.1/' dtcw && \
    ./dtcw install doctoolchain; \
    ./dtcw install java; \
    ./dtcw tasks --group doctoolchain; \
    rm docToolchainConfig.groovy -f ; \
    #cd /.doctoolchain/docToolchain-3.4.0/core/src/main/groovy/org/docToolchain/tasks &&  \
    #sed -i '478s/^/def/' Asciidoc2ConfluenceTask.groovy; \ 
    # Install community.general collection, it contains the 'archive' module used in the doctoolchain playbook
    ansible-galaxy collection install community.general;

CMD ["/bin/bash"]
