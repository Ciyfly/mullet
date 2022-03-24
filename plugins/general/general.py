#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-18 18:23:19
LastEditors: recar
LastEditTime: 2022-03-24 18:43:43
'''

from lib.log import logger
from lib.work import Worker
from lib.utils import Utils
from plugins.scan import Base
import importlib
import copy
import sys
import os

class General(Base):
    def __init__(self, report_work, block=True):
        super(General, self).__init__(report_work)
        self.logger= logger
        self.timeout = 3
        self.block = block
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.plugins_name = "general"
        self.result_list = list()
        self.general_dict = dict()
        self.load_script()

    # 先加上所有script 然后copy测试
    def load_script(self):
        script_path = os.path.join(self.base_path, "scripts")
        sys.path.append(script_path)
        all_general_path_list = Utils.get_all_filepaths(script_path)
        for general_path in all_general_path_list:
            _, general = os.path.split(general_path)
            if not general.endswith(".py"):
                continue
            general = general.replace(".py", "")
            if general=="base":
                continue
            metaclass = importlib.import_module(general)
            self.general_dict[general] = metaclass.Scan(self.report_work)
        self.logger.info("general count: {0}".format(len(self.general_dict.keys())))            

    def run(self, url_info, req, rsp, open_plugins_list=None):
        url =  url_info.get('url')
        def consumer(data):
            general_name, url = data
            general_plugins = copy.copy(self.general_dict.get(general_name))
            match, result = general_plugins.verify(url_info, req, rsp)
            if match:
                result = {
                    "plugins": self.plugins_name,
                    "payload": result,
                    "url": url,
                    "url_info": url_info,
                    "desc": "通用模块"
                }
                self.to_result(result)
        self.general_work = Worker(consumer, consumer_count=10, block=self.block)
        for general_name in self.general_dict.keys():
            if general_name in open_plugins_list:
                self.logger.debug("general plugins: {0}".format(general_name))
                self.general_work.put((general_name, url))
