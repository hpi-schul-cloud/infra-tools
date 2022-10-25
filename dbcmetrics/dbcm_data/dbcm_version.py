from typing import Dict
from typing import List

class DBCMVersionService:
    '''
    Dataclass that stores the a dbc service to get the version.
    '''

    def __init__(self, name, suffix):
        self.suffix = suffix
        self.name = name

    def __str__(self):
        '''
        Assembles the class member content into a string.
        '''
        service_string = self.name + " (Suffix: " + self.suffix + ")"

class DBCMVersionServices:
    '''
    Dataclass that stores the URL suffixes for the dbc services to get the version.
    '''

    def __init__(self, services: List[DBCMVersionService]):
        self.services = services

    def __str__(self):
        '''
        Assembles the class member content into a string.
        '''
        services_string = ""
        for service in self.services.items():
            if len(services_string) != 0:
                services_string += ", "
            services_string += service.__str__()
        return "Services: " + services_string

class DBCMVersion:
    '''
    Dataclass that stores the additional info to get dbc versions.
    '''

    def __init__(self, services: List, interval: float):
        self.services: List  = services
        self.interval = interval

    def __str__(self):
        '''
        Assembles the class member content into a string.
        '''
        # Services
        services_string = self.services.__str__()
        return "Version: " + services_string

