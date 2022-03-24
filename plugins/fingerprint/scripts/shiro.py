#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-23 16:25:57
LastEditors: recar
LastEditTime: 2022-03-24 14:24:43
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
            response=self.request(url, cookies={"rememberMe":"recar"})
        except:
            return False, None
        if "rememberMe=deleteMe" in response.headers.get('Set-Cookie'):
            return True, self.name
        return False, None
