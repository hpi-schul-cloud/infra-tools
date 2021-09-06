'''
Modul for a class that opens a ssh tunnel, Setting a stop event gracefully terminates the thread.
'''
from time import sleep
import threading
import paramiko
import sshtunnel
from sct_logic.hostname import addHost, removeHost


class TunnelThreading(object):
    '''
    '''
    def __init__(self, jumphost, jumphost_user, api_server, stopper, interval=1):
        self.interval = interval
        self.thread = threading.Thread(target=self.run, args=(jumphost, jumphost_user, api_server.api_server_host,api_server.api_server_port,stopper))
        self.thread.daemon = True
        self.thread.start()

    def run(self, jumphost, jumphost_user, api_server_host, api_server_port, stopper):
        '''
        '''
        with sshtunnel.open_tunnel(
            (jumphost, 22),
            ssh_username=jumphost_user,
            ssh_pkey=paramiko.agent.Agent().get_keys(),
            #ssh_pkey="/var/ssh/rsa_key",
            #ssh_private_key_password="secret",
            remote_bind_address=(api_server_host, api_server_port),
            local_bind_address=('0.0.0.0', api_server_port), 
            host_pkey_directories = []
        ) as server:
            def do_something():
                # Here we have to wait
                addHost(api_server_host)
                while True:
                    if not stopper.is_set():
                        stopper.wait(2)
                        sleep(self.interval)
                    else:
                        removeHost(api_server_host)
                        break
            do_something()
    def join(self):
        self.thread.join()
