#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-21 15:28:29
LastEditors: recar
LastEditTime: 2022-03-23 10:07:53
'''

from lib.log import logger
from lib.work import Worker
from lib.utils import Utils
from plugins.scan import Base
from collections import defaultdict
import importlib
import copy
import sys
import os

class PocScan(Base):
    def __init__(self, report_work, block=True):
        super(PocScan, self).__init__(report_work)
        self.logger= logger
        self.timeout = 3
        self.block = block
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.plugins_name = "PocScan"
        self.result_list = list()
        self.poc_fingerprint_dict = defaultdict(list)
        self.poc_name_dict = dict()
        self.load_script()


    # 先加上所有script 然后copy测试
    def load_script(self):
        script_path = os.path.join(self.base_path, "pocs")
        for poc_dir in os.listdir(script_path):
            if poc_dir == "__pycache__":
                continue
            poc_dir_path = os.path.join(script_path, poc_dir)
            sys.path.append(poc_dir_path)
        all_poc_path_list = Utils.get_all_filepaths(script_path)
        count = 0
        for poc_path in all_poc_path_list:
            _, poc = os.path.split(poc_path)
            if not poc.endswith(".py"):
                continue
            poc = poc.replace(".py", "")
            if poc=="base":
                continue
            metaclass = importlib.import_module(poc)
            poc_class = metaclass.Poc()
            fingerprint = poc_class.fingerprint
            name = poc_class.name
            self.poc_fingerprint_dict[fingerprint].append(poc_class)
            self.poc_name_dict[poc] = poc_class
            count +=1
        self.logger.debug("poc count: {0}".format(count))

    def run_poc_by_name(self, url_info, req, rsp, poc_name):
        '''
        指定poc_file_name run poc
        '''
        base_url = url_info.get('base_url')
        ip = url_info.get('ip')
        port = url_info.get('port')
        poc_class = self.poc_name_dict[poc_name]
        poc_plugins = copy.copy(poc_class)
        match, result = poc_plugins.run(self.logger, self.report_work, url_info)
        if match:
            result = {
                "plugins": self.plugins_name,
                "payload": result,
                "url": base_url,
                "url_info": url_info,
                "desc": "poc验证"
            }
            self.print_result(result)
        
    def run(self, url_info, req, rsp, fingerprint):
        base_url = url_info.get('base_url')
        ip = url_info.get('ip')
        port = url_info.get('port')        
        def consumer(poc_plugins):
            match, result = poc_plugins.run(self.logger, self.report_work, url_info)
            if match:
                self.logger.info("[+] PocScan: {0}".format(result.get("plugins")))
                result["url_info"] = url_info
                self.to_result(result)
        self.poc_work = Worker(consumer, consumer_count=10, block=self.block)        
        plugins_class_list = self.poc_fingerprint_dict.get(fingerprint)
        if plugins_class_list is None:
            return
        for plugins_class in plugins_class_list:
            poc_plugins = copy.copy(plugins_class)
            self.logger.debug("test poc: {0}".format(plugins_class.name))
            self.poc_work.put(poc_plugins)
