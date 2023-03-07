from datetime import datetime, timedelta
import logging
import os
from threading import Thread
import time


class RepeatingThread(Thread):
    """
    Creates and starts a thread as daemon, that repeatedly executes a given function in a given interval
    """
    def __init__(self, interval: timedelta, name, target):
        Thread.__init__(self)
        self.daemon = True
        self.name = name
        self.interval = interval
        self.target = target
        logging.info("Run {} every {}".format(self.name, self.interval))
        self.start()

    def run(self):
        try:
            while True:
                next_start = datetime.now() + self.interval
                self.target()
                if datetime.now() < next_start:
                    remaining_time = next_start - datetime.now()
                    logging.debug("Wait for {} until the next {}".format(remaining_time, self.name))
                    time.sleep(remaining_time.seconds)
        except Exception as ex:
            logging.error("Unhandled exception occurred in thread for {}: {}".format(self.name, repr(ex)))
            # Exit to trigger restart or notifications (would otherwise continue to run without this thread)
            os._exit(1)
