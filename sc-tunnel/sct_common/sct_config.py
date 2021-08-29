import os, sys
import yaml
from yaml import load, dump, Loader, FullLoader, Dumper
from typing import Dict
from typing import List

from sct_common.sctexception import SCTException
from sct_common.sct_tools import get_absolute_path
from sct_data.cluster import Cluster
from sct_data.configuration import SCTConfiguration

def read_configuration(configuration_file):
    '''
    Reads an sct_config.yaml configuration file into a SCTConfiguration object and returns the filled data object.
    '''

    configuration_file = get_absolute_path(configuration_file)
    a_yaml_file = open(configuration_file, encoding="utf-8")
    data = load(a_yaml_file, Loader=Loader)['sct_tunnel_configuration']
    # convert into objects
    configuration = SCTConfiguration()

    # jumphost
    configuration.jumphost = data['jumphost']

    # jumphost_user
    configuration.jumphost_user = data['jumphost_user']

    # ionos_username
    configuration.ionos_username = data['ionos_username']

    # ionos_password
    configuration.ionos_password = data['ionos_password']

    return configuration

def get_cluster_k8s_api_server_from_cluster_name(cluster_name):
    '''
    Returns a list of Instance objects where the instance names match the names in the given instance_names list.
    The Instance objects are taken from the given configuration.
    '''
    cluster_k8s_api_server_name: str = ""
    cluster_k8s_api_server_port: int = 0
    return cluster_k8s_api_server_name, cluster_k8s_api_server_port
