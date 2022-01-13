#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 11:56:52
LastEditors: Recar
LastEditTime: 2022-01-13 23:04:13
'''

from lib.work import Worker, ResultInfo
from lib.log import logger
from jinja2 import Environment, FileSystemLoader
import os


class Report(object):
    def __init__(self):
        self.logger = logger
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.base_path,"../", "output")
        self.output_report_path = os.path.join(self.output_path, "report.html")
        report_template_dir = os.path.join(self.base_path,"../", "config")
        # init result
        self.result_list = list()
        # init report template
        env = Environment(loader=FileSystemLoader(report_template_dir))
        self.report_template = env.get_template('report_template.html')

        # init output
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
        # work
        def consumer(result_info):
            self.result_list.append(result_info)
            report_content = self.report_template.render(items=self.result_list)
            with open(self.output_report_path, "w") as f:
                f.write(report_content)
            self.logger.debug("gen report by: {0}".format(result_info.plugins))

        self.report_work = Worker(consumer, consumer_count=1)
