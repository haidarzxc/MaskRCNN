import logging


class Track:
    def __init__(self):
        logging.getLogger().setLevel(logging.INFO)

    def info(self,msg):
        logging.info(msg)

    def warn(self,msg):
        logging.warn(msg)