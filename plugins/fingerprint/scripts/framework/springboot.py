#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-04-01 11:38:28
LastEditors: recar
LastEditTime: 2022-04-01 15:14:11
'''
from plugins.fingerprint.scripts.base import FingerprintCheck
from lib.utils import Utils
class Check(FingerprintCheck):
    def __init__(self):
        super(Check, self).__init__()
    
    def verify(self, url_info, req, rsp):
        host = url_info.get('base_url')
        self.name = "springboot"
        url = f"{host}/favicon.ico"
        try:
            response = self.request(url)
            ico_md5 = Utils.get_md5(response.text)
            if ico_md5=="0488faca4c19046b94d07c3ee83cf9d6":
                return True, self.name
        except:
            return False, None
        return False, None