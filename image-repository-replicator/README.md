# Image Repository Replicator
The purpose of this tool is to replicate a container image repository from one registry to another.

## Configuration

### Environment Variables

The following environment variables are read by the image-repository-replication application:
| Name        | Description | Example Value |
| ----------- | ----------- | ------------- |
| SOURCE_REPOSITORY_URL | The source container image repository for the replication | `docker.io/schulcloud/schulcloud-server` |
| SOURCE_REGISTRY_USER | The user to authenticate crane at the source registry | `mustermann` |
| SOURCE_REGISTRY_PASSWORD | The user password to authenticate at the source registry | `4GXJXE9fenD3jZnzjQFa` (random generated) |
| DEST_REPOSITORY_URL | The destination container image repository for the replication | `docker.io/schulcloud/schulcloud-server` |
| DEST_REGISTRY_USER | The user to authenticate crane at the destination registry | `musterfrau` |
| DEST_REGISTRY_PASSWORD | The user password to authenticate at the destination registry | `m29VK2uezrzaRCYUiVPD` (random generated) |