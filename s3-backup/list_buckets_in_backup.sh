#! /bin/bash
# Lists the buckets that are currently included in the ...full-0 full backup sets.

timestamp=$( date +"%Y%m%d_%H%M%S" )
outputfile="${timestamp}_buckets_in_backup.txt"
backupbucket="full-0"

echo "Listing files in backup ...${backupbucket} into ${outputfile} for all countries."
echo "This will take a while..."
echo "============================================================================" >> $outputfile
echo $( date +"%Y%m%d_%H:%M:%S" ) >> $outputfile
# bosscloud
echo "===bosscloud================================================================" >> $outputfile
rclone lsf hidrivebackup:/s3-backup-bosscloud-iey9mi/boss-${backupbucket} >> $outputfile
# brandenburg
echo "===brandenburg==============================================================" >> $outputfile
rclone lsf hidrivebrandenburgbackup:/s3-backup-brabu-ain5ah/brabu-${backupbucket} >> $outputfile
# open
echo "===open=====================================================================" >> $outputfile
rclone lsf hidriveopenbackup:/s3-backup-open-naem9f/open-${backupbucket} >> $outputfile
# international
echo "===international============================================================" >> $outputfile
rclone lsf hidriveinternationalbackup:/s3-backup-international-put9ai/international-${backupbucket} >> $outputfile
# thueringen
echo "===thueringen===============================================================" >> $outputfile
rclone lsf hidrivethueringenbackup:/s3-backup-thueringen-cee2ae/thueringen-${backupbucket} >> $outputfile
# niedersachsen
echo "===niedersachsen============================================================" >> $outputfile
rclone lsf hidrivenbcbackup:/s3-backup-niedersachsen-sha6cu/niedersachsen-${backupbucket} >> $outputfile
echo $( date +"%Y%m%d_%H:%M:%S" ) >> $outputfile
echo "============================================================================" >> $outputfile
echo "Listing files in backup ...${backupbucket} into ${outputfile} for all countries finished."
echo "============================================================================"
