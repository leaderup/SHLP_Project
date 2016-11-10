#!/usr/bin/env python
#coding: utf8

import os
import re
import sys
import time
import traceback
from log import Log
from bs4 import BeautifulSoup, UnicodeDammit
from collections import OrderedDict
from threading import Thread
from common_func import current_file_directory

# 页面大小
min_page_length = 3000

def myLog():
    l = Log(logname="LouPan")
    l.streamHandler()
    l.fileHandler(fpath="MaLog.txt")
    return l.logger
lplog = myLog()

def clearString(string, encoding="utf-8", blank_to_one=re.compile("\s+")):
    string = string.replace(u"\xa0", "").replace(u'\u2002', "").replace(u"　", "")
    string = blank_to_one.sub(" ", string)
    return string

def scan(name):
    """
    扫描当前目录下的模块
    """
    sys.path.append(name)
    
    result = {}
    pwd = current_file_directory()

    # 模块路径
    module_path = os.path.join(pwd, name)
    if not os.path.isdir(module_path):
        os.makedirs(module_path)
    result["mpath"] = module_path

    # 数据存储数据
    datadir = os.path.join(pwd, "data", name)
    if not os.path.isdir(datadir):
        os.makedirs(datadir)
    #datadir = os.path.join(r"F:\SHLP\Source\data", name)
    result["dpath"] = datadir

    # 页面存储路径
    pattern = r"(item_\d+)\.py$"
    recompile = re.compile(pattern)
    list_file = os.listdir(module_path)
    ufile = filter(recompile.match, list_file)
    models = [x[:-3] for x in ufile]
    models.sort()
    model_objs = map(lazy_import, models)
    result["models"] = model_objs
    
    # URL导入路径
    urlname = "loadurl"
    urlmodel = os.path.join(module_path, "%s.py" % urlname)
    if os.path.isfile(urlmodel):
        result["urlmodel"] = lazy_import(urlname)

    return result

class lazy_import:
    """
    延时加载模块
    m = lazy_import("name")
    m.func()
    """
    def __init__(self, module_name):
        self.module_name = module_name
        self.module = None
    
    def __getattr__(self, name):
        if self.module is None:
            self.module = __import__(self.module_name)
        return getattr(self.module, name)

class mThread(Thread):
    def __init__(self, iqueue, modelobj, log):
        super(mThread, self).__init__()
        self.task_list = OrderedDict()
        self.iqueue = iqueue
        self.mlog = log
        self.datadir = modelobj['dpath']
        if not os.path.isdir(self.datadir):
            os.makedirs(self.datadir)
        self.init(modelobj['models'])

    def init(self, modules):
        for module in modules:
            self.addtask(module)

    def run(self):
        loginfo = u"mThread %s analysis html page thread start." % self.getName()
        self.mlog.debug(loginfo)

        empty_execution = 0
        interative = 10
        time.sleep(interative)
        while 1:
            if not self.isAlive():
                break
            try:
                info = self.iqueue.get_nowait()
            except:
                if empty_execution:
                    loginfo = u"mThread %s wait page to analysis, using time %s(s)" % (self.getName(), interative*empty_execution)
                    self.mlog.debug(loginfo)
                time.sleep(interative)
                empty_execution += 1
                if empty_execution > 30:
                    break
            else:
                empty_execution = 0
                # #注释
                """
                if info:
                    self.mlog.info("get %s" % info['url'])
                    time.sleep(1)
                """

                self._info = info
                if "webtype" in info:
                    webtype = info['webtype']
                else:
                    webtype = None
                if webtype == u"json":
                    self.workwithjson()
                elif webtype == u"download":
                    self.workForDown()
                else:
                    self.work()
                del self._info

        loginfo = "mThread: %s analysis thread stop." % self.getName()
        self.mlog.info(loginfo)

    def stop(self):
        self.__stop()

    def workForDown(self):
        info = self._info
        self.url = info['url']
        content = info['content']
        task_list = self.task_list
        if task_list:
            whole_judgement = False
            for modelobj in task_list.keys():
                infohead = "url: %s, " % self.url
                # 判断页面类型
                dealContent = getattr(modelobj, "dealContent")
                try:
                    dealContent(info)
                except:
                    loginfo = "%s %s" % (infohead, traceback.format_exc())
                    self.mlog.error(loginfo)

            # 完成后更新
            if hasattr(modelobj, "completeTask"):
                complete = getattr(modelobj, "completeTask")
                try:
                    complete(info, whole_judgement, self.datadir)
                except:
                    loginfo += traceback.format_exc()
                    self.mlog.error(loginfo)
        else:
            loginfo = "The tasklist has no task, please check you code."
            self.mlog.critical(loginfo)


    def workwithjson(self):
        info = self._info
        self.url = info['url']
        content = info['content']
        if self.task_list:
            infohead = "URL: %s\n" % self.url
            modelobj = self.task_list.keys()[0]
            jsonfunc = getattr(modelobj, "treatment")
            if jsonfunc:
                retbool, retinfo = jsonfunc(info, self.datadir)
                loginfo = "%s%s" % (infohead, retinfo)
                if retbool:
                    self.mlog.info(loginfo)
                else:
                    self.mlog.error(loginfo)
            else:
                loginfo = "No json function to deal with json series."
                self.mlog.critical(loginfo)
        else:
            loginfo = "The tasklist has no task, please check you code."
            self.mlog.critical(loginfo)

    def work(self):
        info = self._info
        self.url = info['url']
        content = info['content']
        if 'page_type' not in info or info['page_type'] != 1:
            # 专为相册写的
            detect = UnicodeDammit(content)
            encoding = detect.original_encoding
            info["encoding"] = encoding
            soup = BeautifulSoup(content, "html5lib", from_encoding=encoding)
            # soup = BeautifulSoup(content, "lxml")
            info['soup'] = soup
        task_list = self.task_list
        if task_list:
            whole_judgement = False
            infohead = "url: %s, " % self.url
            for modelobj in task_list.keys():
                # 判断页面类型
                judge = getattr(modelobj, "jdugePage")
                retcode, retinfo = judge(info)
                if not retcode:
                    loginfo = "%s %s" % (infohead, retinfo)
                    self.mlog.error(loginfo)
                    continue
                else:
                    # 提取页面值
                    analysis = getattr(modelobj, "analysisPage")
                    try:
                        analysis(info, self.datadir)
                        whole_judgement = True
                        break
                    except:
                        try:
                            loginfo = "%s %s" % (infohead, traceback.format_exc())
                            self.mlog.error(loginfo)
                        except:
                            loginfo = "%s %s" % (infohead, traceback.format_exc())
                            self.mlog.error(loginfo)

            # 完成后更新
            if hasattr(modelobj, "completeTask"):
                complete = getattr(modelobj, "completeTask")
                try:
                    complete(info, whole_judgement, self.datadir)
                except:
                    loginfo = "%s %s" % (infohead, traceback.format_exc())
                    self.mlog.error(loginfo)
        else:
            loginfo = "The tasklist has no task, please check you code."
            self.mlog.critical(loginfo)

        #time.sleep(1)

    def addtask(self, method):
        task_list = self.task_list
        task_list[method] = None
