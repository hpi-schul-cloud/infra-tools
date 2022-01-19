# dbcmetrics

[dbcmetrics](https://github.com/hpi-schul-cloud/infra-tools/tree/master/dbcmetrics)

A containerized Python application which exposes sepcial dBildungscloud values as Prometheus metrics. The application can have multiple modules for different values, e.g. a module for the application version of a running dBildungscloud instance or a further module providing the amount of mails in the dBidlungscloud mailboxes
The port where metrics are exposed is currently hard codeed to 9000

# Prerequisites

* Python 3.6++

# Installation

* Run 'pip3 install -r requirements.txt' to install the required Python packages.

# Configuration
* A filled config file named dbcm_config.yaml will be read either from a global location '/etc/dbcmconfig' or the file is specified in a environment variable name DBCMCONFIG with fullpath and name of the file,
