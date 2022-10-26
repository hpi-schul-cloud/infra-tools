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

print("*****Delete Nic*****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.NetworkInterfacesApi(api_client)
    try:
        nics: List[ionoscloud.Nic] =api_instance.datacenters_servers_nics_get(vm_obj['datacenter_id'], vm_obj['server_id'], depth=3).items
        print(nics)
        for nic in nics:
            properties: ionoscloud.NicProperties = nic.properties
            if(vm_obj['nic_name'] == properties.name):
                api_instance.datacenters_servers_nics_delete(vm_obj['datacenter_id'], vm_obj['server_id'], vm_obj['nic_id'])
    except ApiException as e:
        print('Exception when calling NetworkInterfacesApi.datacenters_servers_nics_post: %s\n' % e)

# Dont have to detach volume first, works fine
print("*****Delete a Volume*****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.VolumesApi(api_client)
    try:
        print(api_instance.datacenters_volumes_delete(vm_obj['datacenter_id'], vm_obj['volume_id']))
    except ApiException as e:
        print('Exception when calling VolumesApi.datacenters_volumes_post: %s\n' % e)


print("*****Delete a Server*****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.ServersApi(api_client)
    try:
        api_instance.datacenters_servers_delete(vm_obj['datacenter_id'],  vm_obj['server_id'])
    except ApiException as e:
        print('Exception when calling ServersApi.datacenters_servers_delete: %s\n' % e)

# this again needs some time
# sleep or something wiser should be used

print("*****Delete Lan*****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.LANsApi(api_client)
    try:
        lans: List[ionoscloud.Lan] = api_instance.datacenters_lans_get(vm_obj['datacenter_id'], depth=3).items
        for lan in lans:
            id = lan.id
            properties: ionoscloud.LanProperties = lan.properties
            if( vm_obj['lan_name'] in properties.name):
                lan_id = id
                api_instance.datacenters_lans_delete(vm_obj['datacenter_id'], lan_id)
    except ApiException as e:
        print('Exception when calling LANsApi.datacenters_lans_delete: %s\n' % e)


print("***** Delete Ipblock *****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.IPBlocksApi(api_client)
    try:
        ipblocks: List[ionoscloud.IpBlock] = api_instance.ipblocks_get(depth=3).items
        for ipblock in ipblocks:
            if (vm_obj['ipblock_name'] == ipblock.properties.name):
                ipblock_id = ipblock.id
                api_instance.ipblocks_delete(ipblock_id)
    except ApiException as e:
        print('Exception when calling IPBlocksApi.ipblocks_delete: %s\n' % e)


# delete/adjust entry in csv


