import logging
import time
from pathlib import Path
from s3b_common.s3b_tools import get_absolute_path

logFilename = None

def get_logfile_name():
    return logFilename

def initLogging():
    '''
    Initializes the logger.
    '''
    global logFilename
    
    logdir = get_absolute_path('logs')
    Path(logdir).mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    applicationName = 's3-backup'
    logFilename = '%s/%s_%s.log' % (logdir, timestamp, applicationName)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s", "%Y-%m-%d %H:%M:%S")

    # The logger
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)
    
    # File handler
    fileHandler = logging.FileHandler(logFilename)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.DEBUG)
    rootLogger.addHandler(fileHandler)

    # Console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.INFO)
    rootLogger.addHandler(consoleHandler)
    
    logging.debug('Logging initialized')
    logging.info('Logging to %s' % logFilename)
