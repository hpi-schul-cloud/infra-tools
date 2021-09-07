import sys, locale, os
import subprocess
import logging
from sct_common.sctexception import SCTException

def run_command_get_output(popenargs):
    with subprocess.Popen(popenargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        (cmd_stdout_bytes, cmd_stderr_bytes) = proc.communicate()
        (cmd_stdout, cmd_stderr) = (cmd_stdout_bytes.decode('utf-8'), cmd_stderr_bytes.decode('utf-8'))
        if proc.returncode != 0:
            raise SCTException("The process has exited with errorcode '%s'." % proc.returncode)
    return (cmd_stdout, cmd_stderr)

def run_command_no_output(popenargs):
    with subprocess.Popen(popenargs) as proc:
        proc.communicate()
        if proc.returncode != 0:
            raise SCTException("The process has exited with errorcode '%s'." % proc.returncode)

def run_command(popenargs):
    logger = logging.getLogger()
    with subprocess.Popen(popenargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        (cmd_stdout_bytes, cmd_stderr_bytes) = proc.communicate()
        (cmd_stdout, cmd_stderr) = (cmd_stdout_bytes.decode('utf-8'), cmd_stderr_bytes.decode('utf-8'))
        if (len(cmd_stdout) > 0):
            logger.log(logging.INFO, cmd_stdout)
        if (len(cmd_stderr) > 0):
            logger.log(logging.ERROR, cmd_stderr)
        if proc.returncode != 0:
            raise SCTException("The process has exited with errorcode '%s'." % proc.returncode)

def run_command_get_output_debug_edition(popenargs):
    print(sys.stdout.encoding)
    print(sys.stdout.isatty())
    print(locale.getpreferredencoding())
    print(sys.getfilesystemencoding())
    logger = logging.getLogger()
    with subprocess.Popen(popenargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        (cmd_stdout_bytes, cmd_stderr_bytes) = proc.communicate(None)
        (cmd_stdout, cmd_stderr) = (cmd_stdout_bytes.decode('utf-8'), cmd_stderr_bytes.decode('utf-8'))
        print(type(cmd_stdout))
        print(repr(cmd_stdout))
        if (len(cmd_stdout) > 0):
            logger.log(logging.INFO, cmd_stdout)
        if (len(cmd_stderr) > 0):
            logger.log(logging.ERROR, cmd_stderr)
        if proc.returncode != 0:
            raise SCTException("The process has exited with errorcode '%s'." % proc.returncode)
    return (cmd_stdout, cmd_stderr)

def run_command_legacy(popenargs):
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
        raise SCTException("The process has exited with errorcode '%s'." % process.returncode)
