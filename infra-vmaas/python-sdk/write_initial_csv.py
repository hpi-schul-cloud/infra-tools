import csv

# values like snapshot id, start time, end time not implemented yet

header_list = ['uuid','tenant','datacenter_id','datacenter_location','datacenter_name','image_id','ipblock_name','ipblock_ips','ipblock_name','ipblock_size','lan_id','lan_name','nic_id','nic_name','server_cores','server_id','server_name','server_ram','server_type','volume_id','volume_name','volume_size','volume_type','volume_size']
header = header_list

with open('vm_file_start.csv', 'w', newline='') as csvfile:
    fieldnames = header_list
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'uuid': 'abcd', 'tenant': 'bw', 'datacenter_location' : 'de/txl', 'server_type': 'type_a'})


