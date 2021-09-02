from typing import Dict, List
from python_hosts import Hosts, HostsEntry


def listHosts():
    '''
    List the hosts entries for 127.0.0.1
    '''
    hosts = Hosts()
    entry: HostsEntry
    for entry in hosts.entries:
        if entry.entry_type == 'ipv4' and entry.address == '127.0.0.1':
            print(entry)
    print("\n")

if __name__ == '__main__':
    listHosts()
    pass