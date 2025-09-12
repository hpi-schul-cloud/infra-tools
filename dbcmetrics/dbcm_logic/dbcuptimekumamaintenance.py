import os
import datetime
import requests
import time
import logging
import pytz
from prometheus_client import Gauge
from dbcm_common.dbcmexception import DBCMException
from dbcm_common.repeating_thread import RepeatingThread

# A class to handle fetching maintenance windows from uptimekuma and exposing them as metrics.
class UptimeKumaMaintenanceWindowThreading(object):
    # Takes a configuration dictionary with keys like API URL, API key, timezone, etc.
    def __init__(self, config: dict):
        try:
            # Initializes instance variables from the config.
            file_configs = config["uptimekuma_maintenance_metrics"]
            self.API_URL = file_configs["api_url"]
            self.API_KEY = os.getenv("UPTIME_KUMA_API_KEY")
            if self.API_KEY is None:
               logging.error("Missing UPTIME_KUMA_API_KEY environment variable.")
               raise DBCMException
            self.TIMEZONE = pytz.timezone(file_configs["timezone"])
            self.METRIC_REFRESH_INTERVAL = datetime.timedelta(seconds=file_configs["metric_refresh_interval_sec"])
            self.STATUS_PAGE_SLUG = file_configs["status_page_slug"]
        except Exception as e:
            logging.error("Missing or invalid configuration for Uptime Kuma API maintenance metrics.")
            raise DBCMException from e

        # stores maintenance windows.
        self.windows = []
        # Prometheus gauge metric
        self.metric = Gauge(
            "uptime_kuma_maintenance_active",
            "1 if any monitor is in a scheduled maintenance window, else 0"
        )

        # Loads initial data, starts a background thread to refresh metrics periodically.   
        self.load_maintenance_windows()
        self.last_loaded = time.time()

        RepeatingThread(interval=self.METRIC_REFRESH_INTERVAL, name="Metrics Refresh", target=self.run)
        logging.info(f"Uptime Kuma Maintenance Metrics Thread started. UTC Time: {datetime.datetime.utcnow()}")

    # Runs in a loop: Reloads maintenance windows if the interval has passed. Refreshes Prometheus metrics. Sleeps for the configured interval.
    def run(self):
        while True:
            if (time.time() - self.last_loaded) > self.METRIC_REFRESH_INTERVAL.total_seconds():
                self.load_maintenance_windows()
                self.last_loaded = time.time()
            self.refresh_metrics()
            time.sleep(self.METRIC_REFRESH_INTERVAL.total_seconds())

    # Fetches maintenance data from Uptime Kuma API.
    def load_maintenance_windows(self):
        try:
            # Makes an authenticated API call to get the status page data.
            headers = {
                "Authorization": f"Bearer {self.API_KEY}",
                "Accept": "application/json"
            }
            url = f"{self.API_URL}/api/status-page/{self.STATUS_PAGE_SLUG}"
            response = requests.get(url, headers=headers)
            data = response.json()

            self.windows.clear()
            for maintenance in data.get("maintenanceList", []):
                for slot in maintenance.get("timeslotList", []):
                    start = self.parse_datetime(slot["startDate"])
                    end = self.parse_datetime(slot["endDate"])
                    self.windows.append((start, end))
            logging.info(f"Loaded {len(self.windows)} maintenance windows.")
        except Exception as e:
            logging.error("Error loading maintenance windows from API.")
            logging.exception(e)

    # Checks if current time is within any maintenance window and sets the metric accordingly.
    def refresh_metrics(self):
        now = datetime.datetime.now(self.TIMEZONE)
        in_window = any(start <= now <= end for start, end in self.windows)
        self.metric.set(1 if in_window else 0)

    # Converts ISO 8601 string to timezone-aware datetime object
    def parse_datetime(self, dt_str: str) -> datetime.datetime:
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
        return self.TIMEZONE.localize(dt)
