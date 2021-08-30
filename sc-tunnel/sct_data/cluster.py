from typing import Dict

from sct_common.sctexception import SCTException

class Cluster:
    '''
    Dataclass that stores cluster.
    '''

    clustername: str = ''
    api_server_host: str = ''
    api_server_port: str = ''
    # The cluster name. 'infra-dev-admin-1', 'sc-prod-legacy',...


    def __init__(self, clustername, api_server_host, api_server_port):
        '''
        The clustername like 'sc-staging-legacy', the hostname of the API server and the port to access the k8s API.
        '''
        self.clustername = clustername
        self.api_server_host = api_server_host
        self.api_server_port = api_server_port

    def __str__(self):
        return "clustername: " + self.clustername
