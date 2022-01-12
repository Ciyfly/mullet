#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-10 10:50:05
LastEditors: Recar
LastEditTime: 2022-01-12 22:01:13
'''

from queue import PriorityQueue
import threading
import traceback
import logging
import signal
import sys


def ctrl_c(signum, frame):
    print()
    print("ctrl c")
    sys.exit()
# ctrl+c
signal.signal(signal.SIGINT, ctrl_c)

class Worker(object):
    def __init__(self, consumer_func, consumer_count=10, logger = logging):
        self.logger = logger
        self.consumer_count = consumer_count
        self.work_queue = PriorityQueue()        
        self.run(consumer_func)

    def put(self, item, priority=10):
        '''
        @params item 数据
        @params priority 优先级 默认是10
        '''
        try:
            if type(item) == list:
                for d in item:
                    self.work_queue.put((priority, d))
            else:
                self.work_queue.put((priority, item))
        except Exception as e:
            self.logger.error(traceback.format_exc()) 


    def consumer(self, func):
        '''
        消费者
        @params func 消费者函数
        '''
        while True:
            item = self.work_queue.get()
            try:
                func(item)
            except Exception:
                self.logger.error("consumer error: {0}".format(traceback.format_exc()))

    def run(self, consumer_func):
        '''
        运行方法
        @params consumer_func 消费者函数
        '''
        threads = []
        for i in range(self.consumer_count):
            t = threading.Thread(target=self.consumer,args=(consumer_func,))
            t.setDaemon(True)
            t.start()
            threads.append(t)
