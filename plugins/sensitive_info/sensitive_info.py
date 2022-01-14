#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-11 18:16:18
LastEditors: recar
LastEditTime: 2022-01-14 17:17:59
'''
from plugins.scan import Base
from lib.work import Worker, WorkData
import os


class SensitiveInfo(Base):
    def __init__(self, report_work):
        super(SensitiveInfo, self).__init__(report_work)
        self.plugins = "sensitive_info"
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self._load_dict()
        def consumer(work_data):
            url = work_data.url
            response = self.send_request(url, method="HEAD")
            if response is None:
                return
            test_response_len = response.headers.get("content-length")
            if test_response_len is None:
                test_response_len = 0
            if test_response_len!= self.response_404_len and \
                abs(int(test_response_len)-int(self.response_404_len))>50 and \
                response.status_code==200:
                self.logger.info(f"[+] SensitiveInfo: {url}")
                result = {
                    "plugins": self.plugins,
                    "url": url,
                    "payload": url,
                    "desc": "敏感信息泄露",
                    "req":"",
                    "rsp": ""
                }
                self.to_result(result)
        self.task_work = Worker(consumer, consumer_count=1)
        self.task_queue_map["SensitiveInfo task"] = self.task_work.work_queue

    def _get_404_header(self, url_info):
        url = url_info.get('url')
        path = self.utils.gen_random_str()
        test_url = f"{url}{path}"
        response = self.send_request(test_url, method="HEAD")
        if response is None:
            self.response_404_len = 0
            return
        self.response_404_len = response.headers.get("content-length")
        if self.response_404_len is None:
            self.response_404_len = 0
        self.logger.debug(f"response_404_len: {self.response_404_len}")

    def _load_dict(self):
        self.seninfo_list = list()
        dict_path = os.path.join(self.base_path,"sensitive_info.txt")
        with open(dict_path, "r") as f:
            for line in f:
                if "#" in line:
                    continue
                if line:
                    self.seninfo_list.append(line.strip())

    def run(self, url_info, req, rsp):
        if url_info.get("type") != "dynamic":
            return
        self._get_404_header(url_info)
        url = url_info.get('url')
        if url[-1]=="/":
            url = url[:-1]
        for path in self.seninfo_list:
            test_url = f"{url}{path}"
            work_data = WorkData()
            work_data.url = test_url
            self.task_work.put(work_data)

'''
需要存储404页面 后面需要比较是否是404页面
随机UA
字典及匹配
'''

