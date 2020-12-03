import logging
import json
import pathlib
import io
from datetime import datetime, date, time
from typing import Dict
from s3b_common import s3b_logging

from s3b_common.s3bexception import S3bException
from s3b_common.s3b_config import get_instance_list_from_instance_names
from s3b_common.run_command import run_command_get_output, run_command, run_command_no_output
from s3b_data.instance import Instance
from s3b_data.s3drive import S3Drive
from s3b_data.validation_result import ValidationResult, BucketInfo, BucketCompare

def validate_configuration(s3_backup_config):
    '''
    Validates the configuration of the s3-backup tool against the rclone
    configuration.
    '''
    # Check the drive configuration in rclone. It is a common problem, that the rclone configuration
    # does not provide the needed drives. So we give a nice message here instead of cryptic rclone messages.
    remotes = list_remotes(s3_backup_config)
    for s3drive_name, s3drive in s3_backup_config.s3drives.items():
        if not s3drive.drivename in remotes:
            raise S3bException("Drive '%s' not found in rclone configuration." % s3drive.drivename)

def list_remotes(s3_backup_config):
    '''
    List the remotes configured with rclone.
    '''
    logging.debug("Listing remotes.")
    rcloneCommand = ['rclone']
    rcloneSubCommand = ['listremotes']
    command = rcloneCommand + rcloneSubCommand
    logging.debug("Running command: '%s'" % ' '.join(command))
    (remotes_string, error) = run_command_get_output(command)
    remotes_list = []
    buffer = io.StringIO(remotes_string)
    line = buffer.readline()
    while line:
        line = buffer.readline()
        remote = line.rstrip().rstrip(':')
        remotes_list.append(remote)
    logging.debug("Number of remotes: '%s'", len(remotes_list))
    return remotes_list

def run_backup(s3_backup_config, instance_names_to_backup, dailyincrement, syncfull, validate, force, whatif):
    '''
    Main method to start backups. Dailyincrement, syncfull and validation may be executed in one go.
    '''
    logging.info("Running backup. Instances: '%s', syncfull: '%s', dailyincrement: '%s', validate: '%s', force: '%s', whatif: '%s'" % (instance_names_to_backup, syncfull, dailyincrement, validate, force, whatif))
    current_day_of_month = int(date.today().day)
    if dailyincrement:
        run_backup_dailyincrement(s3_backup_config, instance_names_to_backup, whatif)
    if syncfull:
        run_backup_syncfull(s3_backup_config, instance_names_to_backup, current_day_of_month, force, whatif)
    if validate:
        run_backup_validate(s3_backup_config, instance_names_to_backup, current_day_of_month, force, whatif)
    logging.info("Running backup finished. Instances: '%s', syncfull: '%s', dailyincrement: '%s', validate: '%s', force: '%s', whatif: '%s'" % (instance_names_to_backup, syncfull, dailyincrement, validate, force, whatif))
    
