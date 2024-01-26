import logging

LIBRARY_LOG_IDENTIFIER = "EnterpriseWeb"

def get_logger():
    return logging.getLogger(__name__)
