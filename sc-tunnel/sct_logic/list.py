from typing import Dict, List
from sct_common.sct_config import read_configuration
from sct_data.configuration import SCTConfiguration
from sct_data.cluster import Cluster

def listCluster(sct_tunnel_config):
    '''
    List all locally available cluster where teh Kubeconfig is store in the $(HOME)/.kube folder
    '''
    for cluster in sct_tunnel_config.clusters:
        myCluster: Dict[Cluster] = sct_tunnel_config.clusters[cluster]
        print(cluster)
        for item in myCluster:
            print(item)
    pass
