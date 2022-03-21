#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 11:05:17
LastEditors: recar
LastEditTime: 2022-03-21 15:59:45
'''
from lib.work import Worker
from plugins.report import Report
from plugins.fingerprint.fingerprint import Fingerprint
from plugins.sensitive_info.sensitive_info import SensitiveInfo
from plugins.general.general import General
from plugins.poc.poc_scan import PocScan
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
        # poc 模块
        self.poc_handler = PocScan(self.report_work, block=self.block)


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
            # poc这里要按指纹来跑
            # report_info 上面的检测结果
            for result_info in self.report.result_list:
                plugins = result_info.plugins
                if plugins == "fingerprint":
                    payload = result_info.payload
                    self.logger.debug("fingerprint: {0} ->poc".format(payload))
                    self.poc_handler.run(url_info, req, rsp, payload)
                #TODO 其他的
            return
