#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-24 10:44:11
LastEditors: recar
LastEditTime: 2022-03-29 14:31:58
'''
from ratelimiter import RateLimiter
from requests.packages.urllib3.exceptions import InsecureRequestWarning
 
from lib.log import logger
import configparser
import requests
import os

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

base_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_path, "../", "config", "config.ini")
conf = configparser.ConfigParser()
conf.read(config_path)
max_calls = conf.getint("rate", "max_calls")
period = conf.getint("rate", "period")
timeout = conf.getint("rate", "timeout")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

@RateLimiter(max_calls=max_calls, period=period)
def rate_request(
    url, method='GET', data=None,
    headers=headers, verify=False,
    allow_redirects=False, cookies=None, timeout=timeout):
    try:
        # get potst 回调函数要加个
        logger.debug("rate url: {0}".format(url))
        response = requests.request(
            method=method, url=url, data=data, verify=verify,
            headers=headers, allow_redirects=allow_redirects,
            cookies=cookies, timeout=timeout)
        return response
    except :
        # logger.error(traceback.format_exc())
        return requests.Response()
