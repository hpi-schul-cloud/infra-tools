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

def parseArguments():
    '''
    Parses the program arguments and returns the data parsed by argparse.
    '''
    parser = argparse.ArgumentParser(description='Tunnels access to IONOS Kubernets cluster via a jump host.')

    parser.add_argument('--version', action='version', version='1.0.0')
    # parser.add_argument("-sc", "--showconfig", action='store_true', help = "Prints out the configuration that will be used, before any other action.")
    #parser.add_argument("-d", "--dailyincrement", action='store_true', help = "Creates a backup of the files that were uploaded during the last day.")
    # parser.add_argument("-s", "--syncfull", action='store_true', help = "Synchronizes the full backup of the configured instances, if scheduled for today.")
    # parser.add_argument("-va", "--validate", action='store_true', help = "Validates the existing syncfull backup. The validation checks the number of objects and the size of the buckets.")
    # parser.add_argument("-i", "--instance", action='append', dest = 'instances_to_backup', help = "Limits the scope to the specified instance. Add the name of an instance to backup as argument.")
    # parser.add_argument("-c", "--configuration", help = "Name of a yaml configuration file to use for the backup. The configuration file contains the definition of the available instances and other static configuration data.", default="s3b_test.yaml")
    # parser.add_argument("-f", "--force", action='store_true', help = "Force. If -s is specified forces a syncfull backup, even if it is not scheduled for today.")
    # parser.add_argument("-w", "--whatif", action='store_true', help = "If set no write operations are executed. rclone operations are executed with --dryrun.")
    # parser.add_argument("-ra", "--restoreall", action='store', dest = 'restore_instance', help = "Restores all buckets from a backup set. The parameter rb must be set additionally. The instance drive where the restore will happen must be empty.")
    # parser.add_argument("-rb", "--restorebackupset", action='store', dest = 'restore_backupset', help = "Use together with -ra. Selects the backupset to restore. E.g. 'demo-full-0'")
    args = parser.parse_args()
    return args

def logWhatIfHeader():
    logging.info("====================================================")
    logging.info("====================================================")
    logging.info("====================================================")
    logging.info("====== Simulation only! No backup performed. =======")
    logging.info("====================================================")
    logging.info("====================================================")
    logging.info("====================================================")

if __name__ == '__main__':
    sc_tunnel_config = None
    try:
        if sys.version_info[0] < 3 or sys.version_info[1] < 6:
            print("This script requires Python version 3.6")
            sys.exit(1)

        #initLogging()
        logging.debug('Call arguments given: %s' % sys.argv[1:])
        parsedArgs = parseArguments()
        #configuration_file = parsedArgs.configuration
        #s3_backup_config = read_configuration(configuration_file)
        exit(0)
    except Exception as ex:
        logging.exception(ex)
        logging.info("Backup failed.")
        exit(1)
