#! /bin/bash
# Lists the buckets that are used as backup containers.
# This shall contain:
# 2 full backups.
# 0 to 31 "incremental" backup-buckets since the last full backup. One per day.

echo "Listing buckets in the backup drives."
# bosscloud
echo "===bosscloud================================================================"
rclone lsd hidrivebackup:/s3-backup-bosscloud-iey9mi
# brandenburg
echo "===brandenburg=============================================================="
rclone lsd hidrivebrandenburgbackup:/s3-backup-brabu-ain5ah
# open
echo "===open====================================================================="
rclone lsd hidriveopenbackup:/s3-backup-open-naem9f
# international
echo "===international============================================================"
rclone lsd hidriveinternationalbackup:/s3-backup-international-put9ai
# thueringen
echo "===thueringen==============================================================="
rclone lsd hidrivethueringenbackup:/s3-backup-thueringen-cee2ae
# niedersachsen
echo "===niedersachsen============================================================"
rclone lsd hidrivenbcbackup:/s3-backup-niedersachsen-sha6cu
echo "============================================================================"
echo "Listing buckets finished."
echo "Expected: 2 full backups per country. Multiple incremental backups done each day."
