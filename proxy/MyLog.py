# -*- coding:utf-8 -*-
__author__ = 'fremcode@gmail.com'

import logging
import datetime


class MyLog():
    #path->log路径
    #name->log文件前缀(生成的日志文件名格式为MyLog20141112.log格式)
    #type->log名称
    #level->log文件级别(DEBUG,INFO,WARNING,ERROR,CRITICAL),默认为DEBUG可存储所有级别日志
    def __init__(self, path='', name='MyLog', type='default', level='DEBUG'):
        nowDate = datetime.date.today()
        self.logFile = path + name + '_' + str(nowDate) + '.log'
        logLevel = getattr(logging, level)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(type)
        self.logger.setLevel(logLevel)

    def debug(self, msg):
        fp = logging.FileHandler(self.logFile)
        fp.setLevel(logging.DEBUG)
        fp.setFormatter(self.formatter)
        self.logger.addHandler(fp)
        self.logger.debug(msg)
        self.logger.removeHandler(fp)

    def info(self, msg):
        fp = logging.FileHandler(self.logFile)
        fp.setLevel(logging.DEBUG)
        fp.setFormatter(self.formatter)
        self.logger.addHandler(fp)
        self.logger.info(msg)
        self.logger.removeHandler(fp)

    def warning(self, msg):
        fp = logging.FileHandler(self.logFile)
        fp.setLevel(logging.DEBUG)
        fp.setFormatter(self.formatter)
        self.logger.addHandler(fp)
        self.logger.warning(msg)
        self.logger.removeHandler(fp)

    def error(self, msg):
        fp = logging.FileHandler(self.logFile)
        fp.setLevel(logging.DEBUG)
        fp.setFormatter(self.formatter)
        self.logger.addHandler(fp)
        self.logger.error(msg)
        self.logger.removeHandler(fp)

    def critical(self, msg):
        fp = logging.FileHandler(self.logFile)
        fp.setLevel(logging.DEBUG)
        fp.setFormatter(self.formatter)
        self.logger.addHandler(fp)
        self.logger.critical(msg)
        self.logger.removeHandler(fp)


#测试方法
def test_except():
    log = MyLog('360')
    try:
        num = 2
        string = 'test' + num
    except Exception, e:
        log.info(e)


if __name__ == '__main__':
    test_except()
