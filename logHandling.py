# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 18:00:20 2021

@author: zefyr
"""

import logging

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    '''
    from https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings
    '''

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger