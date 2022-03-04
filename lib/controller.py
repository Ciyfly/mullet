#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 11:05:17
LastEditors: recar
LastEditTime: 2022-03-04 17:52:56
'''
from lib.work import Worker, WorkData
from plugins.report import Report
from plugins.fingerprint.fingerprint import Fingerprint
from plugins.sensitive_info.sensitive_info import SensitiveInfo
from lib.log import logger
from lib.utils import Utils
import traceback
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
        self.pocs_dir = os.path.join(self.plugins_dir, "poc", "pocs")

        # 类注册到sys pth
        # 通用
        sys.path.append(self.general_plugins_dir)
        sys.path.append(self.pocs_dir)
        # poc

    def init(self):
        self.logger.info("Controller Init ")
        # 启动报告模块
        self.report = Report()
        self.report_work = self.report.report_work
        # self._run_fingerprint()
        # self._run_sensitive_info()
        # # 加载通用检测模块
        # self._load_general_plugins()
        # self._run_general()
        # 加载poc 和poc检测模块
        self._load_pocs()
        self._run_poc()

    def _load_general_plugins(self):
        '''
        加载通用url级的检查插件
        '''
        self.logger.info("load general plugins please wait a moment ~")
        self.general_plugins_dict = dict()
        for _, _, files in os.walk(self.general_plugins_dir):
            for filename in files:
                plugins_name = filename.split(".")[0]
                if plugins_name not in [self.general_plugins_dict.keys()]:
                    self.logger.info("plugins: {0}".format(plugins_name))
                    metaclass = importlib.import_module(plugins_name)
                    self.general_plugins_dict[plugins_name] = metaclass.Scan(self.report_work)
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
            # self.logger.info("[*] gen task plugin: {0}".format(plugin_name))
            # 动态实例插件名称并传递req和rsp来执行
            # scan_plugins = Utils.object_copy(self.general_plugins_dict.get(plugin_name))
            scan_plugins = copy.copy(self.general_plugins_dict.get(plugin_name))
            scan_plugins.run(url_info, req, rsp)
        self.general_work = Worker(consumer, consumer_count=1)

    # poc插件

    # 先直接poc全发一下
    def _load_pocs(self):
        self.logger.info("load pocs")
        self.poc_pocs_dict = dict()
        all_pocs_path_list = Utils.get_all_filepaths(self.pocs_dir)
        for poc_path in all_pocs_path_list:
            _, poc_name = os.path.split(poc_path)
            if not poc_name.endswith(".py"):
                continue
            poc_name = poc_name.replace(".py", "")
            self.logger.info("poc_name: {0}".format(poc_name))
            metaclass = importlib.import_module(poc_name)
            self.poc_pocs_dict[poc_name] = metaclass.Poc()
        self.logger.info("poc count: {0}".format(len(self.poc_pocs_dict.keys())))
    
    def _run_poc(self):
        def consumer(work_data):
            poc_name = work_data.poc_name
            ip = work_data.ip
            port = work_data.port
            ssl = work_data.ssl
            poc_plugin = copy.copy(self.poc_pocs_dict.get(poc_name))
            poc_plugin.run(self.logger, self.report_work, ip, port, ssl=ssl)
        self.poc_work = Worker(consumer, consumer_count=10)

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
            self.logger.debug(f"[*] gen task fingerprint: {domain}")
            # 推指纹
            work_data = WorkData()
            work_data.url_info = url_info
            work_data.req = req
            work_data.rsp = rsp
            # self.fingerprint_work.put(work_data)
            # 推敏感信息扫描
            # self.logger.debug("gen task sensitive_info")
            # self.sensitiveInfo_work.put(work_data)

            # 推poc poc暂时直接打就完事了
            self.logger.info("gen task poc")
            for poc_name in self.poc_pocs_dict.keys():
                work_data.poc_name = poc_name
                self.poc_work.put(work_data)

        # if gener_url not in self.urls:
        #     self.urls[gener_url]=""
        #     # 推通用插件
        #     for plugin_name in self.general_plugins_dict.keys():
        #         work_data = WorkData()
        #         work_data.url_info = url_info
        #         work_data.req = req
        #         work_data.rsp = rsp
        #         work_data.plugin_name = plugin_name           
        #         self.general_work.put(work_data)
