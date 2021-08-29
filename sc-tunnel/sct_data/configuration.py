from typing import Dict
from typing import List

from sct_data.cluster import Cluster

class SCTConfiguration:
    '''
    Dataclass that stores the full backup configuration.
    The data contained here is usually read from a s3b.yaml configuration file.
    See also s3b_common.s3b_config.
    '''

    def __init__(self):
        self.clusters: Dict[str, Cluster] = {}
        # A dictionary that maps cluster names to Cluster objects.

        self.jumphost: str = ""
        self.jumphost_user: str = ""
        self.ionos_username: str = ""
        self.ionos_password: str = ""


    def __str__(self):
        '''
        Assembles the class member content into a string.
        '''
        # instances
        clusters_string = ""
        for cluster_name, k8s_api_server, k8s_api_port in self.clusters.items():
            if len(clusters_string) != 0:
                clusters_string += ", "
            clusters_string += cluster_name.__str__()
        return "clusters: " + clusters_string 
