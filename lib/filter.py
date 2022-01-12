#!/usr/bin/python
# coding=utf-8
'''
Date: 2021-03-23 15:51:56
LastEditors: recar
LastEditTime: 2022-01-12 16:34:55
'''
from lib.utils import Utils
from lib.controller import Controller
from lib.log import logger
import sys
sys.path.append('../')
controller = Controller()

class Filter(object):
    @staticmethod
    def parser_request(flow):
        del flow.request.headers['Accept-Encoding']

    @staticmethod
    def parser_response(flow):
        url_info = Utils.parser_url(flow)
        req = Utils.parser_req(flow)
        rsp = Utils.parser_rsp(flow)
        # check
        if not url_info:
            return
        logger.debug("url: {0} type: {1}".format(url_info["url"], url_info['type']))
        # insert url
        controller.run(url_info, req, rsp)



