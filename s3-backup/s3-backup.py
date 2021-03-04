#!/usr/bin/env python3

'''
This script creates S3 user data copies for backup purposes. 
'''

import sys
import os
import subprocess
import logging
import argparse
import traceback
from contextlib import redirect_stdout

from s3b_common.s3b_logging import initLogging, get_logfile_name
from s3b_common.s3b_config import read_configuration
from s3b_common.s3bexception import S3bException
from s3b_common.s3b_mail import send_error_mail_to_multiple_receivers
from s3b_data.instance import Instance
from s3b_data.s3drive import S3Drive
from s3b_data.configuration import BackupConfiguration
from s3b_logic import rclone

def parseArguments():
    '''
    Parses the program arguments and returns the data parsed by argparse.
    '''
    parser = argparse.ArgumentParser(description='Run S3 instance backups for the HPI Schul-Cloud application.')

    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument("-sc", "--showconfig", action='store_true', help = "Prints out the configuration that will be used, before any other action.")
    parser.add_argument("-d", "--dailyincrement", action='store_true', help = "Creates a backup of the files that were uploaded during the last day.")
    parser.add_argument("-s", "--syncfull", action='store_true', help = "Synchronizes the full backup of the configured instances, if scheduled for today.")
    parser.add_argument("-va", "--validate", action='store_true', help = "Validates the existing syncfull backup. The validation checks the number of objects and the size of the buckets.")
    parser.add_argument("-i", "--instance", action='append', dest = 'instances_to_backup', help = "Limits the scope to the specified instance. Add the name of an instance to backup as argument.")
    parser.add_argument("-c", "--configuration", help = "Name of a yaml configuration file to use for the backup. The configuration file contains the definition of the available instances and other static configuration data.", default="s3b_test.yaml")
    parser.add_argument("-f", "--force", action='store_true', help = "Force. If -s is specified forces a syncfull backup, even if it is not scheduled for today.")
    parser.add_argument("-w", "--whatif", action='store_true', help = "If set no write operations are executed. rclone operations are executed with --dryrun.")
    parser.add_argument("-ra", "--restoreall", action='store', dest = 'restore_instance', help = "Restores all buckets from a backup set. The parameter rb must be set additionally. The instance drive where the restore will happen must be empty.")
    parser.add_argument("-rb", "--restorebackupset", action='store', dest = 'restore_backupset', help = "Use together with -ra. Selects the backupset to restore. E.g. 'demo-full-0'")
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
    s3_backup_config = None
    try:
        if sys.version_info[0] < 3 or sys.version_info[1] < 6:
            print("This script requires Python version 3.6")
            sys.exit(1)

        initLogging()
        logging.debug('Call arguments given: %s' % sys.argv[1:])
        parsedArgs = parseArguments()
        configuration_file = parsedArgs.configuration
        s3_backup_config = read_configuration(configuration_file)
        if parsedArgs.whatif:
            logWhatIfHeader()
        if parsedArgs.showconfig:
            logging.info("Configuration: %s" % s3_backup_config)
        elif parsedArgs.dailyincrement or parsedArgs.syncfull or parsedArgs.validate:
            # Evaluate which instances shall be backed up.
            instances_to_backup = []
            if parsedArgs.instances_to_backup:
                # Check that all instances the user has specified are in the current configuration.
                logging.debug('Run for specific instances: %s' % parsedArgs.instances_to_backup)
                for instance_name_to_check in parsedArgs.instances_to_backup:
                    instance_found = False
                    for current_instance_name, current_instance in s3_backup_config.instances.items():
                        if current_instance.instancename == instance_name_to_check:
                            instance_found = True
                            break
                    if not instance_found:
                        raise S3bException('Instance "%s" not found in configuration.' % instance_name_to_check)
                # All instance names given by the command line are valid
                instances_to_backup = parsedArgs.instances_to_backup
            else:
                # Use all instances in the current configuration.
                logging.debug('Run for all instances.')
                for current_instance_name, current_instance in s3_backup_config.instances.items():
                    instances_to_backup.append(current_instance.instancename)
            logging.info('The following instances are in scope: %s' % instances_to_backup)
            # Validate the s3-backup config.
            rclone.validate_configuration(s3_backup_config)
            # Run the backup or validation.
            rclone.run_backup(s3_backup_config, instances_to_backup, parsedArgs.dailyincrement, parsedArgs.syncfull, parsedArgs.validate, parsedArgs.force, parsedArgs.whatif)
        elif parsedArgs.restore_instance:
            # Restores a backed up buckets or all backed up buckets in a specific backup set.
            # The bucket to restore must not exist
            if parsedArgs.restore_backupset:
                rclone.run_restore_all(s3_backup_config, parsedArgs.restore_instance, parsedArgs.restore_backupset, parsedArgs.whatif)
            else:
                raise S3bException('For restore the parameters "restoreinstance" and "restorebackupset" must be set.')
        else:
            logging.info("No action specified. Use a parameter like -d, -s or -sc to define an action.")
        if parsedArgs.whatif:
            logWhatIfHeader()
        exit(0)
    except Exception as ex:
        logging.exception(ex)
        logging.info("Backup failed.")
        if s3_backup_config != None:
            send_error_mail_to_multiple_receivers(s3_backup_config.receiver_mail_addresses, traceback.format_exc(), get_logfile_name())
        exit(1)
