#! /bin/bash

set -e

# One of: boss, open, brabu, international, niedersachsen, thueringen
instance="boss"
# The name of the bucket that contains all full and incremental backups.
s3_backup_bucket="s3-backup-bosscloud-iey9mi"
# The name of the drives to backup
declare -a sourcedrives=("hidrive" "hidrive2" "hidrive3" "hidrive4")
# The name of the backup drive
targetdrive="hidrivebackup"
# Day of month, when the full backup shall run
#backupdayofmonth="01"
# TODO: Disabled OPS-1545 and OPS-1550
backupdayofmonth="00"

source $(dirname "$0")/backup_lib_v3.sh

runbackup

exit 0
