import logging
from typing import Dict
from s3b_common.s3bexception import S3bException
from s3b_common.s3b_tools import sizeof_fmt

class BucketInfo:
    '''
    Dataclass to store information about a bucket.
    Typically drive and path are different for backup source and target buckets.
    The 'bucket_to_backup' name is typically equal.

    For a bucket the size and object count can be evaluated and stored in this object.
    '''

    def __init__(self, bucket_to_backup):
        self.drivename = None
        # The drive name like 'hidrive' or 'hidrivebrandenburgbackup'.
        
        self.path = None
        # The path like '/s3-backup-brabu-ain5ah/brandenburg-full-1
        # This may contain the backup-bucket name!
        # On source drives this is just '/'.

        self.bucket_to_backup = bucket_to_backup
        # The the bucket to backup. Like 'bucket-3984747367'.
        # This is the primary identifier of a BucketInfo object.

        self.size_in_bytes = -1
        # Accumulated size of all objects in the bucket in bytes

        self.object_count = -1
        # Accumulated number of objects in the bucket

    def get_full_path(self):
        return self.drivename + ':' + self.path + '/' + self.bucket_to_backup

    def __str__(self):
        return "drivename: " + str(self.drivename) + ", path: " + str(self.path) + ", bucket_to_backup: " + str(self.bucket_to_backup) + ", size_in_bytes: " + str(self.size_in_bytes) + ", object_count: " + str(self.object_count)

class BucketCompare:
    '''
    Dataclass to ease the comparison of two buckets.
    One can add a source and a target bucket.
    Comparison methods for the two added buckets are provided by this class.
    '''

    def __init__(self):
        self.source_bucket_info: BucketInfo = None
        self.target_bucket_info: BucketInfo = None

    def is_buckets_equal(self):
        '''
        Compares the source and target buckets.

        Buckets are equal:
        - if they both exist and size and object count match
        - if one exists and the other has a size of 0 bytes
        '''
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
        '''
        Returns a textual representation of the found differences. 
        This method follows the same equal logic as is_buckets_equal.

        For equal buckets this method returns None.
        For unequal buckets a textual description of the difference is returned.
        '''
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

    def get_size_difference(self):
        '''
        Returns the size difference of the source and target buckets.

        If there is a positive difference, something is missing.
        If there is a negative difference, there is additional data.
        '''
        if self.source_bucket_info == None and self.target_bucket_info == None:
            return 0
        if self.target_bucket_info == None:
            return self.source_bucket_info.size_in_bytes
        if self.source_bucket_info == None:
            return 0 - self.target_bucket_info.size_in_bytes
        size_difference = self.source_bucket_info.size_in_bytes - self.target_bucket_info.size_in_bytes
        return size_difference

    def get_object_count_difference(self):
        '''
        Returns the object count difference of the source and target buckets.

        If there is a positive difference, something is missing.
        If there is a negative difference, there are additional objects.
        '''
        if self.source_bucket_info == None and self.target_bucket_info == None:
            return 0
        if self.target_bucket_info == None:
            return self.source_bucket_info.object_count
        if self.source_bucket_info == None:
            return 0 - self.target_bucket_info.object_count
        object_count_difference = self.source_bucket_info.object_count - self.target_bucket_info.object_count
        return object_count_difference
        
