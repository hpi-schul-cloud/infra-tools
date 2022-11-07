'''
Module for a class that queries a s3 bucket for their size and the number of files to provide them as Prometheus Gauge Metrics
'''
from datetime import datetime, timedelta
import logging
import os
from time import sleep
import threading
from prometheus_client import Gauge
import boto3


class StorageMetricsThreading(object):
    '''
    Module to get metrics about an object storage
    '''
    def __init__(self):
        self.storage_interval = int(os.getenv("STORAGE_INTERVAL"))
        self.storage_exclude_subfolders = True if os.getenv("STORAGE_EXCLUDE_SUBFOLDERS").lower() == 'true' else False
        self.storage_provider_url = os.getenv("STORAGE_PROVIDER_URL")
        self.storage_provider_region = os.getenv("STORAGE_PROVIDER_REGION")
        self.storage_bucket_name = os.getenv("STORAGE_BUCKET_NAME")
        self.storage_access_key = os.getenv("STORAGE_ACCESS_KEY")
        self.storage_access_secret = os.getenv("STORAGE_ACCESS_SECRET")

        logging.info("Connecting with Access Key {} to S3 region {} by using the storage provider url: {}".format(self.storage_access_key, self.storage_provider_region, self.storage_provider_url))
        logging.info("Fetching S3 bucket metrics every {} seconds".format(self.storage_interval))
        logging.info("Exclude subfolders when generating metrics: {}".format(self.storage_exclude_subfolders))

        self.s3_client = boto3.client(
            's3',
            region_name=self.storage_provider_region,
            aws_access_key_id=self.storage_access_key,
            aws_secret_access_key=self.storage_access_secret,
            endpoint_url=self.storage_provider_url,
        )

        buckets = self.s3_client.list_buckets()['Buckets']
        logging.debug("For Access Key {} available S3 Buckets: {}".format(self.storage_access_key, buckets))

        self.bucket_availability_gauge = Gauge('storage_bucket_availability','Indicates if the target bucket is available',[
            'name',
            'storage_provider_url',
            'access_key',
        ])

        self.size_bucket_gauge = Gauge('storage_size_bucket','The total size in bytes of all files in a bucket',[
            'name',
            'storage_provider_url',
            'access_key',
        ])

        self.file_count_bucket_gauge = Gauge('storage_file_count_bucket','The total number of files in a bucket',[
            'name',
            'storage_provider_url',
            'access_key',
        ])

        self.size_folder_gauge = Gauge('storage_size_folder','The total size in bytes of all files in a folder',[
            'name',
            'bucket',
            'storage_provider_url',
            'access_key',
        ])

        self.file_count_folder_gauge = Gauge('storage_file_count_folder','The total number of files in a folder',[
            'name',
            'bucket',
            'storage_provider_url',
            'access_key',
        ])

        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        '''
        Function that calls metric functions and waits in a loop until the stop event is send from the main thread
        '''
        while True:
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=self.storage_interval)
            self.fetchStorageMetrics()
            if datetime.now() < end_time:
                remaining_time = end_time - datetime.now()
                logging.info("Wait for {} until the next fetching".format(remaining_time))
                sleep(remaining_time.seconds)

    def fetchStorageMetrics(self):
        '''
        Function that calls the S3 API to fetch all objects in a bucket and calculates the total number of objects and the total size for the whole bucket and for each folder
        '''
        incomplete = True
        marker = ""
        total_keys = 0
        total_size = 0
        object_list = []
        folder_list = []

        logging.info("Start fetching the object list of bucket {}".format(self.storage_bucket_name))
        while incomplete:
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.storage_bucket_name,
                    ContinuationToken=marker,
                    FetchOwner=False,
                )
                key_count = response['KeyCount']
                total_keys += key_count
                if key_count == 0:
                    incomplete = False
                else:
                    marker = response.get('NextContinuationToken')
                    incomplete = response['IsTruncated']
                    object_list = [*object_list, *response['Contents']]
            except Exception as ex:
                logging.error("The bucket {} is not available".format(self.storage_bucket_name))
                self.bucket_availability_gauge.labels(
                    name=self.storage_bucket_name,
                    storage_provider_url=self.storage_provider_url,
                    access_key=self.storage_access_key,
                ).set(0.0)
                return

        logging.debug("The total number of keys in the bucket {} is {}".format(self.storage_bucket_name, total_keys))
        logging.info("The total number of objects in the bucket {} is {}".format(self.storage_bucket_name, len(object_list)))
        self.bucket_availability_gauge.labels(
            name=self.storage_bucket_name,
            storage_provider_url=self.storage_provider_url,
            access_key=self.storage_access_key,
        ).set(1.0)

        # Remove folder objects from object_list because files can be in folders by adding a slash to the path without the folders themselfes existing as objects in the bucket
        file_list = [obj for obj in object_list if obj['Key'].endswith('/') == False]

        for file in file_list:
            total_size += file['Size']
            file_path_parts = file['Key'].split('/')

            # if subfolders should be excluded, add just the top-level folder, else, add also every subfolder
            deepest_folder_level = min(len(file_path_parts),2) - 2 if self.storage_exclude_subfolders == True else len(file_path_parts) - 2
            for current_folder_level in range(deepest_folder_level, -1, -1):
                folder_name = ""
                for sub_current_folder_level in range(0, current_folder_level + 1):
                    folder_name += file_path_parts[sub_current_folder_level] + "/"
                if folder_name not in folder_list:
                    folder_list.append(folder_name)

        logging.info("The total number of folders in the bucket {} is {}".format(self.storage_bucket_name, len(folder_list)))
        logging.info("The total number of files in the bucket {} is {}".format(self.storage_bucket_name, len(file_list)))
        logging.info("The total size of all objects in the bucket {} is {}".format(self.storage_bucket_name, total_size))

        self.file_count_bucket_gauge.labels(
            name=self.storage_bucket_name,
            storage_provider_url=self.storage_provider_url,
            access_key=self.storage_access_key,
        ).set(total_keys)

        self.size_bucket_gauge.labels(
            name=self.storage_bucket_name,
            storage_provider_url=self.storage_provider_url,
            access_key=self.storage_access_key,
        ).set(total_size)

        for folder_name in folder_list:
            folder_file_list = [file for file in file_list if folder_name in file['Key']]
            folder_file_count = len(folder_file_list)

            logging.info("The total number of files in the folder {} is {}".format(folder_name, folder_file_count))
            self.file_count_folder_gauge.labels(
                name=folder_name,
                bucket=self.storage_bucket_name,
                storage_provider_url=self.storage_provider_url,
                access_key=self.storage_access_key,
            ).set(folder_file_count)

            folder_size = 0
            for file in folder_file_list:
                folder_size += file['Size']

            logging.info("The size of all files in the folder {} is {}".format(folder_name, folder_size))
            self.size_folder_gauge.labels(
                name=folder_name,
                bucket=self.storage_bucket_name,
                storage_provider_url=self.storage_provider_url,
                access_key=self.storage_access_key,
            ).set(folder_size)

        return
