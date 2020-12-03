from typing import Dict

from s3b_data.s3drive import S3Drive
from s3b_common.s3bexception import S3bException

class Instance:
    '''
    Dataclass that stores instance information. An instance is one HPI Schul-Cloud 
    application stack running under a uniquely identifiable name. For example
    'niedersachsen' is one instance.

    How the S3 backup of this instance is defined is stored in this class.

    Typically part of the BackupConfiguration.
    '''

    instancename: str = None
    # The full instance name. 'open', 'brandenburg',...

    instancename_short: str = None
    # The abbreviated instance name. 'open', 'brb', ...

    s3_source_drives: Dict[str, S3Drive] = {}
    # The s3drives to backup.
    
    s3_source_bucket_patterns = []
    # Multiple glob patterns or just bucket names that shall be backed up. E.g. 'schul-cloud-hpi' or 'bucket-*'

    s3_target_drive: str = None
    # The s3drive where the backup shall be stored.
    
    s3_target_backup_bucket: str = None
    # The bucket where the backups shall be stored.
    
    backup_day_of_month: int = None
    # The day of the month, when the backup shall run.

    def __init__(self, instancename, instancename_short, s3_source_drives: Dict[str, S3Drive], s3_source_bucket_patterns, s3_target_drive, s3_target_backup_bucket, backup_day_of_month):
        '''
        The instancename like 'brandenburg'.
        The short instancename like 'brb'.
        '''
        self.instancename = instancename
        self.instancename_short = instancename_short
        self.s3_source_drives = s3_source_drives
        self.s3_source_bucket_patterns = s3_source_bucket_patterns
        self.s3_target_drive = s3_target_drive
        self.s3_target_backup_bucket = s3_target_backup_bucket
        self.backup_day_of_month: int = None

        # Validate. Has to be 2 number chars.
        if backup_day_of_month < 0 or backup_day_of_month > 31:
            raise S3bException("backup_day_of_month has to be a positive number lower or equal as 31, but it is '%s'", str(backup_day_of_month))
        self.backup_day_of_month = backup_day_of_month

    def __str__(self):
        return "instancename: " + self.instancename
