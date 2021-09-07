import os, sys, glob
import yaml
from yaml import load, dump, Loader, FullLoader, Dumper
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict
from typing import List

from sct_common.sctexception import SCTException
from sct_common.sct_tools import get_absolute_path
from sct_data.cluster import Cluster
from sct_data.configuration import SCTConfiguration

user_config_dir: str = '.config'
user_kube_dir: str = '.kube'

def read_configuration(configuration_file):
    '''
    Reads an sct_config.yaml configuration file into a SCTConfiguration object and returns the filled data object.
    '''
    try:
        global_configuration_file = get_absolute_path(configuration_file)
        global_yaml_file = open(global_configuration_file, encoding="utf-8")
        global_data = load(global_yaml_file, Loader=Loader)['sc_tunnel_configuration']
    except:
        # No global config file
        global_data = None

    try:
        user_configuration_file = os.path.join(Path.home(), user_config_dir ,os.path.basename(configuration_file))
        user_yaml_file = open(user_configuration_file, encoding="utf-8")
        user_data = load(user_yaml_file, Loader=Loader)['sc_tunnel_configuration']
    except:
        # no local config file
        user_data = None

    # convert into objects
    configuration = SCTConfiguration()

    if global_data != None:
        # jumphost
        if 'jumphost' in global_data: configuration.jumphost = global_data['jumphost']
        # jumphost_user
        if 'jumphost_user' in global_data: configuration.jumphost_user = global_data['jumphost_user']
        # ionos_username
        if 'ionos_username' in global_data: configuration.ionos_username = global_data['ionos_username']
        # ionos_password
        if 'ionos_password' in global_data: configuration.ionos_password = global_data['ionos_password']
    if user_data != None:
        # jumphost
        if 'jumphost' in user_data: configuration.jumphost = user_data['jumphost']
        # jumphost_user
        if 'jumphost_user' in user_data: configuration.jumphost_user = user_data['jumphost_user']
        # ionos_username
        if 'ionos_username' in user_data: configuration.ionos_username = user_data['ionos_username']
        # ionos_password
        if 'ionos_password' in user_data: configuration.ionos_password = user_data['ionos_password']
    if os.environ.get('ionos_username'.upper()): configuration.ionos_username = os.environ.get('ionos_username'.upper())
    if os.environ.get('ionos_password'.upper()): configuration.ionos_password = os.environ.get('ionos_password'.upper())

    if '' == configuration.jumphost or '' == configuration.jumphost_user or '' == configuration.ionos_username or '' == configuration.ionos_password:
        raise RuntimeError('Necessary configuration parameters missing, check config')
    
    configuration = read_available_clusters(configuration)

    return configuration

def get_cluster_k8s_api_server_from_cluster_name(cluster_name):
    '''
    Returns a list of Instance objects where the instance names match the names in the given instance_names list.
    The Instance objects are taken from the given configuration.
    '''
    cluster_k8s_api_server_name: str = ""
    cluster_k8s_api_server_port: int = 0
    return cluster_k8s_api_server_name, cluster_k8s_api_server_port

def read_available_clusters(configuration: SCTConfiguration):
    '''
    Read from user kube directory the available cluster and the name, api_server_host and api_server_port
    into the configuration
    '''
    kubeconfig_dir = os.path.join(Path.home(), user_kube_dir)
    for file in glob.glob(kubeconfig_dir + "**/*.yaml", recursive=False):
        try:
            kubeconfig = get_absolute_path(file)
            kubeconfig_file = open(kubeconfig, encoding="utf-8")
            kubeconfig_data = load(kubeconfig_file, Loader=Loader)['clusters']
        except:
            # No global config file
            kubeconfig_data = None    
        if kubeconfig_data != None:
            if 'name' in kubeconfig_data[0]: 
                clustername = kubeconfig_data[0] ['name']
                if 'cluster' in kubeconfig_data[0]: 
                    if 'server' in kubeconfig_data[0] ['cluster']: 
                        api_server = kubeconfig_data[0] ['cluster'] ['server']
                        url = urlparse(api_server)
                        configuration.clusters[clustername] = Cluster(clustername, url.hostname, url.port)


    return configuration