#!/usr/bin/env python
#coding: utf8

"""
主url函数: urlput
"""

import sys
sys.path.append("../")
import os
import time
import logging
from pypinyin import lazy_pinyin
from utils import lplog

"""
    alltown.txt 文本格式
"""

def loadInfo(datadir):
    # 导入消费城市列表
    fname = "SoufunFamily_obj.txt"
    fpath = os.path.join(datadir, fname)
    try:
        with open(fpath) as f:
            content = f.read()
            f.close()
        return eval(content)
    except:
        print "city objfile: %s not found!" % fpath

def filterCity(datadir):
    # 添加过滤城市
    alltown = set()
    fname = "alltown.txt"
    fpath = os.path.join(datadir, fname)
    try:
        with open(fpath) as f:
            lines = f.readlines()
            f.close()
        for line in lines:
            line = line.strip().decode('utf8')
            alltown.add(line)
        return alltown
    except:
        return set()

def clearOldFile(dataDir):
    # 清理文件
    # town_total.txt
    fpath = os.path.join(dataDir, "town_total.txt")
    if os.path.isfile(fpath):
        os.unlink(fpath)

def urlput(urlqueue, datadir, log=logging.getLogger("urlput")):
    # 清理town_total.txt
    clearOldFile(datadir)
    allcity = loadInfo(datadir)
    filtercity = filterCity(datadir)
    for line in allcity:
        info = line
        city_name = line['city']
        if city_name not in filtercity:
            continue

        curl = info['shortname']
        if city_name == u"北京":
            curl = u"http://newhouse.fang.com/house/s/"
        if not curl.startswith(u"http:"):
            city_url = u"http://newhouse.%s.fang.com/house/s/" % curl
        else:
            city_url = curl

        # 输入元素
        info['url'] = city_url
        storepath = "_".join(["".join(lazy_pinyin(info['prov'])), "".join(lazy_pinyin(info['city']))])
        info['urlpath'] = os.path.join(datadir, "%s.html" % storepath)
        urlqueue.put(info)

if __name__ == "__main__":
    datadir = r"D:\PythonProgram\SHLouPan\data\HouseCounts"
    d = loadInfo(datadir)
    f = filterCity(datadir)
    print "Hello World"
