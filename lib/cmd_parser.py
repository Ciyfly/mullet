#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-12 16:28:33
LastEditors: recar
LastEditTime: 2022-04-07 11:34:53
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
@click.option('-v', '--violent', is_flag=True, help="violent test")
@click.option('-u', '--url', type=str, help="Do it directly without using proxy mode")
@click.option('-f', '--url_file', type=str, help="scan target file")
@click.option('-p', '--poc', type=str, help="run poc")
@click.option('--debug/--no-debug', help="log level set debug default False")
def cli(server_addr, violent, url, url_file, poc, debug):
    # set log level
    if debug:
        logger.setLevel(logging.DEBUG)
    # violent 强力测试模式
    if violent:
        logger.info("开启强力测试模式")
    # url
    urls = list()
    if url or url_file:
        controller.init(block=False, violent=violent)
        # 主动扫描推任务到controller
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
        logger.info("Run Poc: {0}".format(poc))
        for url in urls:
            rsp, req = HTTPParser.get_res_req_by_url(url)
            if rsp is None:
                logger.error("{0} :不能访问".format(url))
                continue
            url_info = HTTPParser.req_to_urlinfo(req)
            controller.run_poc(url_info, req, rsp, poc)
    # scan
    elif not poc and urls:
        logger.info("mode: Scan")
        for url in urls:
            rsp, req = HTTPParser.get_res_req_by_url(url)
            if rsp is None and req is None:
                logger.error("{0} :不能访问".format(url))
                continue            
            url_info = HTTPParser.req_to_urlinfo(req)
            controller.run(url_info, req, rsp)
            logger.info("end")

    else:
        logger.info("mode: Proxy")
        # 被动扫描
        controller.init(violent=violent)
        addr, port = server_addr.split(":")
        proxy_run(addr, int(port))

