# https://docs.ionos.com/python-sdk/
import os
from typing import List
import ionoscloud
from ionoscloud.rest import ApiException
from pprint import pprint
import csv
from csv import DictWriter
import time
import requests



# this config with a token or username/password made it possible to deploy, but it made problems with Anisble and Terraform 
# configuration = ionoscloud.Configuration(token=os.getenv("VMAAS_IONOS_TOKEN"))
configuration = ionoscloud.Configuration( 
    username=os.getenv("DBP_IONOS_USERNAME"),
    password=os.getenv("DBP_IONOS_PASSWORD"))

header_list =header_list = ['uuid','tenant','datacenter_id','datacenter_location','datacenter_name','image_id','ipblock_name','ipblock_ips','ipblock_name','ipblock_size','lan_id','lan_name','nic_id','nic_name','server_cores','server_id','server_name','server_ram','server_type','volume_id','volume_name','volume_size','volume_type','volume_size']

# VARS

# Hard
datacenter_description = "This is a datacenter to place the VMs"
img_filter_str = "ubuntu-22.04-server-cloudimg"
lan_public = True

with open('vm_file_start.csv', newline='') as vm_file:
    reader = csv.DictReader(vm_file)
    for row in reader:
        if row['uuid'] == "abcd":
            vm_obj = row
            # - und +
            server_name = str("vm-" + row['uuid'] + "-" + row['tenant'])
            datacenter_location = row['datacenter_location']
            server_type =  row['server_type']

# Datacenter Name has to be changed
vm_obj['datacenter_name'] = 'AimeesTest'
vm_obj['datacenter_location'] = datacenter_location
vm_obj['server_name'] = server_name
vm_obj['lan_name'] = str(server_name + '-lan')
vm_obj['nic_name'] = str(server_name + '-nic')
vm_obj['volume_name'] =  str(server_name + '-root-volume')
vm_obj['volume_type'] = 'HDD'
vm_obj['ipblock_name'] = str(server_name + '-ipblock-name')
vm_obj['ipblock_size'] = 1

# from OS Envs
ssh_keys = [os.getenv("VMAAS_PUBLIC_SSH_KEY")]


# test for ssh key existence Error Code
if ssh_keys == '':
    raise ValueError('ssh key is not send. Make sure you provide a VMAAS_PUBLIC_SSH_KEY ENV')

# set server tpe
if vm_obj['server_type'] == 'type_a':
    vm_obj['server_cores'] = 1
    vm_obj['server_ram'] = 1024
    vm_obj['volume_size'] = 50
else:
    raise ValueError('server type is not type_a; No other server type defined; Ram etc counld not be set')


print(vm_obj)


