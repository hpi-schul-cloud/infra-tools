class DBCMVersion:
    '''
    Dataclass that stores the additional info to get dbc versions.
    '''

    def __init__(self, services: dict, interval: float):
        self.services: dict = services
        self.interval = interval

    def __str__(self):
        '''
        Assembles the class member content into a string.
        '''
        # Services
        services_string = self.services.__str__()
        return "Version: " + services_string

