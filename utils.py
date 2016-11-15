import sys
import logging
import re


def debug(message, err=False, terminate=False):
    """Log a regular or error message to the standard output, optionally terminating the script."""
    logging.getLogger().log(logging.ERROR if err else logging.INFO, message)

    if terminate:
        sys.exit(1)


def split_note_text(text):
    text_splitted = text.splitlines()

    return text_splitted[0], '\r\n'.join(text_splitted[1:]).strip()
