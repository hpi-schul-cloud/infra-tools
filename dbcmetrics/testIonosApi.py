from datetime import datetime
from typing import List
import ionoscloud
import os

token=os.getenv("IONOS_TOKEN")
print(token)
configuration = ionoscloud.Configuration(token=token)
api_client = ionoscloud.ApiClient(configuration)
kube_api = ionoscloud.KubernetesApi(api_client)
clusters: List[ionoscloud.KubernetesCluster] = kube_api.k8s_get(depth=3).items
filter_str = "infra-dev"
cluster_timeperiod = datetime.timedelta(minutes=15)
nodepool_timeperiod = datetime.timedelta(minutes=120)
maintenance_windows = {}
for cluster in clusters:
    properties: ionoscloud.KubernetesClusterProperties = cluster.properties
    name: str = properties.name
    if(filter_str in name):
        window_list = []
        window: ionoscloud.KubernetesMaintenanceWindow = properties.maintenance_window

        print("Cluster:",name, window, cluster.href)
        nodepools: List[ionoscloud.KubernetesNodePool] = cluster.entities.nodepools.items
        for pool in nodepools:
            pool_props: ionoscloud.KubernetesNodePoolProperties = pool.properties
            print(pool_props.name, pool_props.maintenance_window)