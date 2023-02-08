#!/usr/bin/env python

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def notify_user(author_username):
    if author_username:
        logger.info(f"MR deployée @{author_username}")
    else:
        return "Failed to get username"
    return 'OK'
    