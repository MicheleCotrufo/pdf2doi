# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 23:23:42 2021

@author: michele
"""
import logging
logging.basicConfig(format="%(message)s", level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')
logging.error('And non-ASCII stuff, too, like Øresund and Malmö')