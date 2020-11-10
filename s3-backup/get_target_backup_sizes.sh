#! /bin/bash
timestamp=$( date +"%Y%m%d_%H%M%S" )
outputfile="${timestamp}_backupsizes.txt"
backupbucket="full-0"

echo "Calculating backup sizes for backup ...${backupbucket} into ${outputfile} for all countries."
echo "This will take a while (20 minutes or more)..."
echo "============================================================================" >> $outputfile
# bosscloud
echo "bosscloud..."
echo "===bosscloud================================================================" >> $outputfile
echo $( date +"%Y%m%d_%H:%M:%S" ) >> $outputfile
rclone size hidrivebackup:/s3-backup-bosscloud-iey9mi/boss-${backupbucket} >> $outputfile
# brandenburg
echo "brandenburg..."
echo "===brandenburg==============================================================" >> $outputfile
echo $( date +"%Y%m%d_%H:%M:%S" ) >> $outputfile
rclone size hidrivebrandenburgbackup:/s3-backup-brabu-ain5ah/brabu-${backupbucket} >> $outputfile
# open
echo "open..."
echo "===open=====================================================================" >> $outputfile
echo $( date +"%Y%m%d_%H:%M:%S" ) >> $outputfile
rclone size hidriveopenbackup:/s3-backup-open-naem9f/open-${backupbucket} >> $outputfile
# international
echo "international..."
echo "===international============================================================" >> $outputfile
echo $( date +"%Y%m%d_%H:%M:%S" ) >> $outputfile
rclone size hidriveinternationalbackup:/s3-backup-international-put9ai/international-${backupbucket} >> $outputfile
# thueringen
echo "thueringen..."
echo "===thueringen===============================================================" >> $outputfile
echo $( date +"%Y%m%d_%H:%M:%S" ) >> $outputfile
rclone size hidrivethueringenbackup:/s3-backup-thueringen-cee2ae/thueringen-${backupbucket} >> $outputfile
# niedersachsen
echo "niedersachsen..."
echo "===niedersachsen============================================================" >> $outputfile
rclone size hidrivenbcbackup:/s3-backup-niedersachsen-sha6cu/niedersachsen-${backupbucket} >> $outputfile
echo "============================================================================" >> $outputfile
echo $( date +"%Y%m%d_%H:%M:%S" ) >> $outputfile
echo "============================================================================" >> $outputfile
echo "Calculating backup sizes for backup ...${backupbucket} into ${outputfile} for all countries. finished."
echo "============================================================================"
