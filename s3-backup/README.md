# s3-backup

[s3-backup](https://github.com/hpi-schul-cloud/infra-tools/tree/master/s3-backup)

A tool for the HPI-schul-cloud to backup multiple STRATO S3 Hidrives to a backup STRATO S3 Hidrive using rclone.

# Prerequisites

* One or more STRATO S3 Hidrives as source and a backup target STRATO S3 Hidrives.
* Python 3.6
* [rclone] (https://rclone.org/)

# Installation

* Run 'pip3 install -r requirements.txt' to install the required Python packages.

# Configuration

* Create an s3b_*.yaml file for your backup configuration. You can use the provided s3b_prod.yaml or s3b_test.yaml as example.
** Configure all needed STRATO S3 HiDrives in rclone.conf
** Configure the instances you want to backup
** Add your mail address for error reports

# First run

* Run 's3b-backup.py --help' to print out the command line help.
