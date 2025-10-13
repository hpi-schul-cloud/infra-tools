# dbcmetrics

A containerized Python application which exposes special dBildungscloud values as Prometheus metrics. The application can have multiple modules for different values, e.g. a module for the application version of a running dBildungscloud instance or a further module providing the amount of mails in the dBidlungscloud mailboxes.
The port where metrics are exposed is currently hard coded to 9000.

The source code can be found in the [dbcmetrics](https://github.com/hpi-schul-cloud/infra-tools/tree/master/dbcmetrics) folder of the infra-tools repository of hpi-schul-cloud on github.

## Modules
| Name                  | metrics for       |
| ------------------    | ----------------- |
| storage               | S3 buckets        |
| version               | service versions  |
| ionosmaintenance      | maintenance windows of clusters | 
| plannedmaintenance    | planned maintenance windows (Cachet) | 
| uptimekumamaintenance | planned maintenance windows (Uptime kuma) | 

# Configuration

Modules can be enabled/disabled via environment variables.

Secrets are provided via environment variables.

## Config File
A `dbcm_config.yaml` config file will be read either from a global location `/etc/dbcmconfig` or the file path which is specified in an `DBCMCONFIG` environment variable.

## Environment Variables

The following environment variables are read by the dbcmetrics application:
| Name        | Module      | Description | Example Value |
| ----------- | ----------- | ----------- | ------------- |
| LOGLEVEL | - | Optional variable to set the log level (default is `INFO`) | `DEBUG` |
| DBCMCONFIG | - | Path to the `dbcm_config.yaml` file (default is `/etc/dbcmconfig`) | `./dbcm_config.yaml` |
| VERSION_METRICS_ENABLED | version | Enables or disabled the version monitoring module | `true` |
| IONOS_MAINTENANCE_METRICS_ENABLED | ionosmaintenance | Enables or disabled the ionosmaintenance monitoring module | `true` |
| PLANNED_MAINTENANCE_METRICS_ENABLED | plannedmaintenance | Enables or disabled the ionosmaintenance monitoring module | `true` |
| UPTIMEKUMA_MAINTENANCE_METRICS_ENABLED | uptimekumamaintenance | Enables or disabled the uptimekumamaintenance monitoring module | `true` |
| STORAGE_METRICS_ENABLED | storage | Enables or disabled the storage monitoring module | `true` |
| STORAGE_INTERVAL | storage | Number of seconds between cycles in which the storage metrics are fetched | `30` |
| STORAGE_EXCLUDE_SUBFOLDERS | storage | Defines if metric generation for folders inside of top-level folders should be disabled  | `true` |
| STORAGE_PROVIDER_URL | storage | URL of the S3 storage provider | `http://example-s3-endpoint.com` |
| STORAGE_PROVIDER_REGION | storage | Region of the S3 storage provider | `s3-example-region` |
| STORAGE_BUCKET_NAME | storage | The name of the bucket to monitor by the storage module (Secret in Kubernetes) | `example-bucket-0000` |
| STORAGE_ACCESS_KEY | storage | The Access Key of your Object Storage Key with access to the Bucket (Secret in Kubernetes) | `mkMfCRMp8GpwZwXzkJbp` (random generated) |
| STORAGE_ACCESS_SECRET | storage | The Secret Key of your Object Storage Key with access to the Bucket (Secret in Kubernetes) | `y8R+6P1Je+62xp9QPF7+euO005HbXr95zD/Clztm` (random generated) |
| TERRAFORM_STATE_S3_ACCESS_KEY | ionosmaintenance | The Access Key of your Object Storage Key with access to the Terraform State Bucket (Secret in Kubernetes) | `mkMfCRMp8GpwZwXzkJbp` (random generated) |
| TERRAFORM_STATE_S3_SECRET_KEY | ionosmaintenance | The Secret Key of your Object Storage Key with access to the Terraform State Bucket (Secret in Kubernetes) | `y8R+6P1Je+62xp9QPF7+euO005HbXr95zD/Clztm` (random generated) |
| UPTIME_KUMA_USERNAME | uptimekumamaintenance | The Username for Uptime kuma (Secret in Kubernetes) | `user` |
| UPTIME_KUMA_PASSWORD | uptimekumamaintenance | The Password for Uptime kuma (Secret in Kubernetes) | `khQfofQfCRKl8GpaAwYzkPvpud1_JzlHxS2PMUU-woI8EDUEihABPef5f4dpyCZAXoHKCRMl8GpaZwYzkJvp` (random generated) |


# Run dbcmetrics on your local machine

## As a Python application in Visual Studio Code

First, install Python 3.6 or higher and then run `pip3 install -r requirements.txt` to install all required Python packages.

Afterwards, copy the `dbcm_config_template.yaml` file as `dbcm_config.yaml` and set the values to configure the version module of the dbcmetrics application.

Then you need to create a run configuration by adding or editing the file `.vscode/launch.json` with the content:
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: dbcmmetrics",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/dbcm.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "env": {
                "LOGLEVEL": "DEBUG",
                "DBCMCONFIG": "./dbcm_config.yaml",
                "STORAGE_METRICS_ENABLED": "true",
                "VERSION_METRICS_ENABLED": "false",
                "IONOS_MAINTENANCE_METRICS_ENABLED": "false",
                "PLANNED_MAINTENANCE_METRICS_ENABLED": "false",
                "UPTIMEKUMA_MAINTENANCE_METRICS_ENABLED": "false",
                "STORAGE_INTERVAL": "30",
                "STORAGE_EXCLUDE_SUBFOLDERS": "true",
                "STORAGE_PROVIDER_URL": "<S3 endpoint>",
                "STORAGE_PROVIDER_REGION": "<S3 provider region>",
                // Secrets in Kubernetes
                "STORAGE_BUCKET_NAME": "<The Name of the Bucket to monitor>",
                "STORAGE_ACCESS_KEY": "<The Access Key of your Object Storage Key with access to the Bucket>",
                "STORAGE_ACCESS_SECRET": "<The Secret Key of your Object Storage Key with access to the Bucket>",
                "UPTIME_KUMA_API_KEY": "<The Access Key of Uptime kuma>"
            },
        }
    ]
}
```
If you have done that, you need to run the `Python: dbcmetrics` run configuration by going in the "Run and Debug" panel on the left side and clicking the play button besides the run configuration dropdown.

## As a standalone Docker Container

Build an container image of the dbcmetrics application by running the command
```
docker build --pull --rm -f "Dockerfile" -t dbcmetrics:latest "."
```

Then run a container from the image by executing the command
```
docker run `
    --name dbcmetrics `
    -p 9000:9000 `
    -e DBCMCONFIG="./dbcm_config.yaml" `
    -e STORAGE_METRICS_ENABLED="true" `
    -e VERSION_METRICS_ENABLED="false" `
    -e IONOS_MAINTENANCE_METRICS_ENABLED="false" `
    -e PLANNED_MAINTENANCE_METRICS_ENABLED="false" `
    -e UPTIMEKUMA_MAINTENANCE_METRICS_ENABLED="false" `
    -e STORAGE_INTERVAL="30" `
    -e STORAGE_EXCLUDE_SUBFOLDERS="true" `
    -e STORAGE_PROVIDER_URL="<S3 endpoint>" `
    -e STORAGE_PROVIDER_REGION="<S3 provider region>" `
    -e STORAGE_BUCKET_NAME="<The Name of the Bucket to monitor>" `
    -e STORAGE_ACCESS_KEY="<The Access Key of your Object Storage Key with access to the Bucket>" `
    -e STORAGE_ACCESS_SECRET="<The Secret Key of your Object Storage Key with access to the Bucket>" `
    -e UPTIME_KUMA_API_KEY="<The Access Key of Uptime kuma>" `
    dbcmetrics:latest
```

