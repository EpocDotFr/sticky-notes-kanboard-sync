import sys
import logging

def debug(message, err=False, terminate=False):
    logging.getLogger().log(logging.ERROR if err else logging.INFO, message)

    if terminate:
        sys.exit(1)
