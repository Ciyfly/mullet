#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 10:07:56
LastEditors: recar
LastEditTime: 2022-01-26 11:21:08
'''
from lib.log import logger
from lib.utils import Utils
from lib.work import ResultInfo
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
        plugins = result.get("plugins", "")
        url = result.get("url", "")
        payload = result.get("payload", "")
        req = result.get("req", "")
        rsp = result.get("rsp", "")
        desc = result.get("desc", "")
        result_info = ResultInfo(plugins, url, payload, req, rsp, desc)
        self.report_work.put(result_info)

    # 发起请求
    def send_request(self, url,method="GET",headers=None,data=None,timeout=10):
        if headers is None:
            headers = dict()
        headers["User-Agent"] = self.utils.get_random_ua()
        response = None
        if method == "GET":
            try:
                response = requests.get(url,headers=headers,timeout=timeout)
            except Exception:
                pass
        elif method == "POST":
            try:
                response = requests.post(url,headers=headers, data=data,timeout=timeout)
            except Exception:
                pass
        elif method == "HEAD":
            try:
                response = requests.head(url,headers=headers,timeout=timeout)
            except Exception:
                pass
        return response
