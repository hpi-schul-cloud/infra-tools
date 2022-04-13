# dbcmetrics

A containerized Python application which exposes sepcial dBildungscloud values as Prometheus metrics. The application can have multiple modules for different values, e.g. a module for the application version of a running dBildungscloud instance or a further module providing the amount of mails in the dBidlungscloud mailboxes
The port where metrics are exposed is currently hard codeed to 9000

The source code can be found in the [dbcmetrics](https://github.com/hpi-schul-cloud/infra-tools/tree/master/dbcmetrics) folder of the infra-tools repository of hpi-schul-cloud on github.

# Configuration

## Config File
A `dbcm_config.yaml` config file will be read either from a global location `/etc/dbcmconfig` or the file path which is specified in a `DBCMCONFIG` environment variable.

### Environment Variables

The following environment variables are read by the dbcmetrics application:
| Name | Description | Example Value |
| ----------- | ----------- | ----------- |
| LOGLEVEL | Optional variable to set the log level (default is `INFO`) | `DEBUG` |
| DBCMCONFIG | Path to the `dbcm_config.yaml` file (default is `/etc/dbcmconfig`) | `./dbcm_config.yaml` |
| STORAGE_METRICS_ENABLED | Enables or disabled the storage monitoring module | `true` |
| STORAGE_INTERVAL | Number of seconds between cycles in which the storage metrics are fetched | `30` |
| STORAGE_PROVIDER_URL | URL of the S3 storage provider | `http://s3-de-central.profitbricks.com` |
| STORAGE_PROVIDER_REGION | Region of the S3 storage provider | `s3-de-central` |
| BUCKET_NAME | The name of the bucket to monitor by the storage module (Secret in Kubernetes) | `infra-dev-bucket-0000` |
| ACCESS_KEY | The Access Key of your Object Storage Key with access to the Bucket (Secret in Kubernetes) | `mkMfCRMp8GpwZwXzkJbp` (random generated) |
| ACCESS_SECRET | The Secret Key of your Object Storage Key with access to the Bucket (Secret in Kubernetes) | `y8R+6P1Je+62xp9QPF7+euO005HbXr95zD/Clztm` (random generated) |

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
                "STORAGE_INTERVAL": "30",
                "STORAGE_PROVIDER_URL": "http://s3-de-central.profitbricks.com",
                "STORAGE_PROVIDER_REGION": "s3-de-central",
                // Secrets in Kubernetes
                "BUCKET_NAME": "<The Name of the Bucket to monitor>",
                "ACCESS_KEY": "<The Access Key of your Object Storage Key with access to the Bucket>",
                "ACCESS_SECRET": "<The Secret Key of your Object Storage Key with access to the Bucket>"
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
    -e STORAGE_INTERVAL="30" `
    -e STORAGE_PROVIDER_URL="http://s3-de-central.profitbricks.com" `
    -e BUCKET_NAME="<The Name of the Bucket to monitor>" `
    -e ACCESS_KEY="<The Access Key of your Object Storage Key with access to the Bucket>" `
    -e ACCESS_SECRET="<The Secret Key of your Object Storage Key with access to the Bucket>" `
    dbcmetrics:latest
```

## As a Helm release on Kubernetes

To install dbcmetrics with helm in your local kubernetes cluster you first need to clone the [infra-schulcloud](https://github.com/hpi-schul-cloud/infra-schulcloud) repository.
Then you need to remove the `charts/dbcmetrics/templates/servicemonitor.yaml` file locally (do not commit this change) because this is a Kubernetes Custom Resource Definition (CRD) that is created by installing the [kube-prometheus stack](https://github.com/prometheus-operator/kube-prometheus) helm chart, so it doesn't exist on your local kubernetes cluster as long as you don't have the kube-prometheus stack installed.

Afterwards you need to create a secret with the name `dbcmetrics-secret` with three key-value pairs

| Key |  Value (Example) |
| ----------- | ----------- |
| BUCKET_NAME | `infra-dev-bucket-0000` |
| ACCESS_KEY | `mkMfCRMp8GpwZwXzkJbp` (random generated) |
| ACCESS_SECRET | `y8R+6P1Je+62xp9QPF7+euO005HbXr95zD/Clztm` (random generated) |

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

Besides the default prometheus metrics you should see on this endpoint a section like this for the version module:
```
# HELP dbildungscloud_info Version Information
# TYPE dbildungscloud_info gauge
dbildungscloud_info{app_instance="dbildungscloud",client="27.12.0",dashboard="version_dashboard",nuxt="27.12.0",server="27.12.0"} 1.0
# HELP brandenburg_info Version Information
# TYPE brandenburg_info gauge
brandenburg_info{app_instance="brandenburg",client="27.12.0",dashboard="version_dashboard",nuxt="27.12.0",server="27.12.0"} 1.0
# HELP niedersachsen_info Version Information
# TYPE niedersachsen_info gauge
niedersachsen_info{app_instance="niedersachsen",client="27.12.0",dashboard="version_dashboard",nuxt="27.12.0",server="27.12.0"} 1.0
```

And a section like this for the storage module:
```
# HELP storage_bucket_availability Indicates if the target bucket is available
# TYPE storage_bucket_availability gauge
storage_bucket_availability{access_key="25d7ba3888a652459ae2",name="infra-dev-bucket-0000",storage_provider_url="http://s3-de-central.profitbricks.com"} 1.0
# HELP storage_size_bucket The total size in bytes of all files in a bucket
# TYPE storage_size_bucket gauge
storage_size_bucket{access_key="25d7ba3888a652459ae2",name="infra-dev-bucket-0000",storage_provider_url="http://s3-de-central.profitbricks.com"} 1.188575e+06
# HELP storage_file_count_bucket The total number of files in a bucket
# TYPE storage_file_count_bucket gauge
storage_file_count_bucket{access_key="25d7ba3888a652459ae2",name="infra-dev-bucket-0000",storage_provider_url="http://s3-de-central.profitbricks.com"} 10003.0
# HELP storage_size_folder The total size in bytes of all files in a folder
# TYPE storage_size_folder gauge
storage_size_folder{access_key="25d7ba3888a652459ae2",bucket="infra-dev-bucket-0000",name="testfiles_10k/",storage_provider_url="http://s3-de-central.profitbricks.com"} 140000.0
storage_size_folder{access_key="25d7ba3888a652459ae2",bucket="infra-dev-bucket-0000",name="testfiles_1mb/",storage_provider_url="http://s3-de-central.profitbricks.com"} 1.048575e+06
# HELP storage_file_count_folder The total number of files in a folder
# TYPE storage_file_count_folder gauge
storage_file_count_folder{access_key="25d7ba3888a652459ae2",bucket="infra-dev-bucket-0000",name="testfiles_10k/",storage_provider_url="http://s3-de-central.profitbricks.com"} 10000.0
storage_file_count_folder{access_key="25d7ba3888a652459ae2",bucket="infra-dev-bucket-0000",name="testfiles_1mb/",storage_provider_url="http://s3-de-central.profitbricks.com"} 1.0
```