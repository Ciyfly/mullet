#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-23 16:25:57
LastEditors: recar
LastEditTime: 2022-03-23 18:32:45
'''
from plugins.fingerprint.scripts.base import FingerprintCheck
import requests

class Check(FingerprintCheck):
    def __init__(self):
        super(Check, self).__init__()

    def verify(self, host):
        self.name = "shiro"
        url = f"{host}/"
        try:
            response=requests.get(url,cookies={"rememberMe":"recar"}, verify=False, allow_redirects=False, timeout=3)
        except:
            return False, None
        if "rememberMe=deleteMe" in response.headers['Set-Cookie']:
            return True, self.name
        return False, None
