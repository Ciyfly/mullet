#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-21 20:39:10
LastEditors: recar
LastEditTime: 2022-04-07 11:18:38
'''

from plugins.fingerprint.scripts.base import FingerprintCheck

class Check(FingerprintCheck):
    def __init__(self):
        super(Check, self).__init__()
    
    def verify(self, url_info, req, rsp):
        self.name = "struts2"
        set_cookie = rsp.get("headers").get("Set-Cookie")
        if set_cookie and set_cookie.startswith("JSESSIONID="):
            return True, self.name
        return False, None
