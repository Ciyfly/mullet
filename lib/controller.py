#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 11:05:17
LastEditors: Recar
LastEditTime: 2022-01-12 21:51:38
'''
from lib.work import Worker
from plugins.report import Report
from plugins.fingerprint.fingerprint import Fingerprint
from plugins.sensitive_info.dis_sen_info import DisSenInfo
from lib.log import logger
from lib.utils import Utils
from queue import Queue
import importlib
import os

class Controller(object):
    def __init__(self,):
        self.domains = set()
        self.urls = set()
        self.result_queue = Queue()
        self.logger = logger
        base_path = os.path.dirname(os.path.abspath(__file__))
        plugins_dir = os.path.join(base_path, "../", 'plugins')
        fingerprint_dir = os.path.join(plugins_dir, 'fingerprint')
        sensitive_info_dir = os.path.join(plugins_dir, 'sensitive_info')
        general_dir = os.path.join(plugins_dir, 'general')
        poc_dir = os.path.join(plugins_dir, 'poc')
        # 注册
        fingerprint_list = list()
        sensitive_info_list = list()
        general_list = list()
        poc_list = list()
        
        # 启动报告模块
        self.report = Report()
        self.report_work = self.report.report_work
        # report.run()
        # init modul
        self._run_fingerprint()
        # self._run_sensitive_info()
        # self._run_general()
        # self._run_poc()


    # 指纹
    def _run_fingerprint(self):
        fingerprint_handler = Fingerprint(self.report_work)
        def consumer(data):
            data = data[1].get("data")
            url_info = data.get("url_info")
            req = data.get("req")
            rsp = data.get("rsp")
            fingerprint_handler.run(url_info, req, rsp)
        self.fingerprint_work = Worker(consumer, consumer_count=1, logger=logger)

    # 敏感信息
    # def _run_sensitive_info(self):
    #     disSenInfo_handler = DisSenInfo(self.result_queue)
    #     def consumer(data):
    #         data = data[1].get("data")
    #         url_info = data.get("url_info")
    #         req = data.get("req")
    #         rsp = data.get("rsp")
    #         disSenInfo_handler.run(url_info, req, rsp)
    #     self.disSenInfo_work = Worker(consumer, consumer_count=1)

    # # 通用插件
    # def _run_general(self):
    #     def consumer(data):
    #         data = data[1].get("data")
    #         plugins_name = data.get("plugins")
    #         req = data.get("req")
    #         rsp = data.get("rsp")
    #         url_info = data.get("url_info")
    #         # 动态实例插件名称并传递req和rsp来执行
    #         metaclass = importlib.import_module(plugins_name)
    #         metaclass.Scan().run(url_info, req, rsp)
    #     self.general_work = Worker(consumer, consumer_count=10)

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


    # 入口分发任务
    def run(self, url_info, req, rsp):
        domain =  url_info.get('host')
        gener_url = url_info.get("gener_url")
        if domain not in self.domains:
            self.domains.add(domain)
            self.logger.info(f"[*] gen task fingerprint: {domain}")
            # 推指纹
            self.fingerprint_work.put({"data":{
                "url_info": url_info,
                "req": req,
                "rsp": rsp
            }})
            # 推敏感信息扫描
        #     self.logger.info("gen task disSenInfo")
        #     self.disSenInfo_work.put({
        #         "url_info": url_info,
        #         "req": req,
        #         "rsp": rsp
        #     })
        #     # 推poc
        #     self.logger.info("gen task poc")
        #     self.poc_work.put({
        #         "url_info": url_info,
        #         "req": req,
        #         "rsp": rsp
        #     })
        #     self.domains.add(domain)
        if gener_url not in self.urls:
            # 推通用插件
            self.logger.debug("[*] gen task general")
            self.urls.add(gener_url)
            # self.general_work.put({
            #     "url_info": url_info,
            #     "req": req,
            #     "rsp": rsp
            # })
