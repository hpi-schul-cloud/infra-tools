"""
Module for a class that parses the terraform state in the S3 bucket for the maintenance windows
and provides prometheus metrics, that show whether the clusters are currently in these windows.
"""
import datetime
import json
import logging
import os
from time import sleep
import threading
import time
import boto3
from dbcm_common.dbcmexception import DBCMException
from dbcm_common.repeating_thread import RepeatingThread
from prometheus_client import Gauge

STATEFILE = "terraform.tfstate"


class IonosMaintenanceWindowThreading(object):

    def __init__(self, configuration: dict):
        try:
            file_configs = configuration["maintenance_metrics"]
            self.LOADING_INTERVAL_MIN = file_configs["window_refresh_interval_min"] 
            self.METRICS_INTERVAL = datetime.timedelta(seconds=file_configs["metric_refresh_interval_sec"])
            self.NODEPOOL_MAINTENANCE_DURATION = datetime.timedelta(minutes=file_configs["nodepool_maintenance_duration_min"]) 
            self.CLUSTER_MAINTENANCE_DURATION = datetime.timedelta(minutes=file_configs["cluster_maintenance_duration_min"])
            self.PREFIX = file_configs["s3_stage_directory"] 
            self.S3_ENDPOINT = file_configs["s3_endpoint"] 
            self.S3_BUCKET = file_configs["s3_bucket"] 
        except:
            logging.error("Missing or wrong configuration values for maintenance metrics")
            raise DBCMException

        s3_access_key = os.getenv("TERRAFORM_STATE_S3_ACCESS_KEY")
        s3_secret_key = os.getenv("TERRAFORM_STATE_S3_SECRET_KEY")

        if s3_access_key is None or s3_secret_key is None:
            logging.error("Missing S3 key values for maintenance metrics")
            raise DBCMException

        session = boto3.session.Session()
        self.s3_client = session.client(
          service_name='s3',
          aws_access_key_id=s3_access_key,
          aws_secret_access_key=s3_secret_key,
          endpoint_url= self.S3_ENDPOINT
        )
        self.windows = {}
        self.metric = Gauge("in_hoster_maintenance_window", "Cluster or one of the nodepools is in maintenance window", ["cluster"])
        self.load_maintenance_windows()
        self.last_time_windows_loaded = time.time()
        # Start Thread
        RepeatingThread(interval=self.METRICS_INTERVAL, name="Metrics Refresh", target=self.run)
        logging.info(f"Hoster Maintenance Metrics Thread started. UTC Time: {datetime.datetime.utcnow()}")

    def run(self):
        if (time.time() - self.last_time_windows_loaded)/60 > self.LOADING_INTERVAL_MIN:
            self.load_maintenance_windows()
            self.last_time_windows_loaded = time.time()
        self.refresh_metrics()

    def refresh_metrics(self):
        for cluster_name, windows in self.windows.items():
            in_window = False
            # Check cluster window(s)
            for cluster_window in windows["cluster"]:
                if self.currently_in_window(cluster_window, self.CLUSTER_MAINTENANCE_DURATION):
                    in_window = True
                    continue
            # Check nodepool window(s)
            for cluster_window in windows["nodepools"]:
                if self.currently_in_window(cluster_window, self.NODEPOOL_MAINTENANCE_DURATION):
                    in_window = True
                    continue
            # Set metric
            if in_window:
                self.metric.labels(cluster=cluster_name).set(1)
            else:
                self.metric.labels(cluster=cluster_name).set(0)

    def load_maintenance_windows(self):
        try:
            response = self.s3_client.list_objects(Bucket=self.S3_BUCKET, Prefix=self.PREFIX, Delimiter='/')
            self.windows = {}
            for subdirectory in response.get("CommonPrefixes"):
                path = subdirectory.get("Prefix")
                cluster_name = path.split("/")[-2]
                tf_path = path + STATEFILE
                try:
                    cluster_window = self.get_maintenance_windows_from_tfstate(tf_path)
                    # Add only if at least one window exists
                    if cluster_window["cluster"] or cluster_window["nodepools"]:
                        self.windows[cluster_name] = cluster_window
                        logging.info(f"Saved maintenance windows for {cluster_name}: {cluster_window}")
                except:
                    logging.error(f"Couldn't load/update maintenance window for {cluster_name}")
        except:
            logging.error(f"Couldn't get list of S3 objects with prefix {self.PREFIX}")

    def get_maintenance_windows_from_tfstate(self, tfstate_path: str) -> dict:
        response = self.s3_client.get_object(Bucket=self.S3_BUCKET, Key=tfstate_path)
        state = json.loads(response['Body'].read().decode("UTF-8"))
        resources = state['resources']
        cluster_windows = []
        nodepool_windows = []
        for res in resources:
            if res.get("type") == "ionoscloud_k8s_cluster":
                cluster_windows.extend(self.get_maintenance_windows_of_module(res))
            elif res.get("type") == "ionoscloud_k8s_node_pool":
                nodepool_windows.extend(self.get_maintenance_windows_of_module(res))
        return {"cluster": cluster_windows, "nodepools": nodepool_windows}

    @staticmethod
    def get_maintenance_windows_of_module(module: dict) -> list:
        return module['instances'][0]["attributes"]["maintenance_window"]

    @staticmethod
    def currently_in_window(window: dict, window_duration: datetime.timedelta) -> bool:
        window_weekday = time.strptime(window["day_of_the_week"], "%A").tm_wday
        window_time = datetime.datetime.strptime(window["time"], "%H:%M:%SZ").time()
        current = datetime.datetime.utcnow()
        start_of_last_window_date = (current.date()                 # Current date
            - datetime.timedelta(days=current.weekday())            # Jump back to Monday
            + datetime.timedelta(days=window_weekday, weeks=-1))    # Go to weekday of the window in the week before
        # Combine date with time to datetime
        start_of_last_window_datetime = datetime.datetime.combine(start_of_last_window_date, window_time)
        # If start_of_last_window_datetime is more than one week ago, we jumped back too far -> add one week
        one_week = datetime.timedelta(weeks=1)
        if current - start_of_last_window_datetime >= one_week:
            start_of_last_window_datetime += one_week
        end_of_window = start_of_last_window_datetime + window_duration

        return start_of_last_window_datetime <= current <= end_of_window
