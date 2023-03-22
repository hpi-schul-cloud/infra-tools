# Image Repository Replicator
The purpose of this tool is to replicate a container image repository from one registry to another.

## Configuration

### Environment Variables

The following environment variables are read by the image-repository-replication application:
| Name        | Description | Example Value |
| ----------- | ----------- | ------------- |
| SOURCE_REPOSITORY_URL | The source container image repository for the replication | `docker.io/schulcloud/schulcloud-server` |
| DEST_REPOSITORY_URL | The destination container image repository for the replication | `docker.io/schulcloud/schulcloud-server` |
| REGISTRY_USER | The container image registry user which is used to authenticate crane at the registry | `mustermann` |
| REGISTRY_PASSWORD | The password of the container image registry user | `mkMfCRMp8GpwZwXzkJbp` (random generated) |
