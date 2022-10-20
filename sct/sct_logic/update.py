import ionoscloud
from ionoscloud.rest import ApiException
import os
import yaml
from pathlib import Path
from typing import Dict
from typing import List

user_kube_dir: str = '.kube'

def updateKubeconfigs(username, password):
    '''
    Function to download all kubeconfigs available for the given account.
    Downloaded files are stored in the .kube directory of the current users home.
    '''
    kubeconfig_dir = os.path.join(Path.home(), user_kube_dir)
    if not os.path.exists(kubeconfig_dir):
         os.mkdir(kubeconfig_dir)
    # Defining the host is optional and defaults to https://api.ionos.com/cloudapi/v5
    # See configuration.py for a list of all supported configuration parameters.
    configuration = ionoscloud.Configuration(
    host = 'https://api.ionos.com/cloudapi/v6',
    )
    configuration.username = username
    configuration.password = password
    # Enter a context with an instance of the API client
    with ionoscloud.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        k8s_api_instance = ionoscloud.KubernetesApi(api_client)
        k8s_config_instance = ionoscloud.KubernetesApi(api_client)
        pretty = False # bool | Controls whether response is pretty-printed (with indentation and new lines) (optional) (default to True)
        depth = 1 # int | Controls the details depth of response objects.  Eg. GET /datacenters/[ID]  - depth=0: only direct properties are included. Children (servers etc.) are not included  - depth=1: direct properties and children references are included  - depth=2: direct properties and children properties are included  - depth=3: direct properties and children properties and children's children are included  - depth=... and so on (optional) (default to 0)
        x_contract_number = 0 # int | Users having more than 1 contract need to provide contract number, against which all API requests should be executed (optional)
        print("Updating avaliable Kubeconfigs ...\n")
        try:
            # List Kubernetes Clusters
            api_response = k8s_api_instance.k8s_get(pretty=pretty, depth=depth, x_contract_number=x_contract_number)
            for item in api_response.items:
                config_api_response = k8s_config_instance.k8s_kubeconfig_get(item.id, pretty=pretty, depth=depth, x_contract_number=x_contract_number)
                k8sconfig = eval(config_api_response)
                clustername = item.properties.name
                k8sfile = open(os.path.join(kubeconfig_dir,clustername + ".yaml"), mode="w")
                print("\twriting config for {}".format(clustername))
                yaml.dump(k8sconfig, k8sfile)
                # k8sfile.write(k8sconfig)
                k8sfile.close()
                pass
        except ApiException as e:
            print('Exception when calling Api: %s\n' % e)
