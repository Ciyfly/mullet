#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-01-14 15:23:56
LastEditors: recar
LastEditTime: 2022-01-14 17:02:33
'''

class TaskQueueMap(object):
    def __init__(self):
        self.task_queue_map = dict()

def init():
    return TaskQueueMap()

taskqueue = init()
