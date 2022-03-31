#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-31 16:17:16
LastEditors: recar
LastEditTime: 2022-03-31 17:16:02
'''

from flask import Flask, request, jsonify
from lib.data import controller
from lib.http_parser import HTTPParser
from lib.utils import Utils
from lib.log import logger

app = Flask('mullet')
TOKEN = Utils.gen_random_str(16)

controller.init(block=True)

@app.route('/scan/', methods=['POST'])
def scan():
    data = request.get_json()
    url = data.get("url")
    data_token = data.get("token")
    if data_token is None or data_token!=TOKEN:
        return jsonify({
            "code": 201,
            "message": "Invalid token"
        })
    rsp, req = HTTPParser.get_res_req_by_url(url)
    url_info = HTTPParser.req_to_urlinfo(req)
    controller.run(url_info, req, rsp)
    return jsonify({
        "code": 200,
        "message": "Add success"
    })

if __name__ == '__main__':
    logger.info("TOKEN: {0}".format(TOKEN))
    logger.info("Mullet api ")
    app.run(host='0.0.0.0', port=8787)
