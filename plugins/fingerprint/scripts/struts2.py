#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-21 20:39:10
LastEditors: recar
LastEditTime: 2022-03-23 18:31:17
'''

from plugins.fingerprint.scripts.base import FingerprintCheck
import requests

class Check(FingerprintCheck):
    def __init__(self):
        super(Check, self).__init__()
    
    def verify(self, host):
        self.name = "struts2"
        url = f"{host}/"
        try:
            response = requests.get(url, timeout=3)
        except:
            return False, None
        set_cookie = response.headers["Set-Cookie"]
        # if set_cookie.startswith("JSESSIONID=C09CBBF") and set_cookie.endswith("7CF6D25D4F0"):
        if set_cookie.startswith("JSESSIONID="):
            return True, self.name
        return False, None
