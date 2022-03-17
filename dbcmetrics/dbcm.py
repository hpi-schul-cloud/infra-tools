import os, sys
import random
import time
import logging
import requests, json
from typing import Dict, List
from prometheus_client import start_http_server, Summary
from dbcm_data.configuration import DBCMConfiguration
from dbcm_common.dbcm_config import read_configuration
from dbcm_logic.dbcversion import VersionMetricsThreading

REQUEST_TIME = Summary('request_my_processing_seconds', 'Time spent processing request')
@REQUEST_TIME.time()
def process_request(t):
    time.sleep(t)

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    dbcm_config = None
    dbcmThreads: List = []
    try:
        if sys.version_info < (3,6):
            print("This script requires at least Python version 3.6")
            sys.exit(1)
        dbcm_config: DBCMConfiguration = read_configuration()
        start_http_server(9000)
        if dbcm_config.features['version_metrics'] == 'enabled':
            tr = VersionMetricsThreading(dbcm_config)
            dbcmThreads.append(tr)
            logging.info("Version metrics started")
        while True:
            #while not tr.isUp():
            #    sleep(2)
            process_request(random.random())
    except Exception as ex:
        logging.exception(ex)
        sys.exit(1)
    sys.exit(0)
