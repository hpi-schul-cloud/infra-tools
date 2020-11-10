#! /bin/bash

#: Backups Strato S3 storage.
#: Run "runbackup" to run a backup.
#: There are two full backups that are synced each month alternating.
#: Even months: full-0, uneven months: full-1
#: In between pseudo "incremental". Daily for the last 25 hours.
#: Min retention time is 30 days. Max retention time is 60 days.

# Current date
datestamp=$( date +"%y%m%d" )
# Current day of month
dayofmonth=$( date +"%d" )
# month%2. Toggles between 0 and 1 each month.
month_moduo2=$(( $( date +"%m" )%2 ))
# TODO: For the time being we stick with one backup set until we have one completed.
month_moduo2=1
# Switch to 1 = only show commands executed. Switch to 0 = do the backup.
whatif=0
if [ $whatif == 1 ]; then
	echo "===================================================="
	echo "===================================================="
	echo "=======Simulation only! No backup performed.========"
	echo "===================================================="
	echo "===================================================="
	echo "===================================================="
fi

# Private
# Incremental backup
function incbackup {
	echo '------------------------------------------------------------------------------------------------------------------'
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Daily incremental backup of files with max age 25 hours."
	for sourcedrive in ${sourcedrives[@]}; do
		echo "$( date +"%Y%m%d_%H:%M:%S" ) Incremental backup for drive ${sourcedrive}"
		bucket_array=($( rclone lsd ${sourcedrive}: | grep bucket- | awk '{print $5}' ))
		for i in ${!bucket_array[@]}; do
			current_bucket=${bucket_array[$i]}
			echo "$( date +"%Y%m%d_%H:%M:%S" ) Bucket $(($i+1)) of ${#bucket_array[@]} ${current_bucket} on ${sourcedrive}"
			# TODO: Remove, when OPS-1531 is solved.
			if [ "${sourcedrive}:${current_bucket}" = "hidrivethueringen3:bucket-5e97b98f4fccb20029058807" ]; then
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				echo "================================>>>>>>>>>>>>>>>> Ignoring defective bucket ${sourcedrive}:${current_bucket} <<<<<<<< ========"
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				continue
			fi
			if [ $whatif == 1 ]; then
				echo "rclone copy --max-age 25h --create-empty-src-dirs  --exclude-from /root/backup_s3/exclude_from_backup.txt ${sourcedrive}:$current_bucket ${targetdrive}:${s3_backup_bucket}/${datestamp}-${instance}-inc/$current_bucket"
			else
				(set -x; rclone copy --max-age 25h --create-empty-src-dirs --exclude-from /root/backup_s3/exclude_from_backup.txt ${sourcedrive}:$current_bucket ${targetdrive}:${s3_backup_bucket}/${datestamp}-${instance}-inc/$current_bucket)
			fi
		done
	done
}

