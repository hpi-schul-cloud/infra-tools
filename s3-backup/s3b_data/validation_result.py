import logging
from typing import Dict
from s3b_common.s3bexception import S3bException
from s3b_common.s3b_tools import sizeof_fmt

class BucketInfo:
    drivename = None
    # The drive name like 'hidrive' or 'hidrivebrandenburgbackup'.

    path = None
    # The path like '/s3-backup-brabu-ain5ah/brandenburg-full-1
    # This may contain the backup-bucket name!
    # On source drives this is just '/'.

    bucket_to_backup = None
    # The the bucket to backup. Like 'bucket-3984747367'.
    # This is the primary identifier of a BucketInfo object.

    size_in_bytes = -1
    # Accumulated size of all objects in the bucket in bytes

    object_count = -1
    # Accumulated number of objects in the bucket

    def __init__(self, bucket_to_backup):
        self.bucket_to_backup = bucket_to_backup

    def get_full_path(self):
        return self.drivename + ':' + self.path + '/' + self.bucket_to_backup

    def __str__(self):
        return "drivename: " + str(self.drivename) + ", path: " + str(self.path) + ", bucket_to_backup: " + str(self.bucket_to_backup) + ", size_in_bytes: " + str(self.size_in_bytes) + ", object_count: " + str(self.object_count)

class BucketCompare:
    source_bucket_info: BucketInfo = None
    target_bucket_info: BucketInfo = None

    def is_buckets_equal(self):
        if self.source_bucket_info == None and self.target_bucket_info == None:
            # Equal, but no bucket info
            return True
        elif self.source_bucket_info != None and self.target_bucket_info == None:
            if self.source_bucket_info.size_in_bytes == 0:
                # Source does exist, but is empty.
                return True
            else:
                # Target does not exist and source exists and is not empty
                return False
        elif self.source_bucket_info == None and self.target_bucket_info != None:
            if self.target_bucket_info.size_in_bytes == 0:
                # Target exists, but is empty.
                return True
            else:
                # Source does not exist and target exists and is not empty
                return False
        else:
            # Compare content
            if self.source_bucket_info.size_in_bytes != self.target_bucket_info.size_in_bytes:
                # Size mismatch
                return False
            if self.source_bucket_info.object_count != self.target_bucket_info.object_count:
                # Object count mismatch
                return False
            return True

    def get_difference_info(self):
        if self.source_bucket_info == None and self.target_bucket_info == None:
            # Equal, but no bucket info
            return None
        elif self.source_bucket_info != None and self.target_bucket_info == None:
            if self.source_bucket_info.size_in_bytes == 0:
                # Source does exist, but is empty.
                return None
            else:
                # Target does not exist and source exists and is not empty
                return "Target does not exist, but source exists and contains data."
        elif self.source_bucket_info == None and self.target_bucket_info != None:
            if self.target_bucket_info.size_in_bytes == 0:
                # Target exists, but is empty.
                return None
            else:
                # Source does not exist and target exists and is not empty
                return "Source does not exist, but target exists and contains data."
        else:
            # Compare content
            difference = ""
            if self.source_bucket_info.size_in_bytes != self.target_bucket_info.size_in_bytes:
                # Size mismatch
                missing_bytes = self.source_bucket_info.size_in_bytes - self.target_bucket_info.size_in_bytes
                missing_bytes_human_readable = sizeof_fmt(missing_bytes)
                difference += "Size difference: %s " % missing_bytes_human_readable
            if self.source_bucket_info.object_count != self.target_bucket_info.object_count:
                # Object count mismatch
                object_difference = self.source_bucket_info.object_count - self.target_bucket_info.object_count
                difference += "Object count difference: %s" % object_difference
            return difference
        

class ValidationResult:
    '''
    Dataclass that stores information about validation results.
    '''
    bucket_infos: Dict[str, BucketCompare] = {}
    # Maps bucket names to BucketCompare objects.

    def __init__(self):
        pass

    def set_source_bucket_info(self, source_bucket_info):
        bucket_compare = self.bucket_infos.get(source_bucket_info.bucket_to_backup)
        if bucket_compare == None:
            bucket_compare = BucketCompare()
            bucket_compare.source_bucket_info = source_bucket_info
            self.bucket_infos[source_bucket_info.bucket_to_backup] = bucket_compare
        else:
            if bucket_compare.source_bucket_info != None:
                raise S3bException('Cannot set source bucket. The source bucket is already set.')
            bucketCompare.source_bucket_info = source_bucket_info

    def set_target_bucket_info(self, target_bucket_info):
        bucket_compare = self.bucket_infos.get(target_bucket_info.bucket_to_backup)
        if bucket_compare == None:
            bucket_compare = BucketCompare()
            bucket_compare.target_bucket_info = target_bucket_info
            self.bucket_infos[target_bucket_info.bucket_to_backup] = bucket_compare
        else:
            if bucket_compare.target_bucket_info != None:
                raise S3bException('Cannot set target bucket. The target bucket is already set.')
            bucket_compare.target_bucket_info = target_bucket_info
    
    def compare(self):
        differences_found = 0
        for bucket_to_backup, backup_compare in self.bucket_infos.items():
            if not backup_compare.is_buckets_equal():
                differences_found += 1
                differences_info = backup_compare.get_difference_info()
                logging.warning("Source and target buckets are different: '%s', difference: '%s', Source: '%s', Target: '%s'" % (bucket_to_backup, differences_info, backup_compare.source_bucket_info, backup_compare.target_bucket_info))
        if differences_found > 0:
            logging.warning("Buckets different: %s" % (differences_found))
        else:
            logging.info("All buckets are equal concerning size and object count.")
