"""
Module for providing Prometheus Gauge Metrics for a s3 bucket (availability, size, number of files)
"""
from datetime import timedelta
import logging
import os
from time import sleep
from dbcm_common.repeating_thread import RepeatingThread
from dbcm_common.dbcmexception import DBCMException
from prometheus_client import Gauge
import boto3


class StorageMetricsThreading(object):

    def __init__(self, configuration: dict):
        try:
            file_configs = configuration["storage_metrics"]
            availability_config = file_configs["availability"]
            stats_config = file_configs["stats"]

            self.URL = file_configs["url"]
            self.REGION = file_configs["region"]
            self.BUCKET_NAME = file_configs["bucket_name"]
            self.AVAILABILITY_ENABLED = availability_config["enabled"].lower() == 'true'
            self.AVAILABILITY_INTERVAL = timedelta(seconds=availability_config["interval_sec"])
            self.STATS_ENABLED = stats_config["enabled"].lower() == 'true'
            self.STATS_INTERVAL = timedelta(minutes=stats_config["interval_min"])
            self.STATS_RETRIES = stats_config["retries"]
            self.STATS_BACKOFF_SEC = stats_config["backoff_sec"]
            self.EXCLUDE_SUBFOLDERS = stats_config["exclude_subfolders"].lower() == 'true'
        except Exception as ex:
            logging.error("Missing or wrong configuration values for storage metrics:{}".format(repr(ex)))
            raise DBCMException

        if not self.AVAILABILITY_ENABLED and not self.STATS_ENABLED:
            logging.error("Neither bucket availability nor stats metrics enabled")
            raise DBCMException

        self.S3_ACCESS_KEY = os.getenv("STORAGE_ACCESS_KEY")
        s3_secret_key = os.getenv("STORAGE_ACCESS_SECRET")

        if self.S3_ACCESS_KEY is None or s3_secret_key is None:
            logging.error("Missing S3 key values for maintenance metrics")
            raise DBCMException

        logging.info("Connecting with Access Key {} to S3 region {} by using the storage provider url: {}"
                     .format(self.S3_ACCESS_KEY, self.REGION, self.URL))
        self.s3_client = boto3.client(
            's3',
            region_name=self.REGION,
            aws_access_key_id=self.S3_ACCESS_KEY,
            aws_secret_access_key=s3_secret_key,
            endpoint_url=self.URL
        )

        if self.AVAILABILITY_ENABLED:
            self.availability_gauge = Gauge('storage_bucket_availability', 'Indicates if the target bucket is available',
                                            ['name', 'storage_provider_url', 'access_key'])
            RepeatingThread(name="Availability Check", interval=self.AVAILABILITY_INTERVAL, target=self.check_availability)

        if self.STATS_ENABLED:
            self.size_bucket_gauge = Gauge('storage_size_bucket', 'The total size in bytes of all files in a bucket',
                                           ['name', 'storage_provider_url', 'access_key'])
            self.file_count_bucket_gauge = Gauge('storage_file_count_bucket', 'The total number of files in a bucket',
                                                 ['name', 'storage_provider_url', 'access_key'])
            self.size_folder_gauge = Gauge('storage_size_folder', 'The total size in bytes of all files in a folder',
                                           ['name', 'bucket', 'storage_provider_url', 'access_key'])
            self.file_count_folder_gauge = Gauge('storage_file_count_folder', 'The total number of files in a folder',
                                                 ['name', 'bucket', 'storage_provider_url', 'access_key'])
            RepeatingThread(name="Bucket Stats Fetching", interval=self.STATS_INTERVAL, target=self.fetch_storage_metrics)

    def check_availability(self):
        try:
            # Check if request for list of objects is successful
            self.s3_client.list_objects_v2(Bucket=self.BUCKET_NAME, FetchOwner=False)['KeyCount']
            self.availability_gauge.labels(name=self.BUCKET_NAME, storage_provider_url=self.URL,
                                           access_key=self.S3_ACCESS_KEY).set(1.0)
        except Exception as ex:
            logging.error("The bucket {} is not available (Cause: {})".format(self.BUCKET_NAME, repr(ex)))
            # To help find the cause of the unavailability list buckets accessible with the given key
            self.list_buckets_for_key()
            self.availability_gauge.labels(name=self.BUCKET_NAME, storage_provider_url=self.URL,
                                           access_key=self.S3_ACCESS_KEY).set(0.0)

    def list_buckets_for_key(self):
        try:
            buckets = self.s3_client.list_buckets()['Buckets']
            logging.info("For Access Key {} available S3 Buckets: {}".format(self.S3_ACCESS_KEY, buckets))
        except Exception as ex:
            logging.error("Couldn't list Buckets for Access Key {} (Cause: {})".format(self.S3_ACCESS_KEY, repr(ex)))

    def fetch_storage_metrics(self):
        """
        Function that calls the S3 API to fetch all objects in a bucket and calculates the total number of objects
        and the total size for the whole bucket and for each folder
        """
        incomplete = True
        continuation_token = ""
        total_keys = 0
        fails = 0
        bucket_stats = BucketStats(exclude_subfolders=self.EXCLUDE_SUBFOLDERS)
        logging.info("Start fetching the object list of bucket {}".format(self.BUCKET_NAME))

        while incomplete:
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.BUCKET_NAME,
                    ContinuationToken=continuation_token,
                    FetchOwner=False,
                )
                key_count = response['KeyCount']
                total_keys += key_count
                if key_count == 0:
                    incomplete = False
                else:
                    continuation_token = response.get('NextContinuationToken')
                    incomplete = response['IsTruncated']
                    for s3_object in response["Contents"]:
                        bucket_stats.add_object(s3_object)
                fails = 0
            except Exception as ex:
                fails += 1
                logging.warning("Listing objects of bucket {} failed {} time(s) (Cause: {})"
                                .format(self.BUCKET_NAME, fails, repr(ex)))
                if fails <= self.STATS_RETRIES:
                    logging.warning("Trying again in {} seconds.".format(self.STATS_BACKOFF_SEC))
                    sleep(self.STATS_BACKOFF_SEC)
                else:
                    logging.error("Max retries reached. Stopping this bucket stats run.".format(self.STATS_BACKOFF_SEC))
                    return

        logging.debug("The total number of keys in the bucket {} is {}".format(self.BUCKET_NAME, total_keys))
        self.output_bucket_stats(bucket_stats)

    def output_bucket_stats(self, bucket_stats):
        for folder_name, stats in bucket_stats.folder_stats:
            file_count = stats["file_count"]
            folder_size = stats["size"]
            logging.info("The total number of files in the folder {} is {}".format(folder_name, file_count))
            self.file_count_folder_gauge.labels(name=folder_name, bucket=self.BUCKET_NAME, storage_provider_url=self.URL,
                                                access_key=self.S3_ACCESS_KEY).set(file_count)
            logging.info("The size of all files in the folder {} is {}".format(folder_name, folder_size))
            self.size_folder_gauge.labels(name=folder_name, bucket=self.BUCKET_NAME, storage_provider_url=self.URL,
                                          access_key=self.S3_ACCESS_KEY).set(folder_size)

        logging.info("The total number of folders in the bucket {} is {}"
                     .format(self.BUCKET_NAME, len(bucket_stats.folder_stats)))
        logging.info("The total number of files in the bucket {} is {}".format(self.BUCKET_NAME, bucket_stats.file_count))
        self.file_count_bucket_gauge.labels(name=self.BUCKET_NAME, storage_provider_url=self.URL,
                                            access_key=self.S3_ACCESS_KEY).set(bucket_stats.file_count)
        logging.info("The total size of all objects in the bucket {} is {}".format(self.BUCKET_NAME, bucket_stats.total_size))
        self.size_bucket_gauge.labels(name=self.BUCKET_NAME, storage_provider_url=self.URL,
                                      access_key=self.S3_ACCESS_KEY).set(bucket_stats.total_size)


