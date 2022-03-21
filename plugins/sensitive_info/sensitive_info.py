#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-11 18:16:18
LastEditors: recar
LastEditTime: 2022-03-21 15:59:20
'''
from plugins.scan import Base
from lib.work import Worker, WorkData
import os


class SensitiveInfo(Base):
    def __init__(self, report_work, block=True):
        super(SensitiveInfo, self).__init__(report_work)
        self.plugins = "sensitive_info"
        self.block = block
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.seninfo_dict = dict()
        self._load_dict()
        def consumer(work_data):
            url = work_data.url
            response = self.send_request(url, method="GET")
            if response is None:
                return
            condition_dict = work_data.condition
            for tag in condition_dict.keys():
                if tag == "status":
                    if str(response.status_code)!=str(condition_dict[tag]):
                        return False
                elif tag == "type":
                    if str(response.headers["content-type"])!=str(condition_dict[tag]):
                        return False
                elif tag == "match":
                    if str(condition_dict[tag]) not in response.text:
                        return False
            self.logger.info(f"[+] SensitiveInfo: {url}")
            result = {
                "plugins": self.plugins,
                "url": url,
                "payload": url,
                "desc": "敏感信息泄露",
            }
            self.to_result(result)
        self.seninfo_work = Worker(consumer, consumer_count=1, block=self.block)

    def _load_dict(self):
        dict_path = os.path.join(self.base_path,"sensitive_info.txt")
        with open(dict_path, "r") as f:
            for line in f:
                # 排除注释
                line = line.strip().replace('"',"")
                if "#" in line:
                    continue
                if not line:
                    continue
                path = line.split("            ")[0]
                condition_list = line.split("            ")[1].split("    ")
                condition_dict = dict()
                for condition in condition_list:
                    if not condition:
                        continue
                    condition = condition.replace("{", "").replace("}", "")
                    tag = condition.split("=")[0].strip()
                    value = condition.split("=")[-1].strip()
                    condition_dict[tag]=value
                self.seninfo_dict[path] = condition_dict
        self.logger.debug("load sensitive_info dict: {}".format(len(self.seninfo_dict)))

    def run(self, url_info, req, rsp):
        if url_info.get("type") != "dynamic":
            return
        url = url_info.get('base_url')
        if url[-1]=="/":
            url = url[:-1]
        for path in self.seninfo_dict.keys():
            test_url = f"{url}{path}"
            work_data = WorkData()
            work_data.url = test_url
            self.logger.debug("senitive_info test url: {0}".format(test_url))
            work_data.condition = self.seninfo_dict[path]
            self.seninfo_work.put(work_data)



