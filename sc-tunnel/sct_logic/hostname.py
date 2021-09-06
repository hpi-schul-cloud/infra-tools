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

def addHost(hostname):
    '''
    Add "hostname" to the hosts files as alias for 127.0.0.1
    '''
    hosts = Hosts()
    new_entry = HostsEntry(entry_type='ipv4', address='127.0.0.1', names=[hostname])
    hosts.add([new_entry])
    hosts.write()

def removeHost(hostname):
    '''
    Remove "hostname" from hosts file
    '''
    hosts = Hosts()
    if hosts.exists(address='127.0.0.1',names=[hostname]):
        hosts.remove_all_matching(name=hostname)
        hosts.write()
    
if __name__ == '__main__':
    listHosts()
    addHost('karl.dall')
    addHost('hugo.egon.balder')
    listHosts()
    removeHost('hugo.egon.balder')
    removeHost('karl.dall')
    listHosts()