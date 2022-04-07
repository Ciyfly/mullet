#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-23 16:25:57
LastEditors: recar
LastEditTime: 2022-04-07 11:19:25
'''
from plugins.fingerprint.scripts.base import FingerprintCheck
import requests

class Check(FingerprintCheck):
    def __init__(self):
        super(Check, self).__init__()

    def verify(self, url_info, req, rsp):
        self.name = "shiro"
        if rsp.get("headers") and "rememberMe=deleteMe" in rsp.get("headers").get('Set-Cookie', ''):
            return True, self.name
        return False, None
