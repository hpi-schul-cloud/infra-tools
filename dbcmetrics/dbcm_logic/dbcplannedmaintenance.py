import datetime
import json
import logging
import os
from time import sleep
import threading
import time
from dbcm_common.dbcmexception import DBCMException
from prometheus_client import Gauge


class PlannedMaintenanceWindowThreading(object):
    def __init__(self, configuration: dict):
        try:
            file_configs = configuration["maintenance_metrics"]
            self.LOADING_INTERVAL_MIN = file_configs["window_refresh_interval_min"] 
            self.METRICS_INTERVAL_SEC = file_configs["metric_refresh_interval_sec"] 
        except:
            logging.error("Missing or wrong configuration values for planned maintenance metrics")
            raise DBCMException

        self.windows = {}
        self.metric = Gauge("planned_maintenance_window", "Platform is in planned maintenance window", ["platform"])
        self.load_planned_maintenance_windows()
        self.last_time_windows_loaded = time.time()
        # Start Thread
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        logging.info(f"Planned Maintenance Metrics Thread started. UTC Time: {datetime.datetime.utcnow()}")

    def run(self):
        while True:
            if (time.time() - self.last_time_windows_loaded)/60 > self.LOADING_INTERVAL_MIN:
                self.load_planned_maintenance_windows()
                self.last_time_windows_loaded = time.time()
            self.refresh_metrics()
            sleep(self.METRICS_INTERVAL_SEC)


    def load_planned_maintenance_windows(self):

        # windows is a dict of all platforms e.g.: {"niedersachsen.cloud": [["03.11.2022 13:00","03.11.2022 12:00"]["03.11.2022 13:00","03.11.2022 12:00"]], "next.Platform": ...}
        #                                            platform name          window_start_date      window_end_date   window_start_date  window_end_date       ...
        self.windows = {}
        try:
            cluster_window = self.get_maintenance_windows_from_tfstate(tf_path)
            # Add only if at least one window exists
            if cluster_window["cluster"] or cluster_window["nodepools"]:
                self.windows[cluster_name] = cluster_window
                logging.info(f"Saved maintenance windows for {cluster_name}: {cluster_window}")
        except:
            logging.error(f"Couldn't load/update maintenance window for {cluster_name}")
        


    def refresh_metrics(self):
        for platform_name, plattform_windows in self.windows.items():
            in_window = False
            # Check platform window(s)
            # TODO: window only tuple not dic?
            for platform_window_start, platform_window_end  in plattform_windows:
                if self.currently_in_window(platform_window_start, platform_window_end):
                    in_window = True
                    continue
            # Set metric
            if in_window:
                self.metric.labels(platform=platform_name).set(1)
            else:
                self.metric.labels(platform=platform_name).set(0)


    @staticmethod
    def currently_in_window(platform_window_start: datetime.datetime, platform_window_end: datetime.datetime) -> bool:
        # TODO: Timezone?
        current = datetime.datetime.utcnow()
        # TODO: Validation?
        return platform_window_start <= current <= platform_window_end