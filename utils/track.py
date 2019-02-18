import logging
import time

class Track:


    def __init__(self):
        logging.getLogger().setLevel(logging.INFO)
        self.start_time=None
        self.end_time=None

    def info(self,msg):
        logging.info(msg)

    def warn(self,msg):
        logging.warning(msg)

    def start_timer(self):
        self.start_time=time.time()

    def stop_timer(self):
        self.end_time=time.time()

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def createLogFile(self,output_dir):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=output_dir, level=logging.INFO)

    def get_exection_time(self):
        if self.start_time and self.end_time:
            logging.info(str(self.end_time-self.start_time)+" seconds")
            return
        logging.warn("time was not tracked")
