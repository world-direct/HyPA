import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import values


def get_module_logger(mod_name: str,
                      log_level=logging.DEBUG,
                      log_to_console=False):

    log_dir: str = os.getcwd()

    try:
        log_dir = sys.argv[1]
    except:
        pass

    log_file: str = os.path.basename(sys.argv[0]).split('.')[0]

    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if not logging.root.hasHandlers():
        handler = RotatingFileHandler(f"{log_dir}/{log_file}.log",
                                      maxBytes=values.LOG_MAX_FILE_MBYTES *
                                      1024 * 1024,
                                      backupCount=values.LOG_MAX_BACKUPS)
        handler.setLevel(log_level)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.root.addHandler(handler)

        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logging.root.addHandler(console_handler)

    logger = logging.getLogger(mod_name)
    logger.setLevel(log_level)

    return logger