def run_backup_syncfull(s3_backup_config, instance_names_to_backup, current_day_of_month, force, whatif):
    '''
    Starts a syncfull backup.
    '''
    logging.info("======================================================================")
    logging.info("===== Syncfull =======================================================")
    logging.info("======================================================================")
    instance_list = get_instance_list_from_instance_names(s3_backup_config, instance_names_to_backup)
    backup_set_id = get_backup_set_id()
    # For each instance
    #do_skip = True
    for current_instance in instance_list:
        logging.info("===== Syncfull %s =====" % current_instance.instancename)
        # Check, if today is backup_day_of_month or if force is set
        if force:
            pass
        else:
            if current_instance.backup_day_of_month != current_day_of_month:
                logging.info("Skipping syncfull backup. Today: '%s', Backup day: '%s'. Syncfullbackup will happen only on the configured backup day." %(current_day_of_month, current_instance.backup_day_of_month))
                continue

        create_target_backup_bucket(current_instance.s3_target_drive.drivename, current_instance.s3_target_backup_bucket, whatif)
        # For each drive in the instance
        current_drive_number = 1
        for current_s3drive_name, current_s3drive in current_instance.s3_source_drives.items():
            source_bucket_list = evaluate_source_bucket_list(current_s3drive.drivename, current_instance.s3_source_bucket_patterns)
            # For each bucket on the drive in the instance, rclone it
            current_bucket_number = 1
            for current_bucket_to_backup in source_bucket_list:
                logging.info("Drive '%s' of '%s'. Bucket '%s' of '%s'." % (current_drive_number, len(current_instance.s3_source_drives), current_bucket_number, len(source_bucket_list)))
                current_bucket_number += 1
                #if do_skip and current_bucket_to_backup != "bucket-5bfff495a4605400116bf6db":
                #    continue
                #do_skip = False
                if s3_backup_config.is_defective_bucket(current_s3drive_name, current_bucket_to_backup):
                    logging.info("Skipping bucket '%s' on '%s'. The bucket is marked as defective in the configuration." % (current_bucket_to_backup, current_s3drive_name))
                    continue
                defective_file_list = s3_backup_config.get_defective_file_list(current_s3drive_name, current_bucket_to_backup)
                run_backup_syncfull_for_single_bucket(current_s3drive.drivename, current_bucket_to_backup, current_instance.s3_target_drive.drivename, current_instance.s3_target_backup_bucket, current_instance.instancename, backup_set_id, defective_file_list, whatif)
            current_drive_number += 1
    logging.info("===== Syncfull finished ==============================================")

def run_backup_dailyincrement(s3_backup_config, instance_names_to_backup, whatif):
    '''
    Starts a daily incremental backup.
    '''
    logging.info("======================================================================")
    logging.info("===== Daily Increment ================================================")
    logging.info("======================================================================")
    instance_list = get_instance_list_from_instance_names(s3_backup_config, instance_names_to_backup)
    backup_set_datestamp = get_backup_set_datestamp()
    backup_set_datestamp_as_path = get_backup_set_month_datestamp_as_path()
    # For each instance
    for current_instance in instance_list:
        logging.info("===== Daily Increment %s =====" % current_instance.instancename)
        create_target_backup_bucket(current_instance.s3_target_drive.drivename, current_instance.s3_target_backup_bucket, whatif)
        # For each drive of the instance
        current_drive_number = 1
        for current_s3drive_name, current_s3drive in current_instance.s3_source_drives.items():
            source_bucket_list = evaluate_source_bucket_list(current_s3drive.drivename, current_instance.s3_source_bucket_patterns)
            # For each bucket on the drive of the instance, rclone it
            current_bucket_number = 1
            for current_bucket_to_backup in source_bucket_list:
                logging.info("Drive '%s' of '%s'. Bucket '%s' of '%s'." % (current_drive_number, len(current_instance.s3_source_drives), current_bucket_number, len(source_bucket_list)))
                current_bucket_number += 1
                if s3_backup_config.is_defective_bucket(current_s3drive_name, current_bucket_to_backup):
                    logging.info("Skipping bucket '%s' on '%s'. The bucket is marked as defective in the configuration." % (current_bucket_to_backup, current_s3drive_name))
                    continue
                defective_file_list = s3_backup_config.get_defective_file_list(current_s3drive_name, current_bucket_to_backup)
                run_backup_dailyincrement_for_single_bucket(current_s3drive.drivename, current_bucket_to_backup, current_instance.s3_target_drive.drivename, current_instance.s3_target_backup_bucket, current_instance.instancename, backup_set_datestamp, backup_set_datestamp_as_path, defective_file_list, whatif)
            current_drive_number += 1
    logging.info("===== Daily Increment finished =======================================")

