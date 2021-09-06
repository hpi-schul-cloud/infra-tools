#!/usr/bin/env python3

'''
This script tunnels access to IONOS Kubernets cluster via a jump host.
'''

import sys
import logging
import argparse
import threading
import random
from sct_common.sct_config import read_configuration
from sct_data.configuration import SCTConfiguration
from sct_logic.tunnel import TunnelThreading
from sct_logic.list import listCluster
from sct_logic.update import updateKubeconfigs


def parseArguments():
    '''
    Parses the program arguments and returns the data parsed by argparse.
    '''
    parser = argparse.ArgumentParser(description='Tunnels access to IONOS Kubernetes cluster via a jump host.')

    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument("--list", action='store_true', help = "Lists the locally available IONOS K8S cluster to be used for tunneling.")
    parser.add_argument("--update", action='store_true', help = "Update the locally available IONOS K8S clusterin $(HOME)/.kube/.")
    #parser.add_argument("--cluster", dest='cluster_names', nargs='+', action='append', required=False, default='', help = "One or more cluster names to open  a tunnel for, e.g. sc-prod-admin.")
    parser.add_argument("--connect", dest='cluster', required=False, default='', help = "Cluster name to open  a tunnel for, e.g. sc-prod-admin.")
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
        sct_tunnel_config: SCTConfiguration = read_configuration(configuration_file)
        if 'update' in parsedArgs:
            if parsedArgs.update is True:
                updateKubeconfigs(sct_tunnel_config.ionos_username, sct_tunnel_config.ionos_password)
        if 'list' in parsedArgs:
            if parsedArgs.list is True:
                listCluster(sct_tunnel_config)
        if 'cluster' in parsedArgs:
            if parsedArgs.cluster != '':
                stop = threading.Event()
                tr = TunnelThreading(sct_tunnel_config.jumphost, sct_tunnel_config.jumphost_user, sct_tunnel_config.clusters[parsedArgs.cluster], stopper=stop)
                passcode = random.randint(1111,9999)
                while True:
                    try:
                        name = input("Please enter {} to terminate tunneling: ".format(passcode))
                        if name == str(passcode):
                            stop.set()
                            tr.join()
                            print("Tunneling terminated")
                            break
                        continue
                    except EOFError:
                        print("Please input something....")
                        continue
        sys.exit(0)
    except Exception as ex:
        logging.exception(ex)
        sys.exit(1)
