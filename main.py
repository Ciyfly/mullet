#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-11 18:10:19
LastEditors: recar
LastEditTime: 2022-01-13 15:29:18
'''
from lib.proxy import proxy_run
from lib.log import logger
from lib.utils import Utils
def main():
    proxy_run()

if __name__ == '__main__':
    Utils.banner()
    main()