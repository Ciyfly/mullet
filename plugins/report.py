#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 11:56:52
LastEditors: Recar
LastEditTime: 2022-01-12 22:04:33
'''

from lib.work import Worker
from lib.log import logger
from config.report_template import TEMPLATE
import os


class Report(object):
    def __init__(self):
        self.logger = logger
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.base_path,"../", "output")
        self.report_path = os.path.join(self.output_path, "report.html")
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
        # work
        def consumer(data):
            result = data[1]
            report_str = TEMPLATE.format(result)
            self.logger.info(report_str)
            with open(self.report_path, "w") as f:
                f.write(report_str)
        self.report_work = Worker(consumer, consumer_count=1, logger=logger)