class BucketStats(object):
    """
    Helper class for calculating and storing the bucket stats
    """
    def __init__(self, exclude_subfolders: bool):
        self.exclude_subfolders = exclude_subfolders
        self.folder_stats = {}
        self.total_size = 0
        self.file_count = 0

    def add_object(self, s3_object: dict):
        # Ignore folder objects because files can be in folders by adding a slash to the path
        # without the folders themselves existing as objects in the bucket
        if s3_object['Key'].endswith('/'):
            return
        file_size = s3_object["Size"]
        self.total_size += file_size
        self.file_count += 1
        file_path_parts = s3_object['Key'].split('/')
        deepest_folder_level = len(file_path_parts) - 2  # File outside of folder: Level -1
        if self.exclude_subfolders:
            deepest_folder_level = min(deepest_folder_level, 0)
        # Add stats to folder and all parent folders
        for current_folder_level in range(deepest_folder_level, -1, -1):
            folder_name = ""
            for sub_current_folder_level in range(0, current_folder_level + 1):
                folder_name += file_path_parts[sub_current_folder_level] + "/"
            if folder_name not in self.folder_stats:
                self.folder_stats[folder_name] = {"file_count": 0, "size": 0}
            self.folder_stats[folder_name]["file_count"] += 1
            self.folder_stats[folder_name]["size"] += file_size
