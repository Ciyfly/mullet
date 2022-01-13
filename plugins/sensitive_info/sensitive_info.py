#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-11 18:16:18
LastEditors: recar
LastEditTime: 2022-01-13 19:04:29
'''
from plugins.scan import Base
from lib.work import Worker
import os


class SensitiveInfo(Base):
    def __init__(self, report_work):
        super(SensitiveInfo, self).__init__(report_work)
        self.plugins = "sensitive_info"
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self._load_dict()
        def consumer(data):
            data = data[1]
            url = data.get('url')
            response = self.send_request(url, method="HEAD")
            test_response_len = response.headers.get("content-length")
            if test_response_len!= self.response_404_lengeth and abs(test_response_len-self.response_404_len)>100:
                self.report_work.put({
                    "plugins": self.plugins,
                    "url": url,
                    "payload": url,
                    "desc": "敏感信息泄露"
                })
        self.task_work = Worker(consumer, consumer_count=10, logger=self.logger)

    def _get_404_header(self, url_info):
        url = url_info.get('url')
        path = self.utils.gen_random_str()
        test_url = f"{url}{path}"
        response = self.send_request(test_url, method="HEAD")
        self.response_404_lengeth = response.headers.get("content-length")

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
        self._get_404_header(url_info)
        url = url_info.get('url')
        for path in self.seninfo_list:
            test_url = f"{url}{path}"
            self.task_work.put({"url": test_url})

'''
需要存储404页面 后面需要比较是否是404页面
随机UA
字典及匹配
'''

