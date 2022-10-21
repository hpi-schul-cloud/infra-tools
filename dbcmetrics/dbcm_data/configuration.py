from typing import Dict
from typing import List

from dbcm_data.dbcm_instance import DBCMInstance
from dbcm_data.dbcm_version import DBCMVersionService, DBCMVersionServices, DBCMVersion

class DBCMConfiguration:
    '''
    Dataclass that stores the full backup configuration.
    The data contained here is usually read from a s3b.yaml configuration file.
    See also s3b_common.s3b_config.
    '''

    def __init__(self):
        self.instances: List [DBCMInstance] = []
        # A dictionary that maps cluster names to Cluster objects.

        self.version: DBCMVersion
        self.maintenance: Dict = {}
        self.features: Dict = {}
        
    def __str__(self):
        '''
        Assembles the class member content into a string.
        '''
        # instances
        configuration_string = ""
        for instance in self.instances.items():
            if len(configuration_string) != 0:
                configuration_string += ", "
            configuration_string += instance.__str__()
        for service in self.versionservices.items():
            if len(configuration_string) != 0:
                configuration_string += ", "
            configuration_string += service.__str__()
        return "Configuration: " + configuration_string

    def getInstance(self, name):
        instance: DBCMInstance
        for instance in self.instances:
            if instance.name == name:
                return instance
