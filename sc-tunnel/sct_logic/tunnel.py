'''
Modul for a class that opens a ssh tunnel, Setting a stop event gracefully terminates the thread.
'''
from time import sleep
import threading
import paramiko
import sshtunnel
from sct_logic.hostname import addHost, removeHost
from sct_common.run_command import run_command, run_command_no_output

class TunnelThreading(object):
    '''
    '''
    def __init__(self, jumphost, jumphost_user, api_server, stopper, reuse_connection, interval=1):
        self.interval = interval
        self.tunnel_is_up = False
        self.thread = threading.Thread(target=self.run, args=(jumphost, jumphost_user, api_server.api_server_host,api_server.api_server_port,stopper,reuse_connection))
        self.thread.daemon = True
        self.lock = threading.Lock()
        self.thread.start()

    def run(self, jumphost, jumphost_user, api_server_host, api_server_port, stopper,reuse_connection):
        '''
        '''
        def do_something():
            # Here we have to wait
            if not reuse_connection:
                while not server.tunnel_is_up:
                    sleep(2)
            self.tunnel_is_up = True
            run_command(['sudo', 'hostctl', 'add', 'domains', 'sc', api_server_host])
            while True:
                if not stopper.is_set():
                    stopper.wait(2)
                    sleep(self.interval)
                else:
                    self.lock.acquire()
                    try:
                        run_command(['sudo', 'hostctl', 'remove', 'domains', 'sc', api_server_host])
                    finally:
                        self.lock.release()
                    self.tunnel_is_up = False
                    break
        if not reuse_connection:
            with sshtunnel.open_tunnel(
                (jumphost, 22),
                ssh_username=jumphost_user,
                ssh_pkey=paramiko.agent.Agent().get_keys(),
                remote_bind_address=(api_server_host, api_server_port),
                local_bind_address=('0.0.0.0', api_server_port), 
                host_pkey_directories = []
            ) as server:
                do_something()
        else:
            do_something()
    def join(self):
        '''
        Called from outside to wait until the thread has gracefully teminated
        '''
        self.thread.join()
    def isUp(self):
        '''
        Called from outside to wait until the thread has gracefully teminated
        '''
        return self.tunnel_is_up
