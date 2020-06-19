# infra-tools

## Build

To build a default container image run the following code:
```
make build
```

To customize the build process set some environment variables (details see
Makefile). For example set `DOCKER_IMAGE_TAG` to build a custom image tag:
```
make build DOCKER_IMAGE_TAG="foo/bar:latest"
```

## Push

To push a previously built default container image run the following code:
```
make push
```

To customize the push process set some environment variables (details see
Makefile). For example set `DOCKER_IMAGE_TAG` to push a custom image tag:
```
make push DOCKER_IMAGE_TAG="foo/bar:latest"
```
