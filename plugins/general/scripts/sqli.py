#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-24 09:46:27
LastEditors: recar
LastEditTime: 2022-03-24 09:46:28
'''
from plugins.scan import Base


class Scan(Base):
    def __init__(self, report_work):
        super().__init__(report_work)

    def verify(self, url_info, req, rsp):
        url = url_info.get("url","")
        rsp_text = rsp.get('text',"")
        

