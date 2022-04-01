#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-04-01 11:12:01
LastEditors: recar
LastEditTime: 2022-04-01 14:09:10
'''
from plugins.fingerprint.scripts.base import FingerprintCheck

class Check(FingerprintCheck):
    def __init__(self):
        super(Check, self).__init__()
    
    def verify(self, url_info, req, rsp):
        self.name = "django"
        server = rsp.get("headers").get("server")
        if server.startswith("WSGIServer") and "CPython" in server:
            return True, self.name
        return False, None
