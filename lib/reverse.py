#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-22 11:01:24
LastEditors: recar
LastEditTime: 2022-03-22 15:24:10
'''
import configparser
import requests
import random
import string
import time
import os

# 反连平台  

class Reverse(object):
    def __init__(self, platform="ceye", time_wait=5):
        self.platform = platform
        self.time_wait = time_wait
        self.flag_str = self.gen_random_str()
        self.load_config()
        # return domain
        if self.platform=="ceye":
            self.domain = "{0}.{1}".format(self.flag_str, self.ceye_domain)
        elif self.platform=="dnslog":
            self.domain = "{0}.{1}".format(self.flag_str, self.dnslog_domain)

    def load_config(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "../","config", "config.ini")
        conf = configparser.ConfigParser()
        conf.read(config_path)
        # ceye
        if self.platform == "ceye":
            self.ceye_domain = conf.get('reverse', 'ceye_domain')
            self.ceye_token = conf.get('reverse', 'ceye_token')
        # dnslog
        elif self.platform == "dnslog":
            self.session = requests.Session()
            try:
                response = self.session.get("http://www.dnslog.cn/getdomain.php", timeout=10)
                self.dnslog_domain = response.text
            except:
                self.dnslog_domain = None

    def gen_random_str(self, size=8):
        return ''.join(random.sample(string.ascii_letters + string.digits, size))
        
    def verify(self):
        time.sleep(self.time_wait)
        if self.platform=="ceye":
            url = "http://api.ceye.io/v1/records?token={0}&type=dns&filter={1}".format(self.ceye_token, self.flag_str)
            try:
                response = requests.get(url, timeout=3)
                data = response.json()
                if len(data) >0:
                    return True
                return False
            except:
                return False
        elif self.platform=="dnslog":
            url = "http://www.dnslog.cn/getrecords.php"
            try:
                response = self.session.get(url, timeout=10)
                if self.flag_str in response.text:
                    return True
            except:
                return False
            




