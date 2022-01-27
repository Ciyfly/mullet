#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 11:05:17
LastEditors: recar
LastEditTime: 2022-01-26 17:49:17
'''
from re import I, U
from lib.work import Worker, WorkData
from plugins.report import Report
from plugins.fingerprint.fingerprint import Fingerprint
from plugins.sensitive_info.sensitive_info import SensitiveInfo
from lib.log import logger
from lib.utils import Utils
import importlib
import time
import copy
import sys
import os



class Controller(object):
    def __init__(self,):
        self.domains = dict()
        self.urls = dict()
        self.logger = logger
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.plugins_dir = os.path.join(self.base_path, "../", 'plugins')
        self.general_plugins_dir = os.path.join(self.plugins_dir, "general")

        # 类注册到sys pth
        # 通用
        sys.path.append(self.general_plugins_dir)
        # poc

    def init(self):
        self.logger.info("Controller Init !!!")
        # 启动报告模块
        self.report = Report()
        self.report_work = self.report.report_work
        self._run_fingerprint()
        self._run_sensitive_info()
        # 加载通用检测模块
        self._load_general_plugins()
        self._run_general()

    def _load_general_plugins(self):
        '''
        加载通用url级的检查插件
        '''
        self.logger.info("load general plugins")
        self.general_plugins_dict = dict()
        for _, _, files in os.walk(self.general_plugins_dir):
            for filename in files:
                plugins_name = filename.split(".")[0]
                if plugins_name not in [self.general_plugins_dict.keys()]:
                    self.logger.info("plugins: {0}".format(plugins_name))
                    metaclass = importlib.import_module(plugins_name)
                    self.general_plugins_dict[plugins_name] = metaclass.Scan()
            break
        self.logger.info("general plugins count: {0}".format(len(self.general_plugins_dict.keys())))

    # 指纹
    def _run_fingerprint(self):
        fingerprint_handler = Fingerprint(self.report_work)
        def consumer(work_data):
            url_info = work_data.url_info
            req = work_data.req
            rsp = work_data.rsp
            fingerprint_handler.run(url_info, req, rsp)
        self.fingerprint_work = Worker(consumer, consumer_count=1)
        # self.task_queue_map["fingerprint"] = self.fingerprint_work.work_queue

    # 敏感信息
    def _run_sensitive_info(self):
        sensitiveInfo_handler = SensitiveInfo(self.report_work)
        def consumer(work_data):
            url_info = work_data.url_info
            req = work_data.req
            rsp = work_data.rsp
            sensitiveInfo_handler.run(url_info, req, rsp)
        self.sensitiveInfo_work = Worker(consumer, consumer_count=1)
        # self.task_queue_map["sensitiveInfo"] = self.sensitiveInfo_work.work_queue


    # 通用插件
    def _run_general(self):
        def consumer(work_data):
            url_info = work_data.url_info
            req = work_data.req
            rsp = work_data.rsp
            plugin_name = work_data.plugin_name
            self.logger.info("[*] gen task plugin: {0}".format(plugin_name))
            # 动态实例插件名称并传递req和rsp来执行
            # scan_plugins = Utils.object_copy(self.general_plugins_dict.get(plugin_name))
            scan_plugins = copy.copy(self.general_plugins_dict.get(plugin_name))
            scan_plugins.run(url_info, req, rsp)
        self.general_work = Worker(consumer, consumer_count=1)

    # # poc插件
    # # 先直接poc全发一下
    # def _run_poc(self):
    #     def consumer(data):
    #         data = data[1].get("data")
    #         plugins_name = data.get("plugins")
    #         req = data.get("req")
    #         rsp = data.get("rsp")
    #         url_info = data.get("url_info")
    #         # 动态实例插件名称并传递req和rsp来执行
    #         metaclass = importlib.import_module(plugins_name)
    #         metaclass.Scan().run(url_info, req, rsp)
    #     self.poc_work = Worker(consumer, consumer_count=10)

    def print_task_queue(self):
        while True:
            task_info = ""
            for plugins, queue in self.task_queue_map.items():
                task_info +="|{0}:{1}|".format(plugins, queue.qsize())
            sys.stdout.write("\r{0}".format(task_info))
            sys.stdout.flush()
            time.sleep(0.5)

    # 入口分发任务
    def run(self, url_info, req, rsp):
        domain =  url_info.get('host')
        gener_url = url_info.get("gener_url")
        if domain not in self.domains:
            self.domains[domain]=""
            self.logger.info(f"[*] gen task fingerprint: {domain}")
            # 推指纹
            work_data = WorkData()
            work_data.url_info = url_info
            work_data.req = req
            work_data.rsp = rsp
            self.fingerprint_work.put(work_data)
            # 推敏感信息扫描
            self.logger.info("gen task sensitive_info")
            self.logger.info("sensitive_info queue size: {0}".format(self.sensitiveInfo_work.work_queue.qsize()))
            self.sensitiveInfo_work.put(work_data)

            # 推poc
            #     self.logger.info("gen task poc")
            #     self.poc_work.put({
            #         "url_info": url_info,
            #         "req": req,
            #         "rsp": rsp
            #     })
            #     self.domains.add(domain)
        # if gener_url not in self.urls:
        #     # 推通用插件
        #     self.logger.debug("[*] gen task general")
        #     for plugin_name in self.general_plugins_dict.keys():
        #         work_data = WorkData()
        #         work_data.url_info = url_info
        #         work_data.req = req
        #         work_data.rsp = rsp
        #         work_data.plugin_name = plugin_name           
        #         self.general_work.put(work_data)
