from __future__ import print_function
import os
import time
import ionoscloud
from ionoscloud.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://api.ionos.com/cloudapi/v5
# See configuration.py for a list of all supported configuration parameters.
configuration = ionoscloud.Configuration(
  host = 'https://api.ionos.com/cloudapi/v5',
)
# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples with auth method are provided below
# Configure HTTP basic authorization: Basic Authentication
configuration.username = os.environ.get('IONOS_USERNAME')
configuration.password = os.environ.get('IONOS_PASSWORD')
# Enter a context with an instance of the API client
with ionoscloud.ApiClient(configuration) as api_client:
  # Create an instance of the API class
  api_instance = ionoscloud.KubernetesApi(api_client)
  k8s_cluster_id = '6b8e70ca-59ab-44c1-b1c0-9ee7a7616b8a' # str | The unique ID of the Kubernetes Cluster
  pretty = True # bool | Controls whether response is pretty-printed (with indentation and new lines) (optional) (default to True)
  depth = 1 # int | Controls the details depth of response objects.  Eg. GET /datacenters/[ID]  - depth=0: only direct properties are included. Children (servers etc.) are not included  - depth=1: direct properties and children references are included  - depth=2: direct properties and children properties are included  - depth=3: direct properties and children properties and children's children are included  - depth=... and so on (optional) (default to 0)
  x_contract_number = 0 # int | Users having more than 1 contract need to provide contract number, against which all API requests should be executed (optional)
  try:
      # Retrieve Kubernetes Configuration File
      api_response = api_instance.k8s_kubeconfig_get(k8s_cluster_id, pretty=pretty, depth=depth, x_contract_number=x_contract_number)
      print(api_response)
  except ApiException as e:
      print('Exception when calling KubernetesApi.k8s_kubeconfig_get: %s\n' % e)