# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 12:22:12 2021

@author: zefyr
"""

import logging
import os
import datetime

class Logger:
    '''
    Used for logging.
    '''
    
    def __init__(self):
        if not os.path.exists("logs"): os.makedirs("logs")
        file = "logs\\"+datetime.datetime.now().strftime("%H%M%S.txt")
        logFormat = "%(asctime)s::%(levelname)s::%(name)s::"\
                     "%(filename)s::%(lineno)d::%(message)s"
        print("creating log")
        logging.basicConfig(level='DEBUG', filename=file, format=logFormat)
        
        self.logger = logging.getLogger(__name__)