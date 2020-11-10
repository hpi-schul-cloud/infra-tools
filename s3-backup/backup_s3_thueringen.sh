#! /bin/bash

set -e

# One of: boss, open, brabu, international, niedersachsen, thueringen
instance="thueringen"
# The name of the bucket that contains all full and incremental backups.
s3_backup_bucket="s3-backup-thueringen-cee2ae"
# The name of the drives to backup
declare -a sourcedrives=("hidrivethueringen" "hidrivethueringen2" "hidrivethueringen3" "hidrivethueringen4" "hidrivethueringen5")
# The name of the backup drive
targetdrive="hidrivethueringenbackup"
# Day of month, when the full backup shall run
#backupdayofmonth="23"
# TODO: Full backup disabled OPS-1531
backupdayofmonth="00"


source $(dirname "$0")/backup_lib_v3.sh

runbackup

exit 0
