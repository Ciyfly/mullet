#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-14 11:29:39
LastEditors: recar
LastEditTime: 2022-01-14 15:16:08
'''
from urllib.parse import unquote
from lib.utils import Utils
from lib.log import logger
import traceback
import requests


class HTTPParser(object):

    @staticmethod
    def flow_to_urlinfo(flow):
        url_info = dict()
        url = flow.request.url
        url = unquote(url, 'utf-8')
        url_suffix = Utils.get_url_suffix(url)
        if url_suffix not in [
                    "png", "css", "jpg", "svg",
                    "ttf", "eot", "eot", "woff2", "gif",
                    "bmp" "svg", "less", "sass", "scss", "ico",
                    "woff", "html", "md", "htm"]:
            if  url_suffix == "js":
                url_info["type"] = "js"
            elif url_suffix in ["jsp", "php", "asp", "aspx"]:
                url_info["type"] = url_suffix
            else:
                url_info["type"] = "dynamic"
            gener_url = Utils.generalization(url)
            url_info["gener_url"] = gener_url
            url_info["url"] = url
            url_info["host"] = flow.request.host
            url_info["server_port"] = flow.server_conn.ip_address[1]
            url_info["server_ip"] = flow.server_conn.ip_address[0]
        return url_info

    @staticmethod
    def flow_to_req(flow):
        def raw(request):
            req_data = '%s %s %s\r\n' % (str(request.method), str(request.path), str(request.http_version))
            # Add headers to the request
            for k, v in request.headers.items():
                req_data += k + ': ' + v + '\r\n'
            req_data += '\r\n'
            req_data += str(request.raw_content)
            return req_data
        req = dict()
        req["host"] = flow.request.host
        req["method"] = flow.request.method
        req["scheme"] = flow.request.scheme
        req["authority"] = flow.request.authority
        req["path"] = flow.request.path
        req["http_version"] = flow.request.http_version
        req["headers"] = flow.request.headers
        req["text"] = str(flow.request.content)
        req["timestamp_start"] = flow.request.timestamp_start
        req["timestamp_end"] = flow.request.timestamp_end
        req["raw"] = raw(flow.request)
        return req

    @staticmethod
    def flow_to_rsp(flow):
        rsp = dict()
        rsp["status_code"] = flow.response.status_code
        rsp["reason"] = flow.response.reason
        rsp["headers"] = flow.response.headers
        rsp["text"] = str(flow.response.content)
        rsp["timestamp_start"] = flow.response.timestamp_start
        rsp["timestamp_end"] = flow.response.timestamp_end
        return rsp

    @staticmethod
    def reqs_to_urlinfo(reqs):
        url_info = dict()
        url = reqs.url
        url = unquote(url, 'utf-8')
        url_suffix = Utils.get_url_suffix(url)
        if url_suffix not in [
                    "png", "css", "jpg", "svg",
                    "ttf", "eot", "eot", "woff2", "gif",
                    "bmp" "svg", "less", "sass", "scss", "ico",
                    "woff", "html", "md", "htm"]:
            if  url_suffix == "js":
                url_info["type"] = "js"
            elif url_suffix in ["jsp", "php", "asp", "aspx"]:
                url_info["type"] = url_suffix
            else:
                url_info["type"] = "dynamic"
            gener_url = Utils.generalization(url)
            url_info["gener_url"] = gener_url
            url_info["url"] = url
            url_info["host"] = reqs.headers.get("host")
        return url_info

    @staticmethod
    def reqs_to_req(reqs):
        http_version_map = {
            10: "HTTP/1.0",
            11: "HTTP/1.1"
        }
        def raw(reqs):
            req_data = '%s %s %s\r\n' % (str(reqs.method), str(reqs.path_url), str(http_version_map[reqs.raw.version]))
            # Add headers to the request
            for k, v in reqs.headers.items():
                req_data += k + ': ' + v + '\r\n'
            req_data += '\r\n'
            req_data += str(reqs.raw_content)
            return req_data
        req = dict()
        req["url"] = reqs.url
        req["method"] = reqs.method
        req["scheme"] = reqs.scheme
        req["path"] = reqs.path_url
        req["http_version"] = http_version_map[reqs.raw.version]
        req["headers"] = reqs.headers
        req["text"] = str(reqs.body)
        req["raw"] = raw(reqs)
        return req

    @staticmethod
    def rsps_to_rsp(rsps):
        rsp = dict()
        rsp["status_code"] = rsps.status_code
        rsp["headers"] = rsps.headers
        rsp["text"] = str(rsps.text)
        return rsp

    @staticmethod
    def get_res_req_by_url(url):
        headers = dict()
        headers["User-Agent"] = Utils.get_random_ua()
        try:
            response = requests.get(url,headers=headers,timeout=10)
            return response, response.request
        except:
            logger.error("req error: {0} : {1}".format(url, traceback.format_exc()))