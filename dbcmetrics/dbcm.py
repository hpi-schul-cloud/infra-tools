import os, sys
import time
import logging
from typing import List
from prometheus_client import start_http_server
from dbcm_data.configuration import DBCMConfiguration
from dbcm_common.dbcm_config import read_configuration
from dbcm_logic.dbcstorage import StorageMetricsThreading
from dbcm_logic.dbcversion import VersionMetricsThreading
from dbcm_logic.dbcmaintenance import IonosMaintenanceWindowThreading


if __name__ == '__main__':
    loglevel = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)
    dbcm_config = None
    dbcmThreads: List = []
    try:
        if sys.version_info < (3,6):
            print("This script requires at least Python version 3.6")
            sys.exit(1)
        dbcm_config: DBCMConfiguration = read_configuration()
        start_http_server(9000)
        if dbcm_config.features['version_metrics'] == 'enabled':
            vmtr = VersionMetricsThreading(dbcm_config)
            dbcmThreads.append(vmtr)
            logging.info("Version metrics started")
        if os.getenv("STORAGE_METRICS_ENABLED").lower() == 'true':
            smtr = StorageMetricsThreading()
            dbcmThreads.append(smtr)
            logging.info("Storage metrics started")
        if os.getenv("MAINTENANCE_METRICS_ENABLED").lower() == 'true':
            maintenance_metrics_thread = IonosMaintenanceWindowThreading(dbcm_config)
            dbcmThreads.append(maintenance_metrics_thread)
            logging.info("Maintenance window metrics started")
        while True:
            time.sleep(1)
    except Exception as ex:
        logging.exception(ex)
        sys.exit(1)