def create_target_backup_bucket(drivename, s3_target_backup_bucket, whatif):
    '''
    Creates the backup bucket on the target drive, if it doesn't exist.
    '''
    # Ensure the target bucket exists
    # Old Bash command: rclone mkdir ${targetdrive}:${s3_backup_bucket}
    rcloneCommand = ['rclone']
    rcloneSubCommand = ['mkdir']
    rcloneOptions = []
    if whatif:
        rcloneOptions.append('--dry-run')
    rcloneLogOption = ['--log-file=' + s3b_logging.logFilename]
    rcloneParameters = [drivename + ":" + s3_target_backup_bucket]
    logging.info("Creating the target backup bucket, if it does not exist. '%s'" % rcloneParameters[0])
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.debug("Running command: '%s'" % ' '.join(command))
    run_command(command)
    logging.info("Target backup bucket '%s' created." % rcloneParameters[0])

def evaluate_source_bucket_list(drivename, patterns):
    '''
    Evaluates the list of source buckets that shall be backed up.
    The existing buckets are queried and then compared to the configured bucket names and patterns.
    Whenever there is a match, the bucket is added to the source bucket list.
    '''
    # Get the source buckets
    # Old Bash command: bucket_array=($( rclone lsd ${sourcedrive}: | grep bucket- | awk '{print $5}' ))
    logging.info("Evaluating the source bucket list for drive '%s'." % drivename)
    rcloneCommand = ['rclone']
    rcloneSubCommand = ['lsjson']
    rcloneOptions = []
    rcloneLogOption = ['--log-file=' + s3b_logging.logFilename]
    rcloneParameters = [drivename + ':']
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.debug("Running command: '%s'" % ' '.join(command))
    (source_bucket_json_str, error) = run_command_get_output(command)
    source_bucket_infos = json.loads(source_bucket_json_str)
    source_bucket_list = []
    for source_bucket_info in source_bucket_infos:
        # Only directories
        if source_bucket_info.get('IsDir') == False:
            continue
        # Match the bucket path with the configured pattern
        path_to_check: str = source_bucket_info.get('Path')
        match = False
        for pattern in patterns:
            if pathlib.PurePath(path_to_check).match(pattern):
                match = True
                break
        if not match:
            logging.debug("Skipping bucket. No match of pattern '%s' to path '%s'" % (patterns, path_to_check))
            continue
        logging.debug("Including bucket. One of pattern '%s' matches '%s'" % (patterns, path_to_check))
        source_bucket_list.append(source_bucket_info.get('Path'))
    logging.info("Evaluation of source bucket list for drive '%s' complete. Number of buckets: %s" % (drivename, len(source_bucket_list)))
    return source_bucket_list

def run_backup_syncfull_for_single_bucket(source_drivename, bucket_to_backup, target_drivename, target_backup_bucket, backup_set_instancename, backup_set_id, defective_file_list, whatif):
    '''
    Runs a syncfull backup for a single bucket.
    '''
    source = source_drivename + ':' + bucket_to_backup
    target = target_drivename + ':' + target_backup_bucket + '/' + backup_set_instancename + '-full-' + backup_set_id + '/' + bucket_to_backup
    logging.info("Syncfull backup for '%s'." % source)
    rcloneCommand = ['rclone']
    rcloneSubCommand = ['sync']
    rcloneOptions = ['--create-empty-src-dirs']
    #rcloneOptions.append('--verbose')
    for defective_file in defective_file_list:
        rcloneOptions.append("--exclude")
        rcloneOptions.append(defective_file)
    if whatif:
        rcloneOptions.append('--dry-run')
    rcloneLogOption = ['--log-file=' + s3b_logging.logFilename]
    rcloneParameters = [source, target]
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.debug("Running command: '%s'" % ' '.join(command))
    run_command_no_output(command)
    logging.info("Syncfull backup for '%s' finished." % source)

def get_backup_set_id():
    '''
    Returns a backup set id that is calculated from the current month. Even month: 0, Uneven month: 1
    '''
    dt = datetime.now()
    #dt = date(2020, 1, 1)
    #dt = date(2020, 2, 1)
    backup_set_id = str(int(dt.strftime("%m"))%2)
    logging.debug("Backup_set_id: '%s'", backup_set_id)
    return backup_set_id

