#! /bin/bash


set -e

# One of: boss, open, brabu, international, niedersachsen, thueringen
instance="international"
# The name of the drives to backup
#declare -a sourcedrives=("hidriveinternational")
#declare -a sourcedrives=("hidriveopen" "hidriveopen2")
#declare -a sourcedrives=("hidrivenbc" "hidrivenbc2" "hidrivenbc3" "hidrivenbc4" "hidrivenbc5" "hidrivenbc6" "hidrivenbc7" "hidrivenbc8" "hidrivenbc9" "hidrivenbc10" "hidrivenbc11")
#declare -a sourcedrives=("hidrivethueringen" "hidrivethueringen2" "hidrivethueringen3" "hidrivethueringen4" "hidrivethueringen5")
#declare -a sourcedrives=("hidrivebrandenburg" "hidrivebrandenburg2" "hidrivebrandenburg3" "hidrivebrandenburg4" "hidrivebrandenburg5")
declare -a sourcedrives=("hidrive" "hidrive2" "hidrive3" "hidrive4")
timestamp=$( date +"%Y%m%d_%H%M%S" )


# Full backup
function evaluate_source_sizes {
	for sourcedrive in ${sourcedrives[@]}; do
		outputfile="${timestamp}_${sourcedrive}_source_sizes.json"
		printf '{\n' >> $outputfile
		echo "$( date +"%Y%m%d_%H:%M:%S" ) Calculating usage on drive ${sourcedrive}"
		printf '\t"sourcedrive": "%s",\n' "${sourcedrive}" >> $outputfile
		printf '\t"sizes": [\n' >> $outputfile
		bucket_array=($( rclone lsd ${sourcedrive}: | grep bucket- | awk '{print $5}' ))
		bucket_array_length=${#bucket_array[@]}
		for (( i=0; i<$bucket_array_length; i++ )); do
			current_bucket=${bucket_array[$i]}
			if [ "${sourcedrive}:${current_bucket}" = "hidrivethueringen3:bucket-5e97b98f4fccb20029058807" ]; then
				echo "================================>>>>>>>>>>>>>>>>"
				echo "================================>>>>>>>>>>>>>>>>"
				echo "================================>>>>>>>>>>>>>>>>"
				echo "================================>>>>>>>>>>>>>>>>"
				echo "================================>>>>>>>>>>>>>>>>"
				echo "================================>>>>>>>>>>>>>>>>"
				echo "================================>>>>>>>>>>>>>>>>"
				continue
			fi
			echo "$( date +"%Y%m%d_%H:%M:%S" ) Bucket $(($i+1)) of ${#bucket_array[@]} ${current_bucket} on ${sourcedrive}"
			printf '\t\t{"bucket": "%s", ' "${current_bucket}" >> $outputfile
			json=$(set -x; rclone size ${sourcedrive}:$current_bucket --json)
			json="${json:1}"
			printf '%s' "$json" >> $outputfile
			if (( $i<$bucket_array_length-1 )); then
				printf ',\n'  >> $outputfile
			else
				printf '\n'  >> $outputfile
			fi
		done
		printf '\t]\n' >> $outputfile
		printf '}\n' >> $outputfile
		python aggregate_source_sizes.py  $outputfile
	done
}

evaluate_source_sizes
