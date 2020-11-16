import os, sys
import yaml
from yaml import load, dump, Loader, FullLoader, Dumper
from typing import Dict
from typing import List

from s3b_common.s3b_tools import get_absolute_path
from s3b_common.s3bexception import S3bException
from s3b_data.instance import Instance
from s3b_data.s3drive import S3Drive
from s3b_data.defect_bucket import DefectBucket
from s3b_data.defect_file import DefectFile
from s3b_data.configuration import BackupConfiguration

def read_configuration(configuration_file):
    '''
    Reads an s3b.yaml configuration file into a BackupConfiguration object and returns the filled data object.
    '''

    configuration_file = get_absolute_path(configuration_file)
    a_yaml_file = open(configuration_file)
    data = load(a_yaml_file, Loader=Loader)['s3_backup_configuration']
    # convert into objects
    configuration = BackupConfiguration()

    # s3drives
    s3drives = {}
    for item in data['s3drives']:
        s3drives[item['drivename']] = S3Drive(item['drivename'], item['backupdrive'])
    configuration.s3drives = s3drives

    # Instances
    instances = {}
    for item in data['instances']:
        s3_source_drives: Dict[str, S3Drive] = {}
        s3_source_drive_names = item['s3_source_drives']
        for s3_source_drive_name in s3_source_drive_names:
            current_s3_source_drive = s3drives[s3_source_drive_name]
            # Check, if this is defined as a backup source
            if current_s3_source_drive.isBackupDrive():
                raise S3bException("The drive %s is flagged as backup drive and cannot be used as source drive." % current_s3_source_drive)
            s3_source_drives[s3_source_drive_name] = current_s3_source_drive
        s3_target_drive = s3drives[item['s3_target_drive']]
        # Check, if this is defined as a backup target
        if not s3_target_drive.isBackupDrive():
            raise S3bException("The drive %s is not flagged as backup drive." % s3_target_drive)
        instances[item['instancename']] = Instance(item['instancename'], item['instancename_short'], s3_source_drives, item['s3_source_bucket_patterns'], s3_target_drive, item['s3_target_backup_bucket'], item['backup_day_of_month'])
    configuration.instances = instances

    # defective buckets
    defective_buckets: List[DefectBucket] = []
    for item in data['defect_buckets']:
        defective_buckets.append(DefectBucket(item['drivename'], item['bucketname']))
    configuration.defective_buckets = defective_buckets

    # defective drives
    defective_files: List[DefectFile] = []
    for item in data['defect_files']:
        defective_files.append(DefectFile(item['drivename'], item['bucketname'], item['filename']))
    configuration.defective_files = defective_files

    return configuration

def get_instance_list_from_instance_names(s3_backup_config, instance_names):
    '''
    Returns a list of Instance objects where the instance names match the names in the given instance_names list.
    The Instance objects are taken from the given configuration.
    '''
    instances: [Instance] = []
    for current_instance_name in instance_names:
        instances.append(s3_backup_config.instances[current_instance_name])
    return instances
