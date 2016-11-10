#!/usr/bin/env python
#coding: utf8

import sys
import time
from log import Log
from utils import scan, lazy_import, mThread
# from Queue import Queue
from multiprocessing import Process, Queue, Manager
from threading import Thread
from urlManage import urlproxy

# ls |wc -l && rm -fr $(ll | awk '{if($5 < 3000){print $9}}' ) && ls |wc -l

# 日志
def myLog(name):
    l = Log(logname="LouPan.%s" % name)
    l.streamHandler()
    l.fileHandler(fpath="Log/Ma%s.log" % name)
    return l.logger
mlog = None

# url进程
urlWorks = 1
# 处理进程
dealWorks = 1

def catchHomePage(uin, uout):
    module_names = [
        "HomePage",
        "HouseCounts",
        "LoupanLink",       # 城市链接 2
        "LoupanHomepage",   # 首页 3
        "XQPageLouPan",     # 详情页 4
        "PhotoLouPanStageOne",      # 相册页 - 相册类型与总数 5
        "PhotoLouPanStageTwo",      # 相册页 - 页面类型为1，Ajax请求相册页面 6
        "PhotoLouPanStageThree",      # 相册页 - 相片下载 7
    ]
    module_name = module_names[7]
    threads = []
    # 模块日志
    global mlog
    mlog = myLog(module_name)

    modelobj = scan(module_name)
    dataDir = modelobj['dpath']

    # 导入URL
    luobj = modelobj['urlmodel']
    urlmodel = luobj.urlput
    for i in range(urlWorks):
        product = Thread(target=urlmodel, args=(uin, dataDir, mlog))
        product.setDaemon(True)
        product.start()
        threads.append(product)
    
    # 判断逻辑
    for i in range(dealWorks):
        cusumer = mThread(uout, modelobj, mlog)
        cusumer.setDaemon(True)
        cusumer.start()
        threads.append(cusumer)

    return threads

def joinprocess(threads):
    global mlog
    for thread in threads:
        thread.join()
    
    loginfo = "main process finish."
    mlog.info(loginfo)

def main():
    # 寻找模块
    # 从模块中拿取特定函数
    # 执行塞url线程
    # 取出content内容
    # 进入模块分析阶段
    # 依次进行判断，成功则存储数据并返回
    # 全失败了，说明无效页面，记录数据状态    
    pass

if __name__ == "__main__":
    debug = 1
    manager = Manager()
    uin = manager.Queue(maxsize=300)
    uout = manager.Queue(maxsize=200)

    allthread = catchHomePage(uin, uout)

    if debug == 1:
        process = Process(target=urlproxy, args=(uin, uout))
        process.start()

    joinprocess(allthread)
    print "finish join process"
    if debug == 1:
        process.join()
    print "finish."