class ValidationResult:
    '''
    Dataclass that stores information about validation results.

    The validation result is typically a collection of BucketCompares for all buckets of an instance.
    '''

    def __init__(self):
        self.bucket_infos: Dict[str, BucketCompare] = {}
        # Maps bucket names to BucketCompare objects.

    def add_source_bucket_info(self, source_bucket_info):
        '''
        Adds the given information about the source bucket.
        The bucket_to_backup name is used as key to match source and target bucket.

        If already added, an exception is thrown.
        '''
        bucket_compare = self.bucket_infos.get(source_bucket_info.bucket_to_backup)
        if bucket_compare == None:
            bucket_compare = BucketCompare()
            bucket_compare.source_bucket_info = source_bucket_info
            self.bucket_infos[source_bucket_info.bucket_to_backup] = bucket_compare
        else:
            if bucket_compare.source_bucket_info != None:
                raise S3bException('Cannot set source bucket. The source bucket is already set.')
            bucketCompare.source_bucket_info = source_bucket_info

    def add_target_bucket_info(self, target_bucket_info):
        '''
        Adds the given information about the target bucket.
        The bucket_to_backup name is used as key to match source and target bucket.
        
        If already added, an exception is thrown.
        '''
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
        '''
        Walks over the added buckets and counts the size or object count differences.
        '''
        differences_found = 0
        size_difference = 0
        object_count_difference = 0
        for bucket_to_backup, backup_compare in self.bucket_infos.items():
            if not backup_compare.is_buckets_equal():
                differences_found += 1
                # Size
                current_size_difference = backup_compare.get_size_difference()
                if current_size_difference > 0:
                    # We count only missing data here. Additional data does not fill this up.
                    size_difference += current_size_difference
                else:
                    logging.warning("Unexpected additional size (counts negative). Did you add something to the defect lists? Bucket: '%s', additional size: '%s'\n\tsource: '%s'\n\ttarget: '%s'" % (bucket_to_backup, current_size_difference, backup_compare.source_bucket_info, backup_compare.target_bucket_info))
                # Object count
                current_object_count_difference = backup_compare.get_object_count_difference()
                if current_object_count_difference > 0:
                    # We count only missing data here. Additional data does not fill this up.
                    object_count_difference += current_object_count_difference
                else:
                    logging.warning("Unexpected additional objects (count negative). Did you add something to the defect lists? Bucket: '%s', additional objects: '%s'\n\tsource: '%s'\n\ttarget: '%s'" % (bucket_to_backup, current_object_count_difference, backup_compare.source_bucket_info, backup_compare.target_bucket_info))
                # Textual output
                differences_info = backup_compare.get_difference_info()
                logging.warning("Source and target buckets are different. Bucket: '%s', difference: '%s', source: '%s', target: '%s'" % (bucket_to_backup, differences_info, backup_compare.source_bucket_info, backup_compare.target_bucket_info))
        if differences_found > 0:
            size_difference_human_readable = sizeof_fmt(size_difference)
            logging.warning("Buckets different: %s, missing objects: %s, missing data: %s bytes (%s)" % (differences_found, object_count_difference, size_difference, size_difference_human_readable))
        else:
            logging.info("All buckets are equal concerning size and object count.")

    def log_statistics(self):
        '''
        Walks over the added buckets and summerizes the size and object counts.
        '''
        source_size_in_bytes_total = 0
        source_object_count_total = 0
        target_size_in_bytes_total = 0
        target_object_count_total = 0
        for bucket_to_backup, backup_compare in self.bucket_infos.items():
            source_bucket_info = backup_compare.source_bucket_info
            # Source
            source_size_in_bytes = None
            source_size_in_bytes_human_readable = None
            source_object_count = None
            source_bucket_full_path = None
            if source_bucket_info:
                source_size_in_bytes = source_bucket_info.size_in_bytes
                source_size_in_bytes_total += source_size_in_bytes
                source_size_in_bytes_human_readable = sizeof_fmt(source_size_in_bytes)
                source_object_count = source_bucket_info.object_count
                source_object_count_total += source_object_count
                source_bucket_full_path = source_bucket_info.get_full_path()
            # Target
            target_bucket_info = backup_compare.target_bucket_info
            target_size_in_bytes = None
            target_size_in_bytes_human_readable = None
            target_object_count = None
            target_bucket_full_path = None
            if target_bucket_info:
                target_size_in_bytes = target_bucket_info.size_in_bytes
                target_size_in_bytes_total += target_size_in_bytes
                target_size_in_bytes_human_readable = sizeof_fmt(target_size_in_bytes)
                target_object_count = target_bucket_info.object_count
                target_object_count_total += target_object_count
                target_bucket_full_path = target_bucket_info.get_full_path()
            logging.info("Bucket: '%s'\n\tsource: %s bytes (%s) %s objects %s\n\ttarget: %s bytes (%s) %s objects %s" % (bucket_to_backup, source_size_in_bytes, source_size_in_bytes_human_readable, source_object_count, source_bucket_full_path, target_size_in_bytes, target_size_in_bytes_human_readable, target_object_count, target_bucket_full_path))
        logging.info("Total:\n\tsource: %s bytes (%s) %s objects\n\ttarget: %s bytes (%s) %s objects" % (source_size_in_bytes_total, sizeof_fmt(source_size_in_bytes_total), source_object_count_total, target_size_in_bytes_total, sizeof_fmt(target_size_in_bytes_total), target_object_count_total))
