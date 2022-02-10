#!/usr/bin/python
# coding=utf-8
'''
Date: 2021-06-25 17:36:26
LastEditors: Recar
LastEditTime: 2022-02-10 21:26:11
'''
from plugins.scan import Base
import re

class Scan(Base):
    def __init__(self, report_work):
        super().__init__(report_work)
        self.plugins_name = "js_find"
        self.pattern_raw = r"""
        (?:"|')                               # Start newline delimiter
        (
            ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
            [^"'/]{1,}\.                        # Match a domainname (any character + dot)
            [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
            |
            ((?:/|\.\./|\./)                    # Start with /,../,./
            [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
            [^"'><,;|()]{1,})                   # Rest of the characters can't be
            |
            ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
            [a-zA-Z0-9_\-/]{1,}                 # Resource name
            \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
            (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
            |
            ([a-zA-Z0-9_\-]{1,}                 # filename
            \.(?:php|asp|aspx|jsp|json|
                action|html|js|txt|xml)             # . + extension
            (?:\?[^"|']{0,}|))                  # ? mark with parameters
        )
        (?:"|')                               # End newline delimiter
        """
        self.pattern = re.compile(self.pattern_raw, re.VERBOSE)

    def filter(self, line):
        if len(line.split("."))>1 and "http:" not in line:
            # 可能是 静态资源
            if line.split(".")[-1] in [
                    "png", "css", "jpg", "svg",
                    "ttf", "eot", "eot", "woff2", "gif",
                    "bmp" "svg", "less", "sass", "scss", "ico",
                    "woff", "html", "md", "htm"]:
                    return False
        if "www.w3.org" in line:
            return False
        return True

    def find(self, url_url, rsp_text):
        find_list = list()
        result = self.pattern.findall(rsp_text)
        if not result:
            return find_list
        for res in result:
            for line in res:
                if not line:
                    continue
                if self.filter(line):
                    find_list.append(self.url_completion(url_url, line))
        return find_list

    def run(self, url_info, req, rsp):
        url_type = url_info.get('type')
        url_url = url_info.get('url')
        rsp_text = rsp.get('text', "")
        self.logger.debug("jsfind: {0}".format(url_url))
        if url_type != 'js' or url_type is None:
            return False, []
        find_list = self.find(url_url, rsp_text)
        if find_list:
            result = {
                "plugins": self.plugins_name,
                "url": url_url,
                "payload": find_list,
                "desc": "敏感js"
            }
            self.to_result(result)
