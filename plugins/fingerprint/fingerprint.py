#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-11 18:16:18
LastEditors: recar
LastEditTime: 2022-01-12 18:49:37
'''
from lib.log import logger
from plugins.scan import Base
import traceback
import json
import os

class Fingerprint(Base):
    def __init__(self, result_queue):
        super(Fingerprint, self).__init__(result_queue)
        self.logger= logger
        self.timeout = 3
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.plugins_name = "fingerprint"
        self.result_list = list()
        self._load_dict()

    def _load_dict(self):
        '''
            [{
                "rule_id": "1",
                "level": "1",
                "softhard": "2",
                "product": "PHPSHE",
                "company": "haovip",
                "category": "Other Software System",
                "parent_category": "Software System",
                "rules": [
                    [
                        {
                            "match": "body_contains",
                            "content": "powered by phpshe"
                        }
                    ],
                    [
                        {
                            "match": "body_contains",
                            "content": "content=\"phpshe"
                        }
                    ]
                ]
            }]
        '''
        dict_path = os.path.join(self.base_path, "fingerprint.json")
        try:
            with open(dict_path, "r") as f:
                self.fingerprint_dict = json.load(f)
                # 对列表进行排序 优先级高的放到前面
                def level_sort(info):
                    return info.get('level')
                self.fingerprint_dict.sort(key=level_sort, reverse=True)
        except Exception:
            self.logger.error(traceback.format_exc())

    
    def run(self, url_info, req, rsp):
        fingerprint_result = list()
        rsp_text = rsp.get('text').lower()
        rsp_headers = rsp.get('headers')
        for fin_info in self.fingerprint_dict:
            status = False
            rules_list = fin_info.get('rules')
            product = fin_info.get("product")
            for rules in rules_list:
                for rule in rules:
                    match = rule.get('match')
                    content = rule.get('content')
                    if match == "banner_contains" or match == "protocol_contains":
                        continue
                    if match == "body_contains" or match == "title_contains":
                        if content in rsp_text:
                            status = True
                        else:
                            continue
                    elif match == "header_contains":
                        if content in rsp_headers:
                            status = True
                        else:
                            continue
                    else:
                        logger.error("is unkown match!!!!!!")
                    if status:
                        logger.info(f"fingerprint find: {product}")
                        fingerprint_result.append(product)
                        break
            # else:
            #     break
        if fingerprint_result:
            result = {
                "plugins": self.plugins_name,
                "result": fingerprint_result
            }
            self.to_result(result)
