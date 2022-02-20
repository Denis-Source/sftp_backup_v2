import logging

from config import Config


class Logger(logging.Logger):
    LOGGER_FORMAT = "%(asctime)s\t%(levelname)-7s\t%(name)-6s\t%(message)s"

    def __init__(self, name):
        super().__init__(name)
        self.add_c_handler()
        self.add_f_handler()

    def add_c_handler(self):
        handler = logging.StreamHandler()
        handler.setLevel(Config.LOGGING_COMMAND_LINE_LEVEL)
        formatter = logging.Formatter(self.LOGGER_FORMAT)
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def add_f_handler(self):
        handler = logging.FileHandler(Config.LOGGING_FILE)
        handler.setLevel(Config.LOGGING_FILE_LEVEL)
        formatter = logging.Formatter(self.LOGGER_FORMAT)
        handler.setFormatter(formatter)
        self.addHandler(handler)
