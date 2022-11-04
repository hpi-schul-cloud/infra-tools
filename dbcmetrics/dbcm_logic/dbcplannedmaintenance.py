import datetime
import json
import logging
import os
from time import sleep
import threading
import time
from dbcm_common.dbcmexception import DBCMException
from prometheus_client import Gauge
import requests


class PlannedMaintenanceWindowThreading(object):
    def __init__(self, configuration: dict):
        try:
            file_configs = configuration["maintenance_metrics"]
            self.LOADING_INTERVAL_MIN = file_configs["window_refresh_interval_min"] 
            self.METRICS_INTERVAL_SEC = file_configs["metric_refresh_interval_sec"] 
            self.PLANNNED_MAINTENANCE_DEFAULT_DURATION = datetime.timedelta(minutes=file_configs["default_maintenance_duration_min"])
            self.PLATFORMS = file_configs["platforms"]
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
        for platform in self.PLATFORMS:
            try:
                platform_name = platform['name']
                logging.info(f"platform_name = {platform_name}, plattform_url = {platform['url']}")

                url = platform['url'] + "/api/v1/schedules"

                headers = {
                    "accept": "application/json",
                    "X-Cachet-Application": "Demo"
                }

                response = json.loads(requests.get(url, headers=headers).text)

                platform_windows = []
                # Several maintance_entry can exist in response['data'], default is empty List
                for maintance_entry in response['data']:
                    # load and parse data from response

                    try:
                        logging.info(f"Found Mainenance entry in {platform_name}, message: {maintance_entry['message']}")
                    except Exception as e:
                        logging.warning(f"Couldn't load maintenance entry: message on {platform_name} for entry: {maintance_entry}")
                        logging.error(e)


                    try:
                        platform_window_start = self.parse_string_to_datetime(maintance_entry['scheduled_at'])
                    except Exception as e:
                        logging.warning(f"Couldn't load maintenance entry: platform_window_start on {platform_name} for entry: {maintance_entry}")
                        logging.error(e)
                        continue

                    try:
                        platform_window_end = self.parse_string_to_datetime(maintance_entry['completed_at'])    
                    except Exception as e:
                        logging.warning(f"Couldn't load maintenance entry: platform_window_end on {platform_name} for entry: {maintance_entry}")
                        logging.warning(f"platform_window_end is set to platform_window_start + {self.PLANNNED_MAINTENANCE_DEFAULT_DURATION}min")
                        logging.error(e)
                        platform_window_end = platform_window_start + self.PLANNNED_MAINTENANCE_DEFAULT_DURATION

                    
                    logging(f"platform_window_start = {platform_window_start}, platform_window_end = {platform_window_end}")
                    platform_windows.append([platform_window_start,platform_window_end])
                
            
                # set entry in list
                self.windows[platform_name] = platform_windows
                logging.info(f"Saved planned maintenance windows for {platform_name}: {platform_windows}")

            except Exception as e:
                logging.warning(f"Couldn't load/update maintenance window for {platform}")
                logging.error(e)

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

        
    @staticmethod
    def parse_string_to_datetime(datetime_string: str) -> datetime.datetime:
        return datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S') 