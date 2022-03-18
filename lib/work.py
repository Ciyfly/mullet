#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-10 10:50:05
LastEditors: recar
LastEditTime: 2022-03-18 17:40:48
'''

from queue import PriorityQueue, Queue
from queue import Empty
from datetime import datetime
from lib.log import logger
import threading
import traceback
import signal
import sys


def ctrl_c(signum, frame):
    print()
    print("ctrl c")
    sys.exit()
# ctrl+c
signal.signal(signal.SIGINT, ctrl_c)

class BaseWorker(object):
    def __init__(self, consumer_func, consumer_count=1, block=True):
        self.logger = logger
        self.consumer_count = consumer_count
        self.block = block
        if self.block:
            self.timeout = None
        else:
            self.timeout = 3
        self.work_queue = Queue()
        self.run(consumer_func)

    def put(self, item):
        '''
        @params item 数据
        '''
        try:
            if type(item) == list:
                for d in item:
                    self.work_queue.put(d)
            else:
                self.work_queue.put(item)
        except Exception:
            self.logger.error(traceback.format_exc()) 


    def consumer(self, func):
        '''
        消费者
        @params func 消费者函数
        '''
        while True:
            try:
                item = self.work_queue.get(timeout=self.timeout)
                func(item)
            except Empty:
                return
            except Exception:
                self.logger.error("consumer error: {0}".format(traceback.format_exc()))

    def is_end(self):
        '''
        队列是否空的并且线程永远不会结束那怎么判断任务结束
        '''
        if self.work_queue.qsize() !=0:
            return False
        # 线程是否都结束了
        count = self.consumer_count
        for t in self.threads:
            if not t.isAlive():
                count -=1
        if count ==0:
            return True
        return False

    def run(self, consumer_func):
        '''
        运行方法
        @params consumer_func 消费者函数
        '''
        self.threads = []
        for i in range(self.consumer_count):
            t = threading.Thread(target=self.consumer,args=(consumer_func,))
            t.setDaemon(True)
            t.start()
            self.threads.append(t)

class Worker(BaseWorker):
    '''普通消费队列'''
    def __init__(self, consumer_func, consumer_count=1, block=True):
        super(Worker, self).__init__(consumer_func, consumer_count=consumer_count, block=block)


class WorkerPrior(BaseWorker):
    '''优先消费队列'''
    def __init__(self, consumer_func, consumer_count=1, block=True):
        super(WorkerPrior, self).__init__(consumer_func, consumer_count=consumer_count, block=block)
        self.work_queue = PriorityQueue()

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
        except Exception:
            self.logger.error(traceback.format_exc()) 

    def consumer(self, func):
        '''
        消费者
        @params func 消费者函数
        '''
        while True:
            item = self.work_queue.get()
            try:
                func(item[1])
            except Exception:
                self.logger.error("consumer error: {0}".format(traceback.format_exc()))


class LimitWork(BaseWorker):
    '''
    限流work
    '''
    def __init__(self, consumer_func, consumer_count=1, block=True):
        super(LimitWork, self).__init__(consumer_func, consumer_count=consumer_count, block=block)

    def consumer(self, func, limit_time=1):
        '''
        消费者
        @params func 消费者函数
        @params limit_time 限流的每个work的时间限制 默认1s
        '''
        last_time = None
        while not self.work_queue.empty():
            item = self.work_queue.get(timeout=3)
            if item is None:
                break
            while True:
                current_time = datetime.now()
                if last_time is None or (current_time-last_time).seconds >=limit_time:
                    print("send: {0}".format(current_time.strftime('%Y-%m-%d %H:%M:%S %f')))
                    func(item)
                    last_time = current_time
                    break
                else:
                    continue


class WorkData(object):
    '''
    传递到queue的标准数据
    '''
    @property
    def plugin_name(self):
        return self._plugin_name
    @plugin_name.setter
    def plugin_name(self, plugin_name):
        self._plugin_name = plugin_name

    @property
    def poc_name(self):
        return self._poc_name
    @poc_name.setter
    def poc_name(self, poc_name):
        self._poc_name = poc_name

    @property
    def url_info(self):
        return self._url_info

    @url_info.setter
    def url_info(self, url_info):
        self._url_info = url_info
        self.ip = url_info.get("server_ip")
        self.port = url_info.get("server_port")
        self.ssl = False
        if "https:" in url_info.get('url'):
            self.ssl = True

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def req(self):
        return self._req

    @req.setter
    def req(self,req):
        self._req = req
    
    @property
    def rsp(self):
        return self._rsp

    @rsp.setter
    def rsp(self, rsp):
        self._rsp = rsp

    @property
    def condition(self):
        return self._condition

    @condition.setter
    def condition(self, condition):
        self._condition = condition

class ResultInfo(object):
    '''
    标准的结果数据
    '''
    def __init__(self,plugins, url, payload, req, rsp, desc):
        self._plugin_name = plugins
        self._url = url
        self._payload = payload
        self._req = req
        self._rsp = rsp
        self._desc = desc

    @property
    def plugins(self):
        return self._plugin_name
    @plugins.setter
    def plugins(self, plugins):
        self._plugin_name = plugins

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, payload):
        self._payload = payload

    @property
    def req(self):
        return self._req

    @req.setter
    def req(self, req):
        self._req = req

    @property
    def rsp(self):
        return self._rsp

    @rsp.setter
    def rsp(self, rsp):
        self._rsp = rsp

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, desc):
        self._desc = desc
