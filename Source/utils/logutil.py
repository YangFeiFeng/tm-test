import logging
import os
from logging.handlers import TimedRotatingFileHandler
from settings import LOG_PATH

os.makedirs(LOG_PATH, exist_ok=True)


class Log(object):
    log_instance_list = []

    @staticmethod
    def get_logger(name='main'):
        log_instance = 'log_' + name

        if name not in Log.log_instance_list:
            setattr(Log, log_instance, logging.getLogger(name))
            _logger = getattr(Log, log_instance)
            log_path = os.path.join(LOG_PATH, name + '.log')
            _logger.setLevel(logging.DEBUG)
            _logger = Log.add_console_handler(_logger)
            _logger = Log.add_timed_rotating_file_handler(_logger, log_path)
            Log.log_instance_list.append(name)
            return getattr(Log, log_instance)

    @staticmethod
    def add_console_handler(_logger):
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s [func:%(funcName)s] [line:%(lineno)d]  %(message)s")
        console.setFormatter(formatter)
        _logger.addHandler(console)
        return _logger

    @staticmethod
    def add_timed_rotating_file_handler(_logger, log_path):
        handler = TimedRotatingFileHandler(log_path, 'D', 1, 20)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s [file:%(filename)s] [func:%(funcName)s] [line:%(lineno)d] [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        _logger.addHandler(handler)
        return _logger

logger = Log.get_logger()
