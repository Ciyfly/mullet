#!/usr/bin/python
# coding=utf-8
'''
Date: 2021-06-25 17:42:42
LastEditors: recar
LastEditTime: 2022-01-26 11:54:45
'''
import js2py
import re
from plugins.scan import Base


class Scan(Base):
    def __init__(self):
        super(Base, self).__init__()
        self.plugins_name = "js_jsonp"
        self.callbak_pattern = re.compile('(?m)(?i)(callback)|(jsonp)|(^cb$)|(function)')
        self.seninfo_pattern = re.compile(
            '(?m)(?i)(uid)|(userid)|(user_id)|(nid)|(name)|(username)|(nick)|(login)|(islogin)|(is_login)|(email)|(phone)'
            )
        self.esprima = js2py.require('esprima')
        self.escodegen = js2py.require('escodegen')

    def has_callback(self,url):
        if self.callbak_pattern.findall(url):
            return True
        else:
            return False

    def has_sen_info(self, parse_dict):
        sen_info = list()
        for key, value in parse_dict.items():
            if self.seninfo_pattern.search(key):
                # print("find sen_info: {0}: {1}".format(key, value))
                sen_info.append(
                    {
                        "key": key,
                        "value": value
                    }
                )
        return sen_info

    def parse_properties(self, properties, all_maps):
        for data in properties:
            key = data["key"]["value"]
            if  data["value"].get('properties'):
                self.parse_properties(data["value"]["properties"], all_maps)
            else:
                value = data["value"]["value"]
                all_maps[key] = value

    def run(self, url_info, req, rsp):
        url = url_info.get("url","")
        rsp_text = rsp.get('text',"")
        all_maps = dict()
        if not self.has_callback(url):
            return False, []
        try:
            self.logger.debug("hased callbak")
            tree = self.esprima.parse(rsp_text)
        except Exception:
            return False, []
        tree_json = tree.to_dict()
        self.logger.debug(tree_json)
        body = tree_json['body']
        if not body:
            return False, []
        for expression in body:
            expression = expression.get('expression')
            if not expression:
                continue
            if not expression.get("arguments"):
                continue
            arguments = expression["arguments"]
            for properties in arguments:
                properties = properties["properties"]
                self.parse_properties(properties, all_maps)
        self.logger.debug("all_maps: {0}".format(all_maps))
        sen_info = self.has_sen_info(all_maps)
        self.logger.debug("sen_info: {0}".format(sen_info))
        if sen_info:
            return True, sen_info
        else:
            return False, []
