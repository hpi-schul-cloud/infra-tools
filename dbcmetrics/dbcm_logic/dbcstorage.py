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
        logging.info("Available S3 Buckets: {}".format(buckets))

        self.bucket_size_gauge = Gauge('bucket_storage_size','The total bucket size',(self.bucket_name))
        self.file_number_gauge = Gauge('number_of_files','The total number of files in a bucket',(self.bucket_name))

        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        '''
        Function that calls metric functions and waits in a loop until the stop event is send from the main thread
        '''
        def do_something():
            self.getSize()
            self.getNumberOfFiles()
            sleep(self.interval)
        while True:
            do_something()
        
    def getSize(self):
        #TODO: Add boto3 size operation request
        bucket_url = 'https://' + self.bucket_name + '.' + self.storage_provider_url

        try:
            #url = requests.get(request_url)
            #text = url.text
            #data = json.loads(text)
            #TODO: Log result of the request
            logging.info("Info")
        except:
            #TODO: Add exception handling
            logging.error("Error!")
        return

    def getNumberOfFiles(self):
        #TODO: Add boto3 number of files request
        return
