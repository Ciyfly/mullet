#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-11 18:16:18
LastEditors: recar
LastEditTime: 2022-03-18 17:36:47
'''
from lib.log import logger
from lib.work import Worker
from lib.utils import Utils
from plugins.scan import Base
import traceback
import importlib
import copy
import json
import sys
import os

class Fingerprint(Base):
    def __init__(self, report_work):
        super(Fingerprint, self).__init__(report_work)
        self.logger= logger
        self.timeout = 3
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.plugins_name = "fingerprint"
        self.result_list = list()
        self.fingerprint_dict = dict()
        self.load_script()


    # 先加上所有script 然后copy测试
    def load_script(self):
        script_path = os.path.join(self.base_path, "scripts")
        sys.path.append(script_path)
        all_fingerprint_path_list = Utils.get_all_filepaths(script_path)
        for fingerprint_path in all_fingerprint_path_list:
            _, fingerprint = os.path.split(fingerprint_path)
            if not fingerprint.endswith(".py"):
                continue
            fingerprint = fingerprint.replace(".py", "")
            if fingerprint=="base":
                continue
            metaclass = importlib.import_module(fingerprint)
            self.fingerprint_dict[fingerprint] = metaclass.Check()
        self.logger.info("fingerprint count: {0}".format(len(self.fingerprint_dict.keys())))            

    def run(self, url_info, req, rsp):
        host = url_info.get('base_url')
        def consumer(data):
            fingerprint_name, host = data
            fingerprint_plugins = copy.copy(self.fingerprint_dict.get(fingerprint_name))
            match, result = fingerprint_plugins.verify(host)
            if match:
                result = {
                    "plugins": self.plugins_name,
                    "payload": result,
                    "url": host,
                    "url_info": url_info,
                    "desc": "指纹识别"
                }
                self.to_result(result)
        self.fingerprint_work = Worker(consumer, consumer_count=10, block=False)        
        for fingerprint_name in self.fingerprint_dict.keys():
            self.fingerprint_work.put((fingerprint_name, host))
