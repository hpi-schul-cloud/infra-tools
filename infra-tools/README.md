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

List of available docker image tags is under https://hub.docker.com/r/schulcloud/infra-tools/tags

## Provided Tools
* [curl](https://curl.haxx.se/docs/manpage.html)
* [nc](https://man.openbsd.org/nc.1)
* [git](https://git-scm.com/docs/git)
* [make](https://www.gnu.org/software/make/manual/make.html)
* [ssh](https://man.openbsd.org/ssh)
* [openssl](https://www.openssl.org/docs/man1.1.1/man1/)
* [python3](https://docs.python.org/3/)
* [unzip](https://linux.die.net/man/1/unzip)
* [nslookup](https://linux.die.net/man/1/nslookup)
* [dig](https://linux.die.net/man/1/dig)
* [redis](https://redis.io/topics/rediscli)
* [mongo](https://docs.mongodb.com/manual/reference/program/mongo/)
* [psql](https://www.postgresql.org/docs/9.0/app-psql.html)
* [procps](https://man7.org/linux/man-pages/man1/procps.1.html)
