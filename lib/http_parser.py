#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-14 11:29:39
LastEditors: recar
LastEditTime: 2022-04-07 11:40:59
'''
from urllib.parse import unquote
from urllib.parse import urlparse, parse_qs
from lib.utils import Utils
from lib.log import logger
import traceback
import requests

http_version_map = {
    10: "HTTP/1.0",
    11: "HTTP/1.1"
}

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
                    "woff", "md"]:
            if  url_suffix == "js":
                url_info["type"] = "js"
            elif url_suffix in ["jsp", "php", "asp", "aspx"]:
                url_info["type"] = url_suffix
            else:
                url_info["type"] = "dynamic"
            gener_url = Utils.generalization(url)
            url_info["gener_url"] = gener_url
            url_info["url"] = url
            url_info["origin_url"] = url
            # url parse
            parse_url = urlparse(url)
            url_info["path"] = parse_url.path
            url_info["params"] = parse_url.params
            url_info["query"] = parse_url.query
            url_info["method"] = flow.request.method
            url_info["data"] = flow.request.text
            url_info["headers"] = flow.request.headers
            url_info["json"] = False
            req_type = flow.request.headers.get("Content-Type")
            if "application/json"==req_type:
                url_info["json"] = True
            if url_info["method"]=="GET":
                url_info["query_dict"] = parse_qs(parse_url.query)
            elif url_info["method"]=="POST":
                url_info["query_dict"] = parse_qs(url_info["data"])
            url_info["host"] = flow.request.host
            url_info["server_port"] = flow.server_conn.ip_address[1]
            url_info["server_ip"] = flow.server_conn.ip_address[0]
            if "https" in url:
                url_info["ssl"] = True
                url_info["base_url"] = "https://{0}:{1}".format(url_info["server_ip"], url_info["server_port"])
            else:
                url_info["ssl"] = False
                url_info["base_url"] = "http://{0}:{1}".format(url_info["server_ip"], url_info["server_port"])


        return url_info


    @staticmethod
    def req_to_urlinfo(req):
        url_info = dict()
        url = req.get('url')
        url = unquote(url, 'utf-8')
        url_info["origin_url"] = url
        url_info["method"] = 'GET'
        url_info["url"] = url
        parse_url = urlparse(url)
        url_info["path"] = parse_url.path
        url_info["params"] = parse_url.params
        url_info["query"] = parse_url.query
        url_info["host"] = parse_url.netloc
        url_info["query_dict"] = parse_qs(parse_url.query)
        if ":" in url_info["host"]:
            url_info["ip"] = url_info["host"].split(":")[0]
            url_info["port"] = url_info["host"].split(":")[1]
        if "https" in url:
            url_info["ssl"] = True
            url_info["base_url"] = "https://{0}".format(url_info["host"])
            if ":" not in url_info["host"]:
                url_info["port"] = url_info["443"]
        else:
            url_info["ssl"] = False
            url_info["base_url"] = "http://{0}".format(url_info["host"])
            if ":" not in url_info["host"]:
                url_info["port"] = url_info["80"]            
        url_suffix = Utils.get_url_suffix(url)
        if url_suffix not in [
                    "png", "css", "jpg", "svg",
                    "ttf", "eot", "eot", "woff2", "gif",
                    "bmp" "svg", "less", "sass", "scss", "ico",
                    "woff", "md"]:
            if  url_suffix == "js":
                url_info["type"] = "js"
            elif url_suffix in ["jsp", "php", "asp", "aspx"]:
                url_info["type"] = url_suffix
            else:
                url_info["type"] = "dynamic"
            gener_url = Utils.generalization(url)
            url_info["gener_url"] = gener_url

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
        rsp["text"] = str(flow.response.content.decode('utf-8', 'ignore'))
        rsp["timestamp_start"] = flow.response.timestamp_start
        rsp["timestamp_end"] = flow.response.timestamp_end
        return rsp

    @staticmethod
    def rsp_to_reqtext(rsp):
        req = rsp.request
        req_data = '%s %s %s\r\n' % (str(req.method), str(req.path_url), str(http_version_map[rsp.raw.version]))
        # Add headers to the request
        for k, v in req.headers.items():
            req_data += k + ': ' + v + '\r\n'
        req_data += '\r\n'
        if req.body:
            req_data += str(req.body)
        return req_data

    @staticmethod
    def rsp_to_dict(response):
        rsp = dict()
        rsp["status_code"] = response.status_code
        rsp["headers"] = response.headers
        rsp["text"] = str(response.text)
        rsp['req'] = response.request
        return rsp

    @staticmethod
    def rsp_to_req_dict(response):
        request = response.request
        url = request.url
        req = dict()
        parse_url = urlparse(url)
        req["url"] = request.url
        req["path"] = parse_url.path
        req["params"] = parse_url.params
        req["query"] = parse_url.query
        req["host"] = parse_url.netloc        
        req["method"] = request.method
        req["path"] = request.path_url
        req["http_version"] = http_version_map[response.raw.version]
        req["headers"] = request.headers
        req["text"] = str(request.body)
        req["raw"] = HTTPParser.rsp_to_reqtext(response)
        return req

    @staticmethod
    def get_res_req_by_url(url):
        headers = dict()
        headers["User-Agent"] = Utils.get_random_ua()
        try:
            response = requests.get(url,headers=headers,timeout=10)
            return HTTPParser.rsp_to_dict(response), HTTPParser.rsp_to_req_dict(response)
        except:
            logger.debug(traceback.format_exc())
            return None, None