#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-17 17:09:30
LastEditors: recar
LastEditTime: 2022-03-24 11:44:53
'''

from lib.log import logger
from lib.rate import rate_request

class FingerprintCheck(object):
    def __init__(self):
        self.logger = logger
        self.request = rate_request

