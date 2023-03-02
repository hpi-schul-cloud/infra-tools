from datetime import datetime, timedelta
import logging
from threading import Thread
import time


class RepeatingThread(Thread):
    """
    Creates and starts a thread as deamon, that repeatatly executes a given function in a given interval
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
        while True:
            next_start = datetime.now() + self.interval
            self.target()
            if datetime.now() < next_start:
                remaining_time = next_start - datetime.now()
                logging.debug("Wait for {} until the next {}".format(remaining_time, self.name))
                time.sleep(remaining_time.seconds)
