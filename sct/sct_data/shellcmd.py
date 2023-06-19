from typing import Dict

from sct_common.sctexception import SCTException

class ShellCmd:
    '''
    Dataclass that stores command.
    '''
    def __init__(self):
        '''
        The clustername like 'sc-staging-legacy', the hostname of the API server and the port to access the k8s API.
        '''
        self.args = list()

    def addArg(self, arg):
        self.args.append(arg)
