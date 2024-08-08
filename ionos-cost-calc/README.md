# Prerequisite

- Go 1.18 or higher

# Installation

1. Clone the repo

````go
git clone https://github.com/hpi-schul-cloud/infra-tools/
cd ionos-cost-calc

`````


2. Install Dependencies
	`go mod tidy`


# Configuration

Tool requires a configuration file in YAML format.

*config.yaml*

````yaml
api:
  url: "https://your-prometheus-api-url/api/v1/query_range"
  token: "your-api-token"

queries_by_source:
  source1:
    - metric: "container_cpu_usage_seconds_total"
      timeframe: "1d"
      label: "namespace"
    - metric: "container_memory_usage_bytes"
      timeframe: "1d"
      label: "namespace"
  source2:
    - metric: "container_memory_usage_bytes"
      timeframe: "1d"
      label: "source"

namespaces-tenants:
  - "namespace1"
  - "namespace2"

email:
  from: "your-email@example.com"
  to: "recipient-email@example.com"
  subject: "Monthly Cost Calculation Report"
  smtp_host: "smtp.example.com"
  smtp_port: "587"
  username: "your-email@example.com"
  password: "your-email-password"

`````

# Usage

To run the program, use the following command

`````c
go run cost-calc.go -config ./config.yaml
`````

# Important

always specify in metrics which label it should use, if for example we want to se 
S3 Buckets shares, choose tenant or maybe enviroment Tag, it is important that the
tags are set on the bucket. Ionos-Exporter should export all the tags to prometheus/grafana.

Also important to add sources/cluster which are going to have those namespaces/tenants.
Only the ones in config are going to be taken into calculation for all the shares.

To send E-Mail also fill the example data in config.yaml