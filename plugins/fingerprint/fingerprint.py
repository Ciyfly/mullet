#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-11 18:16:18
LastEditors: recar
LastEditTime: 2022-04-07 18:08:38
'''
from lib.log import logger
from lib.work import Worker
from lib.utils import Utils
from plugins.scan import Base
import importlib
import copy
import sys
import os

class Fingerprint(Base):
    def __init__(self, report_work, block=True):
        super(Fingerprint, self).__init__(report_work)
        self.logger= logger
        self.timeout = 3
        self.block = block
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.plugins_name = "fingerprint"
        self.result_list = list()
        self.fingerprint_dict = dict()
        self.load_script()


    # 先加上所有script 然后copy测试
    def load_script(self):
        script_path = os.path.join(self.base_path, "scripts")
        framework_script_path = os.path.join(self.base_path, "scripts", "framework")
        sys.path.append(framework_script_path)
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
        self.logger.info("load fingerprint count: {0}".format(len(self.fingerprint_dict.keys())))            

    def run(self, url_info, req, rsp):
        def consumer(data):
            fingerprint_name, url_info, rsp = data
            fingerprint_plugins = copy.copy(self.fingerprint_dict.get(fingerprint_name))
            match, data = fingerprint_plugins.verify(url_info, req, rsp)
            if match:
                result = {
                    "plugins": self.plugins_name,
                    "payload": data,
                    "url": url_info.get("url"),
                    "url_info": url_info,
                    "desc": "指纹识别"
                }
                self.print_result(result)
                self.to_result(result)
        self.fingerprint_work = Worker(consumer, consumer_count=10, block=self.block)        
        for fingerprint_name in self.fingerprint_dict.keys():
            self.fingerprint_work.put((fingerprint_name, url_info, rsp))
