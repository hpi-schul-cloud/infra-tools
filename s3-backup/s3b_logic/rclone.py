import logging
import json
import pathlib
from datetime import datetime, date, time
from s3b_common import s3b_logging

from s3b_common.s3bexception import S3bException
from s3b_common.s3b_config import get_instance_list_from_instance_names
from s3b_common.run_command import run_command_get_output, run_command, run_command_no_output
from s3b_data.instance import Instance
from s3b_data.s3drive import S3Drive

def run_backup(s3_backup_config, instance_names_to_backup, dailyincrement, syncfull, validate, force, whatif):
    '''
    Main method to start backups. Dailyincrement, syncfull and validation may be executed in one go.
    '''

    logging.info("Running backup. Instances: '%s', syncfull: '%s', dailyincrement: '%s', validate: '%s', force: '%s'" % (instance_names_to_backup, syncfull, dailyincrement, validate, force))
    if dailyincrement:
        run_backup_dailyincrement(s3_backup_config, instance_names_to_backup, whatif)
    if syncfull:
        run_backup_syncfull(s3_backup_config, instance_names_to_backup, force, whatif)
    if validate:
        run_backup_validate(s3_backup_config, instance_names_to_backup, whatif)

def run_backup_syncfull(s3_backup_config, instance_names_to_backup, force, whatif):
    '''
    Starts a syncfull backup.
    '''
    instance_list = get_instance_list_from_instance_names(s3_backup_config, instance_names_to_backup)
    backup_set_id = get_backup_set_id()
    # For each instance
    for current_instance in instance_list:
        create_target_backup_bucket(current_instance.s3_target_drive.drivename, current_instance.s3_target_backup_bucket, whatif)
        # For each drive in the instance
        for current_s3drive_name, current_s3drive in current_instance.s3_source_drives.items():
            source_bucket_list = evaluate_source_bucket_list(current_s3drive.drivename, current_instance.s3_source_bucket_patterns)
            # For each bucket on the drive in the instance, rclone it
            for current_bucket_to_backup in source_bucket_list:
                run_backup_syncfull_for_single_bucket(current_s3drive.drivename, current_bucket_to_backup, current_instance.s3_target_drive.drivename, current_instance.s3_target_backup_bucket, current_instance.instancename, backup_set_id, whatif)

def run_backup_dailyincrement(s3_backup_config, instance_names_to_backup, whatif):
    '''
    Starts a daily incremental backup.
    '''
    instance_list = get_instance_list_from_instance_names(s3_backup_config, instance_names_to_backup)
    backup_set_datestamp = get_backup_set_datestamp()
    # For each instance
    for current_instance in instance_list:
        create_target_backup_bucket(current_instance.s3_target_drive.drivename, current_instance.s3_target_backup_bucket, whatif)
        # For each drive of the instance
        for current_s3drive_name, current_s3drive in current_instance.s3_source_drives.items():
            source_bucket_list = evaluate_source_bucket_list(current_s3drive.drivename, current_instance.s3_source_bucket_patterns)
            # For each bucket on the drive of the instance, rclone it
            for current_bucket_to_backup in source_bucket_list:
                run_backup_dailyincrement_for_single_bucket(current_s3drive.drivename, current_bucket_to_backup, current_instance.s3_target_drive.drivename, current_instance.s3_target_backup_bucket, current_instance.instancename, backup_set_datestamp, whatif)

def run_backup_validate(s3_backup_config, instance_names_to_backup, whatif):
    '''
    Starts a backup validation for a syncfull backup.
    '''
    instance_list = get_instance_list_from_instance_names(s3_backup_config, instance_names_to_backup)
    backup_set_id = get_backup_set_id()
    # For each instance
    for current_instance in instance_list:
        # For each drive of the instance
        for current_s3drive_name, current_s3drive in current_instance.s3_source_drives.items():
            source_bucket_list = evaluate_source_bucket_list(current_s3drive.drivename, current_instance.s3_source_bucket_patterns)
            # For each bucket on the drive of the instance, validate it
            for current_bucket_to_backup in source_bucket_list:
                validate_backup_syncfull_for_single_bucket(current_s3drive.drivename, current_bucket_to_backup, current_instance.s3_target_drive.drivename, current_instance.s3_target_backup_bucket, current_instance.instancename, backup_set_id, whatif)

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
    logging.info("Creating the target backup bucket. '%s'" % rcloneParameters[0])
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.info("Running command: '%s'" % ' '.join(command))
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
    logging.info("Running command: '%s'" % ' '.join(command))
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
            logging.info("Skipping bucket. No match of pattern '%s' to path '%s'" % (patterns, path_to_check))
            continue
        logging.info("Including bucket. One of pattern '%s' matches '%s'" % (patterns, path_to_check))
        source_bucket_list.append(source_bucket_info.get('Path'))
    return source_bucket_list

