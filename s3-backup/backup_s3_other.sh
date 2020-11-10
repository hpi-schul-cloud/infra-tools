#! /bin/bash

set -e

source $(dirname "$0")/backup_lib_v3.sh

# The name of the drives to backup
sourcedrive="hidrive"
# The name of the backup drive
targetdrive="hidrivebackup"
# Day of month, when the full backup shall run
#backupdayofmonth="28"
backupdayofmonth="00"

# The bucket that shall be backed up.
bucket_to_backup="schul-cloud-hpi"
run_single_bucket_backup

# The bucket that shall be backed up.
bucket_to_backup="rocketchat-uploads"
run_single_bucket_backup

exit 0
