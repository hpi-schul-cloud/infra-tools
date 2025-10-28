import os
import datetime
from zoneinfo import ZoneInfo

from dateutil.parser import parse
import time
import logging
from prometheus_client import Gauge
from uptime_kuma_api import UptimeKumaApi

from dbcm_common.dbcmexception import DBCMException
from dbcm_common.repeating_thread import RepeatingThread


# A class to handle fetching maintenance windows from uptimekuma and exposing them as metrics.
class UptimeKumaMaintenanceWindowThreading(object):
  # Takes a configuration dictionary with keys like API URL, API key, timezone, etc.
  def __init__(self, config: dict):
    try:
      # Initializes instance variables from the config.
      file_configs = config["uptime_kuma_maintenance_metrics"]
      self.LOADING_INTERVAL_MIN = file_configs["window_refresh_interval_min"]
      self.METRICS_INTERVAL = datetime.timedelta(seconds=file_configs["metric_refresh_interval_sec"])

      self.API_URL = file_configs["api_url"]

      # cannot use api key as the socket.io api needed for retrieval of planned maintenance does not support it, cf. https://github.com/louislam/uptime-kuma/issues/3625#issuecomment-1686760395
      self.UPTIME_KUMA_USERNAME = os.getenv("UPTIME_KUMA_USERNAME")
      self.UPTIME_KUMA_PASSWORD = os.getenv("UPTIME_KUMA_PASSWORD")

      if self.UPTIME_KUMA_USERNAME is None or self.UPTIME_KUMA_PASSWORD is None:
        logging.error("Missing uptime kuma credentials")
        raise DBCMException

    except Exception as e:
      logging.error("Missing or invalid configuration for Uptime Kuma API maintenance metrics.")
      raise DBCMException from e

    # stores maintenance windows.
    self.windows = {}
    # stores monitor ids and corresponding names
    self.monitors = {}
    # Prometheus gauge metric
    self.metric = Gauge(
      "uptime_kuma_maintenance_active",
      "1 if any monitor is in a scheduled maintenance window, else 0",
      ["monitor_id", "monitor_name"]
    )

    # Loads initial data, starts a background thread to refresh metrics periodically.
    self.load_maintenance_windows()
    self.last_time_windows_loaded = time.time()

    RepeatingThread(interval=self.METRICS_INTERVAL, name="Metrics Refresh", target=self.run)
    logging.info(f"Uptime Kuma Maintenance Metrics Thread started. UTC Time: {datetime.datetime.now(datetime.UTC)}")

  def run(self):
    if (time.time() - self.last_time_windows_loaded)/60 > self.LOADING_INTERVAL_MIN:
      self.load_maintenance_windows()
      self.last_time_windows_loaded = time.time()
    self.refresh_metrics()

  # Fetches maintenance data from Uptime Kuma API.
  def load_maintenance_windows(self):
    try:
      windows_temp = {}

      with UptimeKumaApi(self.API_URL) as api:
        api.login(self.UPTIME_KUMA_USERNAME, self.UPTIME_KUMA_PASSWORD)

        monitors_temp = {}

        for monitor in api.get_monitors():
          windows_temp[monitor.get("id")] = []
          monitors_temp[monitor.get("id")] = monitor.get("name")

        self.monitors = monitors_temp

        def is_active_and_not_ended(item):
          return item.get("active") and item.get("status") != "ended"

        maintenances = api.get_maintenances()
        filtered_maintenances = list(filter(is_active_and_not_ended, maintenances))

        for maintenance in filtered_maintenances:
          monitors = api.get_monitor_maintenance(maintenance.get("id"))

          for monitor in monitors:
            tz = ZoneInfo(maintenance.get("timezone"))
            for slot in maintenance.get("timeslotList", []):
              start = parse(slot["startDate"])
              end = parse(slot["endDate"])

              if start.tzinfo is None:
                start = start.replace(tzinfo=tz)
              if end.tzinfo is None:
                end = end.replace(tzinfo=tz)

              windows_temp[monitor.get("id")].append((start, end))
            logging.info(f"Loaded {len(windows_temp)} maintenance windows for monitor {monitor.get("id")}.")

        # only set self.windows when all api calls have been successful
        self.windows = windows_temp

    except Exception as e:
      logging.error("Error loading maintenance windows from API.")
      logging.exception(e)

  # Checks if current time is within any maintenance window and sets the metric accordingly.
  def refresh_metrics(self):
    now = datetime.datetime.now(datetime.UTC)

    # Handle cases when monitors are deleted / renamed - accept small probability of metrics being empty on request in favor of shorter code
    self.metric.clear()

    for monitor_id, monitor_windows in self.windows.items():
      monitor_name = self.monitors[monitor_id]
      if any(start <= now <= end for start, end in monitor_windows):
        self.metric.labels(monitor_id=monitor_id,monitor_name=monitor_name).set(1)
      else:
        self.metric.labels(monitor_id=monitor_id,monitor_name=monitor_name).set(0)
