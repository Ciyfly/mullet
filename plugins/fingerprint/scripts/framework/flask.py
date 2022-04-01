#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-04-01 11:01:59
LastEditors: recar
LastEditTime: 2022-04-01 11:47:37
'''
from plugins.fingerprint.scripts.base import FingerprintCheck

class Check(FingerprintCheck):
    def __init__(self):
        super(Check, self).__init__()
    
    def verify(self, url_info, req, rsp)):
        self.name = "flask"
        server = rsp.get("headers").get("server")
        if server.startswith("Werkzeug") and "Python" in server:
            return True, self.name
        return False, None
