#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-24 09:46:27
LastEditors: recar
LastEditTime: 2022-03-24 18:57:00
'''
from plugins.scan import Base
import re

class Scan(Base):
    def __init__(self, report_work):
        super().__init__(report_work)
        self.plugins_name = "sqli"
        self.error_str_list = [
                {'regex': '\[(ODBC SQL Server Driver|SQL Server|ODBC Driver Manager)\]', 'type': 'Microsoft SQL Server'},
                {'regex': 'Cannot initialize the data source object of OLE DB provider "[\w]*" for linked server "[\w]*"',
                'type': 'Microsoft SQL Server'}, {
                'regex': 'You have an error in your SQL syntax',
                'type': 'MySQL'},
                {'regex': 'Illegal mix of collations \([\w\s\,]+\) and \([\w\s\,]+\) for operation', 'type': 'MySQL'},
        ]


    def heuristic(self, url_info):
        heuristic_payloads = [
            # "'",'"',")","(",";"
            """'"();"""
        ]
        query_dict = url_info.get("query_dict")
        origin_url = url_info.get("origin_url")
        base_url = url_info.get("url").split("?")[0]
        method = url_info.get("method")
        if method == "GET":
            payload_query = ""
            for payload in heuristic_payloads:
                for q_d in query_dict.keys():
                    tmp = "{0}={1}&".format(q_d, query_dict[q_d][0]+payload)
                    payload_query +=tmp
                payload_query = "&".join(payload_query.split("&")[0:-1])
                url = base_url+"?"+payload_query
                response = self.request(url)
                for check in self.error_str_list:
                    regex = check.get("regex")
                    match_type = check.get("type")
                    regex_compile = re.compile(regex)
                    match = regex_compile.findall(response.text)
                    if len(match)>0:
                        result = {
                            "plugins": self.plugins_name,
                            "url": origin_url,
                            "payload": url,
                            "desc": "数据库报错匹配: {0}".format(match_type)
                        }
                        self.print_result(result)

        elif method == "POST":
            self.logger.debug("post")
        else:
            self.logger.debug("method: {0}".format(method))
            

    def error_sqli(self):
        pass


    def verify(self, url_info, req, rsp):
        self.heuristic(url_info)
        return True, ""