# Private
# Full backup
function fullbackup {
	echo '------------------------------------------------------------------------------------------------------------------'
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Running full backup."
	for sourcedrive in ${sourcedrives[@]}; do
		echo "$( date +"%Y%m%d_%H:%M:%S" ) Full backup for drive ${sourcedrive}"
		bucket_array=($( rclone lsd ${sourcedrive}: | grep bucket- | awk '{print $5}' ))
		bucket_array_length=${#bucket_array[@]}
		for (( i=0; i<$bucket_array_length; i++ )); do
			current_bucket=${bucket_array[$i]}
			echo "$( date +"%Y%m%d_%H:%M:%S" ) Bucket $(($i+1)) of ${#bucket_array[@]} ${current_bucket} on ${sourcedrive}"
			# TODO: Remove, when OPS-1531 is solved.
			if [ "${sourcedrive}:${current_bucket}" = "hidrivethueringen3:bucket-5e97b98f4fccb20029058807" ]; then
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				echo "================================>>>>>>>>>>>>>>>> Ignoring defective bucket ${sourcedrive}:${current_bucket} <<<<<<<< ========"
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				echo '=================================================================================================================='
				continue
			fi
			if [ $whatif == 1 ]; then
				echo "rclone sync --create-empty-src-dirs --exclude-from /root/backup_s3/exclude_from_backup.txt ${sourcedrive}:$current_bucket ${targetdrive}:${s3_backup_bucket}/${instance}-full-${month_moduo2}/$current_bucket"
			else
				(set -x; rclone sync -v --create-empty-src-dirs --exclude-from /root/backup_s3/exclude_from_backup.txt ${sourcedrive}:$current_bucket ${targetdrive}:${s3_backup_bucket}/${instance}-full-${month_moduo2}/$current_bucket)
			fi
		done
	done
}

# Public
# Use this method to backup the HPI schul-cloud user data buckets.
# Files stored in buckets that begin with "bucket-" are backed up.
# It creates a daily backup increment of the last 25 hours.
# If today is the defined backupdayofmonth, a full backup sync will be done after the daily backup increment.
function runbackup {
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Backup run for ${instance}."
	# Create the s3-backup-bucket if it does not exist.
	# All full and incremental backups will be stored in that bucket.
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Checking backup bucket."
	if [[ $(rclone lsd ${targetdrive}: ) != *"${s3_backup_bucket}"* ]]; then
		echo "$( date +"%Y%m%d_%H:%M:%S" ) Creating backup bucket on target drive."
		if [ $whatif == 1 ]; then
			echo "rclone mkdir ${targetdrive}:${s3_backup_bucket}"
		else
			(set -x; rclone mkdir ${targetdrive}:${s3_backup_bucket})
		fi
	fi

	# Incremental backup each day.
	#if [[ ("${instance}" == "boss") || ("${instance}" == "brabu")  || ("${instance}" == "thueringen") ]]; then
	#	# Some instances are so big, an incremental backup does not work with the current performance anymore.
	#	# Incremental daily backup disabled  for:
	#	# boss > OPS-1550, performance
	#	# brabu > OPS-1550, performance
	#	# thueringen > OPS-1550, performance
	#	echo "$( date +"%Y%m%d_%H:%M:%S" ) Skipping incremental backup for ${instance}."
	#else
	#	incbackup
	#fi

	# Full backup at a defined day of the month.
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Full backup sync if today is the ${backupdayofmonth}th of this month."
	if [[ ${dayofmonth} = ${backupdayofmonth} ]]
	then
	  fullbackup
	fi
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Backup run for ${instance} finished."
}

# Public
# Use this method to backup a single bucket.
# It creates a daily backup increment of the last 25 hours.
# If today is the defined backupdayofmonth, a full backup sync will be done after the daily backup increment.
function run_single_bucket_backup {
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Running single bucket backup."
	# Parametercheck
	if [ "$backupdayofmonth" = $"" ]; then
		echo "Error. backupdayofmonth not set."
		exit 1
	fi
	if [ "$sourcedrive" = $"" ]; then
		echo "Error. sourcedrive not set."
		exit 1
	fi
	if [ "$bucket_to_backup" = $"" ]; then
		echo "Error. bucket_to_backup not set."
		exit 1
	fi
	if [ "$targetdrive" = $"" ]; then
		echo "Error. targetdrive not set."
		exit 1
	fi
	
	# The name of the bucket that contains the backups.
	s3_backup_bucket="s3-backup-${bucket_to_backup}"
	
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Backup run for bucket ${sourcedrive}:${bucket_to_backup} into ${targetdrive}:${s3_backup_bucket}."
	
	# Create the s3-backup-bucket if it does not exist.
	# All full and incremental backups will be stored in that bucket.
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Checking backup bucket."
	if [[ $(rclone lsd ${targetdrive}: ) != *"${s3_backup_bucket}"* ]]; then
		echo "$( date +"%Y%m%d_%H:%M:%S" ) Creating backup bucket on target drive."
		if [ $whatif == 1 ]; then
			echo "rclone mkdir ${targetdrive}:${s3_backup_bucket}"
		else
			(set -x; rclone mkdir ${targetdrive}:${s3_backup_bucket})
		fi
	fi

	#echo '------------------------------------------------------------------------------------------------------------------'
	#echo "$( date +"%Y%m%d_%H:%M:%S" ) Daily incremental backup of files with max age 25 hours."
	#if [ $whatif == 1 ]; then
	#	echo "rclone copy --max-age 25h --create-empty-src-dirs ${sourcedrive}:${bucket_to_backup} ${targetdrive}:${s3_backup_bucket}/${datestamp}-inc/${bucket_to_backup}"
	#else
	#	(set -x; rclone copy --max-age 25h --create-empty-src-dirs ${sourcedrive}:${bucket_to_backup} ${targetdrive}:${s3_backup_bucket}/${datestamp}-inc/${bucket_to_backup})
	#fi
	
	# Full backup sync.
	echo '------------------------------------------------------------------------------------------------------------------'
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Full backup sync if today is the ${backupdayofmonth}th of this month."
	if [[ ${dayofmonth} = ${backupdayofmonth} ]]
	then
		echo '------------------------------------------------------------------------------------------------------------------'
		echo "$( date +"%Y%m%d_%H:%M:%S" ) Running full backup."
		if [ $whatif == 1 ]; then
			echo "rclone sync --create-empty-src-dirs ${sourcedrive}:${bucket_to_backup} ${targetdrive}:${s3_backup_bucket}/full-${month_moduo2}/${bucket_to_backup}"
		else
			(set -x; rclone sync -v --create-empty-src-dirs ${sourcedrive}:${bucket_to_backup} ${targetdrive}:${s3_backup_bucket}/full-${month_moduo2}/${bucket_to_backup})
		fi
	fi
	
	echo "$( date +"%Y%m%d_%H:%M:%S" ) Backup run for bucket ${sourcedrive}:${bucket_to_backup} into ${targetdrive}:${s3_backup_bucket} finished."
}
