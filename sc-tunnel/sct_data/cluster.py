from typing import Dict

from sct_common.sctexception import SCTException

class Cluster:
    '''
    Dataclass that stores cluster.
    '''

    clustername: str = None
    # The cluster name. 'infra-dev-admin-1', 'sc-prod-legacy',...


    def __init__(self, clustername):
        '''
        The clustername like 'sv-staging-legacy'.
        '''
        self.clustername = clustername
    def __str__(self):
        return "clustername: " + self.clustername
