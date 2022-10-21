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
from prometheus_client import Gauge
from dbcm_data.configuration import DBCMConfiguration

BUCKET = "sc-tf-remote-state-01"
STATEFILE = "terraform.tfstate"


class IonosMaintenanceWindowThreading(object):

    def __init__(self, configuration: DBCMConfiguration):
        # TODO: Load configuration
        file_configs = configuration.maintenance
        try:
            self.LOADING_INTERVAL_MIN = file_configs["window_refresh_interval"] # 30
            self.METRICS_INTERVAL_SEC = file_configs["metric_refresh_interval"] # 15
            self.NODEPOOL_MAINTENANCE_DURATION = datetime.timedelta(minutes=file_configs["nodepool_maintenance_duration"]) # datetime.timedelta(minutes=240)
            self.CLUSTER_MAINTENANCE_DURATION = datetime.timedelta(minutes=file_configs["cluster_maintenance_duration"]) # datetime.timedelta(minutes=120)
            self.PREFIX = file_configs["s3_stage_directory"] # "env:/dev/"
        except:
            logging.error("Missing or wrong configuration values for maintenance metrics")
            raise DBCMException

        session = boto3.session.Session()
        self.s3_client = session.client(
          service_name='s3',
          aws_access_key_id=os.getenv("SC_AWS_ACCESS_KEY_ID"),
          aws_secret_access_key=os.getenv("SC_AWS_SECRET_ACCESS_KEY"),
          endpoint_url='https://s3-eu-central-1.ionoscloud.com',
        )
        self.windows = {}
        self.metrics = {}
        self.load_maintenance_windows()
        self.last_time_windows_loaded = time.time()
        # Start Thread
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        while True:
            if (time.time() - self.last_time_windows_loaded)/60 > self.LOADING_INTERVAL_MIN:
                self.refresh_metrics()
                self.last_time_windows_loaded = time.time()
            self.refresh_metrics()
            sleep(self.METRICS_INTERVAL_SEC)

    def refresh_metrics(self):
        for cluster, windows in self.windows.items():
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
                self.metrics[cluster].set(1)
            else:
                self.metrics[cluster].set(0)

    def load_maintenance_windows(self):
        response = self.s3_client.list_objects(Bucket=BUCKET, Prefix=self.PREFIX, Delimiter='/')
        # TODO: Filter clusters?
        self.windows = {}
        self.metrics = {}
        for subdirectory in response.get("CommonPrefixes"):
            path = subdirectory.get("Prefix")
            cluster_name = path.split("/")[-2]
            tf_path = path + STATEFILE
            cluster_window = self.get_maintenance_windows_from_tfstate(tf_path)
            # Add only if at least one window exists
            if cluster_window["cluster"] or cluster_window["nodepools"]:
                if cluster_name not in self.metrics:
                    print("Creating Gauge:", cluster_name.replace("-", "_") + "_in_maintenance")
                    self.metrics[cluster_name] = Gauge(cluster_name.replace("-", "_") + "_in_maintenance",
                                                       "Cluster or one of the nodepools is in maintenance window")
                self.windows[cluster_name] = cluster_window
                print(f"Saved maintenance windows for {cluster_name}")

    def get_maintenance_windows_from_tfstate(self, tfstate_path: str) -> dict:
        response = self.s3_client.get_object(Bucket=BUCKET, Key=tfstate_path)
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
