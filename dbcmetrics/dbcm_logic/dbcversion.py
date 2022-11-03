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
from dbcm_data.dbcm_version import DBCMVersion

class VersionMetricsThreading(object):

    def __init__(self, configuration_content: dict):
        try:
            version_data = configuration_content['version_metrics']
            self.version = DBCMVersion(version_data['services'], version_data['interval'])
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

        label_names = ['app_instance', 'dashboard'] + list(self.version.services.keys())
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
            sleep(self.version.interval)

    def get_instance_versions(self, instance: DBCMInstance):
        # Loop over all services of the give instance, gather the version and store them in the returned dictionary
        labels: Dict = {}
        for service_name, service_suffix in self.version.services.items():
            instance_url = instance.url
            fvurl = urllib.parse.urljoin(instance_url, service_suffix)
            try:
                url = requests.get(fvurl)
                text = url.text
                data = json.loads(text)
                logging.info("{} version of {} is: {}".format(service_name, instance.name, data['version']))
                labels[service_name] = data['version']
            except:
                logging.error("Get {} version of {} failed!".format(service_name, instance.name))
                labels[service_name] = ""
        return labels
