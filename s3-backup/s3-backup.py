#!/usr/bin/env python3

'''
This script creates S3 user data copies for backup purposes. 

'''

import sys
import os
import subprocess
import logging
import argparse
from contextlib import redirect_stdout

from s3b_common.run_command import runCommand
from s3b_common.s3b_logging import initLogging
from s3b_common.s3b_config import read_configuration
from s3b_data.instance import Instance
from s3b_data.s3drive import S3Drive
from s3b_data.configuration import BackupConfiguration

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    parser.add_argument("-c", "--Configuration", help = "Name of a yaml configuration file for the backup.", default="s3b_test.yaml")
    args = parser.parse_args()
    if args.Configuration:
        print("Configuration: %s" % args.Configuration)

    return args

if __name__ == '__main__':
    try:
        if sys.version_info[0] < 3 or sys.version_info[1] < 6:
            print("This script requires Python version 3.6")
            sys.exit(1)

        initLogging()
        logging.info('Call arguments given: %s' % sys.argv[1:])
        args = parseArguments()
        configuration_file = args.Configuration
        s3_backup_config = read_configuration(configuration_file)
        print(s3_backup_config)
        exit(0)
    except Exception as ex:
        logging.exception(ex)
        logging.info("Backup failed.")
        exit(1)
