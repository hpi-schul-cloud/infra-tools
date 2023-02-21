'''
Modul for a class that query the configured dBildungscloud instances for their known service versions and provide the version via Prometheus compatible metrics.
'''
import logging
from time import sleep
import threading, requests, json, urllib.parse
from typing import Dict
from typing import List
from dbcm_common.dbcmexception import DBCMException
from prometheus_client import Info
from dbcm_data.dbcm_instance import DBCMInstance

class VersionMetricsThreading(object):

    def __init__(self, configuration_content: dict):
        try:
            version_data = configuration_content['version_metrics']
            self.endpoint = version_data['endpoint']
            self.interval = version_data['interval']
        except:
            logging.error("Missing or wrong 'version_metrics' value in configuration file.")
            raise DBCMException

        try:
            self.instances: List[DBCMInstance] = []
            logging.info("Reading instances:")
            instances_data = configuration_content['instances']
            for instance in instances_data:
                dbcm_instance = DBCMInstance(instance['name'], instance['url'], instance['shortname'])
                self.instances.append(dbcm_instance)
                logging.info(dbcm_instance)
        except:
            logging.error("Missing or wrong 'instances' value in configuration file.")
            raise DBCMException

        label_names = ['app_instance', 'dashboard']
        self.pmc_infos: Info = Info('version', 'Version Information', label_names)
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        while True:
            self.pmc_infos.clear()
            for i in self.instances:
                labels: Dict = self.get_instance_versions(i)
                labels['app_instance'] = i.name
                labels['dashboard'] = 'version_dashboard'
                self.pmc_infos.labels(**labels)
            sleep(self.interval)

    def get_instance_versions(self, instance: DBCMInstance):
        # Get the version info, loop over all entries/components and 
        # if a version exists, store it in the returned dictionary.
        labels: Dict = {}
        try:
            version_url = urllib.parse.urljoin(instance.url, self.endpoint)
            response = requests.get(version_url)
            resp_json = json.loads(response.text)
            for component_name, component_info in resp_json.items():
                if "version" in component_info:
                    version = component_info["version"]
                    labels[component_name] = version
                    logging.info(f"{component_name} version of {instance.name}: {version}")
        except:
                logging.error("Getting versions for {} failed!".format(instance.name))
        return labels
