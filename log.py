#!/usr/bin/env python
#coding:utf8

import os
import logging
from common_func import current_file_directory

class Log:
    def __init__(self, logname="", logLevel=logging.DEBUG):
        """日志文件默认等级为WARNING(logging.NOTSET)"""
        # 创建一个logger
        self.logger = logging.getLogger(logname)
        # 控制所有日志输出，对各个Handler也可以指定对应的日志等级。
        self.logger.setLevel(logLevel)

    def init(self):
        """如果同时需要定向输出，可以写在这个函数里。"""
        pass
        
    def streamHandler(self,
                      logLevel=logging.DEBUG,
                      fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
        """输出日志信息到控制台"""
        # 创建输出到控制台的handler
        sh =  logging.StreamHandler()
        # 设置日志输出等级
        sh.setLevel(logLevel)
        # 设置日志输出格式
        sh.setFormatter(logging.Formatter(fmt))
        # 绑定到logger
        self.logger.addHandler(sh)
        
    def fileHandler(self, 
                    fpath="app.log", 
                    logLevel=logging.DEBUG, 
                    fmt='%(asctime)s - %(name)s - %(levelname)s - %(thread)d - %(module)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s'):
        """输出日志信息到文件"""
        self.logpath(fpath)
        # 创建文件handler
        fh = logging.FileHandler(fpath)
        # 日志等级s
        fh.setLevel(logLevel)
        # 日志格式
        fh.setFormatter(logging.Formatter(fmt))
        # 绑定
        self.logger.addHandler(fh)
    
    def rotatingFileHandler(self, 
                            fpath="app.log", 
                            maxBytes=10*1024*1024,
                            backupCount=5,
                            logLevel=logging.INFO,
                            fmt='%(asctime)s - %(name)s - %(levelname)s - %(thread)d - %(module)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s'):
        """创建回滚日志格式，默认日志文件大小为10M，最多5个日志文件"""
        self.logpath(fpath)
        # 创建回滚日志句柄
        from logging.handlers import RotatingFileHandler
        rh = RotatingFileHandler(fpath, maxBytes=maxBytes, backupCount=backupCount)
        rh.setLevel(logLevel)
        rh.setFormatter(logging.Formatter(fmt))
        self.logger.addHandler(rh)

    def timeRotatingFileHandler(self,
                                fpath="app.log",
                                logLevel=logging.DEBUG,
                                fmt='%(asctime)s - %(name)s - %(levelname)s - %(thread)d - %(module)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s',
                                when="midnight",
                                backupCount=5):
        """创建时间回滚日志，默认时间为每天临晨更新一个文件，默认为5个日志文件"""
        self.logpath(fpath)
        # 创建时间回滚日志句柄
        from logging.handlers import TimedRotatingFileHandler
        th = TimedRotatingFileHandler(fpath, when=when, interval=1, backupCount=backupCount)
        th.setLevel(logLevel)
        th.setFormatter(logging.Formatter(fmt))
        self.logger.addHandler(th)

    def logpath(self, fpath):
        """尝试建立日志文件所在目录及日志文件"""
        if not os.path.isabs(fpath):
            fpath = os.path.join(current_file_directory(), fpath)
        dirname = os.path.dirname(fpath)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        if not os.path.isfile(fpath):
            with open(fpath, "w") as fp:
                fp.close()


def testOne():
    l = Log(logname="log")
    l.streamHandler()
    l.fileHandler(fpath="Log/test.log")

    l.logger.debug("Debug.")
    l.logger.info("Info.")
    l.logger.warning("Waring.")
    l.logger.error("Error.")
    l.logger.critical("Critical.")

def testRotate():
    l = Log(logname="log")
    l.rotatingFileHandler(fpath="Log/test.log", maxBytes=1*1024*1024)
    
    log = l.logger.error
    i = 0
    while 1:
        i += 1
        tmp = i % 100
        string = "*"*tmp,"--",str(tmp)
        log(string)

def testTimeRote():
    l = Log(logname="log")
    l.timeRotatingFileHandler(fpath="Log\MaLog", when='M')
    
    log = l.logger.info
    i = 0
    import time
    while 1:
        time.sleep(1/100)
        i += 1
        tmp = i % 100
        string = "*"*tmp,"--",str(tmp)
        log(string)     

if __name__ == "__main__":
    testOne()
    # testRotate()
    #testTimeRote()
   
