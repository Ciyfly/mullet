#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 10:07:56
LastEditors: recar
LastEditTime: 2022-01-12 17:17:27
'''
import os
import urllib.parse
from lib.log import logger

class Base(object):
    def __init__(self, result_queue):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.logger = logger
        self.result_queue = result_queue

    def url_completion(self, url, path):
        if "http" in path:
            return path
        parse_url =  urllib.parse.urlparse(url)
        scheme = parse_url.scheme
        netloc = parse_url.netloc
        return f"{scheme}://{netloc}{path}"

    def to_result(self, result):
        self.result_queue.put(result)