def run_backup_syncfull_for_single_bucket(source_drivename, bucket_to_backup, target_drivename, target_backup_bucket, backup_set_instancename, backup_set_id, whatif):
    '''
    Runs a syncfull backup for a single bucket.
    '''
    # Old Bash command: rclone sync -v --create-empty-src-dirs ${sourcedrive}:${bucket_to_backup} ${targetdrive}:${s3_backup_bucket}/${instance}-full-${month_moduo2}/${bucket_to_backup}
    rcloneCommand = ['rclone']
    rcloneSubCommand = ['sync']
    #rcloneOptions = ['--verbose', '--create-empty-src-dirs', '--use-server-modtime']
    rcloneOptions = ['--create-empty-src-dirs']
    if whatif:
        rcloneOptions.append('--dry-run')
    rcloneLogOption = ['--log-file=' + s3b_logging.logFilename]
    rcloneParameters = [source_drivename + ':' + bucket_to_backup, target_drivename + ':' + target_backup_bucket + '/' + backup_set_instancename + '-full-' + backup_set_id + '/' + bucket_to_backup]
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.info("Running command: '%s'" % ' '.join(command))
    run_command_no_output(command)

def get_backup_set_id():
    '''
    Returns a backup set id that is calculated from the current month. Even month: 0, Uneven month: 1
    '''
    dt = datetime.now()
    #dt = date(2020, 1, 1)
    #dt = date(2020, 2, 1)
    backup_set_id = str(int(dt.strftime("%m"))%2)
    logging.info("Backup_set_id: '%s'", backup_set_id)
    return backup_set_id

def run_backup_dailyincrement_for_single_bucket(source_drivename, bucket_to_backup, target_drivename, target_backup_bucket, backup_set_instancename, backup_set_datestamp, whatif):
    '''
    Runs a daily incremental backup for a single bucket.
    '''
    # Old Bash command: rclone copy --max-age 25h --create-empty-src-dirs --exclude-from /root/infra-tools/s3-backup/exclude_from_backup.txt ${sourcedrive}:$current_bucket ${targetdrive}:${s3_backup_bucket}/${datestamp}-${instance}-inc/$current_bucket
    rcloneCommand = ['rclone']
    rcloneSubCommand = ['copy']
    rcloneOptions = ['--verbose', '--max-age', '25h', '--use-server-modtime']
    #rcloneOptions = ['--create-empty-src-dirs']
    if whatif:
        rcloneOptions.append('--dry-run')
    rcloneLogOption = ['--log-file=' + s3b_logging.logFilename]
    rcloneParameters = [source_drivename + ':' + bucket_to_backup, target_drivename + ':' + target_backup_bucket + '/dailyinc/' + backup_set_datestamp + '-' + backup_set_instancename + '-dailyinc/' + bucket_to_backup]
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.info("Running command: '%s'" % ' '.join(command))
    run_command_no_output(command)

def get_backup_set_datestamp():
    '''
    Calculate a backup_set_datestamp from the current date.
    E.g. "2020_10_30"
    '''
    dt = date.today()
    backup_set_datestamp = "%s_%s_%s" % (dt.year, dt.month, dt.day)
    logging.info("Backup_set_datestamp: '%s'", backup_set_datestamp)
    return backup_set_datestamp

def validate_backup_syncfull_for_single_bucket(source_drivename, bucket_to_backup, target_drivename, target_backup_bucket, backup_set_instancename, backup_set_id, whatif):
    '''
    Performs some validation, to check, if backup source and backup target match.
    The main check is the bucket size.
    '''
    # TODO: give some control, which backup set to compare.
    backup_set_id = "0"
    rcloneCommand = ['rclone']
    rcloneSubCommand = ['size']
    #rcloneOptions = ['--verbose', '--use-server-modtime']
    rcloneOptions = ['--json']
    if whatif:
        rcloneOptions.append('--dry-run')
    rcloneLogOption = []
    rcloneParameters = [source_drivename + ':' + bucket_to_backup]
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.info("Running command: '%s'" % ' '.join(command))
    (source_bucket_json_str, error) = run_command_get_output(command)
    source_bucket_infos = json.loads(source_bucket_json_str)

    rcloneParameters = [target_drivename + ':' + target_backup_bucket + '/' + backup_set_instancename + '-full-' + backup_set_id + '/' + bucket_to_backup]
    command = rcloneCommand + rcloneSubCommand + rcloneOptions + rcloneLogOption + rcloneParameters
    logging.info("Running command: '%s'" % ' '.join(command))
    (target_bucket_json_str, error) = run_command_get_output(command)
    target_bucket_infos = json.loads(target_bucket_json_str)

    # TODO: report differences
    logging.info("Source: '%s'" % source_bucket_infos)
    logging.info("Target: '%s'" % target_bucket_infos)

    # TODO: compare timestamps
