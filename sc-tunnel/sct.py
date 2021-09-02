#!/usr/bin/env python3

'''
This script tunnels access to IONOS Kubernets cluster via a jump host. 
'''

import sys
import os
import subprocess
import logging
import argparse
import traceback
from contextlib import redirect_stdout
from sct_common.sct_config import read_configuration
from sct_data.configuration import SCTConfiguration
from sct_logic.tunnel import openTunnel
from sct_logic.list import listCluster

def parseArguments():
    '''
    Parses the program arguments and returns the data parsed by argparse.
    '''
    parser = argparse.ArgumentParser(description='Tunnels access to IONOS Kubernetes cluster via a jump host.')

    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument("--list", action='store_true', help = "Lists the locally available IONOS K8S cluster to be used for tunneling.")
    parser.add_argument("--update", action='store_true', help = "Update the locally available IONOS K8S clusterin $(HOME)/.kube/.")
    #parser.add_argument("--cluster", dest='cluster_names', nargs='+', action='append', required=False, default='', help = "One or more cluster names to open  a tunnel for, e.g. sc-prod-admin.")
    parser.add_argument("--cluster", required=False, default='', help = "Cluster name to open  a tunnel for, e.g. sc-prod-admin.")
    args = parser.parse_args()
    return args



if __name__ == '__main__':
    sc_tunnel_config = None
    try:
        if sys.version_info[0] < 3 or sys.version_info[1] < 6:
            print("This script requires Python version 3.6")
            sys.exit(1)

        #initLogging()
        logging.debug('Call arguments given: %s' % sys.argv[1:])
        parsedArgs = parseArguments()
        configuration_file = 'sct_config.yaml'
        sct_tunnel_config = read_configuration(configuration_file)
        if 'list' in parsedArgs:
            if parsedArgs.list is True:
                listCluster(sct_tunnel_config)
        #api_server = sct_tunnel_config.clusters['sc-prod-admin']
        #openTunnel(sct_tunnel_config.jumphost, sct_tunnel_config.jumphost_user, api_server.api_server_host, api_server.api_server_port)
        exit(0)
    except Exception as ex:
        logging.exception(ex)
        exit(1)
