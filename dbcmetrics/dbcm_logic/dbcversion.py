'''
Modul for a class that query the configured dBildungscloud instances for their known service versions and provide the version via Prometheus compatible metrics.
'''
import logging
from re import I
from time import sleep
import threading, requests, json, urllib.parse
from typing import Dict
from typing import List
from prometheus_client import Gauge, Info
from dbcm_data.configuration import DBCMConfiguration
from dbcm_data.dbcm_instance import DBCMInstance
from dbcm_data.dbcm_version import DBCMVersion, DBCMVersionService, DBCMVersionServices
class VersionMetricsThreading(object):
    '''
    '''
    def __init__(self, configuration: DBCMConfiguration):
        self.configuration = configuration
        # Loop over instances create a Info metrics object for each and store them in a list
        self.pmc_infos: Dict [Info] = {}
        instance: DBCMInstance
        for instance in self.configuration.instances:
            self.pmc_infos[instance.name] = Info(instance.name, 'Version Information')
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        '''
        Function that opens the tunnel and wait in a loop until the stop event is send from the main thread
        '''
        def do_something():
            for i in self.pmc_infos:
                labels: Dict = self.getInstanceVersions(i)
                instance_info: Info = self.pmc_infos[i]
                labels['app_instance'] = i
                labels['dashboard'] = ''
                instance_info.info(labels)
            sleep(self.configuration.version.interval)
        while True:
            do_something()
        
    def getInstanceVersions(self, name):
        # Loop over all services of the give instance, gather the version and store them in the returned dictionary
        labels: Dict = {}
        for service in self.configuration.version.services:
            for skey in service.keys():
                vservice: DBCMVersionService = DBCMVersionService(skey, service[skey])
            instance_url = self.configuration.getInstance(name).url
            fvurl = urllib.parse.urljoin(instance_url, vservice.suffix)
            try:
                url = requests.get(fvurl)
                text = url.text
                data = json.loads(text)
                logging.info("{} version of {} is: {}".format(vservice.name, name, data['version']))
                labels[vservice.name] = data['version']
            except:
                logging.error("Get {} version of {} failed!".format(vservice.name, name))
        return labels
