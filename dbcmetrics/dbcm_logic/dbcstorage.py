'''
Module for a class that queries a s3 bucket for their size and the number of files to provide them as Prometheus Gauge Metrics
'''
import logging
import os
from re import I
from time import sleep
import threading, requests, json, urllib.parse
from typing import Dict
from typing import List
from prometheus_client import Gauge, Info
import boto3
from botocore.config import Config


class StorageMetricsThreading(object):
    '''
    Module to get metrics about an object storage
    '''
    def __init__(self):
        self.storage_interval = int(os.getenv("STORAGE_INTERVAL"))
        self.storage_exclude_subfolders = os.getenv("STORAGE_EXCLUDE_SUBFOLDERS").lower()
        self.storage_provider_url = os.getenv("STORAGE_PROVIDER_URL")
        self.storage_provider_region = os.getenv("STORAGE_PROVIDER_REGION")
        self.bucket_name = os.getenv("BUCKET_NAME")
        self.access_key = os.getenv("ACCESS_KEY")
        self.access_secret = os.getenv("ACCESS_SECRET")

        logging.info("Connecting with Access Key {} to S3 region {} by using the storage provider url: {}".format(self.access_key, self.storage_provider_region, self.storage_provider_url))
        logging.info("Exclude subfolders when generating metrics: {}".format(self.storage_exclude_subfolders))

        self.s3_client = boto3.client(
            's3',
            region_name=self.storage_provider_region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.access_secret,
            endpoint_url=self.storage_provider_url,
        )

        buckets = self.s3_client.list_buckets()['Buckets']
        logging.debug("For Access Key {} available S3 Buckets: {}".format(self.access_key, buckets))

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
            self.fetchStorageMetrics()
            sleep(self.storage_interval)

    def fetchStorageMetrics(self):
        '''
        Function that calls the S3 API to fetch all objects in a bucket and calculates the total number of objects and the total size for the whole bucket and for each folder
        '''
        incomplete = True
        marker = ""
        total_keys = 0
        total_size = 0
        objectlist = []

        while incomplete:
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    ContinuationToken=marker,
                    #StartAfter='string',
                    FetchOwner=False,
                    #Prefix='foldername/',
                    )
                total_keys += response['KeyCount']
                marker = response.get('NextContinuationToken')
                incomplete = response['IsTruncated']
                objectlist = [*objectlist, *response['Contents']]
            except Exception as ex:
                logging.error("The bucket {} is not available".format(self.bucket_name))
                self.bucket_availability_gauge.labels(
                    name=self.bucket_name,
                    storage_provider_url=self.storage_provider_url,
                    access_key=self.access_key,
                    ).set(0.0)
                return

        self.bucket_availability_gauge.labels(
            name=self.bucket_name,
            storage_provider_url=self.storage_provider_url,
            access_key=self.access_key,
            ).set(1.0)

        logging.debug("The total number of keys in the bucket {} is {}".format(self.bucket_name, total_keys))
        logging.info("The total number of objects in the bucket {} is {}".format(self.bucket_name, len(objectlist)))
        self.file_count_bucket_gauge.labels(
            name=self.bucket_name,
            storage_provider_url=self.storage_provider_url,
            access_key=self.access_key,
            ).set(total_keys)

        if(self.storage_exclude_subfolders == 'true'):
            folders = [object for object in objectlist if object['Key'].endswith('/') and object['Key'].count('/') == 1]
        else:
            folders = [object for object in objectlist if object['Key'].endswith('/')]
        
        logging.info("The total number of folders in the bucket {} is {}".format(self.bucket_name, len(folders)))
        logging.info("The total number of files in the bucket {} is {}".format(self.bucket_name, len(objectlist) - len(folders)))

        for folder in folders:
            folder_name = folder['Key']
            files = [object for object in objectlist if object['Key'].startswith(folder_name)]
            folder_file_count = len(files)-1

            logging.info("The total number of files in the folder {} is {}".format(folder_name, folder_file_count))
            self.file_count_folder_gauge.labels(
                name=folder_name,
                bucket=self.bucket_name,
                storage_provider_url=self.storage_provider_url,
                access_key=self.access_key,
                ).set(folder_file_count)

            folder_size = 0
            for file in files:
                folder_size += file['Size']
            
            logging.info("The size of all files in the folder {} is {}".format(folder_name, folder_size))
            self.size_folder_gauge.labels(
                name=folder_name,
                bucket=self.bucket_name,
                storage_provider_url=self.storage_provider_url,
                access_key=self.access_key,
                ).set(folder_size)

            total_size += folder_size

        logging.info("The total size of all objects in the bucket {} is {}".format(self.bucket_name, total_size))
        self.size_bucket_gauge.labels(
            name=self.bucket_name,
            storage_provider_url=self.storage_provider_url,
            access_key=self.access_key,
            ).set(total_size)

        return