## As a Helm release on Kubernetes

To install dbcmetrics with helm in your local kubernetes cluster you first need to clone the [infra-schulcloud](https://github.com/hpi-schul-cloud/infra-schulcloud) repository.
Then you need to remove the `charts/dbcmetrics/templates/servicemonitor.yaml` file locally (do not commit this change) because this is a Kubernetes Custom Resource Definition (CRD) that is created by installing the [kube-prometheus stack](https://github.com/prometheus-operator/kube-prometheus) helm chart, so it doesn't exist on your local kubernetes cluster as long as you don't have the kube-prometheus stack installed.

Afterwards you need to create a secret with the name `dbcmetrics-secret` with three key-value pairs (for the storage module)

| Key |  Value (Example) |
| ----------- | ----------- |
| s3_bucket_name | `example-bucket-0000` |
| s3_access_key | `mkMfCRMp8GpwZwXzkJbp` (random generated) |
| s3_access_secret | `y8R+6P1Je+62xp9QPF7+euO005HbXr95zD/Clztm` (random generated) |

If the ionosmaintenance module is enabled you need a secret with the name `ionos-maintenance-metrics` with the following key-value pairs for the terraform state s3 bucket:

| Key |  Value (Example) |
| ----------- | ----------- |
| s3_access_key | `mkMfCRMp8GpwZwXzkJbp` (random generated) |
| s3_access_secret | `y8R+6P1Je+62xp9QPF7+euO005HbXr95zD/Clztm` (random generated) |

If the uptimekumamaintenance module is enabled you need a secret with the name `uptimekuma-maintenance-metrics` with the following key-value pairs for the uptime kuma status page:

| Key |  Value (Example) |
| ----------- | ----------- |
| api-key | `ofQfCRKl8GpaAwYzkPvpud1_JzlHxS2PMUU-woI8EDUEihABPef5f4dpyCZAXoHK` (random generated) |

If you have done that you can install the dbcmetrics helm chart by in the `charts/` directory of the cloned `infra-schulcloud` repository and run the command
```
helm install dbcmetrics .\dbcmetrics\ --set image.repository=ghcr.io/hpi-schul-cloud/dbcmetrics --set image.tag=latest
```
This will install the container image with the `latest` tag from [dbcmetrics image repository](https://github.com/hpi-schul-cloud/infra-tools/pkgs/container/dbcmetrics) of the `infra-tools` github repository.

If the installation is successful you can look up the dbcmetrics deployment for example in Lens, click on the pod, look at the ports of the `dbcmetrics` container on the pod and create a port forward with port `9000` to access the container endpoint from your local machine.

Alternatively you can run the following command to create a port-forward of the port `9000` from pod of the dbcmetrics deployment to the port `9000` of your local machine.
```
kubectl port-forward deployment/dbcmetrics 9000:9000
```

# Access the dbcmetrics endpoint on your local machine

After running dbcmetrics as a python application, as a standalone container or as a helm release you can open the URL `http://localhost:9000/` in your browser to see the metrics endpoint generated by the prometheus client with all metrics according to your configuration.

Besides the default prometheus metrics you should see on this endpoint a section for each enabled module.
Like this for the version module:
```
# HELP version_info Version Information
# TYPE version_info gauge
version_info{app_instance="example_instance_name",dashboard="version_dashboard",service_a="12.2.0",service_b="1.3.4"} 1.0
```

And a section like this for the storage module:
```
# HELP storage_bucket_availability Indicates if the target bucket is available
# TYPE storage_bucket_availability gauge
storage_bucket_availability{access_key="mkMfCRMp8GpwZwXzkJbp",name="example-bucket-0000",storage_provider_url="http://example-s3-endpoint.com"} 1.0
# HELP storage_size_bucket The total size in bytes of all files in a bucket
# TYPE storage_size_bucket gauge
storage_size_bucket{access_key="mkMfCRMp8GpwZwXzkJbp",name="example-bucket-0000",storage_provider_url="http://example-s3-endpoint.com"} 1.188575e+06
# HELP storage_file_count_bucket The total number of files in a bucket
# TYPE storage_file_count_bucket gauge
storage_file_count_bucket{access_key="mkMfCRMp8GpwZwXzkJbp",name="example-bucket-0000",storage_provider_url="http://example-s3-endpoint.com"} 10003.0
# HELP storage_size_folder The total size in bytes of all files in a folder
# TYPE storage_size_folder gauge
storage_size_folder{access_key="mkMfCRMp8GpwZwXzkJbp",bucket="example-bucket-0000",name="testfiles_10k/",storage_provider_url="http://example-s3-endpoint.com"} 140000.0
storage_size_folder{access_key="mkMfCRMp8GpwZwXzkJbp",bucket="example-bucket-0000",name="testfiles_1mb/",storage_provider_url="http://example-s3-endpoint.com"} 1.048575e+06
# HELP storage_file_count_folder The total number of files in a folder
# TYPE storage_file_count_folder gauge
storage_file_count_folder{access_key="mkMfCRMp8GpwZwXzkJbp",bucket="example-bucket-0000",name="testfiles_10k/",storage_provider_url="http://example-s3-endpoint.com"} 10000.0
storage_file_count_folder{access_key="mkMfCRMp8GpwZwXzkJbp",bucket="example-bucket-0000",name="testfiles_1mb/",storage_provider_url="http://example-s3-endpoint.com"} 1.0
```
And a section like this for the ionosmaintenance module:
```
# HELP in_hoster_maintenance_window Cluster or one of the nodepools is in maintenance window
# TYPE in_hoster_maintenance_window gauge
in_hoster_maintenance_window{cluster="example-cluster-1"} 0.0
in_hoster_maintenance_window{cluster="example-cluster-2"} 0.0
```
And a section like this for the plannedmaintenance module:
```
# HELP planned_maintenance_window Platform is in planned maintenance window
# TYPE planned_maintenance_window gauge
planned_maintenance_window{platform="exampleplatform-1"} 0.0
planned_maintenance_window{platform="exampleplatform-2"} 1.0
```

And a section like this for the uptimekumamaintenance module:
```
# HELP uptime_kuma_maintenance_active 1 if any monitor is in a scheduled maintenance window, else 0
# TYPE uptime_kuma_maintenance_active gauge
uptime_kuma_maintenance_active 1.0
```