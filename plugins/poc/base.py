#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-04 15:31:48
LastEditors: recar
LastEditTime: 2022-03-24 11:45:25
'''

# poc
from lib.rate import rate_request
import requests
import random
import string
import base64
import hashlib


requests.packages.urllib3.disable_warnings()

def raw2req(raw):
        CRLF ="\n"
        def _parse_request_line(request_line):
            request_parts = request_line.split(' ')
            method = request_parts[0]
            path = request_parts[1]
            protocol = request_parts[2] if len(request_parts) > 2 else "HTTP 1.1"
            return method, path, protocol

        req_lines = raw.split("\n")
        method, path, protocol = _parse_request_line(req_lines[0])
        ind = 1
        headers = dict()
        while ind < len(req_lines) and len(req_lines[ind]) > 0:
            colon_ind = req_lines[ind].find(':')
            header_key = req_lines[ind][:colon_ind]
            header_value = req_lines[ind][colon_ind + 1:]
            headers[header_key] = header_value.strip()
            ind += 1
        ind += 1
        body = req_lines[ind:] if ind < len(req_lines) else None
        is_json = headers.get('Content-Type')
        if body is not None:
            if is_json=="application/json":
                 body = "".join([b.strip() for b in body])
            else:
                body = CRLF.join(body)
        return method, path, headers, body


def rsp2req_raw(response):
    request = response.request
    http_version_int = response.raw.version
    if http_version_int ==10:
        http_version = "HTTP/1.0"
    else:
        http_version = "HTTP/1.1"
    raw = '%s %s %s\r\n' % (request.method, str(request.path_url), http_version)
    # Add headers to the request
    req_data = ""
    for k, v in request.headers.items():
        req_data += k + ': ' + v + '\r\n'
    req_data += '\r\n'
    req_data += str(request.body)
    return raw    


class PocBase(object):

    def __init__(self,):
        pass
    
    def setup(self):
        ''' 
        测试前准备 比如需要先发几个包去做最后验证的前置条件
        '''
        pass

    def send_payload(self):
        '''
        验证前的最后一个发送请求
        '''
        pass

    def verify(self):
        pass

    def tear_down(self):
        '''
        清理方法 有些poc需要清除前置条件
        '''
        pass


    
    def send_raw(self, raw):
        method,path,headers, data = raw2req(raw)
        url = "{0}{1}".format(self.base_url, path)
        headers["host"] ="{0}:{1}".format(self.ip, self.port)
        tmp = self.request(method, url, headers=headers, data=data, verify=False)
        return tmp


    # 辅助函数

    def gen_random_str(self, size=8):
        return ''.join(random.sample(string.ascii_letters + string.digits, size)).lower()

    def gen_random_int(self, a, b):
        return  random.randint(a, b)

    def base64(self, s):
        return base64.b64encode(s.encode())

    def unbase64(self, s):
        return base64.b64decode(s).decode()

    def md5(self, s):
        return hashlib.md5(s.encode()).hexdigest()

    # 统一入口
    def run(self, logger, report_work, url_info):
        self.request = rate_request
        # 初始化赋值
        self.logger = logger
        self.report_work = report_work
        self.url_info = url_info
        self.base_url = url_info.get('base_url')
        self.ip = url_info.get('ip')
        self.port = url_info.get('port')
        # 测试流程
        # 前置条件
        self.setup()
        # 验证
        verify_status, payload = self.verify()
        self.logger.debug("{0}  verify_status: {1}".format(self.name, verify_status))
        # 清理环境
        self.tear_down()
        result = dict()
        if verify_status:
            result = {
                "plugins": self.name,
                "payload": payload,
                "url": self.base_url,
                "desc": self.desc
            }
        return verify_status, result

