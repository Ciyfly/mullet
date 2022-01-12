#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 10:07:56
LastEditors: Recar
LastEditTime: 2022-01-12 21:51:06
'''
import os
import urllib.parse
from lib.log import logger

class Base(object):
    def __init__(self, report_work):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.logger = logger
        self.report_work = report_work

    def url_completion(self, url, path):
        if "http" in path:
            return path
        parse_url =  urllib.parse.urlparse(url)
        scheme = parse_url.scheme
        netloc = parse_url.netloc
        return f"{scheme}://{netloc}{path}"

    def to_result(self, result):
        self.report_work.put(result)
