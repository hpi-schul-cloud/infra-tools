import datetime
import json
import logging
import time
from dbcm_common.repeating_thread import RepeatingThread
from dbcm_common.dbcmexception import DBCMException
from prometheus_client import Gauge
import requests
import pytz
import re


class PlannedMaintenanceWindowThreading(object):
    def __init__(self, configuration: dict):
        try:
            file_configs = configuration["planned_maintenance_metrics"]
            self.LOADING_INTERVAL_MIN = file_configs["window_refresh_interval_min"] 
            self.METRICS_INTERVAL = datetime.timedelta(seconds=file_configs["metric_refresh_interval_sec"])
            self.PLANNNED_MAINTENANCE_DEFAULT_DURATION = int(file_configs["default_maintenance_duration_min"])
            self.PLATFORMS = file_configs["platforms"]
            self.TIMEZONE = pytz.timezone(file_configs["cachet_timezone"])
        except:
            logging.error("Missing or wrong configuration values for planned maintenance metrics")
            raise DBCMException

        self.windows = {}
        self.metric = Gauge("planned_maintenance_window", "Platform is in planned maintenance window", ["platform"])
        self.load_planned_maintenance_windows()
        self.last_time_windows_loaded = time.time()
        # Start Thread
        RepeatingThread(interval=self.METRICS_INTERVAL, name="Metrics Refresh", target=self.run)
        logging.info(f"Planned Maintenance Metrics Thread started. UTC Time: {datetime.datetime.utcnow()}")

    def run(self):
        if (time.time() - self.last_time_windows_loaded)/60 > self.LOADING_INTERVAL_MIN:
            self.load_planned_maintenance_windows()
            self.last_time_windows_loaded = time.time()
        self.refresh_metrics()


    def load_planned_maintenance_windows(self):

        # windows is a dict of all platforms e.g.: {"status.plattform1": [["03.11.2022 13:00","03.11.2022 12:00"]["03.11.2022 13:00","03.11.2022 12:00"]], "next.Platform": ...}
        #                                            platform name          window_start_date      window_end_date   window_start_date  window_end_date       ...

        for platform in self.PLATFORMS:
            try:
                platform_name = platform["name"]
                url = platform["url"] + "/api/v1/schedules"

                logging.info(f"platform_name = {platform_name}, platform_url = {url}")

                headers = {
                    "accept": "application/json"
                }

                response = json.loads(requests.get(url, headers=headers).text)

                platform_windows = []
                # Several maintance_entry may exist in response['data'], default is empty List
                for maintance_entry in response['data']:
                    # load and parse data from response

                    try:
                        logging.info(f"Found Mainenance entry in {platform_name}, title: {maintance_entry['name']}, message: {maintance_entry['message']}")
                    except Exception as e:
                        # Triggered if message field is empty
                        # It is not a requiered field, so code will continue for this entry
                        logging.warning(f"Couldn't load maintenance entry: title or message on {platform_name} for entry: {maintance_entry}")
                        logging.exception(f"\t {e}")


                    try:
                        platform_window_start = self.parse_string_to_datetime(maintance_entry['scheduled_at'])
                    except Exception as e:
                        # Triggered if field for start of platform maintenance window is empty
                        logging.warning(f"Couldn't load maintenance entry: platform_window_start on {platform_name} for entry: {maintance_entry}")
                        logging.exception(f"\t {e}")
                        continue

                    try:
                        message_string: str = maintance_entry['message']

                        regex_result = re.search(r"Dauer:\s*((?P<hours>\d+)\s*h)?\s*((?P<minutes>\d+)\s*m)?", message_string)
                        hours: int  = regex_result.group('hours')
                        minutes: int  = regex_result.group('minutes')

                        if hours is not None:
                            start_to_end_window_hours: int  = int(hours)
                        else:
                            start_to_end_window_hours: int  = 0

                        if minutes is not None:
                            start_to_end_window_min: int  = int(minutes)
                        elif hours is None:
                            start_to_end_window_min: int = self.PLANNNED_MAINTENANCE_DEFAULT_DURATION
                        else:
                            start_to_end_window_min: int  = 0
                    except Exception as e:
                        logging.warning(f"\tCouldn't parse duration for end of maintenance window, using default offset (60 minutes).")
                        start_to_end_window_min: int = self.PLANNNED_MAINTENANCE_DEFAULT_DURATION
                        start_to_end_window_hours: int = 0

                    # Create offset timedelta obj for maintenance duration
                    start_to_end_window_offset = datetime.timedelta(minutes=start_to_end_window_min, hours=start_to_end_window_hours)

                    platform_window_end = platform_window_start + start_to_end_window_offset

                    logging.info(f"\tplatform_window_start = {platform_window_start}, platform_window_end = {platform_window_end}")
                    platform_windows.append([platform_window_start,platform_window_end])

                # set entry in list
                self.windows[platform_name] = platform_windows
                logging.info(f"\tSaved planned maintenance windows for {platform_name}; window count: {len(platform_windows)}")

            except Exception as e:
                logging.warning(f"Couldn't load/update maintenance window for {platform})")
                logging.exception(e)

    def refresh_metrics(self):
        for platform_name, plattform_windows in self.windows.items():
            in_window = False
            for platform_window_start, platform_window_end  in plattform_windows:
                if self.currently_in_window(platform_window_start, platform_window_end):
                    in_window = True
                    continue
            # Set metric
            if in_window:
                self.metric.labels(platform=platform_name).set(1)
            else:
                self.metric.labels(platform=platform_name).set(0)

    def currently_in_window(self, platform_window_start: datetime.datetime, platform_window_end: datetime.datetime) -> bool:

        time_now = datetime.datetime.now(self.TIMEZONE)

        # The formatting is needed for the calculation with time zones
        in_window: bool = platform_window_start.strftime('%Y:%m:%d %H:%M:%S') <= time_now.strftime('%Y:%m:%d %H:%M:%S') <= platform_window_end.strftime('%Y:%m:%d %H:%M:%S')
        return in_window


    @staticmethod
    def parse_string_to_datetime(datetime_string: str) -> datetime.datetime:
        return datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S') 