#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 10:07:56
LastEditors: recar
LastEditTime: 2022-03-31 15:22:26
'''
from lib.log import logger
from lib.utils import Utils
from lib.work import ResultInfo
from lib.rate import rate_request
from lib.http_parser import HTTPParser
import json
import os


class Base(object):
    def __init__(self, report_work):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.logger = logger
        self.report_work = report_work
        self.utils = Utils
        self.request = rate_request
        
    def print_result(self, result):
        self.logger.info(json.dumps(result, sort_keys=True, indent=4, separators=(',', ':'), ensure_ascii=False))

    def to_result(self, result):
        plugins = result.get("plugins", "")
        url = result.get("url", "")
        payload = result.get("payload", "")
        # 对payload如果是list的结果就很多换行处理
        if type(payload)==list:
            payload = "</br>".join(payload)
        req = result.get("req", "")
        rsp = result.get("rsp", "")
        desc = result.get("desc", "")
        result_info = ResultInfo(plugins, url, payload, req, rsp, desc)
        self.report_work.put(result_info)

