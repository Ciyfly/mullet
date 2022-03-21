#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 16:28:33
LastEditors: recar
LastEditTime: 2022-03-21 21:05:23
'''
from cmath import log
from lib.data import controller
from lib.http_parser import HTTPParser
from lib.proxy import proxy_run
from lib.log import logger
import logging
import click
import os

@click.command()
@click.option('-s', 'server_addr', type=str, default="0.0.0.0:8686", help='listen server addr defalut 0.0.0.0:8686')
@click.option('-v', '--verbose', count=True, help="use attack level")
@click.option('-u', '--url', type=str, help="Do it directly without using proxy mode")
@click.option('-f', '--url_file', type=str, help="scan target file")
@click.option('-p', '--poc', type=str, help="run poc")
@click.option('--debug/--no-debug', help="log level set debug default False")
def cli(server_addr, verbose, url, url_file, poc, debug):
    # set log level
    if debug:
        logger.setLevel(logging.DEBUG)
    # url
    if url or url_file:
        controller.init(block=False)
        # 主动扫描推任务到controller
        urls = list()
        if url_file:
            if os.path.exists(url_file):
                with open(url_file, 'r') as f:
                    for line in f:
                        urls.append(line.strip())
            else:
                click.echo("url_file is not exists")
                click.exit()
        if url:
            urls.append(url)
    # 单个poc
    if poc:
        logger.info("run poc: {0}".format(poc))
        for url in urls:
            rsp, req = HTTPParser.get_res_req_by_url(url)
            if rsp is None:
                logger.error("{0} :不能访问".format(url))
                continue
            url_info = HTTPParser.req_to_urlinfo(req)
            controller.run_poc(url_info, req, rsp, poc)
    # scan
    elif not poc:
        logger.info("scan")
        for url in urls:
            rsp, req = HTTPParser.get_res_req_by_url(url)
            if rsp is None:
                logger.error("{0} :不能访问".format(url))
                continue            
            url_info = HTTPParser.req_to_urlinfo(req)
            controller.run(url_info, req, rsp)
            logger.info("end")

    else:
        logger.info("proxy")
        # 被动扫描
        controller.init()
        addr, port = server_addr.split(":")
        proxy_run(addr, int(port))

