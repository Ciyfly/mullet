#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 10:07:56
LastEditors: recar
LastEditTime: 2022-01-13 18:58:22
'''
from lib.log import logger
from lib.utils import Utils
import urllib.parse
import traceback
import requests
import os


class Base(object):
    def __init__(self, report_work):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.logger = logger
        self.report_work = report_work
        self.utils = Utils

    def url_completion(self, url, path):
        if "http" in path:
            return path
        parse_url =  urllib.parse.urlparse(url)
        scheme = parse_url.scheme
        netloc = parse_url.netloc
        return f"{scheme}://{netloc}{path}"

    def to_result(self, result):
        self.report_work.put(result)

    # 发起请求
    def send_request(self, url,method="GET",headers=None,data=None,timeout=10):
        headers["User-Agent"] = self.utils.get_random_ua()
        if method == "GET":
            try:
                response = requests.get(url,headers=headers,timeout=timeout)
            except Exception:
                self.logger.error(traceback.format_exc())
        elif method == "POST":
            try:
                response = requests.post(url,headers=headers, data=data,timeout=timeout)
            except Exception:
                self.logger.error(traceback.format_exc())
        elif method == "HEAD":
            try:
                response = requests.head(url,headers=headers,timeout=timeout)
            except Exception:
                self.logger.error(traceback.format_exc())            
        return response
