#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-17 17:09:23
LastEditors: recar
LastEditTime: 2022-04-01 15:09:34
'''

from plugins.fingerprint.scripts.base import FingerprintCheck

class Check(FingerprintCheck):
    def __init__(self):
        super(Check, self).__init__()
    
    def verify(self, url_info, req, rsp):
        host = url_info.get('base_url')
        self.name = "thinkphp"
        url = f"{host}/?c=4e5e5d7364f443e28fbf0d3ae744a59a"
        try:
            response = self.request(url)
        except:
            return False, None
        if "IHDR" in response.text and "PNG" in response.text:
            return True, self.name
        return False, None
