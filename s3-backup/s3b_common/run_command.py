import subprocess
import logging
from s3b_common.s3bexception import S3bException

def runCommand(popenargs):
    '''
    Runs the given command and writes all output to the logger.
    '''
    logger = logging.getLogger()
    process = subprocess.Popen(popenargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def check_io():
           while True:
                output = process.stdout.readline().decode().rstrip()
                if output:
                    logger.log(logging.INFO, output)
                else:
                    break

    # keep checking stdout/stderr until the child exits
    while process.poll() is None:
        check_io()

    logging.debug("runCommand returncode: '%s'" % process.returncode)
    if process.returncode != 0:
        raise S3bException("The process has exited with an error.")