def run_backup_dailyincrement_for_single_bucket(source_drivename, bucket_to_backup, target_drivename, target_backup_bucket, backup_set_instancename, backup_set_datestamp, backup_set_datestamp_as_path, defective_file_list, whatif):
    '''
    Runs a daily incremental backup for a single bucket.
    '''
    source = source_drivename + ':' + bucket_to_backup
    target = target_drivename + ':' + target_backup_bucket + '/' + backup_set_instancename + '-dailyinc/' + backup_set_datestamp_as_path + "/" + backup_set_datestamp + '-' + backup_set_instancename + '-dailyinc/' + bucket_to_backup
    logging.info("Daily incremental backup for '%s'." % source)
    rcloneCommand = ['rclone']
    rcloneSubCommand = ['copy']
    rcloneOptions = ['--max-age', '25h', '--use-server-modtime']
    #rcloneOptions.append('--verbose')
    for defective_file in defective_file_list:
        rcloneOptions.append("--exclude")
        rcloneOptions.append(defective_file)
    if whatif:
        rcloneOptions.append('--dry-run')
    rcloneLogOption = ['--log-file=' + s3b_logging.logFilename]
    rcloneParameters = [source, target]
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.debug("Running command: '%s'" % ' '.join(command))
    run_command_no_output(command)
    logging.info("Daily incremental backup for '%s' finished." % source)

def get_backup_set_datestamp():
    '''
    Calculate a backup_set_datestamp from the current date.
    E.g. "2020_10_30"
    '''
    dt = date.today()
    backup_set_datestamp = "%s_%s_%s" % (dt.year, dt.month, dt.day)
    logging.debug("Backup_set_datestamp: '%s'", backup_set_datestamp)
    return backup_set_datestamp

def get_backup_set_month_datestamp_as_path():
    '''
    Calculate a backup_set_datestamp from the current date.
    E.g. "2020/10/30"
    '''
    dt = date.today()
    backup_set_datestamp = "%s/%s" % (dt.year, dt.month)
    logging.debug("Backup_set_datestamp: '%s'", backup_set_datestamp)
    return backup_set_datestamp

