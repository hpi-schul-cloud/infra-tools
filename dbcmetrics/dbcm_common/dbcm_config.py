import logging
import os, sys
from yaml import safe_load

from dbcm_common.dbcmexception import DBCMException

CONFIGFILE_NAME = "dbcm_config.yaml"
GLOBAL_CONFIGDIR = "/etc/dbcmetrics/"

def read_configuration() -> dict:
    '''
    Reads an dbcm_config.yaml configuration file into a dict and returns it.
    Try first to read from global configuration location, in case it does not exist
    read from the config file specified in the environment variable DBCMCONFIG else terminate with error
    '''
    global_configuration_file = get_absolute_path(os.path.join(GLOBAL_CONFIGDIR, CONFIGFILE_NAME))
    local_configuration_file = os.environ.get("DBCMCONFIG")

    if os.path.exists(global_configuration_file):
        config_yaml_file = open(global_configuration_file, encoding="utf-8")
    elif os.path.exists(local_configuration_file):
        config_yaml_file = open(local_configuration_file, encoding="utf-8")
    else:
        logging.error("No configuration file found.")
        raise DBCMException
    all_data = safe_load(config_yaml_file)
    return all_data


def get_absolute_path(a_file):
    '''
    Returns the given file as absolute path.

    Checks, if the given file is an absolute path. If not
    the script path is prepended.
    '''
    a_file_abs = a_file
    if not os.path.isabs(a_file):
        script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        a_file_abs = os.path.join(script_path, a_file)
    return a_file_abs
