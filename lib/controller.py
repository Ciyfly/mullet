#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 11:05:17
LastEditors: recar
LastEditTime: 2022-03-21 14:25:32
'''
from lib.work import Worker, WorkData
from plugins.report import Report
from plugins.fingerprint.fingerprint import Fingerprint
from plugins.sensitive_info.sensitive_info import SensitiveInfo
from plugins.general.general import General
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
        self.pocs_dir = os.path.join(self.plugins_dir, "poc", "pocs")

        # 类注册到sys pth
        # 通用
        sys.path.append(self.general_plugins_dir)
        sys.path.append(self.pocs_dir)
        # poc

    def init(self, block=True):
        self.logger.info("Controller Init ")
        # 启动报告模块
        self.report = Report()
        # 阻塞状态 True的话是被动代理 False的话是主动扫描
        self.block = block
        # 报告
        self.report_work = self.report.report_work
        # 指纹
        self.fingerprint_handler = Fingerprint(self.report_work, block=self.block)
        # 敏感信息
        self.sensitiveInfo_handler = SensitiveInfo(self.report_work, block=self.block)
        # 通用检测模块
        if self.block:
            self.general_plugins_handler = General(self.report_work, block=self.block)

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
        self.logger.debug("block: {0}".format(self.block))
        if domain not in self.domains:
            self.logger.debug("Domain: {0}".format(domain))
            self.domains[domain]=""
            # 推指纹
            self.logger.debug("fingerprint")
            self.fingerprint_handler.run(url_info, req, rsp)

            # 推敏感信息扫描
            self.logger.debug("sensitiveInfo")
            self.sensitiveInfo_handler.run(url_info, req, rsp)
            # poc这里要按指纹来跑
            # TODO poc
            # 根据指纹的结果推poc
            # 指纹的结果怎么拿
            

        # 被动代理模式才用通用插件
        if self.block and gener_url not in self.urls:
            self.urls[gener_url]=""
            # 推通用插件
            self.general_plugins_handler.run(url_info, req, rsp)
        # 主动扫描的话阻塞任务
        if not self.block:
            while not self.fingerprint_handler.fingerprint_work.is_end():
                time.sleep(3)
            while not self.sensitiveInfo_handler.seninfo_work.is_end():
                time.sleep(3)                
            return
