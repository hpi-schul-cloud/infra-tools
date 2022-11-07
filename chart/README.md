# dbcmetrics

![Version: 0.4.1](https://img.shields.io/badge/Version-0.4.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.4.0](https://img.shields.io/badge/AppVersion-1.4.0-informational?style=flat-square)

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
| dbcmconfig | object | `{"instances":[{"name":"myinstancename","shortname":"min","url":"https://myinstance.dbildungscloud.dev"}],"maintenance_metrics":{"cluster_maintenance_duration_min":15,"metric_refresh_interval_sec":15,"nodepool_maintenance_duration_min":240,"s3_bucket":"sc-tf-remote-state-01","s3_endpoint":"https://s3-eu-central-1.ionoscloud.com","s3_stage_directory":"env:/dev/","window_refresh_interval_min":30},"version_metrics":{"interval":600,"services":{"client":"/version","nuxt":"/nuxtversion","server":"/serverversion"}}}` | The values below 'dbcmconfig' will be copied via the configmap into the file system of the dbcmetrics pod below the mount point specified in the deployment template which is '/etc/dbcmetrics/dbcm_config.yaml' |
| dbcmconfig.instances[0] | object | `{"name":"myinstancename","shortname":"min","url":"https://myinstance.dbildungscloud.dev"}` | This part contains a list of instances which versions should be observed and provided as Prometheus metrics - the name will be part of the Prometheus value, for the sample the Prometheus value will be 'myinstance_info' - url is the base url of an existing dBildungscloud instance to be monitored - shortname is for further filtering in future scenarios |
| dbcmconfig.maintenance_metrics | object | `{"cluster_maintenance_duration_min":15,"metric_refresh_interval_sec":15,"nodepool_maintenance_duration_min":240,"s3_bucket":"sc-tf-remote-state-01","s3_endpoint":"https://s3-eu-central-1.ionoscloud.com","s3_stage_directory":"env:/dev/","window_refresh_interval_min":30}` | This part holds the maintenance module specific configuration |
| dbcmconfig.maintenance_metrics.cluster_maintenance_duration_min | int | `15` | Duration of a cluster maintenance in minutes |
| dbcmconfig.maintenance_metrics.metric_refresh_interval_sec | int | `15` | Interval for checking wether a cluster is currently in its maintenace window in seconds |
| dbcmconfig.maintenance_metrics.nodepool_maintenance_duration_min | int | `240` | Duration of a noodpool maintenance in minutes |
| dbcmconfig.maintenance_metrics.s3_bucket | string | `"sc-tf-remote-state-01"` | Name of the terraform state bucket |
| dbcmconfig.maintenance_metrics.s3_endpoint | string | `"https://s3-eu-central-1.ionoscloud.com"` | S3 endpoint for the terraform state bucket |
| dbcmconfig.maintenance_metrics.s3_stage_directory | string | `"env:/dev/"` | Prefix for the terraform state s3 object |
| dbcmconfig.maintenance_metrics.window_refresh_interval_min | int | `30` | Interval for polling the maintenance windows from the terraform state in minutes |
| dbcmconfig.version_metrics | object | `{"interval":600,"services":{"client":"/version","nuxt":"/nuxtversion","server":"/serverversion"}}` | This part holds the version module specific configuration - interval definces the cycle in seconds how often the version information is queried - services contains a list of services the version will be queried with the parte that needs to be added    to the base url to receive the version information |
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
| ionos_maintenance_metrics_enabled | bool | `false` | Enables/disables ionosmaintenance module |
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
| storage_access_key_key | string | `"s3_access_key"` |  |
| storage_access_secret_key | string | `"s3_access_secret"` |  |
| storage_access_secret_name | string | `"dbcmetrics-secret"` |  |
| storage_bucket_name_key | string | `"s3_bucket_name"` |  |
| storage_exclude_subfolders | bool | `true` |  |
| storage_interval | int | `30` |  |
| storage_metrics_enabled | bool | `false` | Enables/disables storage module |
| storage_provider_region | string | `"s3-de-central"` |  |
| storage_provider_url | string | `"http://s3-de-central.profitbricks.com"` |  |
| tfstate_s3_access_key_key | string | `"s3_access_key"` | 1Password field name for the S3 access key for the terraform state bucket |
| tfstate_s3_access_secret_key | string | `"s3_access_secret"` | 1Password field name for the S3 access secret for the terraform state bucket |
| tfstate_s3_secret_name | string | `"ionos-maintenance-metrics"` | Name of the kubernetes secret for the terraform state bucket |
| tolerations | list | `[]` |  |
| version_metrics_enabled | bool | `false` | Enables/disables version module |

