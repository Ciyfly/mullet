#!/usr/bin/python
# coding=utf-8
'''
Date: 2021-03-23 15:51:56
LastEditors: recar
LastEditTime: 2022-01-26 11:24:28
'''
from lib.http_parser import HTTPParser
from lib.data import controller
from lib.log import logger
import sys
sys.path.append('../')

class Filter(object):
    @staticmethod
    def parser_request(flow):
        del flow.request.headers['Accept-Encoding']

    @staticmethod
    def parser_response(flow):
        url_info = HTTPParser.flow_to_urlinfo(flow)
        req = HTTPParser.flow_to_req(flow)
        rsp = HTTPParser.flow_to_rsp(flow)
        # check
        if not url_info:
            return
        logger.debug("[*] url: {0} type: {1}".format(url_info["url"], url_info['type']))
        # insert url
        controller.run(url_info, req, rsp)



