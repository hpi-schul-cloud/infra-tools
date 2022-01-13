# sct

[sct](https://github.com/hpi-schul-cloud/infra-tools/tree/master/sct) is a tool, that can download IONOS Kubeconfig for available K8S cluster and open a tunnel for accessing the K8S API server.
Additionally this tool can tunnel connections to any other server and port which is not already in use

## Prerequisites

* An account to IONOS datacenter or preloaded Kubernetes config files from IONOS clusters
* SSH Access to a jump host which can connect to the IONOS clusters
* Python 3.6++
* The utility 'hostctl' which is used by sct to set the local host entries. Please note that you need sudo rights for using the tool
* A terminal shell in a Linux operated environment

## Installation

* Run 'pip3 install -r requirements.txt' to install the required Python packages.
* See: https://guumaster.github.io/hostctl/docs/installation/ for the installation of 'hostctl'
* Alternatively one can execute 'make requirements' on the root of the repo

## Configuration

* The tool reads it configuration from a file sct_config.yaml
* A template with description is provided in this folder
* Copy the template to the '.config' folder and fill the values properly
* The values for your IONOS account can also be read from the environment and take precedence over the values of the config file
* The location of the config file can also be specified on the commandline
* The IONOS account is only necessary to update the available Kubernetes config files from IONOS

## First run

* Run 'sct.py --help' to print out the command line help.
## Termination

* The application prints out a 4-digit code that you should use to terminate the application. This ensure that the additonal host entries are deleted. You can verify this by executing 
```bash
hostctl list
```
No additional entries with profile ***sc*** should be visible.