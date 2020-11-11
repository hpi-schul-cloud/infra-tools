from typing import Dict
from typing import List

from s3b_data.instance import Instance
from s3b_data.s3drive import S3Drive
from s3b_data.defect_bucket import DefectBucket
from s3b_data.defect_file import DefectFile

class BackupConfiguration:
    '''
    Dataclass that stores the full backup configuration.
    '''

    instances: Dict[str, Instance] = {}
    # A dictionary that maps instance names to instance objects.

    s3drives: Dict[str, S3Drive] = {}
    # A dictionary that maps s3drive names to s3drive objects.

    defective_buckets: List[DefectBucket] = []
    # These buckets are skipped during backup, because the are defect.

    defective_files: List[DefectFile] = []
    # These files are skipped during backup, because the are defect.

    def __init__(self):
        '''
        
        '''

    def __str__(self):
        # instances
        instances_string = ""
        for instance_name, instance in self.instances.items():
            if len(instances_string) != 0:
                instances_string += ", "
            instances_string += instance.__str__()
        # s3drives
        drives_string = ""
        for s3drive_name, s3drive in self.s3drives.items():
            if len(drives_string) != 0:
                drives_string += ", "
            drives_string += s3drive.__str__()
        # defective_buckets
        defective_buckets_string = ""
        for defective_bucket in self.defective_buckets:
            if len(defective_buckets_string) != 0:
                defective_buckets_string += ", "
            defective_buckets_string += defective_bucket.__str__()
        # defective_files
        defective_files_string = ""
        for defective_file in self.defective_files:
            if len(defective_files_string) != 0:
                defective_files_string += ", "
            defective_files_string += defective_file.__str__()
        return "instances: " + instances_string + ", s3drives: " + drives_string + ", defective_buckets: " + defective_buckets_string + ", defective_files: " + defective_files_string
