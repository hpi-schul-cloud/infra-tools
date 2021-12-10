
FROM jnorwood/helm-docs:latest

RUN apk add --no-cache bash
RUN apk add --no-cache git

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/bin/bash", "-c", "/entrypoint.sh"]
