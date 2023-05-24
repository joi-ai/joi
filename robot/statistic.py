# -*- coding: utf -8-*-

from . import config
import uuid
import requests
import threading


def getUUID():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e : e + 2] for e in range(0, 11, 2)])


def report(t):
    ReportThread(t).start()


class ReportThread(threading.Thread):
    def __init__(self, t):
        # 需要执行父类的初始化方法
        threading.Thread.__init__(self)
        self.t = t

    def run(self):
        pass
