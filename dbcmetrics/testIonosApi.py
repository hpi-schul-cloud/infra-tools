import datetime
from typing import List
import ionoscloud
import os


# Only works if the current API JWT Token has Admin priviledges 
# Will append all ressources (e.g. all viewable Ressources as Admin) to a specific name
def add_ressources_to_group(list_of_all_ressorces: ionoscloud.Resource, group_name: str):
    api_instance = ionoscloud.UserManagementApi(api_client)
    try:

        print("--------------------------------------------------")
        print(f"Check list_of_all_ressorces")  
        for ressource in list_of_all_ressorces:
            print(ressource.properties.name, ressource.id)


        print("--------------------------------------------------")
        print(f"Get all Groups")  
        api_response_retrieve_groups: ionoscloud.Groups = api_instance.um_groups_get(depth = 5)
        for group in api_response_retrieve_groups.items:
            print(f"Retrieve group:  name -> {group.properties.name}  id -> {group.id}")
        
        print("--------------------------------------------------")
        print(f"Get correct Group")    
        kubernetes_group: ionoscloud.Group = next(x for x in api_response_retrieve_groups.items if group_name == x.properties.name)
        print(f"Group id: {kubernetes_group.id}")

        print("--------------------------------------------------")
        print(f"Check ressource items befor appending more ressources")  
        for item in kubernetes_group.entities.resources.items:
            print(item.properties.name, item.id, item.href)

        print("--------------------------------------------------")
        print(f"Append nodepools to local group-object")

        kubernetes_group.entities.resources.items.extend(list_of_all_ressorces)

        # for ressource in list_of_all_ressorces:
        #     newRessource: ionoscloud.Resource =  ionoscloud.Resource() #{'id': ressource.id, 'type': ressource.type, 'href': ressource.href}
        #     newRessource.id = ressource.id
        #     newRessource.type = ressource.type
        #     newRessource.href = ressource.href
        #     print(newRessource)
        #     kubernetes_group.entities.resources.items.append(newRessource)
        #     print(ressource.properties.name, ressource.id)

        print("Check ressource items of local group-object")
        for item in kubernetes_group.entities.resources.items:
            print(item.properties.name, item.id, item.href)
            #print(item.id, item.href)
            # print(item)
        # print(f"infra dev group: {kubernetes_group}")


        print("--------------------------------------------------")
        print(f"Update updated group {group_name} via REST-PUT")
        api_response_update_group = api_instance.um_groups_put(group_id=kubernetes_group.id, group=kubernetes_group)
        print(f"Check items on api response")
        for items in api_response_update_group.items:
            print(items.properties.name, items.id, items.href)
        

        print("--------------------------------------------------")
        print(f"Check items on remote group {group_name}")
        
        api_response_get_group: ionoscloud.ResourceGroups = api_instance.um_groups_resources_get(group_id = kubernetes_group.id, depth = 3)
        for items in api_response_get_group.items:
            print(items.properties.name, items.id, items.href)
    except Exception as e:
        print('Exception when calling UserManagementApi.um_groups_resources_get: %s\n' % e)


if __name__ == '__main__':
    token=os.getenv("IONOS_TOKEN")
    print(token)
    configuration = ionoscloud.Configuration(token=token)
    with ionoscloud.ApiClient(configuration) as api_client:
        kube_api = ionoscloud.KubernetesApi(api_client)
        clusters: List[ionoscloud.KubernetesCluster] = kube_api.k8s_get(depth=3).items
        filter_str = "infra-dev"
        cluster_timeperiod = datetime.timedelta(minutes=15)
        nodepool_timeperiod = datetime.timedelta(minutes=120)
        maintenance_windows = {}
        list_of_all_nodepools: List[ionoscloud.KubernetesNodePool] = []
        for cluster in clusters:
            properties: ionoscloud.KubernetesClusterProperties = cluster.properties
            name: str = properties.name
            if(filter_str in name):
                window_list = []
                window: ionoscloud.KubernetesMaintenanceWindow = properties.maintenance_window
                print("--------------------------------------------------")
                
                print("Cluster:",name, window, cluster.href, cluster.id)
                #print("Cluster Object:", cluster)
                nodepools: List[ionoscloud.KubernetesNodePool] = cluster.entities.nodepools.items
                for pool in nodepools:
                    list_of_all_nodepools.append(pool)
                    pool_props: ionoscloud.KubernetesNodePoolProperties = pool.properties
                    print(pool.id, pool_props.name, pool_props.maintenance_window, pool_props.datacenter_id)


        #print(list_of_all_nodepools)
        group_name = "infra-dev-kubernetes"
        add_ressources_to_group(list_of_all_ressorces = list_of_all_nodepools, group_name = group_name)



