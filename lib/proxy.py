#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-11 18:12:13
LastEditors: recar
LastEditTime: 2022-01-26 11:23:09
'''
from mitmproxy.options import Options
from mitmproxy.proxy.config import ProxyConfig
from mitmproxy.proxy.server import ProxyServer
from mitmproxy.tools.dump import DumpMaster
from lib.filter import Filter
from lib.log import logger
import traceback


class Addon(object):
    def __init__(self,): 
        pass
	
    def request(self, flow):
        try:
            Filter.parser_request(flow)
        except:
            logger.error(traceback.format_exc())
    def response(self, flow):
        try:
            Filter.parser_response(flow)
        except:
            logger.error(traceback.format_exc())

class ProxyMaster(DumpMaster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        try:
            DumpMaster.run(self)
        except KeyboardInterrupt:
            self.shutdown()

def proxy_run(addr="0.0.0.0", port=8686):
    logger.info(f"Proxy {addr}:{port}")
    try:
        options = Options(listen_host=addr, listen_port=port, http2=True)
        config = ProxyConfig(options)
        master = ProxyMaster(options, with_termlog=False, with_dumper=False)
        master.server = ProxyServer(config)
        master.options.set('block_global=false')
        master.addons.add(Addon())
        master.run()
    except Exception:
        logger.error(traceback.format_exc())
