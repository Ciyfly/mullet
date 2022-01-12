#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 11:56:52
LastEditors: recar
LastEditTime: 2022-01-12 18:53:37
'''

import os


class Report(object):
    def __init__(self, result_queue):
        self.result_queue = result_queue
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.report_template_path = os.path.join(self.base_path,"../", "config", "report.template")
        self.output_path = os.path.join(self.base_path,"../", "output")
        self.report_path = os.path.join(self.output_path, "report.html")
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
        with open(self.report_path, "a+") as f:
            self.report_str = f.read()
        
    def run(self):
        while True:
            result = self.result_queue.get()
            self.report_str.format(result)
            with open(self.report_path, "w") as f:
                f.write(self.report_str)
