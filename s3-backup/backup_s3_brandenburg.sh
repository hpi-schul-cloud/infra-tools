#! /bin/bash

set -e

# One of: boss, open, brabu, international, niedersachsen, thueringen
instance="brabu"
# The name of the bucket that contains all full and incremental backups.
s3_backup_bucket="s3-backup-brabu-ain5ah"
# The name of the drives to backup
declare -a sourcedrives=("hidrivebrandenburg" "hidrivebrandenburg2" "hidrivebrandenburg3" "hidrivebrandenburg4" "hidrivebrandenburg5")
# The name of the backup drive
targetdrive="hidrivebrandenburgbackup"
# Day of month, when the full backup shall run
#backupdayofmonth="13"
# TODO: Disabled OPS-1545 and OPS-1550
backupdayofmonth="00"

source $(dirname "$0")/backup_lib_v3.sh

runbackup

exit 0
