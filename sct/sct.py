#!/usr/bin/env python3

'''
This script tunnels access to IONOS Kubernets cluster via a jump host.
'''

import os
import sys
import logging
import argparse
import threading
import multiprocessing
import random
from time import sleep
from typing import Dict, List
from urllib.parse import urlparse
from sct_common.sct_config import read_configuration
from sct_data.configuration import SCTConfiguration
from sct_data.cluster import Cluster
from sct_logic.tunnel import TunnelThreading
from sct_logic.list import listCluster
from sct_common.run_command import run_command, run_command_no_output
from sct_common.sct_tools import *
from sct_data.systemtools import SCT_OS



def parseArguments():
    '''
    Parses the program arguments and returns the data parsed by argparse.
    '''
    parser = argparse.ArgumentParser(description='Tunnels access to IONOS Kubernetes cluster via a jump host.')

    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument("--list", action='store_true', help = "Lists the locally available IONOS K8S cluster to be used for tunneling.")
    parser.add_argument("--connect-all", dest='connectall', action='store_true', help = "Open a tunnel to all clusters")
    parser.add_argument("--connect", dest='clusters', type=str, nargs='+', required=False, default='', help = "Cluster name to open  a tunnel for, e.g. sc-prod-admin.")
    parser.add_argument("--tunnel", dest='tunnels', type=str, nargs='+', required=False, default='', help = "Server to tunnel, <host>:<port>, e.g. gitea.example.com:2345.")
    parser.add_argument("--config", dest='configfile', required=False, default='sct_config.yaml', help = "Configfile location.")
    args = parser.parse_args()
    return args

  
if __name__ == '__main__':
    sc_tunnel_config = None
    sc_hostctl_cmd = None 
    connectThreads: List = []
    openedPorts: Dict = {}
    try:
        if sys.version_info[0] < 3 or sys.version_info[1] < 6:
            print("This script requires Python version 3.6")
            sys.exit(1)

        logging.debug('Call arguments given: %s' % sys.argv[1:])
        parsedArgs = parseArguments()
        configuration_file = parsedArgs.configfile
        sct_tunnel_config: SCTConfiguration = read_configuration(configuration_file)
        if 'list' in parsedArgs:
            if parsedArgs.list is True:
                listCluster(sct_tunnel_config)
        if parsedArgs.clusters != '' or parsedArgs.connectall is True or parsedArgs.tunnels != '':
            stop = threading.Event()
            if parsedArgs.tunnels != '':
                for tunnel in parsedArgs.tunnels:
                    # Adding "https://" is just to satisfy the urlparse function and ist not used further
                    url = 'https://' + tunnel
                    parsed_url = urlparse(url)
                    cluster = Cluster('tunnel', parsed_url.hostname, parsed_url.port)
                    if parsed_url.port in openedPorts.keys():
                        # Tunneling to the same port is not possible so we just add a host entry
                        print("Tunneling to {} not possible, port {} already in use!".format(parsed_url.hostname, parsed_url.port))
                    else:
                        tr = TunnelThreading(sct_tunnel_config.jumphost, sct_tunnel_config.jumphost_user, cluster, stopper=stop)
                        openedPorts[cluster.api_server_port] = cluster.api_server_host
                        connectThreads.append(tr)
                        while not tr.isUp():
                            sleep(2)
            if parsedArgs.clusters != '':
                enableSudochache()
                for cluster in parsedArgs.clusters:
                    if sct_tunnel_config.clusters[cluster].api_server_port in openedPorts.keys():
                        # Tunneling to the same port is not possible so we just add a host entry
                        print("Tunneling to {} not possible, port {} already in use!".format(sct_tunnel_config.clusters[cluster].api_server_host, sct_tunnel_config.clusters[cluster].api_server_port))
                    else:
                        tr = TunnelThreading(sct_tunnel_config.jumphost, sct_tunnel_config.jumphost_user, sct_tunnel_config.clusters[cluster], stopper=stop)
                        openedPorts[sct_tunnel_config.clusters[cluster].api_server_port] = sct_tunnel_config.clusters[cluster].api_server_host
                        connectThreads.append(tr)
                        while not tr.isUp():
                            sleep(2)
            if parsedArgs.connectall is True:
                # Open a tunnel for all cluster with looping over all available cluster
                enableSudochache()
                for cluster in sct_tunnel_config.clusters:
                    if sct_tunnel_config.clusters[cluster].api_server_port in openedPorts.keys():
                        # Tunneling to the same port is not possible so we just add a host entry
                        print("Tunneling to {} not possible, port {} already in use!".format(sct_tunnel_config.clusters[cluster].api_server_host, sct_tunnel_config.clusters[cluster].api_server_port))
                    else:
                        tr = TunnelThreading(sct_tunnel_config.jumphost, sct_tunnel_config.jumphost_user, sct_tunnel_config.clusters[cluster], stop)
                        openedPorts[sct_tunnel_config.clusters[cluster].api_server_port] = sct_tunnel_config.clusters[cluster].api_server_host
                        connectThreads.append(tr)
                        while not tr.isUp():
                            sleep(2)
            passcode = random.randint(1111,9999)
            while True:
                try:
                    name = input("Please enter {} to terminate tunneling: ".format(passcode))
                    if name == str(passcode):
                        stop.set()
                        for cThread in connectThreads:
                            #cThread.stop()
                            while cThread.isUp():
                                continue
                            cThread.join()
                        sct_systemtools = getSystemtools()
                        if sct_systemtools.os == SCT_OS.DEVCONTAINER:
                            sct_removeargs = list()
                            sct_addargs = sct_systemtools.getArgs(SCT_OS.WSL2)
                            sct_removeargs.append(sct_addargs[0])
                            sct_removeargs.append(sct_addargs[1])
                            sct_removeargs.append(sct_addargs[2])
                            sct_removeargs.append(sct_addargs[3])
                            sct_removeargs.append('remove')
                            sct_removeargs.append('sc')
                            run_command(sct_removeargs)
                            sct_systemtools.addArg('remove', SCT_OS.DEVCONTAINER)
                            sct_systemtools.addArg('sc', SCT_OS.DEVCONTAINER)
                            run_command(sct_systemtools.getArgs(SCT_OS.DEVCONTAINER))
                        else:
                            sct_systemtools.addArg('remove', sct_systemtools.os)
                            sct_systemtools.addArg('sc', sct_systemtools.os)
                            run_command(sct_systemtools.getArgs(sct_systemtools.os))
                        disableSudochache()
                        print("Tunneling terminated")
                        break
                    continue
                except KeyboardInterrupt or EOFError:
                    print("\t Please input the passcode to terminate ....")
                    continue
        sys.exit(0)
    except Exception as ex:
        logging.exception(ex)
        sys.exit(1)
