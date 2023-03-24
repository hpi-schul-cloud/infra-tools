FROM gcr.io/go-containerregistry/crane:debug

WORKDIR /usr/src/app
COPY image_repository_replication.sh image_repository_replication.sh

ENTRYPOINT [ "/busybox/sh", "image_repository_replication.sh" ]