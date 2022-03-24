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
from dbcm_data.dbcm_bucket import DBCMBucket
import boto3
from botocore.config import Config


class StorageMetricsThreading(object):
    '''
    Module to get metrics about an object storage
    '''
    def __init__(self):
        self.interval = int(os.getenv("STORAGE_INTERVAL"))
        self.storage_provider_url = os.getenv("STORAGE_PROVIDER_URL")
        self.bucket_name = os.getenv("BUCKET_NAME")
        self.access_key = os.getenv("ACCESS_KEY")
        self.access_secret = os.getenv("ACCESS_SECRET")

        self.s3_client = boto3.client(
            's3',
            region_name='s3-de-central',
            aws_access_key_id=os.getenv("ACCESS_KEY"),
            aws_secret_access_key=os.getenv("ACCESS_SECRET"),
            endpoint_url=os.getenv("STORAGE_PROVIDER_URL")
        )

        buckets = self.s3_client.list_buckets()['Buckets']
        logging.info("For Access Key {} available S3 Buckets: {}".format(self.access_key, buckets))

        self.size_gauge = Gauge('storage_size','The total size in bytes',[
            'name',
            'type',
            'bucket',
            'storage_provider_url',
            'access_key',
            ])

        self.file_number_gauge = Gauge('storage_number_of_files','The total number of files',[
            'name',
            'type',
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
        def do_something():
            self.fetchStorageMetrics()
            sleep(self.interval)
        while True:
            do_something()

    def fetchStorageMetrics(self):
        '''
        Function that calls the S3 API to fetch all objects in a bucket and calculates the total number of objects and the total size for the whole bucket and for each folder
        '''
        #TODO: Convert to methode that returns the objectlist for reusability
        incomplete = True
        marker = ""
        totalKeys = 0
        totalSize = 0
        objectlist = []
        
        while incomplete:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                ContinuationToken=marker,
                #StartAfter='string',
                FetchOwner=False,
                #Prefix='foldername/',
                )
            totalKeys += response['KeyCount']
            marker = response.get('NextContinuationToken')
            incomplete = response['IsTruncated']
            objectlist = [*objectlist, *response['Contents']]

        logging.debug("The total number of keys in the bucket {} is {}".format(self.bucket_name, totalKeys))
        logging.info("The total number of objects in the bucket {} is {}".format(self.bucket_name, len(objectlist)))
        self.file_number_gauge.labels(
            name=self.bucket_name,
            type='bucket',
            bucket=self.bucket_name,
            storage_provider_url=self.storage_provider_url,
            access_key=self.access_key,
            ).set(totalKeys)

        folders = [object for object in objectlist if object['Key'].endswith('/')]
        logging.info("The total number of folders in the bucket {} is {}".format(self.bucket_name, len(folders)))
        logging.info("The total number of files in the bucket {} is {}".format(self.bucket_name, len(objectlist) - len(folders)))

        for folder in folders:
            foldername = folder['Key']
            files = [object for object in objectlist if object['Key'].startswith(foldername)]

            logging.info("The total number of files in the folder {} is {}".format(foldername, len(files)))
            self.file_number_gauge.labels(
                name=foldername,
                type='folder',
                bucket=self.bucket_name,
                storage_provider_url=self.storage_provider_url,
                access_key=self.access_key,
                ).set(len(files))

            folderSize = 0
            for file in files:
                folderSize += file['Size']
            
            logging.info("The size of all files in the folder {} is {}".format(foldername, folderSize))
            self.size_gauge.labels(
                name=foldername,
                type='folder',
                bucket=self.bucket_name,
                storage_provider_url=self.storage_provider_url,
                access_key=self.access_key,
                ).set(folderSize)

            totalSize += folderSize

        logging.debug("The total size of all objects in the bucket {} is {}".format(self.bucket_name, totalSize))
        self.size_gauge.labels(
            name=self.bucket_name,
            type='bucket',
            bucket=self.bucket_name,
            storage_provider_url=self.storage_provider_url,
            access_key=self.access_key,
            ).set(totalSize)

        return
