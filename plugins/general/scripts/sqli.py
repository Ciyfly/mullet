#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-24 09:46:27
LastEditors: recar
LastEditTime: 2022-03-31 12:29:49
'''
from plugins.scan import Base
import xml.etree.ElementTree as ET
from lib.utils import Utils
import time
import json
import re
import os

class Scan(Base):
    def __init__(self, report_work):
        super().__init__(report_work)
        self.plugins_name = "sqli"
        # https://github.com/sqlmapproject/sqlmap/blob/master/data/xml/errors.xml
        self.load_xml()
        self.sqli_info = dict()

    def _load_errors_check(self):
        self.errors_check_list = list()
        tree = ET.parse(self.errors_check_path)
        root = tree.getroot()
        for dbms in root.findall("dbms"):
            db_name = dbms.attrib.get("value")
            for errors in dbms.findall("error"):
                regex = errors.attrib.get("regexp")
                self.errors_check_list.append(
                    {
                        "type": db_name,
                        "regex": regex
                    }
                )

    def _load_boundaries(self):
        self.boundaries_list = list()
        tree = ET.parse(self.boundaries_path)
        root = tree.getroot()
        for boundary in root.findall("boundary"):
            boundary_info = dict()
            for prefix, suffix in zip(boundary.findall("prefix"), boundary.findall("suffix")):
                boundary_info["prefix"] = prefix.text
                boundary_info["suffix"] = suffix.text
                self.boundaries_list.append(boundary_info)

    def _load_error_payload(self):
        error_payload_list = list()
        tree = ET.parse(self.error_payload_path)
        root = tree.getroot()
        for test in root.findall("test"):
            test_info = dict()
            for request, response, details in zip(test.findall("request"), test.findall("response"), test.findall("details")):
                for grep in response.findall("grep"):
                    test_info["grep"] = grep.text
                for payload in request.findall("payload"):
                    test_info["payload"] = payload.text
                for dbms in details.findall("dbms"):
                    if self.sqli_info.get("dbms") and self.sqli_info.get("dbms")==dbms.text or self.sqli_info.get("dbms")==None:
                        error_payload_list.append(test_info)
        self.sqli_info["error_payload_list"] = error_payload_list
        self.logger.debug("error_payload_list: {0}".format(len(error_payload_list)))

    def _load_bool_blind_payload(self, dbms=None):
        bool_blind_payload_list = list()
        tree = ET.parse(self.bool_blind_payload_path)
        root = tree.getroot()
        for test in root.findall("test"):
            test_info = dict()
            for request, response, details in zip(test.findall("request"), test.findall("response"), test.findall("details")):
                for comparison in response.findall("comparison"):
                    test_info["comparison"] = comparison.text
                for payload in request.findall("payload"):
                    test_info["payload"] = payload.text
                for dbms in details.findall("dbms"):
                    if self.sqli_info.get("dbms") and self.sqli_info.get("dbms")==dbms.text or self.sqli_info.get("dbms")==None:
                        bool_blind_payload_list.append(test_info)
        self.sqli_info["bool_blind_payload_list"] = bool_blind_payload_list
        self.logger.debug("bool_blind_payload_list: {0}".format(len(bool_blind_payload_list)))


    def _load_time_blind_payload(self, dbms=None):
        time_blind_payload_list = list()
        tree = ET.parse(self.time_blind_payload_path)
        root = tree.getroot()
        for test in root.findall("test"):
            test_info = dict()
            for request, response, details in zip(test.findall("request"), test.findall("response"), test.findall("details")):
                for time in response.findall("time"):
                    test_info["time"] = time.text
                for payload in request.findall("payload"):
                    test_info["payload"] = payload.text
                for dbms in details.findall("dbms"):
                    if self.sqli_info.get("dbms") and self.sqli_info.get("dbms")==dbms.text or self.sqli_info.get("dbms")==None:
                        time_blind_payload_list.append(test_info)
        self.sqli_info["time_blind_payload_list"] = time_blind_payload_list
        self.logger.debug("time_blind_payload_list: {0}".format(len(time_blind_payload_list)))

    def load_xml(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.errors_check_path = os.path.join(base_path, "sqli", "errors.xml")
        self.boundaries_path = os.path.join(base_path, "sqli", "boundaries.xml")
        self._load_errors_check()
        self._load_boundaries()

    def update_payload(self):
        '''
        根据数据库类型 更新payload到sqli_info中
        '''
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.error_payload_path = os.path.join(base_path, "sqli", "error_based.xml")
        self.bool_blind_payload_path = os.path.join(base_path, "sqli", "boolean_blind.xml")
        self.time_blind_payload_path = os.path.join(base_path, "sqli", "time_blind.xml")        
        self._load_error_payload()
        self._load_bool_blind_payload()
        self._load_time_blind_payload()


    def heuristic(self, url_info):
        heuristic_payloads = [
            # "'",'"',")","(",";"
            """'"();"""
        ]
        query_dict = url_info.get("query_dict")
        origin_url = url_info.get("origin_url")
        base_url = url_info.get("url").split("?")[0]
        method = url_info.get("method")
        payload_query = ""
        for payload in heuristic_payloads:
            for q_d in query_dict.keys():
                tmp = "{0}={1}&".format(q_d, query_dict[q_d][0]+payload)
                payload_query +=tmp
            payload_query = "&".join(payload_query.split("&")[0:-1])
            if method=="GET":
                url = base_url+"?"+payload_query
            else: # post
                url = base_url
            response = self.request(url, method=method, data=payload_query)
            for check in self.errors_check_list:
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
                    # 存储数据库类型
                    self.sqli_info["dbms"] = match_type
                    self.print_result(result)
                    self.to_result(result)
                    return

    def _handle_tag(self, s, error=False):
        if s is None or s=="":
            return ""
        if "[RANDNUM]" in s:
            if error:
                s = s.replace("[RANDNUM]", str(Utils.gen_random_num()),1)
                s = s.replace("[RANDNUM]", str(Utils.gen_random_num()),1)
            else:
                s = s.replace("[RANDNUM]", str(Utils.gen_random_num()))
        if "[RANDSTR]" in s:
            if error:
                s = s.replace("[RANDSTR]", Utils.gen_random_str(),1)
                s = s.replace("[RANDSTR]", Utils.gen_random_str(),1)
            else:
                s = s.replace("[RANDSTR]", Utils.gen_random_str())
        if "[GENERIC_SQL_COMMENT]" in s:
            s = s.replace("[GENERIC_SQL_COMMENT]", "-- "+ Utils.gen_random_str())

        if "[RANDNUM1]" in s:
            s = s.replace("[RANDNUM1]", str(Utils.gen_random_num()))
        if "[RANDNUM2]" in s:
            s = s.replace("[RANDNUM2]", str(Utils.gen_random_num()))
        if "[RANDNUM3]" in s:
            s = s.replace("[RANDNUM3]", str(Utils.gen_random_num()))
        if "[RANDNUM4]" in s:
            s = s.replace("[RANDNUM4]", str(Utils.gen_random_num()))        

        if "[DELIMITER_START]" in s:
            s = s.replace("[DELIMITER_START]", Utils.gen_random_str())
        if "[DELIMITER_STOP]" in s:
            s = s.replace("[DELIMITER_STOP]", Utils.gen_random_str())

        if "[SLEEPTIME]" in s:
            s = s.replace("[SLEEPTIME]", str(5))

        if "[QUERY]" in s:
            s = s.replace("[QUERY]", "recar")

        return s

    def _fix_query(self,url_info, rsp, boundaries_list, error=False, payload=""):
        '''
        混合参数
        '''
        match_boundaries = list()
        origin_rsp_text = Utils.remove_html_tag(rsp.get("text"))
        query_dict = url_info.get("query_dict")
        origin_url = url_info.get("origin_url")
        base_url = url_info.get("url").split("?")[0]
        method = url_info.get("method")
        data = url_info.get("data")
        for boundarie_info in boundaries_list: 
            payload_query = ""
            prefix = boundarie_info.get("prefix")
            suffix = boundarie_info.get("suffix")
            for q_d in query_dict.keys():
                origin_query = q_d+"="+query_dict[q_d][0]
                payload_query = origin_query+self._handle_tag(prefix, error=error)+self._handle_tag(payload)+self._handle_tag(suffix, error=error)
                if method=="GET":
                    url = origin_url.replace(origin_query, payload_query)
                else: # post
                    url = base_url
                    data.replace(origin_query, payload_query)
                response = self.request(url, method=method, data=data)
                if response.status_code==200:
                    payload_rsp_text = Utils.remove_html_tag(response.text)
                    ratio = Utils.similarity(origin_rsp_text, payload_rsp_text)
                    if error:
                        if ratio <0.9:
                            match_boundaries.append(
                                {
                                    "prefix": prefix,
                                    "suffix": suffix,
                                    "url": url,
                                    "data": data,
                                    "query": q_d
                                }
                            )
                    else:
                        if ratio>0.9:
                            match_boundaries.append(
                                {
                                    "prefix": prefix,
                                    "suffix": suffix,
                                    "query": q_d
                                }
                            )
        return match_boundaries


    def boundarie(self, url_info, rsp):
        '''
        用来闭合前后sql语句
        '''
        match_boundaries = self._fix_query(url_info, rsp, self.boundaries_list, error=False)
        match_result = self._fix_query(url_info, rsp, match_boundaries, error=True)
        # 存储闭合的参数
        self.sqli_info["boundaries"] = match_result
        if len(match_result)>0:
            for match in match_result:
                payload= match.get('url')
                if match.get('data'):
                    payload+"\r\n"+match.get('data')
                result = {
                "plugins": self.plugins_name,
                "url": url_info.get("origin_url"),
                "payload": payload,
                "desc": "可能存在sql注入漏洞"
                }
                self.print_result(result)
                self.to_result(result)


    def _fix_query_by_payload(self, url_info, boundaries_list, payload, grep=""):

        def send(method, base_url, data, payload,headers, origin_query, payload_query, grep=None):
            if method=="GET":
                url = origin_url.replace(origin_query, payload_query)
            else: # post
                url = base_url
                if url_info.get("json"):
                    # 如果是json的
                    data_dict = json.loads(data)
                    data_dict[query] = payload_query
                    data = json.dumps(data)
                else:
                    data.replace(origin_query, payload_query)
            start = time.time()
            response = self.request(url, method=method, data=data, headers=headers, timeout=10)
            end = time.time()
            return {"response": response,
                    "url": url,
                    "data": data,
                    "payload": payload,
                    "grep": grep,
                    "use_time": end-start}

        response_info_list = list()
        query_dict = url_info.get("query_dict")
        origin_url = url_info.get("origin_url")
        base_url = url_info.get("url").split("?")[0]
        method = url_info.get("method")
        data = url_info.get("data")
        headers = url_info.get("headers")
        all_boundaries=False
        if len(boundaries_list)==0:
            all_boundaries=True
            boundaries_list = self.boundaries_list
        for boundarie_info in boundaries_list: 
            payload_query = ""
            prefix = boundarie_info.get("prefix")
            suffix = boundarie_info.get("suffix")
            # 如果没有找到闭合 则全部拿来跟后续的payload测试
            if all_boundaries:
                for q_d in query_dict.keys():
                    origin_query = q_d+"="+query_dict[q_d][0]
                    payload, fix_grep = self._handle_tag(payload+"@@recar@@"+grep).split("@@recar@@")
                    payload_query = origin_query+self._handle_tag(prefix)+payload+self._handle_tag(suffix)
                    response_info = send(method, base_url, data, payload,headers, origin_query, payload_query, grep=fix_grep)
                    response_info_list.append(response_info)
            else:
                query = boundarie_info.get("query")
                origin_query = query+"="+query_dict[query][0]
                payload, fix_grep = self._handle_tag(payload+"@@recar@@"+grep).split("@@recar@@")
                payload_query = origin_query+self._handle_tag(prefix)+payload+self._handle_tag(suffix)
                response_info = send(method, base_url, data, payload,headers, origin_query, payload_query, grep=fix_grep)
                response_info_list.append(response_info)
        return response_info_list

    def error_sqli(self, url_info):
        # 报错测试
        self.logger.debug("error sqli test")
        for error_payload_info in self.sqli_info["error_payload_list"]:
            payload = error_payload_info.get('payload')
            grep = error_payload_info.get('grep')
            response_info_list = self._fix_query_by_payload(url_info, self.sqli_info.get("boundaries"), payload)
            for response_info in response_info_list:
                response = response_info.get("response")
                url = response_info.get("url")
                data  = response_info.get("data")
                regex_compile = re.compile(grep)
                match = regex_compile.findall(response.text)
                if match:
                    payload= url
                    if data:
                        payload+"\r\n"+data
                    result = {
                    "plugins": self.plugins_name,
                    "url": url_info.get("origin_url"),
                    "payload": payload,
                    "desc": "可能存在报错注入"
                    }
                    self.print_result(result)
                    self.to_result(result)
                    return True

    def bool_blind(self, url_info):
        # 发payload然后再发payload2 比较相似度
        self.logger.debug("bool blind sqli test")
        for bool_blind in self.sqli_info.get("bool_blind_payload_list", []):
            payload = bool_blind.get('payload')
            comparison = bool_blind.get("comparison")
            response_info_list_1 = self._fix_query_by_payload(url_info, self.sqli_info.get("boundaries"), payload)
            response_info_list_2 = self._fix_query_by_payload(url_info, self.sqli_info.get("boundaries"), comparison)
            for r_1, r_2 in zip(response_info_list_1, response_info_list_2):
                response_text_1 = r_1.get("response").text
                response_text_2 = r_2.get("response").text
                ratio = Utils.similarity(response_text_1, response_text_2)
                url = r_1.get("url")
                data = r_1.get("data")
                if ratio <0.8:
                    payload= url
                    if data:
                        payload+"\r\n"+data
                    result = {
                    "plugins": self.plugins_name,
                    "url": url_info.get("origin_url"),
                    "payload": payload,
                    "desc": "可能存在布尔盲注"
                    }
                    self.print_result(result)
                    self.to_result(result)
                    return True

    def time_blind(self,url_info):
        # 先暂时直接用5s来判断后续优化为时间波动 参考sqli
        self.logger.debug("time blind sqli test")
        for time_blind_payload_info in self.sqli_info.get("time_blind_payload_list", []):
            payload = time_blind_payload_info.get('payload')
            response_info_list = self._fix_query_by_payload(url_info, self.sqli_info.get("boundaries"), payload)
            for response_info in response_info_list:
                use_time = response_info.get("use_time")
                url = response_info.get("url")
                data = response_info.get("data")
                if use_time>5:
                    payload= url
                    if data:
                        payload+"\r\n"+data
                    result = {
                    "plugins": self.plugins_name,
                    "url": url_info.get("origin_url"),
                    "payload": payload,
                    "desc": "可能存在时间盲注"
                    }
                    self.print_result(result)
                    self.to_result(result)
                    return True

    def verify(self, url_info, req, rsp, violent=False):
        '''
            默认只跑简单的注入验证 不会发payload
            目前是只要跑出来一个注入就不在跑了 
            violent 设置为True会死命的拿payload测试 会产生大量请求
        '''
        query_dict = url_info.get("query_dict")
        if query_dict is None:
            return
        # 启发式报错看报错信息输出是否有数据库类型
        self.heuristic(url_info)
        # 尝试闭合 获取前后缀
        self.boundarie(url_info, rsp)
        # 根据数据库信息加载payload
        # 如果开启下面会发大量的payload
        if not violent:
            return
        self.logger.debug("find boundarie: {0}".format(len(self.sqli_info.get("boundaries"))))
        self.logger.debug(" star violent sqli test")
        self.update_payload()
        # 报错注入
        error_status = self.error_sqli(url_info)
        if error_status:
            return
        # bool盲注
        bool_status = self.bool_blind(url_info)
        if bool_status:
            return
        # 时间盲注
        time_status = self.time_blind(url_info)
        if time_status:
            return
