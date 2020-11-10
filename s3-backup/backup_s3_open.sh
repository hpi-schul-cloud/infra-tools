#! /bin/bash

set -e

# One of: boss, open, brabu, international, niedersachsen, thueringen
instance="open"
# The name of the bucket that contains all full and incremental backups.
s3_backup_bucket="s3-backup-open-naem9f"
# The name of the drives to backup
declare -a sourcedrives=("hidriveopen" "hidriveopen2")
# The name of the backup drive
targetdrive="hidriveopenbackup"
# Day of month, when the full backup shall run
#backupdayofmonth="21"
backupdayofmonth="00"

source $(dirname "$0")/backup_lib_v3.sh

runbackup

exit 0
