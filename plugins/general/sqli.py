#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-17 15:23:07
LastEditors: recar
LastEditTime: 2022-03-17 15:23:07
'''

from plugins.scan import Base


class Scan(Base):
    def __init__(self, report_work):
        super().__init__(report_work)
        self.plugins_name = "sqli"

    def run(self, url_info, req, rsp):
        url = url_info.get("url","")
        rsp_text = rsp.get('text',"")
        all_maps = dict()
