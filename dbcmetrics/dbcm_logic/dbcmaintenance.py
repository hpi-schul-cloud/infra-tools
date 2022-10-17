'''
Modul for a class that calls the IONOS API for the maintenance window and 
provides a prometheus metric, that shows wether the cluster is currently in that window.
'''
import logging
from time import sleep
import threading
from typing import List
from prometheus_client import Gauge
from dbcm_data.configuration import DBCMConfiguration
import ionoscloud

class IonosMaintenanceWindowThreading(object):

    def __init__(self, configuration: DBCMConfiguration):
        # TODO: Load configuration
        self.configuration = configuration
        configuration = ionoscloud.Configuration(token='YOUR_TOKEN')
        self.api_client = ionoscloud.ApiClient(configuration)
        # TODO: Generate Gauges for monitored Clusters
        self.maintenance_gauges = {} # Gauge('in_maintenance_window', 'Cluster is in IONOS maintenance window')
        # Start Thread
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        while True:
            # TODO: Call API and check window
            if(in_maintenance)
                self.maintenance_gauge.set(1)
            else:
                self.maintenance_gauge.set(0)
            # TODO: wait
            sleep(60)

    def refresh_kubernetes_infos(self, filter):
        kube_api = ionoscloud.KubernetesApi(self.api_client)
        self.clusters: List[ionoscloud.KubernetesCluster] = [x for x in kube_api.k8s_get().items if filter in x.properties.name]


        