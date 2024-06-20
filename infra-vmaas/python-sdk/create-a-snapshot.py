# https://docs.ionos.com/python-sdk/
import os
from typing import List
import ionoscloud
from ionoscloud.rest import ApiException
import csv

# need to have a ssh key in your envs
configuration = ionoscloud.Configuration( 
    username=os.getenv("DBP_IONOS_USERNAME"),
    password=os.getenv("DBP_IONOS_PASSWORD"))

with open('vm_file_filled.csv', newline='') as vm_file:
    # needs to filter specific line
    for i in csv.DictReader(vm_file):
        vm_obj = (dict(i))
print(vm_obj)

with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.VolumesApi(api_client)
    try:
        api_instance.datacenters_volumes_create_snapshot_post(vm_obj['datacenter_id'], vm_obj['volume_id'])
    except ApiException as e:
        print('Exception when calling VolumesApi.datacenters_volumes_create_snapshot_post: %s\n' % e)


# save snapshot id 