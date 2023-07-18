# Image Repository Replicator
The purpose of this tool is to replicate a container image repository from one registry to another.

## Configuration

### Environment Variables

The following environment variables are read by the image-repository-replication application:
| Name        | Description | Example Value |
| ----------- | ----------- | ------------- |
| SOURCE_REPOSITORY_URL | The source container image repository for the replication | `docker.io/schulcloud/schulcloud-server` |
| SOURCE_REGISTRY_USER | The user to authenticate crane at the source registry | `myuser` |
| SOURCE_REGISTRY_PASSWORD | The user password to authenticate at the source registry | `4GXJXE9fenD3jZnzjQFa` (random generated) |
| DEST_REPOSITORY_URL | The destination container image repository for the replication | `docker.io/schulcloud/schulcloud-server` |
| DEST_REGISTRY_USER | The user to authenticate crane at the destination registry | `myotheruser` |
| DEST_REGISTRY_PASSWORD | The user password to authenticate at the destination registry | `m29VK2uezrzaRCYUiVPD` (random generated) |

# How to run

## As a standalone container

Build an container image by running bash the command
```
docker build --rm -f ./Dockerfile -t image-repository-replicator .
```

Then run a container from the image by executing the command
```
docker run \
    --name image-repository-replicator \
    --rm \
    -e SOURCE_REPOSITORY_URL="<your source repository url>" \
    -e SOURCE_REGISTRY_USER="<your source registry user>" \
    -e SOURCE_REGISTRY_PASSWORD="<your source registry user password>" \
    -e DEST_REPOSITORY_URL="<your destination repository url>" \
    -e DEST_REGISTRY_USER="<your destination registry user>" \
    -e DEST_REGISTRY_PASSWORD="<your destination registry user password>" \
    image-repository-replicator:latest
```
