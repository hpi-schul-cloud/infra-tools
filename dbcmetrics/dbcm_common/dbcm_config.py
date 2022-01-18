import logging
import os, sys, glob
import yaml
from yaml import safe_load, load, dump, Loader, FullLoader, Dumper
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict
from typing import List

from dbcm_common.dbcmexception import DBCMException
from dbcm_common.dbcm_tools import get_absolute_path
from dbcm_data.configuration import DBCMConfiguration
from dbcm_data.dbcm_instance import DBCMInstance
from dbcm_data.dbcm_version import DBCMVersion, DBCMVersionService, DBCMVersionServices

CONFIGFILE_NAME = "dbcm_config.yaml"
GLOBAL_CONFIGDIR = "/etc/dbcmetrics/"

def read_configuration():
    '''
    Reads an dbcm_config.yaml configuration file into a DBCMConfiguration object and returns the filled data object.
        Try first to read from global configuration location, in case it does not exist  
        read from the config file specified in th eenvironment vbvariable DBMCCONFIG else terminate with error
    '''
    global_configuration_file = get_absolute_path(os.path.join(GLOBAL_CONFIGDIR, CONFIGFILE_NAME))

    local_configuration_file = os.environ.get("DBCMCONFIG")
    feature_data = None
    version_data = None
    instances_data = None
    
    if os.path.exists(global_configuration_file):
        config_yaml_file = open(global_configuration_file, encoding="utf-8")
    elif os.path.exists(local_configuration_file):
        config_yaml_file = open(local_configuration_file, encoding="utf-8")
    else:
        # no config file
        raise DBCMException
    all_data = safe_load(config_yaml_file)
    try:
        feature_data = all_data['features']
    except:
        logging.error("No features found in configuration file: {}".format(config_yaml_file))
        raise DBCMException
    if feature_data['version_metrics'] == 'enabled':
        try:
            version_data = all_data['version_metrics']
        except:
            logging.error("Feature 'version_metrics' enabled, but no config specified in configuration file {}".format(config_yaml_file))
            raise DBCMException
    try:
        instances_data = all_data['instances']
    except:
        logging.error("No instances found in configuration file: {}".format(config_yaml_file))
        raise DBCMException

    # new configuration object
    # Here are at leats the features an dinstances defined
    configuration = DBCMConfiguration()
    configuration.features = feature_data
    if configuration.features['version_metrics'] == 'enabled':
        try:
            dbcmVersion: DBCMVersion = DBCMVersion(version_data['services'],version_data['intervall'])
            configuration.version = dbcmVersion
        except:
            logging.error("Missing or wrong 'version_metrics' value in configuration file: {}".format(config_yaml_file))

    for instance in instances_data:
        dbcmInstance: DBCMInstance = DBCMInstance(instance['name'], instance['url'], instance['shortname'])
        configuration.instances.append(dbcmInstance) 
    for instance in configuration.instances:
        logging.info(instance)
    # configuration.versionservices = services_data
    return configuration