def run_backup_validate(s3_backup_config, instance_names_to_backup, current_day_of_month, force, whatif):
    '''
    Starts a backup validation for a syncfull backup.
    '''
    logging.info("======================================================================")
    logging.info("===== Validation =====================================================")
    logging.info("======================================================================")
    validation_results: Dict[str, ValidationResult] = {}
    # Maps instance names to validation results

    instance_list = get_instance_list_from_instance_names(s3_backup_config, instance_names_to_backup)
    backup_set_id = get_backup_set_id()
    # For each instance
    for current_instance in instance_list:
        logging.info("===== Validation %s =====" % current_instance.instancename)
        # Check, if today is backup_day_of_month or if force is set
        if force:
            pass
        else:
            if current_instance.backup_day_of_month != current_day_of_month:
                logging.info("Skipping validation. Today: '%s', Backup day: '%s'. Validation will happen only on the configured backup day." %(current_day_of_month, current_instance.backup_day_of_month))
                continue

        # The validation results for this instance
        validation_result = ValidationResult()
        validation_results[current_instance.instancename] = validation_result

        # On the source side, we look just on the bucket that are configured. 
        # So we can reuse evaluate_source_bucket_list, which delivers the buckets to backup.
        # For each drive of the instance
        current_drive_number = 1
        for current_s3drive_name, current_s3drive in current_instance.s3_source_drives.items():
            source_bucket_list = evaluate_source_bucket_list(current_s3drive.drivename, current_instance.s3_source_bucket_patterns)
            # For each bucket on the drive of the instance, add it to the validation list.
            path = ""
            current_bucket_number = 1
            for current_bucket_to_backup in source_bucket_list:
                logging.info("Drive '%s' of '%s'. Bucket '%s' of '%s'." % (current_drive_number, len(current_instance.s3_source_drives), current_bucket_number, len(source_bucket_list)))
                current_bucket_number += 1
                if s3_backup_config.is_defective_bucket(current_s3drive_name, current_bucket_to_backup):
                    logging.info("Skipping bucket '%s' on '%s'. The bucket is marked as defective in the configuration." % (current_bucket_to_backup, current_s3drive_name))
                    continue
                defective_file_list = s3_backup_config.get_defective_file_list(current_s3drive_name, current_bucket_to_backup)
                source_bucket_info = read_bucket_info(current_s3drive.drivename, path, current_bucket_to_backup, defective_file_list, whatif)
                validation_result.add_source_bucket_info(source_bucket_info)
            current_drive_number += 1

        # On the target side, we read the buckets that exist on the backup bucket.
        backup_drive = current_instance.s3_target_drive.drivename
        backup_path = current_instance.s3_target_backup_bucket + '/' + current_instance.instancename + '-full-' + backup_set_id
        target_bucket_list = read_directory_list(backup_drive, backup_path, whatif)
        for current_bucket_to_backup in target_bucket_list:
            defective_file_list = []
            target_bucket_info = read_bucket_info(current_instance.s3_target_drive.drivename, backup_path, current_bucket_to_backup, defective_file_list, whatif)
            validation_result.add_target_bucket_info(target_bucket_info)

        # Compare the collected bucket information.
        logging.info("===== Validation Statistics %s =====" % current_instance.instancename)
        validation_result.log_statistics()
        logging.info("===== Validation Compare %s ===== "% current_instance.instancename)
        validation_result.compare()
        logging.info("Note that file exclusions do not work with 'rclone size' and may occure as difference here.")
    logging.info("===== Validation finished ============================================")

def read_directory_list(drivename, path, whatif):
    '''
    Reads list of buckets/directories from the given drive and path.
    '''
    logging.debug("Reading directory information drive '%s' and path '%s'." % (drivename, path))
    rcloneCommand = ['rclone']
    rcloneSubCommand = ['lsjson']
    rcloneOptions = []
    if whatif:
        rcloneOptions.append('--dry-run')
    rcloneLogOption = []
    rcloneParameters = [drivename + ':' + path]
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.debug("Running command: '%s'" % ' '.join(command))
    (json_str, error) = run_command_get_output(command)
    directory_infos = json.loads(json_str)
    directory_list = []
    for directory_info in directory_infos:
        # Only directories
        if directory_info.get('IsDir') == False:
            continue
        sub_path: str = directory_info.get('Path')
        directory_list.append(sub_path)
    return directory_list

def read_bucket_info(drivename, path, bucket_to_backup, defective_file_list, whatif):
    '''
    '''
    bucket_info = BucketInfo(bucket_to_backup)
    bucket_info.drivename = drivename
    bucket_info.path = path
    bucket_info.bucket_to_backup = bucket_to_backup
    rcloneCommand = ['rclone']
    rcloneSubCommand = ['size']
    rcloneOptions = ['--json']
    # Unfortunatly excludes do not seem to work.
    # At least the *-https-/ problems cannot be excluded and lead to differences.
    # Stays here until confirmed with normal files.
    for defective_file in defective_file_list:
        rcloneOptions.append("--exclude")
        rcloneOptions.append(defective_file)
    if whatif:
        rcloneOptions.append('--dry-run')
    rcloneLogOption = []
    full_path = bucket_info.get_full_path()
    rcloneParameters = [full_path]
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.debug("Running command: '%s'" % ' '.join(command))
    (bucket_json_str, error) = run_command_get_output(command)
    bucket_info_struct = json.loads(bucket_json_str)
    bucket_info.size_in_bytes = bucket_info_struct['bytes']
    bucket_info.object_count = bucket_info_struct['count']
    return bucket_info
