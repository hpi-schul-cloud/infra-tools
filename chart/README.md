# dbcmetrics

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.1.2](https://img.shields.io/badge/AppVersion-1.1.2-informational?style=flat-square)

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
| dbcmconfig.features.version_metrics | string | `"enabled"` |  |
| dbcmconfig.instances[0].name | string | `"brandenburg"` |  |
| dbcmconfig.instances[0].shortname | string | `"brb"` |  |
| dbcmconfig.instances[0].url | string | `"https://brandenburg.cloud"` |  |
| dbcmconfig.instances[1].name | string | `"niedersachsen"` |  |
| dbcmconfig.instances[1].shortname | string | `"nbc"` |  |
| dbcmconfig.instances[1].url | string | `"https://niedersachsen.cloud"` |  |
| dbcmconfig.instances[2].name | string | `"thueringen"` |  |
| dbcmconfig.instances[2].shortname | string | `"thr"` |  |
| dbcmconfig.instances[2].url | string | `"https://schulcloud-thueringen.de"` |  |
| dbcmconfig.instances[3].name | string | `"international"` |  |
| dbcmconfig.instances[3].shortname | string | `"int"` |  |
| dbcmconfig.instances[3].url | string | `"https://international.hpi-schul-cloud.de"` |  |
| dbcmconfig.instances[4].name | string | `"dbildungscloud"` |  |
| dbcmconfig.instances[4].shortname | string | `"dbc"` |  |
| dbcmconfig.instances[4].url | string | `"https://dbildungscloud.de"` |  |
| dbcmconfig.instances[5].name | string | `"demo"` |  |
| dbcmconfig.instances[5].shortname | string | `"demo"` |  |
| dbcmconfig.instances[5].url | string | `"https://demo.hpi-schul-cloud.de"` |  |
| dbcmconfig.version_metrics.interval | int | `600` |  |
| dbcmconfig.version_metrics.services[0].server | string | `"/api/v1/version"` |  |
| dbcmconfig.version_metrics.services[1].client | string | `"/version"` |  |
| dbcmconfig.version_metrics.services[2].nuxt | string | `"/nuxtversion"` |  |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"schulcloud/dbcmetrics"` |  |
| image.tag | string | `"latest"` |  |
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
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |

