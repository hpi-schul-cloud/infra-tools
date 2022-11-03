class DBCMInstance:
    '''
    Dataclass that stores the specification about an dbc instance.
    '''

    def __init__(self, name, url, shortname):
        self.name = name
        self.url = url
        self.shortname = shortname

    def __str__(self):
        '''
        Assembles the class member content into a string.
        '''
        # instances
        instance_string = self.name + ": " +  self.url + " (" + self.shortname + ")"
        return "instance: " + instance_string

