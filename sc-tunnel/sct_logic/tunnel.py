'''
Modul for a class that opens a ssh tunnel, Setting a stop event gracefully terminates the thread.
'''
from time import sleep
from multiprocessing import Process
import threading
import os
import paramiko
import sshtunnel
from sct_logic.hostname import addHost, removeHost
from sct_common.run_command import run_command

class TunnelThreading(object):
    '''
    '''
    def __init__(self, jumphost, jumphost_user, api_server, stopper, interval=1):
        self.interval = interval
        self.thread = Process(target=self.run, args=(jumphost, jumphost_user, api_server.api_server_host,api_server.api_server_port,stopper))
        self.thread.daemon = True
        self.thread.start()
        print('parent process:', os.getppid())
        print('process id:', os.getpid())
        print('child pid: ',self.thread.pid)

    def run(self, jumphost, jumphost_user, api_server_host, api_server_port, stopper):
        '''
        '''
        with sshtunnel.open_tunnel(
            (jumphost, 22),
            ssh_username=jumphost_user,
            ssh_pkey=paramiko.agent.Agent().get_keys(),
            remote_bind_address=(api_server_host, api_server_port),
            local_bind_address=('0.0.0.0', api_server_port), 
            host_pkey_directories = []
        ) as server:
            def do_something():
                # Here we have to wait
                run_command(['sudo', 'hostctl', 'add', 'domains', 'sc', api_server_host])
                #addHost(api_server_host)
                while True:
                    if not stopper.is_set():
                        stopper.wait(2)
                        sleep(self.interval)
                    else:
                        run_command(['sudo', 'hostctl', 'remove', 'domains', 'sc', api_server_host])
                        #removeHost(api_server_host)
                        break
            do_something()
    def join(self):
        '''
        Called from outside to wait until the thread has gracefully teminated
        '''
        self.thread.join()
