import os, sys
import time
import logging
from typing import List
from prometheus_client import start_http_server
from dbcm_common.dbcm_config import read_configuration
from dbcm_logic.dbcstorage import StorageMetricsThreading
from dbcm_logic.dbcversion import VersionMetricsThreading
from dbcm_logic.dbcionosmaintenance import IonosMaintenanceWindowThreading
from dbcm_logic.dbcplannedmaintenance import PlannedMaintenanceWindowThreading
from dbcm_logic.dbcuptimekumamaintenance import UptimeKumaMaintenanceWindowThreading

if __name__ == '__main__':
    loglevel = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)
    dbcmThreads: List = []
    logging.info("DBCMetrics startup")
    try:
        if sys.version_info < (3,6):
            print("This script requires at least Python version 3.6")
            sys.exit(1)
        dbcm_config: dict = read_configuration()
        start_http_server(9000)
        active_modules = 0
        if os.getenv("VERSION_METRICS_ENABLED", default = "false").lower() == 'true':
            vmtr = VersionMetricsThreading(dbcm_config)
            dbcmThreads.append(vmtr)
            logging.info("Version metrics started")
            active_modules += 1
        if os.getenv("STORAGE_METRICS_ENABLED", default = "false").lower() == 'true':
            smtr = StorageMetricsThreading(dbcm_config)
            dbcmThreads.append(smtr)
            logging.info("Storage metrics started")
            active_modules += 1
        if os.getenv("IONOS_MAINTENANCE_METRICS_ENABLED", default = "false").lower() == 'true':
            logging.info("Ionos Maintenance window metrics starting...")
            maintenance_metrics_thread = IonosMaintenanceWindowThreading(dbcm_config)
            dbcmThreads.append(maintenance_metrics_thread)
            logging.info("Ionos Maintenance window metrics started")
            active_modules += 1
        if os.getenv("PLANNED_MAINTENANCE_METRICS_ENABLED", default = "false").lower() == 'true':
            logging.info("Planned Maintenance window metrics starting...")
            planned_maintenance_metrics_thread = PlannedMaintenanceWindowThreading(dbcm_config)
            dbcmThreads.append(planned_maintenance_metrics_thread)
            logging.info("Planned Maintenance window metrics started")
            active_modules += 1
        if os.getenv("UPTIME_KUMA_MAINTENANCE_METRICS_ENABLED", default = "false").lower() == 'true':
            logging.info("Uptimekuma Maintenance window metrics starting...")
            uptime_kuma_maintenance_metrics_thread = UptimeKumaMaintenanceWindowThreading(dbcm_config)
            dbcmThreads.append(uptime_kuma_maintenance_metrics_thread)
            logging.info("Uptimekuma Maintenance window metrics started")
            active_modules += 1
        if active_modules == 0:
            logging.warning("No module is enabled!")
        elif active_modules > 1:
            logging.warning("More than one module enabled!")
        while True:
            time.sleep(1)
    except Exception as ex:
        logging.exception(ex)
        sys.exit(1)
