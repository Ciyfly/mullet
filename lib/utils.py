#!/usr/bin/python
# coding=utf-8
'''
Author: Recar
Date: 2021-06-28 22:40:10
LastEditors: Recar
LastEditTime: 2022-01-12 21:39:34
'''
from os import stat
from lib.log import logger
from urllib.parse import unquote
import urllib.parse
import traceback
import platform
import hashlib
import uuid


class Utils(object):

    @staticmethod
    def get_md5(string):
        m = hashlib.md5()
        m.update(string.encode())
        return m.hexdigest()        

    @staticmethod
    def generalization(url):
        '''
        泛化后计算md5值 数字换成@ 纯字符串换成# 混合或者其他换成$
        '''
        parse_url =  urllib.parse.urlparse(url)
        url_paths = parse_url.path.split("/")
        url_paths = sorted(url_paths)
        netloc = parse_url.netloc
        query_dict = urllib.parse.parse_qs(parse_url.query)
        for key, value in query_dict.items():
            if type(value) is list:
                value = value[0]
            if value.isdigit():
                query_dict[key] = "@"
            elif value.isalpha():
                query_dict[key] = "#"
            else:
                query_dict[key] = "$"
        query_key_list = sorted(list(query_dict.keys()))
        query_str = ""
        for key in query_key_list:
            value = query_dict[key]
            query_str +=f"{key}={value}"
        path_str = "_".join(url_paths)
        url_str = f"{netloc}_{path_str}_{query_str}"
        logger.debug(f"[*] url_str: {url_str}")
        return Utils.get_md5(url_str)

    @staticmethod
    def get_url_suffix(url):
        if len(url.split("http"))>2:
            return ""
        if len(url)>140:
            return ""
        url = url.split("/")[-1]

        if "?" in url and url.split("?")[0].split(".")[-1] in [
                    "png", "css", "jpg", "svg",
                    "ttf", "eot", "eot", "woff2", "gif",
                    "bmp" "svg", "less", "sass", "scss", "ico",
                    "woff", "html", "md", "htm", "js", "php", "jsp", "asp", "aspx"]:
            url = url.split("?")[0]
        # https://image.3001.net/images/20210628/1624847546_60d934ba57cd0d7c4b4c8.png!small
        elif "!" in url and url.split("!")[-2].split(".")[-1] in [
                    "png", "css", "jpg", "svg",
                    "ttf", "eot", "eot", "woff2", "gif",
                    "bmp" "svg", "less", "sass", "scss", "ico",
                    "woff", "html", "md", "htm", "js", "php", "jsp", "asp", "aspx"]:
            url = url.split("!")[0]
        if len(url.split("."))>1:
            url_suffix = url.split(".")[-1]
        else:
            url_suffix = ""
        return url_suffix

    # @staticmethod
    # def js_is_relative(url, project_id):
    #     key = "_".join([project_id, Utils.generalization(url)])
    #     if resvars.redis_jsfind_url.exists(key):
    #         return True
    #     else:
    #         resvars.redis_jsfind_url.set(key, url)
    #         resvars.redis_jsfind_url.expire(key, 86400)
    #         return False

    @staticmethod
    def insert_all_url(url, project_id):
        # 泛化后入redis
        # 判断是否重复
        # 存储
        # 发送到队列里
        # 不存在第一次插入返回True 重复False
        if Utils.get_url_suffix(url)=="js":
            if Utils.js_is_relative(url, project_id):
                return False
            else:
                return True
        url_hash = Utils.generalization(url)
        try:
            if not resvars.redis_all_url.hexists(project_id, url_hash):
                #logger.debug(f"url_hash: {url_hash} url: {url} project_id: {project_id}")
                resvars.redis_all_url.hset(project_id, url_hash, "1")
                # TODO 入所有url的队列交给处理url的work
                logger.info(f"insert utl url_hash: {url_hash} url: {url} project_id: {project_id}")
                return True
            else:
                return False
        except:
            logger.error("url instert redis error: {0}".format(traceback.format_exc()))

    @staticmethod
    def parser_url(flow):
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
    def parser_req(flow):
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
        return req

    @staticmethod
    def parser_rsp(flow):
        rsp = dict()
        rsp["status_code"] = flow.response.status_code
        rsp["reason"] = flow.response.reason
        rsp["headers"] = flow.response.headers
        rsp["text"] = str(flow.response.content)
        rsp["timestamp_start"] = flow.response.timestamp_start
        rsp["timestamp_end"] = flow.response.timestamp_end
        return rsp

    @staticmethod
    def gen_project_id():
        return str(uuid.uuid4())

    @staticmethod
    def url_completion(url, path):
        if "http" in path:
            return path
        parse_url =  urllib.parse.urlparse(url)
        scheme = parse_url.scheme
        netloc = parse_url.netloc
        return f"{scheme}://{netloc}{path}"

    @staticmethod
    def is_windows():
        if platform.system().lower() == 'windows':
            return True
        return False