print("*****Get Datacenters ID*****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.DataCentersApi(api_client)
    try:
        api_response = api_instance.datacenters_get()
        datacenters: List[ionoscloud.Datacenter] = api_instance.datacenters_get(depth=1).items
        for datacenter in datacenters:
            if (vm_obj['datacenter_name'] == datacenter.properties.name):
                id: str = datacenter.id
                datacenter_id = id
    except ApiException as e:
        pprint('Exception when calling DataCentersApi.datacenters_get: %s\n' % e)

print("datacenter_id: " + datacenter_id)
vm_obj['datacenter_id'] = datacenter_id


print("*****Create an ipblock ans return ipblocks_ips*****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.IPBlocksApi(api_client)
    try:
        ipblocks: List[ionoscloud.IpBlock] = api_instance.ipblocks_get(depth=3).items
        ipblock_exists = False
        for ipblock in ipblocks:
            if ipblock.properties.name ==  vm_obj['ipblock_name']:
                ipblock_exists = True
                print("ipblock with name: " + vm_obj['ipblock_name'] + " already existend")
        if ipblock_exists == False:
            # test return code
            print("ipblock with name: " + vm_obj['ipblock_name'] + " will be created")
            properties=ionoscloud.IpBlockProperties(name=vm_obj['ipblock_name'], location=vm_obj['datacenter_location'], size=1)
            ipblock = ionoscloud.IpBlock(properties=properties)
            print(api_instance.ipblocks_post(ipblock))
        for ipblock in ipblocks:
            if (vm_obj['ipblock_name'] == ipblock.properties.name):
                vm_obj['ipblock_ips']= ipblock.properties.ips
    except ApiException as e:
        print('Exception when calling IPBlocksApi.ipblocks_get: %s\n' % e)


print("*****Get Image Id *****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.ImagesApi(api_client)
    try:
        images: List[ionoscloud.Image] = api_instance.images_get(depth=3).items
        for image in images:
            id: ionoscloud.ImageProperties = image.id
            properties: ionoscloud.ImageProperties = image.properties
            if(img_filter_str in properties.name and datacenter_location in properties.location):
                vm_obj['image_id'] = id
                print(vm_obj['image_id'])
    except ApiException as e:
        print('Exception when calling ImagesApi.images_get: %s\n' % e)


print("*****Create a Lan and get lan_id*****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.LANsApi(api_client)
    try:
        lans: List[ionoscloud.Lan] = api_instance.datacenters_lans_get(vm_obj['datacenter_id'], depth=3).items
        lan_exists = False
        for lan in lans:
            if lan.properties.name == vm_obj['lan_name']:
                lan_exists = True
                print("Lan with name: " + vm_obj['lan_name'] + " already existend")
        if lan_exists == False:
            print("Lan with name: " + vm_obj['lan_name'] + " will be created")
            properties = ionoscloud.LanPropertiesPost(name=vm_obj['lan_name'], public=lan_public)
            lan = ionoscloud.LanPost(properties=properties)
            api_instance.datacenters_lans_post(vm_obj['datacenter_id'], lan)
        for lan in lans:
            if (vm_obj['lan_name'] == lan.properties.name):
                vm_obj['lan_id']= lan.id
    except ApiException as e:
        print('Exception when calling LANsApi.datacenters_lans_post: %s\n' % e)

print('*****Create a Server and get server_id*****')
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.ServersApi(api_client)
    properties = ionoscloud.ServerProperties(name=vm_obj['server_name'], cores=vm_obj['server_cores'], ram=vm_obj['server_ram'])
    server = ionoscloud.Server(properties=properties)
    try:
        servers: List[ionoscloud.Server] =api_instance.datacenters_servers_get(vm_obj['datacenter_id'], depth=3).items
        server_exists = False
        for server in servers:
            if server.properties.name == vm_obj['server_name']:
                server_exists = True
                print("Server with name: " + vm_obj['server_name'] + " already existend")
        if server_exists == False:
            print("Server with name: " + vm_obj['server_name'] + " will be created")
            properties = ionoscloud.ServerProperties(name=vm_obj['server_name'], cores=vm_obj['server_cores'], ram=vm_obj['server_ram'])
            server = ionoscloud.Server(properties=properties)
            api_instance.datacenters_servers_post(vm_obj['datacenter_id'], server)
        for server in servers:
            if (vm_obj['server_name'] == server.properties.name):
                vm_obj['server_id']= server.id
    except ApiException as e:
        print('Exception when calling ServersApi.datacenters_servers_post: %s\n' % e)


print("*****Create a Volume*****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.VolumesApi(api_client)
    properties = ionoscloud.VolumeProperties(name=vm_obj['volume_name'], size=vm_obj['volume_size'], type=vm_obj['volume_type'], image=vm_obj['image_id'], ssh_keys=ssh_keys)
    volume = ionoscloud.Volume(properties=properties)
    try:
        volumes: List[ionoscloud.Volume] =api_instance.datacenters_volumes_get(datacenter_id, depth=3).items
        volume_exists = False
        for volume in volumes:
            if volume.properties.name == vm_obj['volume_name']:
                volume_exists = True
                print("Volume with name: " + vm_obj['volume_name'] + " already existend")
        if volume_exists == False:
            print("Volume with name: " + vm_obj['volume_name'] + " will be created")
            properties = ionoscloud.VolumeProperties(name=vm_obj['volume_name'], size=vm_obj['volume_size'], type=vm_obj['volume_type'], image=vm_obj['image_id'], ssh_keys=ssh_keys)   
            volume = ionoscloud.Volume(properties=properties)
            api_instance.datacenters_volumes_post(vm_obj['datacenter_id'], volume)
            attach_volume = True
        for volume in volumes:
            if (vm_obj['volume_name'] == volume.properties.name):
                vm_obj['volume_id']= volume.id
    except ApiException as e:
        print('Exception when calling VolumesApi.datacenters_volumes_post: %s\n' % e)



# this needs improvement
# state can not be shown right after
time.sleep(15)
volume_ready = False
print("*****Check readiness of Volume*****")
while volume_ready is not True:
    with ionoscloud.ApiClient(configuration) as api_client:
        api_instance = ionoscloud.VolumesApi(api_client)
        volume: ionoscloud.Volume = api_instance.datacenters_volumes_find_by_id(vm_obj['datacenter_id'], vm_obj['volume_id'])
        if volume.metadata.state == "AVAILABLE":
            volume_ready = True
            print("Volume is in an available state")
        else:
            print("Waiting for volume to be ready for attachment")
            time.sleep(10)



print("*****Attach a Volume*****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.ServersApi(api_client)
    volume = ionoscloud.Volume(id=vm_obj['volume_id'])
    try:
        api_instance.datacenters_servers_volumes_post(vm_obj['datacenter_id'], vm_obj['server_id'], volume=volume)
    except ApiException as e:
        print('Exception when calling ServersApi.datacenters_servers_volumes_post: %s\n' % e)

print("*****Create a nic and get nic_id*****")
with ionoscloud.ApiClient(configuration) as api_client:
    api_instance = ionoscloud.NetworkInterfacesApi(api_client)
    try:
        nics: List[ionoscloud.Nic] =api_instance.datacenters_servers_nics_get(vm_obj['datacenter_id'], vm_obj['server_id'], depth=3).items
        nic_exists = False
        for nic in nics:
            if nic.properties.name == vm_obj['nic_name']:
                nic_exists = True
                print("nic with name: " + vm_obj['nic_name'] + " already existend")
        if nic_exists == False:
            print("nic with name: " + vm_obj['nic_name'] + " will be created")
            properties = ionoscloud.NicProperties(name=vm_obj['nic_name'], ips=list(vm_obj['ipblock_ips']), lan=vm_obj['lan_id'] )
            nic = ionoscloud.Nic(properties=properties)
            api_instance.datacenters_servers_nics_post(vm_obj['datacenter_id'], vm_obj['server_id'], nic)
            attach_volume = True
        for nic in nics:
            if (vm_obj['nic_name'] == nic.properties.name):
                vm_obj['nic_id']= nic.id
    except ApiException as e:
        print('Exception when calling NetworkInterfacesApi.datacenters_servers_nics_post: %s\n' % e)

print(vm_obj)

# server_id has not been put in the csv file properly once, may need further testing
with open('vm_file_filled.csv', 'a') as vm_file:
    dictwriter_object = DictWriter(vm_file, fieldnames=header_list)
    dictwriter_object.writerow(vm_obj)


