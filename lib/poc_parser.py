#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-02-21 11:28:24
LastEditors: recar
LastEditTime: 2022-02-21 15:56:35
'''
import urllib.parse
import collections
import string
import hashlib
import random
import base64 as b64
import yaml
import re
import os

ASCII_LOWERCASE = string.ascii_lowercase

def urlencode(s):
    return urllib.parse.quote(str(s))

def base64(s):
    return b64.b64encode(str(s).encode())

def randomInt(x,y):
    return random.randint(int(x),int(y))

def randomLowercase(count):
    return "".join([random.choice(ASCII_LOWERCASE) for count in range(6)])

def md5(value):
    return hashlib.md5().update(value)

def string(x):
    return str(x)

def byteds(x):
    return bytes(x)

class XaryPocParser(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.variable_dict = dict()
        self.rule_flow = collections.OrderedDict()
        self.expr_list = list()
        
    def set_parser(self, set_dict):
        for variable in set_dict.keys():
            expr = set_dict[variable]
            if expr!="request.url.host":
                self.variable_dict[variable] = eval(expr)
                globals()[variable]=self.variable_dict[variable]

    def rules_parser(self, rules_dict):
        for rule_name, rule_value in rules_dict.items():
            self.rule_flow[rule_name+"()"] = rule_value

    def expression_parser(self, expression_str):
        self.expr_list = expression_str.split("&&")
        for expr in self.expr_list:
            expr = expr.strip()

    def detail_parser(self, detail_dict):
        self.detail_dict = detail_dict

    def parser_expr2set(self, expr_str):
        # 表达式 {{}} 替换为set的变量
        # 是发送poc的需要函数
        if type(expr_str)!=str:
            return expr_str
        if r"{{" not in expr_str:
            return expr_str
        match_list = re.findall(r'{{(.*)}}', expr_str)
        if not match_list:
            return expr_str
        for match in match_list:
            if match in self.variable_dict.keys():
                replace_match = "{{{{{0}}}}}".format(match)
                expr_str = expr_str.replace(replace_match, str(self.variable_dict[match]))
        return expr_str

    def parser_expr2re(self, expr_str):
        # 根据表达式 返回匹配的正则字符串和显示位置
        # 是诱骗需要的函数
        match_dict = dict()
        for index_name in ["response.body", "response.status", "response.content_type", "response.headers"]:
            if expr_str.startswith(index_name) and index_name=="response.body":
                match_dict["index"] = "body"
                tmp_expr_str = expr_str.replace(index_name,"")
                match_dict["func"] = tmp_expr_str.split("(")[0].replace(".", "")
                match_dict["match"] = tmp_expr_str.split("(")[-1].split(")",)[0]
            elif expr_str.startswith(index_name) and index_name=="response.status":
                match_dict["index"] = "status"
                match_dict["func"] = "=="
                match_dict["match"] = expr_str.split("==")[-1].strip()
            elif expr_str.startswith(index_name) and index_name=="response.content_type":
                tmp_expr_str = expr_str.replace(index_name,"")
                match_dict["index"] = "content_type"
                match_dict["func"] = tmp_expr_str.split("(")[0].replace(".", "")
                match_dict["match"] = tmp_expr_str.split("(")[-1].split(")",)[0]
            elif "bmatches" in expr_str:
                # "root:[x*]:0:0:".bmatches(response.body)
                match_dict["index"] = expr_str.split(".bmatches(")[-1].split(")")[0]
                match_dict["func"] = "bmatches"
                match_dict["match"] = expr_str.split(".bmatches(")[0]
            # elif 
            elif expr_str.startswith(index_name) and index_name=="response.headers":
                # response.headers["location"] ==/in "xx"
                match_dict["index"] = "headers"
                match_dict["func"] = "in"
                if "==" in expr_str:
                    match_dict["match"] = expr_str.split("==")[-1].strip()
                elif "contains" in expr_str:
                    match_dict["match"] = expr_str.split("contains(")[-1].replace(")", "").replace('"',"")
            elif expr_str.endswith(index_name) and index_name=="response.headers":
                # "location" in response.headers
                match_dict["index"] = "headers"
                match_dict["func"] = "in"
                match_dict["match"] = expr_str.split("in")[0].strip()                
            

        return match_dict

    def parser_expr2match(self, expr_match):
        # 位置 函数 匹配值
        return ""

    def gen_request(self):
        # 刷新request里面的表达式
        for rule_name, rule in self.rule_flow.items():
            request_info = rule["request"]
            new_request_info = dict()
            for key, value in request_info.items():
                new_request_info[key]= self.parser_expr2set(value)
            # return request_info
            self.rule_flow[rule_name]["request"] = new_request_info

    def gen_response_match(self):
        # 根据 rule里的 expression 生成匹配的正则
        for rule_name, rule in self.rule_flow.items():
            expressions = rule["expression"]
            expressions_list = expressions.split("&&")
            new_expressions_match = []
            for expression in expressions_list:
                expression = expression.strip()
                new_expressions_match.append(self.parser_expr2re(expression))
            self.rule_flow[rule_name]["expressions"] = new_expressions_match

    def gen_http_raw(self, **kwargs):
        path = kwargs.get("path","/")
        method = kwargs.get("method", "GET")
        data = kwargs.get("data", None)
        headers = kwargs.get("headers", {})
        ip = kwargs.get("ip", "127.0.0.1")
        port = kwargs.get("ip", 80)
        raw = ""
        raw += "{0} {1}\r\n".format(method, path)
        raw += "Host: {0}:{1}\r\n".format(ip, port)
        for key, value in headers.items():
            raw += "{0}: {1}\r\n".format(key, value)
        raw += "\r\n\r\n"
        raw += "{0}".format(data)
        return raw

    # 攻击
    def gen_attck(self):
        # self.variable_dict 是所有的set值
        self.gen_request()
        self.gen_response_match()
        # request
        for rule_name, rule in self.rule_flow.items():
            request_info = rule["request"]
            method = request_info.get("method", "GET")
            headers = request_info.get("headers", {})
            data = request_info.get("body", "")
            # redirect = request_info.get("redirect", False)
            path = request_info.get("path", "/")
            http_raw = self.gen_http_raw(path=path,method=method, headers=headers, data=data)
            self.rule_flow[rule_name]["request"]["raw"] = http_raw
        # response
        for rule_name, rule in self.rule_flow.items():
            expressions = rule["expressions"]
            for i, expression in enumerate(expressions):
                match = expression.get("match")
                if match in self.variable_dict.keys():
                    self.rule_flow[rule_name]["expressions"][i][match] = self.variable_dict[match]

    def parser(self, ip, port):
        self.ip = ip
        self.port = port
        self.variable_dict["request.url.host"] = "{0}:{1}".format(ip, port)
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, encoding='utf-8') as f:
            poc = yaml.unsafe_load(f)
            for key in poc.keys():
                if key=="set":
                    self.set_parser(poc[key])
                elif key=="rules":
                    self.rules_parser(poc[key])
                elif key=="expression":
                    self.expression_parser(poc[key])
                elif key=="detail":
                    self.detail_parser(poc[key])
        # 生成一个攻击需要的raw 以及对应的匹配
        self.gen_attck()
        return self.rule_flow
