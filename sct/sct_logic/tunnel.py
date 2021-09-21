'''
Modul for a class that opens a ssh tunnel, Setting a stop event gracefully terminates the thread.
'''
from time import sleep
import threading
import paramiko
import sshtunnel
from sct_common.run_command import run_command

class TunnelThreading(object):
    '''
    '''
    def __init__(self, jumphost, jumphost_user, api_server, stopper, interval=1):
        self.interval = interval
        self.tunnel_is_up = False
        self.thread = threading.Thread(target=self.run, args=(jumphost, jumphost_user, api_server.api_server_host,api_server.api_server_port,stopper))
        self.thread.daemon = True
        self.thread.start()

    def run(self, jumphost, jumphost_user, api_server_host, api_server_port, stopper):
        '''
        Function that opens the tunnel and wait in a loop until the stop event is send from the main thread
        '''
        def do_something():
            # Here we have to wait
            while not server.tunnel_is_up:
                sleep(2)
            self.tunnel_is_up = True
            run_command(['sudo', 'hostctl', 'add', 'domains', 'sc', api_server_host])
            while True:
                if not stopper.is_set():
                    stopper.wait(2)
                    sleep(self.interval)
                else:
                    self.tunnel_is_up = False
                    break
        with sshtunnel.open_tunnel(
            (jumphost, 22),
            ssh_username=jumphost_user,
            ssh_pkey=paramiko.agent.Agent().get_keys(),
            remote_bind_address=(api_server_host, api_server_port),
            local_bind_address=('0.0.0.0', api_server_port), 
            host_pkey_directories = []
        ) as server:
            do_something()
    def join(self):
        '''
        Called from outside to wait until the thread has gracefully teminated
        '''
        self.thread.join()

    def isUp(self):
        '''
        Called from outside to read tunnel status
        '''
        return self.tunnel_is_up
