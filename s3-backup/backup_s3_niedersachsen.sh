#! /bin/bash

set -e

# One of: boss, open, brabu, international, niedersachsen, thueringen
instance="niedersachsen"
# The name of the bucket that contains all full and incremental backups.
s3_backup_bucket="s3-backup-niedersachsen-sha6cu"
# The name of the drives to backup
declare -a sourcedrives=("hidrivenbc" "hidrivenbc2" "hidrivenbc3" "hidrivenbc4" "hidrivenbc5" "hidrivenbc6" "hidrivenbc7" "hidrivenbc8" "hidrivenbc9" "hidrivenbc10" "hidrivenbc11")
# The name of the backup drive
targetdrive="hidrivenbcbackup"
# Day of month, when the full backup shall run
#backupdayofmonth="19"
backupdayofmonth="00"

source $(dirname "$0")/backup_lib_v3.sh

runbackup

exit 0
