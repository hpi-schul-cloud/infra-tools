# dbcmetrics

![Version: 0.1.1](https://img.shields.io/badge/Version-0.1.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.1.3](https://img.shields.io/badge/AppVersion-1.1.3-informational?style=flat-square)

A Helm chart for Kubernetes

## How to install this chart

```console
helm install chart_name ./dbcmetrics
```

To install the chart with the release name `my-release`:

```console
helm install chart_name ./dbcmetrics
```

To install with some set values:

```console
helm install chart_name ./dbcmetrics --set values_key1=value1 --set values_key2=value2
```

To install with custom values file:

```console
helm install chart_name ./dbcmetrics -f values.yaml
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `1` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| containerPort | int | `9000` |  |
| dbcmconfig | object | `{"features":{"version_metrics":"enabled"},"instances":[{"name":"myinstancename","shortname":"min","url":"https://myinstance.dbildungscloud.dev"}],"version_metrics":{"interval":600,"services":[{"server":"/api/v1/version"},{"client":"/version"},{"nuxt":"/nuxtversion"}]}}` | The values below 'dbcnconfigwill be copied via the configmap into the file system of the dbcmetrics pod below the mount point specified in the deployment template which is '/etc/dbcmetrics/dbcm_config.yaml' |
| dbcmconfig.features.version_metrics | string | `"enabled"` | each supported feature can be disabled or enabled. In additon each feature has its own configuration section with the same name below |
| dbcmconfig.instances[0] | object | `{"name":"myinstancename","shortname":"min","url":"https://myinstance.dbildungscloud.dev"}` | This part contains a list of instances which evrsions should be observed and provided as Prometheus metrics - the name will be part of the Prometheus value, for the sample the Prometheus value will be 'myinstance_info' - url is the base url of an existing dBildungscloud instance to be monitored - shortname is for further filtering in  future scenarios |
| dbcmconfig.version_metrics | object | `{"interval":600,"services":[{"server":"/api/v1/version"},{"client":"/version"},{"nuxt":"/nuxtversion"}]}` | This part hold the feature specif configuration - interval definces the cycle in seconds how often the version information is queried - services contains a list of services the version will be queried with the parte that needs to be added    to the base url to receive the version information |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"schulcloud/dbcmetrics"` |  |
| image.tag | string | `nil` | Overrides the image tag whose default is the chart appVersion. |
| imagePullSecrets | list | `[]` |  |
| ingress.annotations | object | `{}` |  |
| ingress.className | string | `""` |  |
| ingress.enabled | bool | `false` |  |
| ingress.hosts[0].host | string | `"chart-example.local"` |  |
| ingress.hosts[0].paths[0].path | string | `"/metrics"` |  |
| ingress.hosts[0].paths[0].pathType | string | `"ImplementationSpecific"` |  |
| ingress.tls | list | `[]` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| service.port | int | `80` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` | Annotations to add to the service account |
| serviceAccount.create | bool | `true` | Specifies whether a service account should be created |
| serviceAccount.name | string | `""` | The name of the service account to use. If not set and create is true, a name is generated using the fullname template |
| tolerations | list | `[]` |  |

